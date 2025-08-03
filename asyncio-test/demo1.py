import asyncio

from sqlalchemy.util import await_only


async def say_hello():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

