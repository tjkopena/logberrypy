#!python3

import logberry

@logberry.wrap
class Sushi:
    @logberry.wrap
    def __init__(self):
        self.log.info("INIT")

    @logberry.wrap
    def mycall(self):
        logberry.log().info("wrapped")
        self.log.info("In mycall")

@logberry.wrap
def foo(log=None):
    log.info("HELP")
    return 4

logberry.start()

t = logberry.task("Outer", rule="Bananana")
x = logberry.task("Inner")
foo()

y = logberry.task("MORE Inner")
y.end()

x.end()
t.end()

s = Sushi()
s.mycall()

logberry.stop()
