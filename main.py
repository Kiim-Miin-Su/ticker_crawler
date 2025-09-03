from fastapi import FastAPI
from pydantic import BaseModel
from ticker_crawler import TickerCrawler, to_excel, to_csv
import asyncio

app = FastAPI()

class ExportRequest(BaseModel):
    file_type: str   # "excel" or "csv"
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

    return {"message": f"File {req.filename} created successfully."}
