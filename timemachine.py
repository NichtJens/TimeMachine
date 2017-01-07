#!/usr/bin/env python

from functools import wraps
from copy import deepcopy


def reset(obj, *args, **kwargs):
    return obj.__reset__(*args, **kwargs)

def undo(obj, *args, **kwargs):
    return obj.__undo__(*args, **kwargs)

def redo(obj, *args, **kwargs):
    return obj.__redo__(*args, **kwargs)


def altering(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.redostack = []
        self.undostack.append((func, args, kwargs))
        func(self, *args, **kwargs)
    return wrapper

def timemachine(cls):
    cls.__original_init__ = cls.__init__
    cls.__init__ = tm_init
    return cls



def tm_init(self, *args, **kwargs):
    cls = type(self)
    cls.__original_init__(self, *args, **kwargs)

    assert not hasattr(self, "redostack")
    assert not hasattr(self, "undostack")
    assert not hasattr(self, "original")
    self.redostack = []
    self.undostack = []
    self.original  = deepcopy(self)

    assert not hasattr(self, "__reset__")
    assert not hasattr(self, "__undo__")
    assert not hasattr(self, "__redo__")
    #binds the functions as bound methods
    self.__reset__ = tm_reset.__get__(self, cls)
    self.__undo__  = tm_undo.__get__(self, cls)
    self.__redo__  = tm_redo.__get__(self, cls)


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



