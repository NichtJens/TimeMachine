#!/usr/bin/env python

from copy import deepcopy


def reset(obj, *args, **kwargs):
    return obj.__reset__(*args, **kwargs)

def undo(obj, *args, **kwargs):
    return obj.__undo__(*args, **kwargs)

def redo(obj, *args, **kwargs):
    return obj.__redo__(*args, **kwargs)



def altering(f):
    def n(self, *args, **kwargs):
        self.redostack = []
        self.undostack.append((f, args, kwargs))
        f(self, *args, **kwargs)
    return n


def timemachine(c):

    def __init__(self, *args, **kwargs):
        c_init(self, *args, **kwargs)
        assert not hasattr(self, "redostack")
        assert not hasattr(self, "undostack")
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

        self.__reset__()
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



    assert not hasattr(c, "__reset__")
    assert not hasattr(c, "__undo__")
    assert not hasattr(c, "__redo__")

    c.__reset__ = reset
    c.__undo__ = undo
    c.__redo__ = redo

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

undo(ex)
print ex
undo(ex)
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
reset(ex)
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
undo(ex)
print ex
undo(ex)
print ex
undo(ex)
print ex

print ex.redostack
print ot.redostack

print "redo"
redo(ex)
print ex
redo(ex)
print ex
redo(ex)
print ex
redo(ex)
print ex

print "undo"
undo(ex)
print ex
undo(ex)
print ex
undo(ex)
print ex

print "redo"
redo(ex)
print ex
redo(ex)
print ex
redo(ex)
print ex
redo(ex)
print ex

print "undo+new_cmd"
undo(ex)
print ex.redostack
ex.down()
print ex.redostack



