# Coding Rules

## General Principles

Write code that is:

- Simple
- Readable
- Testable
- Maintainable
- Secure

Prefer clarity over cleverness.

---

## Python

Always:

- Use type hints
- Use async for I/O
- Keep functions small
- Write reusable services
- Raise explicit exceptions

Avoid:

- Global mutable state
- Deep nesting
- Magic values
- Duplicate code

---

## FastAPI

Routes should:

- Validate input
- Call services
- Return responses

Business logic must never exist inside route handlers.

---

## Database

Always use:

Repository Layer

↓

Service Layer

↓

API

Never access the database directly from routes.

---

## AI

Always:

- Retrieve context before generation
- Ground responses
- Return uncertainty instead of hallucinating
- Escalate unsupported requests

---

## Security

Never:

- Hardcode secrets
- Trust user input
- Log sensitive information

Always:

- Validate input
- Sanitize uploads
- Verify authorization

---

## Testing

Every feature should include:

- Unit tests
- Integration tests
- API tests

Future AI changes must pass evaluation before release.

---

## Documentation

Keep documentation synchronized with implementation.

Update relevant files in `/docs` when architecture or APIs change.