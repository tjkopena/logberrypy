import janus

_queue = None

def queue_create():
    global _queue
    _queue = janus.Queue()

def queue_put(event):
    global _queue
    _queue.sync_q.put(event)

async def queue_get():
    global _queue
    r = await _queue.async_q.get()
    _queue.async_q.task_done()
    return r

def queue_stop():
    global _queue
    if _queue:
        _queue.sync_q.put(False)

async def queue_close():
    global _queue
    _queue.close()
    await _queue.wait_closed()
