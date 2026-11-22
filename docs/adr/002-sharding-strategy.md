
# ADR-002: Sharding Strategy

## Status
Accepted

## Context
The key-value store needs to distribute records
across multiple shard instances.

The system should support adding new shards
without remapping every key.

## Decision
- Use SHA-256 for deterministic hashing.
- Use consistent hashing for shard selection.
- Assign 64 virtual nodes to each shard.
- Use tableName + key as the routing key.
- Register shards in the Coordinator through an API.
- Use the same hashing algorithm for reads and writes.

## Alternatives Considered
- Modulo hashing: simple, but adding a shard
  changes the mapping of many keys.
- Rendezvous hashing: also supports dynamic
  membership, but consistent hashing was chosen
  for its ring-based routing model.

## Consequences
- Records are distributed across multiple shards.
- Virtual nodes help improve key distribution.
- Adding shards changes the ownership of only
  part of the key space.
- The Coordinator is responsible for routing.
- Data migration is needed when ownership changes.
- The current implementation does not yet
  perform automatic data migration.
