import inspect
from datetime import datetime
import string
import asyncio

from .exception import Exception, _exception_label
from .utils import params_text
from .event import Event
from .queue import queue_put
import logberry._globals as _globals

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
        msg = _exception_label(ex, msg, kwargs)
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
        msg = _exception_label(ex, msg, kwargs)
        self.event(Event.ERROR, msg, **kwargs)

    def error(self, msg, **kwargs):
        self.event(Event.ERROR, msg, **kwargs)

    def warning(self, msg, **kwargs):
        self.event(Event.WARNING, msg, **kwargs)
