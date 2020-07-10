import asyncio
import threading

from .printer import Printer
from .queue import queue_create, queue_get, queue_stop, queue_close

import logberry._globals as _globals

_thread = None
_emitters = None
_eventloop = None

def _start(emitters=None):
    async def _loop():
        global _emitters

        while True:
            evt = await queue_get()
            if not evt:
                break
            for e in _emitters:
                e.emit(evt)

    async def _task(ready: threading.Event):
        queue_create()
        ready.set()
        await _loop()

        await queue_close()

    def _run(ready):
        global _eventloop
        _eventloop = asyncio.new_event_loop()
        asyncio.set_event_loop(_eventloop)
        _eventloop.run_until_complete(_task(ready))
        _eventloop.stop()

    global _thread
    if _thread:
        raise Exception("Logberry already started")

    global _emitters
    _emitters = emitters if emitters else [Printer()]

    ready = threading.Event()
    _thread = threading.Thread(target=_run, args=[ready], daemon=True)
    _thread.start()
    ready.wait()

def _stop():
    global _thread
    global _eventloop

    if not _thread or not _eventloop:
        raise Exception("Logberry never started")

    if _globals.stopped:
        raise Exception("Logberry already stopped")
    _globals.stopped = True

    queue_stop()

    _thread.join()
