from typing import List, Dict, Optional, Final, Callable, Tuple
from playwright.async_api import async_playwright, Page, BrowserContext
import asyncio
import pandas as pd

class TickerCrawler:
    const_BASE_URL: Final[str] = "https://finance.naver.com/sise/"
    const_HEADER:   Final[Dict[str, str]] = {"User-Agent": "Mozilla/5.0"}
    const_WAIT:     Final[str] = "domcontentloaded"
    const_TIMEOUT:  Final[int] = 8000  # ms

    _pw = None
    _context: Optional[BrowserContext] = None
    _page: Optional[Page] = None

    async def __aenter__(self):
        self._pw = await async_playwright().start()
        browser = await self._pw.chromium.launch(headless=True)
        self._context = await browser.new_context(extra_http_headers=self.const_HEADER)
        self._page = await self._context.new_page()
        self._page.set_default_timeout(self.const_TIMEOUT)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._context:
            await self._context.close()
        if self._pw:
            await self._pw.stop()

    async def fetch(self) -> None:
        assert self._page
        await self._page.goto(self.const_BASE_URL, wait_until=self.const_WAIT)

    async def get_ticker_list(self) -> List[Dict[str, Optional[str]]]:
        assert self._page
        # 필요 시 대기
        await self._page.wait_for_selector("ul.lst_pop li", timeout=self.const_TIMEOUT)
        items = await self._page.query_selector_all("ul.lst_pop li")

        result: List[Dict[str, Optional[str]]] = []
        for li in items:
            a = await li.query_selector("a")
            if not a:
                continue
            name = (await a.inner_text()).strip()

            # 가격 span이 여러 개일 수 있어 첫 번째 텍스트 사용
            sp = await li.query_selector("span")
            price = (await sp.inner_text()).strip() if sp else None

            result.append({"Name": name, "Price": price})
        return result

def to_excel(data: List[Dict[str, Optional[str]]], filename: str = "ticker_list.xlsx") -> bool:
    df = pd.DataFrame(data, columns=["Name", "Price"])
    df.to_excel(filename, index=False)
    return True

def to_csv(data: List[Dict[str, Optional[str]]], filename: str = "ticker_list.csv") -> bool:
    df = pd.DataFrame(data, columns=["Name", "Price"])
    df.to_csv(filename, index=False)
    return True

def get_type() -> Callable[[List[Dict[str, Optional[str]]], str], bool]:
    while True:
        x = input("Enter the file type to download (1. excel | 2. csv): ").strip().lower()
        if x in ("1", "excel"): return to_excel
        if x in ("2", "csv"):   return to_csv
        print("Invalid input. Please enter 'excel' or 'csv'.")

def _ensure_ext(name: str, ext: str) -> str:
    n = name.strip()
    if not n: n = "ticker_list"
    if not n.lower().endswith(f".{ext}"):
        n = f"{n}.{ext}"
    return n

def get_filename(func: Callable) -> str:
    while True:
        x = input("Enter the file name to save (ex: KOSPI top 10): ").strip()
        if func is to_excel: return _ensure_ext(x, "xlsx")
        if func is to_csv:   return _ensure_ext(x, "csv")

async def main(callback, file_name: Optional[str]) -> bool:
    async with TickerCrawler() as ticker:
        await ticker.fetch()
        data = await ticker.get_ticker_list()
        return callback(data, file_name)

if __name__ == "__main__":
    download_type = get_type()
    download_filename = get_filename(download_type)
    ok = asyncio.run(main(download_type, download_filename))
    print(f"File '{download_filename}' has been created successfully." if ok else "Failed to create the file.")
