
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Shard Service")

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
