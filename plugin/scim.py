# Majority of the functionality of the scim plugin. It's out in its own module to namespace it
# from Vim's shared Python interpreter
import os, subprocess, vim

def cursorword():
    start = vim.eval('getpos(".")')
    vim.command("normal wbyw")
    return vim.eval("getreg()").strip(), start

def open():
    vim.command('let theUsersInput=input("Class to open: ")')
    result = vim.eval("theUsersInput")
    if result is None or result.strip() == "":
        return
    navigate(result, False)

def jump(over=False):
    navigate(cursorword()[0], over)

def open_full_class(fullclass):
    for possible, loc in classname_to_full[fullclass.split('.')[-1]]:
        if possible == fullclass:
            openfound(loc)

def navigate(dest, over):
    found = choose_lookup(dest)
    if found:
        openfound(found[1], over)
    else:
        print "Nothing found for", dest

def openfound(found, over=False):
    if found.endswith('.html'):
        subprocess.check_call(['open', found])
    else:
        if over:
            vim.command("wincmd p")
        vim.command("edit " + found)

def addimport():
    classname, start = cursorword()
    found = choose_lookup(classname)
    if found:
        toimport = found[0]
        if vim.eval('bufname("%")').endswith('.java'):
            toimport += ";"
        vimexec("cursor(0, 0)")# Search for package from the beginning
        vim.command("let packageline = search('^package ', 'c')")
        vimexec('append(packageline + 1, "import %s")' % toimport)
        vimexec("cursor(%s + 1, %s)" % (start[1], start[2]))

def vimexec(cmd):
    vim.command("let ignored=" + cmd)

def valexists(val):
    return bool(int(vim.eval('exists("%s")' % val)))

last_lookup_paths = []
classname_to_full = {}
def lookup(classname, scan_if_not_found=True):
    if (scan_if_not_found and not classname in classname_to_full) or scanneeded():
        if not scan():
            return None, None
    return sorted(classname_to_full.get(classname, set()))

def list_classes():
    if scanneeded():
        scan()
    classes = []
    for entries in classname_to_full.values():
        classes.extend([f[0] for f in entries])
    return classes

def choose_lookup(classname, scan=True):
    fulls = lookup(classname, scan)
    if fulls == None:
        return None
    if len(fulls) == 0:
        if scan:
            print "No classes found for '%s'" % classname
        return None

    if len(fulls) == 1:
        idx = "1"
    else:
        print "Multiple classes found for", classname
        for idx, full in enumerate(fulls):
            print idx + 1, full[0]
        vim.command('let idx=input("Class number or blank to abort: ")')
        idx = vim.eval("idx")
        if idx is None or idx.strip() == "":
            return None
    return fulls[int(idx) - 1]

def locs():
    return vim.eval("g:scim_locations")

def scanneeded():
    return last_lookup_paths != locs() or not classname_to_full

def scan():
    if not valexists("g:scim_locations"):
        print "Set 'g:scim_locations' to a list of as paths"
        return False
    classname_to_full.clear()
    for path in locs():
        path = os.path.abspath(os.path.expanduser(path))
        if os.path.isdir(path) and 'docs' in path:
            addclasses(scan_doc_dir(path))
        elif os.path.isdir(path) and 'src' in path:
            addclasses(scan_src_dir(path))
        else:
            print "Don't know how to handle", path
    global last_lookup_paths
    last_lookup_paths = locs
    return True

def addclasses(classes):
    for fullname, path in classes:
        simplename = fullname.split('.')[-1]
        if simplename not in classname_to_full:
            classname_to_full[simplename] = set()
        classname_to_full[simplename].add((fullname, path))

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
