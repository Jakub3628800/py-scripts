#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
# "aiohttp",
# ]
# ///
import asyncio
import aiohttp

# Limit number of concurrent connections
semaphore = asyncio.Semaphore(50)


async def make_request(url: str, session: aiohttp.ClientSession):
    async with semaphore:
        async with session.get(url=url) as r:
            print(await r.text())


async def main() -> None:
    targets = ["https://github.com/", "https://github.com/"]
    async with aiohttp.ClientSession(headers={}) as session:
        tasks = [make_request(target, session=session) for target in targets]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    raise SystemExit(0)
