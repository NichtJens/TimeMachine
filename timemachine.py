#!/usr/bin/env python

from copy import deepcopy


def altering(f):
    def n(self, *args, **kwargs):
        self.commands.append((f, args, kwargs))
        f(self, *args, **kwargs)
    return n


def timemachine(c):

    def __init__(self, *args, **kwargs):
        c_init(self, *args, **kwargs)
        self.commands = []
        self.original = deepcopy(self)

    c_init = c.__init__
    c.__init__ = __init__


    def reset(self):
        self.__dict__.update(self.original.__dict__)

    def undo(self):
        commands = self.commands[:-1]
        self.reset()
        self.commands = commands
        for f, args, kwargs in commands:
            f(self, *args, **kwargs)

    assert not hasattr(c, "reset")
    assert not hasattr(c, "undo")

    c.reset = reset
    c.undo = undo

    return c



### EXAMPLE ###

@timemachine
class Counter(object):

    def __init__(self):
        self.count = 1

    def __str__(self):
        return "c: " + str(self.count)

    @altering
    def up(self):
        self.count += 1

    @altering
    def down(self):
        self.count -= 1



### TESTING ###

ot = Counter()
ex = Counter()
print ex
ex.up()
print ex
ex.up()
print ex
ex.down()
print ex
ex.up()
print ex

print ex.commands
print ot.commands

print ex.original
print ot.original

print ex
print "reset"
ex.reset()
print ex

ex.up()
print ex
ex.up()
print ex
ex.up()
print ex
ex.up()
print ex
ex.up()
print ex

print "undo"
ex.undo()
print ex
ex.undo()
print ex
ex.undo()
print ex



