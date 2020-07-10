#!python3

import logberry

import asyncio
import contextvars

request_id = contextvars.ContextVar('ID of request')

@logberry.wrap
async def some_core_coroutine(preq):

    cxt = request_id.get()
    req_id = cxt[-1]
    req_id += " core"
    cxt.append(req_id)
    request_id.set(cxt)

    #    log.attach(req=req_id)
    await asyncio.sleep(2)
    logberry.info(f"CORE         {req_id:32} {preq}")

    cxt = request_id.get()
    cxt.pop()
    request_id.set(cxt)

@logberry.wrap
async def some_inner_coroutine(preq):

    cxt = request_id.get()
    req_id = cxt[-1]
    req_id += " inner"
    cxt.append(req_id)
    request_id.set(cxt)

#    log.attach(req=req_id)
    await asyncio.sleep(2)
    logberry.info(f"INNER BEG    {req_id:32} {preq}")
    await some_core_coroutine(preq)
    logberry.info(f"INNER END    {req_id:32} {preq}")

    cxt = request_id.get()
    cxt.pop()
    request_id.set(cxt)

@logberry.wrap()
async def some_outer_coroutine(preq):

    req_id = f"{preq} outer"
    request_id.set([req_id])
#    log.attach(req=req_id)

    logberry.info(f"OUTER BEG    {req_id:32} {preq}")
    await some_inner_coroutine(preq)
    logberry.info(f"OUTER END    {req_id:32} {preq}")

    cxt = request_id.get()
    cxt.pop()
    request_id.set(cxt)

async def main():
    tasks = []
    for req_id in range(1, 5):
        tasks.append(asyncio.create_task(some_outer_coroutine(req_id)))
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    logberry.start()
    t = logberry.Task(None, 'mushi')
    asyncio.run(main())
    logberry.stop()
