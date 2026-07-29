import asyncio
import aiohttp
import time
import re
from datetime import datetime

# ============ SETTINGS ============
LINKS_FILE = "links.txt"
TARGET_NUMBER = "14582"
CONCURRENCY = 50
RESULT_FILE = "result.txt"
# ===========================================================

def load_urls(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

async def check_page(session, url, sem):
    async with sem:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                html = await resp.text()
                found = re.search(rf'\b{TARGET_NUMBER}\b', html) is not None
                return url, found
        except Exception:
            return url, None

async def main():
    urls = load_urls(LINKS_FILE)
    sem = asyncio.Semaphore(CONCURRENCY)
    t0 = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [check_page(session, url, sem) for url in urls]
        results = await asyncio.gather(*tasks)

    matched = [u for u, ok in results if ok is True]
    not_matched = [u for u, ok in results if ok is False]
    errored = [u for u, ok in results if ok is None]

    lines = []
    lines.append(f"Check kiya gaya: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    lines.append(f"Kul samay: {time.time() - t0:.2f} second — {len(urls)} pages check hue")
    lines.append(f"\nMATCH mila ({len(matched)} pages):")
    lines.extend([f"  {u}" for u in matched])
    lines.append(f"\nMatch NAHI mila: {len(not_matched)} pages")
    if errored:
        lines.append(f"\nError aayi in pages me ({len(errored)}):")
        lines.extend([f"  {u}" for u in errored])

    output = "\n".join(lines)
    print(output)

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    asyncio.run(main())
