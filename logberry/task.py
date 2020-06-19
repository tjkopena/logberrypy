import inspect
from datetime import datetime
import string
import asyncio

from .printer import Printer
from .event import Event
from .queue import queue_put
import logberry._globals as _globals

class Task:
    _counter = 0

    def __init__(self, parent, label, is_component=False, **kwargs):
        Task._counter += 1
        self.id = Task._counter

        self.failed = False
        self.reported_end = False

        self.is_component = is_component

        if self.is_component:
            self.identifiers = kwargs
            ephemeral = {}
        else:
            self.identifiers = {}
            ephemeral = kwargs

        self.parent = parent
        while parent and not parent.is_component:
            parent = parent.parent
        self.component = parent

        self.label = label if label else "Task"

        self.event(Event.BEGIN, '', **ephemeral)

    def __del__(self):
        if self.reported_end:
            return
        if _globals.stopped:
            return
        self.end()

    def new_component(self, label, **kwargs):
        return Task(self, label, is_component=True, **kwargs)

    def task(self, label=None, **kwargs):
        if not label:
            label = inspect.stack()[1].function
        return Task(self, label, **kwargs)

    def attach(self, **kwargs):
        self.identifiers.update(kwargs)

    def event(self, evt, msg, timestamp=None, blob=None, **kwargs):
        if not timestamp:
            timestamp = datetime.utcnow()
        event = Event(evt, self.component, self, msg, timestamp, blob, kwargs)
        queue_put(event)

    def end(self, msg='', **kwargs):
        assert(not self.reported_end)
        self.reported_end = True
        self.event(Event.END, msg, **kwargs)
        return None

    def success(self, msg='', **kwargs):
        self.failed = False
        self.end(msg, **kwargs)
        return None

    def exception(self, msg='', ex=None, **kwargs):
        self.failed = True
        if not msg:
            msg = "Exception"
        if ex:
            msg = f"{msg}: {ex}"
        self.end(msg, **kwargs)
        return ex

    def failure(self, msg='', type=None, **kwargs):
        self.failed = True
        if not msg:
            msg = "Failure"
        self.end(msg, **kwargs)
        if not type:
            type = Exception
        return type(msg, **self.identifiers, **kwargs)

    def info(self, msg, **kwargs):
        self.event(Event.INFO, msg, **kwargs)


class Exception(Exception):
    def __init__(self, msg='Exception',  **kwargs):
        self.identifiers = kwargs
        super().__init__(msg)

    def __str__(self):
        d = ', '.join([f'{k}: {v}' for (k, v) in self.identifiers.items()])
        if d:
            d = f" {{{d}}}"
        return f'{super().__str__()}{d}'
