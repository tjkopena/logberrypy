import inspect
from datetime import datetime
import string
import asyncio
import threading
import janus

from printer import Printer
from event import Event

class Exception(Exception):
    def __init__(self, msg='Exception',  **kwargs):
        self.identifiers = kwargs
        super().__init__(msg)

    def __str__(self):
        d=''
        for k,v in self.identifiers.items():
            if any(c in k for c in string.whitespace):
                k = f'"{k}"'
            d = d + (', ' if d else '') + f'{k}: "{v}"'
        if d:
            d = f"{{{d}}}"

        return f'{super().__str__()} {d}'


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
        emit(event)

    def end(self, msg='', **kwargs):
        assert(not self.reported_end)
        m = ''
        if msg:
            m = "Failed: {msg}" if self.failed else "Success: {msg}"
        self.reported_end = True
        self.event(Event.END, m, **kwargs)
        return None

    def success(self, msg='', **kwargs):
        self.failed = False
        self.end(msg, **kwargs)
        return None

    def failure(self, msg='', ex=None, **kwargs):
        self.failed = True
        self.end(msg, **kwargs)
        if not ex:
            ex = Exception
        return ex(msg if msg else 'Unknown', **self.identifiers, **kwargs)

    def info(self, msg, **kwargs):
        self.event(Event.INFO, msg, **kwargs)

_queue = None
async def _process():
    global _queue
    assert(_queue)
    while True:
        evt = await _queue.async_q.get()
        _queue.async_q.task_done()
        if not evt:
            break
        for e in _emitters:
            e.emit(evt)

main = None
_emitters = None
_started = False
_thread = None
def start(emitters=None):
    async def _loop(ready: threading.Event):
        global _queue
        _queue = janus.Queue()
        ready.set()
        await _process()
        _queue.close()
        await _queue.wait_closed()

    def _run(ready):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_loop(ready))

    global _started
    if _started:
        raise Exception("Logberry already started")

    global _emitters
    _emitters = emitters if emitters else [Printer()]

    global _thread
    ready = threading.Event()
    _thread = threading.Thread(target=_run, args=[ready])
    _thread.start()
    ready.wait()

    global main
    main = Task(None, "main", is_component=True)

    _started = True

_stopped = False
def stop():
    global _stopped
    global main
    global _queue
    global _thread

    if _stopped:
        raise Exception("Logberry already stopped")
    _stopped = True

    if main:
        main.end()

    if _queue:
        _queue.sync_q.put(False)

    _thread.join()

def emit(evt):
    global _queue
    _queue.sync_q.put(evt)


if __name__ == "__main__":
    start()
    main.info("Logberry is functional")
    t = main.task("Calculation")
    u = t.task("Work", attachment="mushi.jpg")
    u.success()
    import time
    time.sleep(2)
    t.success()
    stop()
