from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from ticker_crawler import TickerCrawler, to_excel, to_csv
import asyncio
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kiim-miin-su.github.io"],  # 정확히 GitHub Pages 도메인
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

        os.makedirs("/tmp", exist_ok=True)

        # 확장자 보정
        if req.file_type == "excel":
            if not req.filename.endswith(".xlsx"):
                req.filename += ".xlsx"
        elif req.file_type == "csv":
            if not req.filename.endswith(".csv"):
                req.filename += ".csv"
        else:
            return {"error": "Invalid file type"}

        filepath = os.path.join("/tmp", req.filename)

        if req.file_type == "excel":
            to_excel(data, filepath)
        else:
            to_csv(data, filepath)

    return FileResponse(
        path=filepath,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if req.file_type == "excel"
            else "text/csv"
        ),
        filename=req.filename,
    )
