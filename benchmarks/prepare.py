
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"
TABLE = "benchmark"
COUNT = 1000


def post(path, payload):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


post("/tables", {"name": TABLE, "partitionKey": "id"})

with open("benchmarks/read_urls.txt", "w") as trace:
    for i in range(COUNT):
        key = f"record_{i}"
        post(
            f"/tables/{TABLE}/records",
            {"key": key, "value": {"number": i}},
        )
        trace.write(f"/tables/{TABLE}/records/{key}\n")

print(f"Created {COUNT} records and URL trace.")
