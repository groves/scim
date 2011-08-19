# Majority of the functionality of the scim plugin. It's out in its own module to namespace it
# from Vim's shared Python interpreter
import os, subprocess, vim

def openfound(found, over=False):
    if found.endswith('.html'):
        subprocess.check_call(['open', found])
    else:
        if over:
            vim.command("wincmd p")
        vim.command("edit " + found)

def vimexec(cmd):
    vim.command("let ignored=" + cmd)

def vimexists(val):
    return bool(int(vim.eval('exists("%s")' % val)))

def locs():
    return vim.eval("g:scim_locations")

class Scim(object):
    def __init__(self):
        self.last_paths = []
        self.classname_to_full = {}
        self.choices = {}
        self.lastchoice = None

    def jump(self, over=False):
        self.navigate(vim.eval('expand("<cword>")'), over)

    def open(self, fullclass):
        for possible, loc in self.lookup(fullclass.split('.')[-1]):
            if possible == fullclass:
                openfound(loc)

    def navigate(self, dest, over):
        found = self.choose(dest)
        if found:
            openfound(found[1], over)
        else:
            print "Nothing found for", dest

    def addimport(self):
        found = self.choose(vim.eval('expand("<cword>")'))
        if found:
            toimport = found[0]
            if vim.eval('bufname("%")').endswith('.java'):
                toimport += ";"
            vim.command('let s:startpos = getpos(".")')
            vimexec("cursor(0, 0)")# Search for package from the beginning
            vim.command("let packageline = search('^package ', 'c')")
            vimexec('append(packageline + 1, "import %s")' % toimport)
            vimexec("cursor(s:startpos[1] + 1, s:startpos[2])")

    def lookup(self, classname, scan_if_not_found=True):
        if (scan_if_not_found and not classname in self.classname_to_full) or self.scanneeded():
            if not self.scan():
                return None, None
        return sorted(self.classname_to_full.get(classname, set()))

    def list_classes(self):
        if self.scanneeded():
            self.scan()
        classes = []
        for entries in self.classname_to_full.values():
            classes.extend([f[0] for f in entries])
        return classes

    def choose(self, classname, scan=True):
        fulls = self.lookup(classname, scan)
        if fulls == None:
            return None
        if len(fulls) == 0:
            if scan:
                print "No classes found for '%s'" % classname
            return None

        if len(fulls) == 1:
            idx = "1"
        elif classname in self.choices:
            choice = self.choices[classname]
            print "Reused last choice %s. Use <leader>r to clear the cache" % choice[0]
            return choice
        else:
            print "Multiple classes found for", classname
            for idx, full in enumerate(fulls):
                print idx + 1, full[0]
            idx = vim.eval('input("Class number or blank to abort: ")')
            if idx is None or idx.strip() == "":
                return None
        idx = int(idx) - 1
        self.choices[classname] = fulls[idx]
        self.lastchoice = classname
        return fulls[idx]

    def scanneeded(self):
        return self.last_paths != locs() or not self.classname_to_full

    def scan(self):
        if not vimexists("g:scim_locations"):
            print "Set 'g:scim_locations' to a list of as paths"
            return False
        self.classname_to_full.clear()
        for path in locs():
            path = os.path.abspath(os.path.expanduser(path))
            if os.path.isdir(path) and 'docs' in path:
                self.addclasses(scan_doc_dir(path))
            elif os.path.isdir(path) and 'src' in path:
                self.addclasses(scan_src_dir(path))
            else:
                print "Don't know how to handle", path
        self.last_paths = locs()
        return True

    def addclasses(self, classes):
        for fullname, path in classes:
            simplename = fullname.split('.')[-1]
            if simplename not in self.classname_to_full:
                self.classname_to_full[simplename] = set()
            self.classname_to_full[simplename].add((fullname, path))

i = Scim()

pathtofull = lambda path: '.'.join(path.split('/'))

def scan_src_dir(base):
    for d, dns, fns in os.walk(base):
        try:
            dns.remove('.svn')
        except:
            pass
        package = pathtofull(d[len(base) + 1:]) + "."
        for fn in fns:
            yield package + fn.split('.')[0], d + "/" + fn

def scan_doc_dir(base):
    for d, dns, fns in os.walk(base):
        try:
            dns.remove('class-use')
        except:
            pass
        package = pathtofull(d[len(base) + 1:]) + "."
        for fn in fns:
            # - gets all the java overview bidness
            if not fn.endswith('.html') or '-' in fn or fn == 'index.html':
                continue
            yield package + fn[:-5].replace('$$', '.'), d + "/" + fn
