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

        filepath = os.path.join("/tmp", req.filename)  # 임시 디렉토리에 저장
        if req.file_type == "excel":
            to_excel(data, filepath)
        elif req.file_type == "csv":
            to_csv(data, filepath)
        else:
            return {"error": "Invalid file type"}

    return FileResponse(
        path=filepath,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if req.file_type == "excel"
            else "text/csv"
        ),
        filename=req.filename,
    )
