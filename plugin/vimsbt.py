import sbtrunner, subprocess, vim

class ResultLoadingSbt(sbtrunner.Sbt):
    def executed(self, cmd):
        # We should be doing the following instead of using shell, but  doing so just prints
        # "ScimPostCompile()" to the terminal that launched vim. Who knows?
        #subprocess.check_call(["/usr/local/bin/vim", "--remote-expr", "'ScimPostCompile()'"])
        subprocess.check_call("vim --remote-expr 'ScimPostRun()'", shell=True)

class SbtContext(object):
    def __init__(self, location):
        self.proc, self.conn = sbtrunner.start(location, ResultLoadingSbt)
        self.location = location
        self.runningcmd = None

    def exit(self):
        self.conn.send("exit")
        self.proc.join()

    def run(self, cmd):
        self.conn.send(cmd)
        self.runningcmd = cmd

ctx = None

def valexists(val):
    return bool(int(vim.eval('exists("%s")' % val)))

def run(cmd):
    global ctx
    if not valexists("g:scim_sbt_dir"):
        print "Set 'g:scim_sbt_dir' to where sbt should be run"
        return
    location = vim.eval("g:scim_sbt_dir")
    if ctx is not None:
        if ctx.runningcmd:
            print "Running %s; wait for it to finish" % ctx.runningcmd
            return
        elif ctx.location != location:
            print "Restarting sbt in '%s'" % location
            exit()
    if ctx is None:
        ctx = SbtContext(location)
    ctx.run(cmd)
    vim.command("redraw")
    print "Running", cmd

def exit():
    global ctx
    if ctx is not None:
        ctx.exit()
        ctx = None

def loadrunresults():
    if ctx is None or not ctx.runningcmd:
        print "Run a ccommand before calling loadrunresults"
        return
    results = ctx.conn.recv()
    cmd = ctx.runningcmd
    ctx.runningcmd = None
    vim.command('cexpr %s' % results)
    vim.command("redraw")
    print "Finished", cmd

