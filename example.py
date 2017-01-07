#!/usr/bin/env python

from timemachine import altering, timemachine, reset, undo, redo


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



