#!/usr/bin/env python3

import asyncio
import logberry

@logberry.wrap
async def some_core_coroutine(req):
    req = f"{req} core"
    logberry.attach(req=req)
    await asyncio.sleep(2)

@logberry.wrap
async def some_inner_coroutine(req):
    req = f"{req} inner"
    logberry.attach(req=req)
    await asyncio.sleep(2)
    await some_core_coroutine(req)

@logberry.wrap
async def some_outer_coroutine(req):
    req = f"{req} outer"
    logberry.attach(req=req)
    await some_inner_coroutine(req)

async def main():
    tasks = []
    for req in range(1, 5):
        tasks.append(asyncio.create_task(some_outer_coroutine(req)))
    await asyncio.gather(*tasks)

logberry.start()
asyncio.run(main())
logberry.stop()
