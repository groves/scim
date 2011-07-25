import sbtrunner, subprocess, vim

class ResultLoadingSbt(sbtrunner.Sbt):
    def executed(self, cmd):
        # We should be doing the following while using the real multiprocessing module in sbtrunner
        # However, doing so just prints "ScimPostCompile()" to the terminal that launched vim.
        # Who knows? Using threading and calling directly as the uncommented line does kinda works,
        # but it complains about some bad NSAutorelease action. I guess there's no way to make this
        # horse dance.
        #subprocess.check_call(["vim", "--remote-expr", "'ScimPostCompile()'"])
        vim.command('call ScimPostCompile()')

class SbtContext(object):
    def __init__(self, location):
        self.proc, self.conn = sbtrunner.start(location, ResultLoadingSbt)
        self.location = location
        self.compilerunning = False

    def exit(self):
        self.conn.send("exit")
        self.proc.join()

    def compile(self):
        self.conn.send("compile")
        self.compilerunning = True

ctx = None

def valexists(val):
    return bool(int(vim.eval('exists("%s")' % val)))

def compile():
    global ctx
    if not valexists("g:scim_sbt_dir"):
        print "Set 'g:scim_sbt_dir' to where sbt should be run"
        return
    location = vim.eval("g:scim_sbt_dir")
    if ctx is not None:
        if ctx.compilerunning:
            print "Compile running; wait for it to finish"
            return
        elif ctx.location != location:
            print "Restarting sbt in '%s'" % location
            exit()
    if ctx is None:
        ctx = SbtContext(location)
    ctx.compile()
    vim.command("redraw")
    print "Compiling"

def exit():
    global ctx
    if ctx is not None:
        ctx.exit()
        ctx = None

def loadcompileresults():
    if ctx is None or not ctx.compilerunning:
        print "Call compile before calling loadcompileresults"
        return
    results = ctx.conn.recv()
    ctx.compilerunning = False
    vim.command('cexpr %s' % results)
    print "Compile finished"

