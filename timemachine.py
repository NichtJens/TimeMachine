#!/usr/bin/env python

from copy import deepcopy


def altering(f):
    def n(self, *args, **kwargs):
        self.redostack = []
        self.undostack.append((f, args, kwargs))
        f(self, *args, **kwargs)
    return n


def timemachine(c):

    def __init__(self, *args, **kwargs):
        c_init(self, *args, **kwargs)
        self.redostack = []
        self.undostack = []
        self.original = deepcopy(self)

    c_init = c.__init__
    c.__init__ = __init__


    def reset(self):
        self.__dict__.update(self.original.__dict__)


    def undo(self):
        if not self.undostack:
            return

        undostack = self.undostack
        redostack = self.redostack

        cmd = undostack.pop()
        redostack.append(cmd)

        self.reset()
        self.undostack = undostack
        self.redostack = redostack
        for f, args, kwargs in undostack:
            f(self, *args, **kwargs)


    def redo(self):
        if not self.redostack:
            return

        cmd = self.redostack.pop()
        self.undostack.append(cmd)

        f, args, kwargs = cmd
        f(self, *args, **kwargs)



    assert not hasattr(c, "reset")
    assert not hasattr(c, "undo")
    assert not hasattr(c, "redo")

    c.reset = reset
    c.undo = undo
    c.redo = redo

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

ex.undo()
print ex
ex.undo()
print ex

ex.up()
print ex
ex.up()
print ex
ex.down()
print ex
ex.up()
print ex

print ex.undostack
print ot.undostack

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

print "redo"
ex.redo()
print ex #, ex.redostack, ex.undostack
ex.redo()
print ex #, ex.redostack, ex.undostack
ex.redo()
print ex #, ex.redostack, ex.undostack
ex.redo()
print ex #, ex.redostack, ex.undostack

print "undo"
ex.undo()
print ex
ex.undo()
print ex
ex.undo()
print ex

print "redo"
ex.redo()
print ex #, ex.redostack, ex.undostack
ex.redo()
print ex #, ex.redostack, ex.undostack
ex.redo()
print ex #, ex.redostack, ex.undostack
ex.redo()
print ex #, ex.redostack, ex.undostack


print "undo+new_cmd"
ex.undo()
print ex.redostack
ex.down()
print ex.redostack



