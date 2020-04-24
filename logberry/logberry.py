import asyncio
import threading
import janus

class Logberry:
    def __init__(self):
        self.queue = None

    async def _run(self):
        while True:
            item = await self.queue.async_q.get()
            self.queue.async_q.task_done()
            if not item:
                break
            print(item)

    def start(self, event_loop=None):
        async def _run(ready: threading.Event):
            self.queue = janus.Queue()
            ready.set()
            await self._run()
            self.queue.close()
            await self.queue.wait_closed()

        def _thread(ready):
            loop = asyncio.new_event_loop()
            loop = loop
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_run(ready))

        ready = threading.Event()
        t = threading.Thread(target=_thread, args=[ready])
        t.start()
        ready.wait()

        return self

    def stop(self):
        self.queue.sync_q.put(False)

    def event(self, msg):
        self.queue.sync_q.put(msg)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'sync':
        import time

        log = Logberry().start()
        log.event(f"main 1")
        time.sleep(1)
        log.event(f"main 2")
        log.stop()

    elif len(sys.argv) > 1 and sys.argv[1] == 'async':
        async def _produce():
            log.event(f"main 1")
            await asyncio.sleep(1)
            log.event(f"main 2")

        log = Logberry().start()
        asyncio.get_event_loop().run_until_complete(_produce())
        log.stop()

    else:
        log = Logberry().start()
        log.stop()
