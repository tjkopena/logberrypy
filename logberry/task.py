import inspect
from datetime import datetime
import string
import asyncio

from .utils import params_text
from .event import Event
from .queue import queue_put
import logberry._globals as _globals

class Exception(Exception):
    def __init__(self, msg='',  **kwargs):
        self.msg = msg
        self.identifiers = kwargs
        super().__init__(msg)

    def __str__(self):
        d = params_text(self.identifiers)
        if d:
            d = f" {{{d}}}"
        msg = (': ' if self.msg else '') + self.msg
        return f'{self.text()}{d}'

    def text(self):
        msg = (': ' if self.msg else '') + self.msg
        return f'{type(self).__name__}{msg}'

    def data(self):
        return self.identifiers

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
        self.reports = {}

        self.parent = parent
        while parent and not parent.is_component:
            parent = parent.parent
        self.containing_component = parent

        self.label = label if label else "Task"

        self.event(Event.BEGIN, '')

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

    def detach(self, **kwargs):
        if kwargs:
            for k in kwargs:
                if k in self.identifiers:
                    del self.identifiers[k]
        else:
            self.identifiers.clear()

    def report(self, **kwargs):
        self.reports.update(kwargs)

    def retract(self, **kwargs):
        if kwargs:
            for k in kwargs:
                if k in self.reports:
                    del self.reports[k]
        else:
            self.reports.clear()

    def event(self, evt, msg, timestamp=None, **kwargs):
        if not timestamp:
            timestamp = datetime.utcnow()
        args = { **self.reports, **kwargs }
        event = Event(evt, self.containing_component, self, msg, timestamp, args)
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
        if isinstance(ex, Exception):
            msg = f'{msg}: {ex.text()}' if msg else ex.text()
            kwargs.update(ex.data())
        else:
            ex_str = str(ex)
            type_str = type(ex).__name__
            type_str = '' if ex_str.startswith(type_str) else (type_str + ': ')
            text = f"{type_str}{ex_str}"
            msg = f"{msg}: {text}" if msg else text
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
