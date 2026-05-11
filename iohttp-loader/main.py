import aiohttp
import asyncio
import csv

urls = [
    "https://example.com",
    "https://httpbin.org/get",
    "https://www.python.org",
    "https://badurl.test"
]

async def fetch(session, url, semaphore):
    for attempt in range(3):
        async with semaphore:
            try:
                print(f"start {url}, attempt {attempt + 1}")
                async with session.get(url) as response:
                    text = await response.text()
                    print(f"done {url}", f"status: {response.status}, size: {len(text)} chars")
                    return {
                        "name":url,
                        "status":response.status,
                        "size":len(text)
                    }
            except asyncio.TimeoutError:
                print(f"timeout {url}")

                if attempt == 2: return {"name":url,"status":"Error","size":"Error"}
            except aiohttp.ClientError as error:
                print(f"error {url}: {error}")
                if attempt == 2: return {"name":url,"status":"Error","size":"Error"}


    print(f"failed {url}")

async def main():
    timeout = aiohttp.ClientTimeout(total=5)
    semaphore = asyncio.Semaphore(2)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [fetch(session, url, semaphore) for url in urls]
        print("loading...")
        results = await asyncio.gather(*tasks)

    with open("results.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["name", "status", "size"]
        )
        writer.writeheader()
        writer.writerows(results)




if __name__ == "__main__":
    asyncio.run(main())
