#!/usr/bin/env python

from copy import deepcopy


def reset(obj, *args, **kwargs):
    return obj.__reset__(*args, **kwargs)

def undo(obj, *args, **kwargs):
    return obj.__undo__(*args, **kwargs)

def redo(obj, *args, **kwargs):
    return obj.__redo__(*args, **kwargs)



def altering(func):
    def wrapper(self, *args, **kwargs):
        self.redostack = []
        self.undostack.append((func, args, kwargs))
        func(self, *args, **kwargs)
    return wrapper



def tm_reset(self):
    self.__dict__.update(self.original.__dict__)


def tm_undo(self):
    if not self.undostack:
        return

    undostack = self.undostack
    redostack = self.redostack

    cmd = undostack.pop()
    redostack.append(cmd)

    self.__reset__()
    self.undostack = undostack
    self.redostack = redostack
    for func, args, kwargs in undostack:
        func(self, *args, **kwargs)


def tm_redo(self):
    if not self.redostack:
        return

    cmd = self.redostack.pop()
    self.undostack.append(cmd)

    func, args, kwargs = cmd
    func(self, *args, **kwargs)



def timemachine(cls):

    def __init__(self, *args, **kwargs):
        cls_init(self, *args, **kwargs)
        assert not hasattr(self, "redostack")
        assert not hasattr(self, "undostack")
        self.redostack = []
        self.undostack = []
        self.original = deepcopy(self)

    cls_init = cls.__init__
    cls.__init__ = __init__


    assert not hasattr(cls, "__reset__")
    assert not hasattr(cls, "__undo__")
    assert not hasattr(cls, "__redo__")

    cls.__reset__ = tm_reset
    cls.__undo__ = tm_undo
    cls.__redo__ = tm_redo

    return cls



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



