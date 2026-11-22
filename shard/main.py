import os
import asyncio
import httpx

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

SHARD_ID = os.getenv("SHARD_ID", "shard-1")
SHARD_URL = os.getenv("SHARD_URL", "http://127.0.0.1:8001")
COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://127.0.0.1:8000")


async def register_with_coordinator():
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.post(
                    f"{COORDINATOR_URL}/shards/register",
                    json={
                        "shardId": SHARD_ID,
                        "url": SHARD_URL,
                    },
                    timeout=5.0,
                )
                response.raise_for_status()
                print(f"Shard {SHARD_ID} registered successfully")
                return
            except (httpx.RequestError, httpx.HTTPStatusError) as error:
                print(f"Registration failed: {error}. Retrying in 3 seconds...")
                await asyncio.sleep(3)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await register_with_coordinator()
    yield

app = FastAPI(title="Shard Service", lifespan=lifespan)

records = {}


class Record(BaseModel):
    key: str
    value: dict[str, Any]


@app.post("/tables/{tableName}/records", status_code=201)
def create_record(tableName: str, record: Record):
    table_records = records.setdefault(tableName, {})

    if record.key in table_records:
        raise HTTPException(409, "Record already exists")

    table_records[record.key] = record.value
    return {"message": "Record created"}


@app.get("/tables/{tableName}/records/{key}")
def read_record(tableName: str, key: str):
    if key not in records.get(tableName, {}):
        raise HTTPException(404, "Record not found")

    return {"key": key, "value": records[tableName][key]}


@app.head("/tables/{tableName}/records/{key}")
def record_exists(tableName: str, key: str):
    if key not in records.get(tableName, {}):
        raise HTTPException(404, "Record not found")

    return Response(status_code=200)


@app.delete("/tables/{tableName}/records/{key}", status_code=204)
def delete_record(tableName: str, key: str):
    if key not in records.get(tableName, {}):
        raise HTTPException(404, "Record not found")

    del records[tableName][key]
    return Response(status_code=204)
