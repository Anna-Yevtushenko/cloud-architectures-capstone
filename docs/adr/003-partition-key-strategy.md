
# ADR-003: Partition Key Strategy

## Status
Accepted

## Context
The key-value store supports multiple tables.

Records from different tables may have identical keys,
so routing must take the table name into account.

## Decision
- Each table has a declared partitionKey field.
- Each record has a unique key within its table.
- Use tableName:key as the routing key.
- Apply SHA-256 and consistent hashing to this key.
- Use the same routing strategy for CREATE,
  READ, EXISTS, and DELETE.
- Do not implement compound primary keys
  in Milestone 2.

## Alternatives Considered
- Hash only the record key: simple, but does not
  include the table namespace in routing.
- Compound partition and sort key: supports
  more complex data access, but adds complexity.

## Consequences
- Records from different tables are routed
  using separate key namespaces.
- All operations for the same table and key
  are directed to the same shard.
- The implementation remains simple.
- The declared partitionKey is currently metadata;
  routing uses the record's key field.
- Compound primary keys are not supported yet.
