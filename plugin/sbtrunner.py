import os, multiprocessing, multiprocessing.connection, re, subprocess, sys

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
        self.proc = subprocess.Popen(["sbt"], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def waitforinput(self):
        debug("Waiting for sbt to be ready for input")
        output = [""]
        while True:
            char = self.proc.stdout.read(1)
            sys.stdout.write(char)
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


class Server(object):
    def __init__(self):
        self.subsbt = None
        self.conn = None
        self.sbtdir = None
        self.listener = multiprocessing.connection.Listener(('localhost', 6000))

    def handleCmd(self):
        lconn = self.listener.accept()
        try:
            received, cmddir, resultcommand, outputlocation = lconn.recv()
        finally:
            lconn.close()
        if received == "exit":
            self.exit()
            return
        if cmddir != self.sbtdir:
            self.exit()
            self.subsbt, self.conn = start(cmddir)
            self.sbtdir = cmddir
        self.conn.send(received)
        debug("Writing to %s" % outputlocation)
        open(outputlocation, "w").write("\n".join(self.conn.recv()))
        subprocess.call(resultcommand, shell=True)

    def exit(self):
        if self.sbtdir:
            self.conn.send("exit")
            self.subsbt.join()
        self.sbtdir = None

if __name__ == "__main__":
    server = Server()
    try:
        while True:
            server.handleCmd()
    except KeyboardInterrupt:
        pass
    finally:
        server.exit()
