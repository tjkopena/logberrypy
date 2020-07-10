import inspect
from datetime import datetime
import string
import asyncio

from .event import Event
from .queue import queue_put
import logberry._globals as _globals

class Exception(Exception):
    def __init__(self, msg='Exception',  **kwargs):
        self.identifiers = kwargs
        super().__init__(msg)

    def __str__(self):
        d = ', '.join([f'{k}: {v}' for (k, v) in self.identifiers.items()])
        if d:
            d = f" {{{d}}}"
        return f'{super().__str__()}{d}'

class Task:
    _counter = 0

    def __init__(self, parent, label, is_func=False, is_component=False, **kwargs):
        Task._counter += 1
        self.id = Task._counter

        self.failed = False
        self.reported_end = False

        self.is_func = is_func
        self.is_component = is_component

        self.identifiers = kwargs
        ephemeral = {}

        self.parent = parent
        while parent and not parent.is_component:
            parent = parent.parent
        self.containing_component = parent

        self.label = label if label else "Task"

        self.event(Event.BEGIN, '', **ephemeral)

    def __del__(self):
        if self.reported_end:
            return
        if _globals.stopped:
            return
        self.end()

    def __repr__(self):
        return self.label

    def __str__(self):
        t = "Component" if self.is_component else ("Function" if self.is_func else "Task")
        idents = ', '.join([f'{k}: {v}' for (k, v) in self.identifiers.items()])
        delim =  ('[', ']') if self.is_component else (('(', ')') if self.is_func else (' {', '}'))
        return f"{t} {self.label}{delim[0]}{idents}{delim[1]} #{self.id}"

    def attach(self, **kwargs):
        self.identifiers.update(kwargs)

    def event(self, evt, msg, timestamp=None, text=None, binary=None, **kwargs):
        if not timestamp:
            timestamp = datetime.utcnow()
        event = Event(evt, self.containing_component, self, msg, timestamp, text, binary, kwargs)
        queue_put(event)


    def component(self, label, **kwargs):
        return Task(self, label, is_component=True, **kwargs)

    def task(self, label=None, is_func=False, **kwargs):
        if not label:
            is_func = True
            label = inspect.stack()[1].function
        return Task(self, label, is_func=is_func, **kwargs)


    def end(self, msg='', **kwargs):
        assert not self.reported_end, f"Already reported end of {self}"
        self.reported_end = True
        self.event(Event.END, msg, **kwargs)
        return None

    def end_success(self, msg='', **kwargs):
        self.failed = False
        self.end(msg, **kwargs)
        return None

    def end_exception(self, ex, msg='', **kwargs):
        self.failed = True
        text = f"{type(ex).__name__} {ex}"
        if msg:
            msg = f"{msg}: {text}"
        else:
            msg = f"{text}"
        self.end(msg, **kwargs)
        return ex

    def end_failure(self, msg='', type=None, **kwargs):
        self.failed = True
        if not msg:
            msg = "Failure"
        self.end(msg, **kwargs)
        if not type:
            type = Exception
        return type(msg, **self.identifiers, **kwargs)


    def info(self, msg, **kwargs):
        self.event(Event.INFO, msg, **kwargs)

    def exception(self, ex, msg='', **kwargs):
        label = f"{type(ex).__name__} {ex}"
        msg = f"{msg}: {label}" if msg else f"{label}"
        self.event(Event.ERROR, msg, **kwargs)

    def error(self, msg, **kwargs):
        self.event(Event.ERROR, msg, **kwargs)

    def warning(self, msg, **kwargs):
        self.event(Event.WARNING, msg, **kwargs)
