import os, multiprocessing, re, subprocess

ansi = re.compile("\\x1b\[\d+?m") # -Dsbt.nologformat isn't being respected, so strip ansi colors

debugout = None
debugout = open("/tmp/sbt-runner.debug", "w", 0)
def debug(msg):
    if debugout is None:
        return
    debugout.write("%s\n" % msg)

def run(conn, sbtdir, runnerClass):
    os.chdir(sbtdir)
    runnerClass(conn).run()

class Sbt(object):
    def __init__(self, conn):
        self.conn = conn
        self.proc = subprocess.Popen(["sbt", "-Dsbt.nologformat=true"], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def waitforinput(self):
        debug("Waiting for sbt to be ready for input")
        output = [""]
        while True:
            char = self.proc.stdout.read(1)
            if output[-1] == "" and char == ">":
                return output[:-1]
            if char == "\n":
                output[-1] = ansi.sub("", output[-1])
                output.append("")
            else:
                output[-1] = output[-1] + char

    def executed(self, cmd):
        pass

    def run(self):
        self.waitforinput()
        debug("Ready")
        while True:
            cmd = self.conn.recv()
            debug("Running %s" % cmd)
            self.proc.stdin.write("%s\n" % cmd)
            if cmd == "exit":
                break
            result = self.waitforinput()
            debug(result)
            self.conn.send(result)
            self.executed(cmd)
        debug("Exiting")
        self.proc.communicate()

def start(sbtdir, runnerClass=Sbt):
    parentconn, childconn = multiprocessing.Pipe()
    subsbt = multiprocessing.Process(target=run,
            args=(childconn, os.path.expanduser(sbtdir), runnerClass))
    subsbt.start()
    return subsbt, parentconn

if __name__ == "__main__":
    subsbt, conn = start("/Users/charlie/dev/ionic")
    conn.send("compile")
    print conn.recv()
    conn.send("exit")
    subsbt.join()
