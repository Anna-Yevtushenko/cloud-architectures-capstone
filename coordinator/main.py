
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Any
from coordinator.consistent_hash import ConsistentHashRing
import httpx

app = FastAPI(title="Key-Value Store API")

tables = {}
records = {}
shards = {}
hash_ring = ConsistentHashRing(virtual_nodes=64)


class Table(BaseModel):
    name: str
    partitionKey: str


class Record(BaseModel):
    key: str
    value: dict[str, Any]

class ShardRegistration(BaseModel):
    shardId: str
    url: str


@app.post("/tables", status_code=201, tags=["Tables"])
def create_table(table: Table):
    if table.name in tables:
        raise HTTPException(409, "Table already exists")

    tables[table.name] = table.partitionKey
    records[table.name] = {}
    return {"message": "Table created"}



@app.post(
    "/tables/{tableName}/records",
    status_code=201,
    tags=["Records"]
)
def create_record(tableName: str, record: Record):
    if tableName not in tables:
        raise HTTPException(404, "Table not found")

    routing_key = f"{tableName}:{record.key}"
    shard_id = hash_ring.get_node(routing_key)

    if shard_id is None:
        raise HTTPException(503, "No shards registered")

    shard_url = shards[shard_id]

    try:
        response = httpx.post(
            f"{shard_url}/tables/{tableName}/records",
            json=record.model_dump(),
            timeout=5.0
        )
    except httpx.RequestError:
        raise HTTPException(503, "Shard unavailable")

    if response.status_code == 409:
        raise HTTPException(409, "Record already exists")

    if response.status_code != 201:
        raise HTTPException(502, "Shard write failed")

    return {
        "message": "Record created",
        "shardId": shard_id
    }




@app.get("/tables/{tableName}/records/{key}", tags=["Records"])
def read_record(tableName: str, key: str):
    if tableName not in tables:
        raise HTTPException(404, "Table not found")

    routing_key = f"{tableName}:{key}"
    shard_id = hash_ring.get_node(routing_key)

    if shard_id is None:
        raise HTTPException(503, "No shards registered")

    shard_url = shards[shard_id]

    try:
        response = httpx.get(
            f"{shard_url}/tables/{tableName}/records/{key}",
            timeout=5.0
        )
    except httpx.RequestError:
        raise HTTPException(503, "Shard unavailable")

    if response.status_code == 404:
        raise HTTPException(404, "Record not found")

    if response.status_code != 200:
        raise HTTPException(502, "Shard read failed")

    return response.json()




@app.head("/tables/{tableName}/records/{key}", tags=["Records"])
def record_exists(tableName: str, key: str):
    if tableName not in tables:
        raise HTTPException(404, "Table not found")

    routing_key = f"{tableName}:{key}"
    shard_id = hash_ring.get_node(routing_key)

    if shard_id is None:
        raise HTTPException(503, "No shards registered")

    shard_url = shards[shard_id]

    try:
        response = httpx.head(
            f"{shard_url}/tables/{tableName}/records/{key}",
            timeout=5.0
        )
    except httpx.RequestError:
        raise HTTPException(503, "Shard unavailable")

    if response.status_code == 404:
        raise HTTPException(404, "Record not found")

    if response.status_code != 200:
        raise HTTPException(502, "Shard request failed")

    return Response(status_code=200)




@app.delete(
    "/tables/{tableName}/records/{key}",
    status_code=204,
    tags=["Records"]
)
def delete_record(tableName: str, key: str):
    if tableName not in tables:
        raise HTTPException(404, "Table not found")

    routing_key = f"{tableName}:{key}"
    shard_id = hash_ring.get_node(routing_key)

    if shard_id is None:
        raise HTTPException(503, "No shards registered")

    shard_url = shards[shard_id]

    try:
        response = httpx.delete(
            f"{shard_url}/tables/{tableName}/records/{key}",
            timeout=5.0
        )
    except httpx.RequestError:
        raise HTTPException(503, "Shard unavailable")

    if response.status_code == 404:
        raise HTTPException(404, "Record not found")

    if response.status_code != 204:
        raise HTTPException(502, "Shard delete failed")

    return Response(status_code=204)




@app.post("/shards/register", status_code=201, tags=["Shards"])
def register_shard(shard: ShardRegistration):
    if shard.shardId in shards:
        raise HTTPException(409, "Shard already registered")

    shards[shard.shardId] = shard.url
    hash_ring.add_node(shard.shardId)

    return {
        "message": "Shard registered",
        "shardId": shard.shardId,
        "url": shard.url
    }


@app.get("/shards", tags=["Shards"])
def list_shards():
    return {
        "shards": [
            {"shardId": shard_id, "url": url}
            for shard_id, url in shards.items()
        ]
    }


@app.get("/shards/lookup/{key}", tags=["Shards"])
def lookup_shard(key: str):
    shard_id = hash_ring.get_node(key)

    if shard_id is None:
        raise HTTPException(503, "No shards registered")

    return {
        "key": key,
        "shardId": shard_id,
        "url": shards[shard_id]
    }

