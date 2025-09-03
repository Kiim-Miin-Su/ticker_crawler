from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from ticker_crawler import TickerCrawler, to_excel, to_csv
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kiim-miin-su.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExportRequest(BaseModel):
    file_type: str  # "excel" or "csv"
    filename: str


@app.post("/export")
async def export(req: ExportRequest):
    async with TickerCrawler() as crawler:
        await crawler.fetch()
        data = await crawler.get_ticker_list()

        if req.file_type == "excel":
            to_excel(data, req.filename)
        elif req.file_type == "csv":
            to_csv(data, req.filename)
        else:
            return {"error": "Invalid file type"}

    return FileResponse(
        path=req.filename,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if req.file_type == "excel"
            else "text/csv"
        ),
        filename=req.filename,
    )
