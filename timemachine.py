
from functools import wraps
from copy import deepcopy


def reset(obj, *args, **kwargs):
    return obj.__tm_reset__(*args, **kwargs)

def undo(obj, *args, **kwargs):
    return obj.__tm_undo__(*args, **kwargs)

def redo(obj, *args, **kwargs):
    return obj.__tm_redo__(*args, **kwargs)


def altering(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self._tm_redostack = []
        self._tm_undostack.append((func, args, kwargs))
        func(self, *args, **kwargs)
    return wrapper

def timemachine(cls):
    cls.__original_init__ = cls.__init__
    cls.__init__ = _tm_init
    return cls



### INTERNALS ###

def _tm_init(self, *args, **kwargs):
    cls = type(self)
    cls.__original_init__(self, *args, **kwargs)

    assert not hasattr(self, "_tm_redostack")
    assert not hasattr(self, "_tm_undostack")
    assert not hasattr(self, "_tm_initial_state")
    self._tm_redostack = []
    self._tm_undostack = []
    self._tm_initial_state  = deepcopy(self)

    assert not hasattr(self, "__tm_reset__")
    assert not hasattr(self, "__tm_undo__")
    assert not hasattr(self, "__tm_redo__")
    #binds the functions as bound methods
    self.__tm_reset__ = _tm_reset.__get__(self, cls)
    self.__tm_undo__  = _tm_undo.__get__(self, cls)
    self.__tm_redo__  = _tm_redo.__get__(self, cls)


def _tm_reset(self):
    self.__dict__.update(self._tm_initial_state.__dict__)


def _tm_undo(self):
    if not self._tm_undostack:
        return

    undostack = self._tm_undostack
    redostack = self._tm_redostack

    cmd = undostack.pop()
    redostack.append(cmd)

    reset(self)
    self._tm_undostack = undostack
    self._tm_redostack = redostack
    for func, args, kwargs in undostack:
        func(self, *args, **kwargs)


def _tm_redo(self):
    if not self._tm_redostack:
        return

    cmd = self._tm_redostack.pop()
    self._tm_undostack.append(cmd)

    func, args, kwargs = cmd
    func(self, *args, **kwargs)



