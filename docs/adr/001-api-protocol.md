
# ADR-001: API Protocol and Format

## Status
Accepted

## Context
The key-value store needs an API for managing tables
and performing CRUD operations on records.

The Coordinator must communicate with clients
and downstream shards.

## Decision
- Use REST over HTTP.
- Use JSON for request and response bodies.
- Use OpenAPI 3.0 for API documentation.
- Use FastAPI for implementation.
- Support CREATE (POST), READ (GET),
  EXISTS (HEAD), and DELETE (DELETE).
- Use standard HTTP status codes.

## Alternatives Considered
- GraphQL: more flexible queries, but unnecessary
  for simple key-value operations.
- gRPC: efficient communication, but requires
  additional tooling and is less convenient
  for testing directly in a browser.

## Consequences
- The API is simple to implement and test.
- Swagger UI provides interactive documentation.
- Standard HTTP methods make the API predictable.
- JSON is human-readable but has more overhead
  than binary formats.
