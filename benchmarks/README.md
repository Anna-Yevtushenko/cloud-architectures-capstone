# Milestone 2 — YCSB Benchmark

## Configuration

- Tool: YCSB 0.18.0-SNAPSHOT
- Workload: REST read-only
- Coordinator: HTTP port 8000
- Shards: 2
- Dataset: 1000 records
- Operations: 5000 READ
- Threads: 1
- Request distribution: Uniform
- Storage: In-memory

## Results

| Metric | Value |
|---|---:|
| Throughput | 284.97 ops/sec |
| Runtime | 17.55 sec |
| Average latency | 3.48 ms |
| P50 latency | 3.03 ms |
| P95 latency | 5.51 ms |
| P99 latency | 7.67 ms |
| Successful reads | 5000 |
| Failed reads | 0 |

## Workload Choice

A read-only REST workload was selected to measure
read routing through the Coordinator and consistent
hashing across two shards.

The workload provides a reproducible baseline for
comparison with Milestones 3 and 5.

Limitations: single client thread, in-memory storage,
and no concurrent writes.
