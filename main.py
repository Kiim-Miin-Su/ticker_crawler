from fastapi import FastAPI
from fastapi.responses import FileResponse
import asyncio
import os

from starlette.middleware.cors import CORSMiddleware

from ticker_crawler import TickerCrawler, to_excel

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5500",
    "http://localhost:8080",
    "https://Kiim-Miin-Su.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Controller:
    def __init__(self):
        self.state = "Initialized"

    async def get_tickers(self, file_name: str = "ticker_list.xlsx"):
        async with TickerCrawler() as ticker:
            await ticker.fetch()
            data = await ticker.get_ticker_list()
            to_excel(data, file_name)
            return file_name

controller = Controller()

@app.post("/to-excel")
async def tickers():
    file = await controller.get_tickers()
    return FileResponse(file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=os.path.basename(file))
