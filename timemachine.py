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
        self._tm_redostack = []
        self._tm_undostack.append((func, args, kwargs))
        func(self, *args, **kwargs)
    return wrapper

def timemachine(cls):
    cls.__original_init__ = cls.__init__
    cls.__init__ = tm_init
    return cls



def tm_init(self, *args, **kwargs):
    cls = type(self)
    cls.__original_init__(self, *args, **kwargs)

    assert not hasattr(self, "_tm_redostack")
    assert not hasattr(self, "_tm_undostack")
    assert not hasattr(self, "_tm_initial_state")
    self._tm_redostack = []
    self._tm_undostack = []
    self._tm_initial_state  = deepcopy(self)

    assert not hasattr(self, "__reset__")
    assert not hasattr(self, "__undo__")
    assert not hasattr(self, "__redo__")
    #binds the functions as bound methods
    self.__reset__ = tm_reset.__get__(self, cls)
    self.__undo__  = tm_undo.__get__(self, cls)
    self.__redo__  = tm_redo.__get__(self, cls)


def tm_reset(self):
    self.__dict__.update(self._tm_initial_state.__dict__)


def tm_undo(self):
    if not self._tm_undostack:
        return

    undostack = self._tm_undostack
    redostack = self._tm_redostack

    cmd = undostack.pop()
    redostack.append(cmd)

    self.__reset__()
    self._tm_undostack = undostack
    self._tm_redostack = redostack
    for func, args, kwargs in undostack:
        func(self, *args, **kwargs)


def tm_redo(self):
    if not self._tm_redostack:
        return

    cmd = self._tm_redostack.pop()
    self._tm_undostack.append(cmd)

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

print ex._tm_undostack
print ot._tm_undostack

print ex._tm_initial_state
print ot._tm_initial_state

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

print ex._tm_redostack
print ot._tm_redostack

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
print ex._tm_redostack
ex.down()
print ex._tm_redostack



