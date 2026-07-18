# Feature Development Checklist

## Purpose

This checklist must be completed before a feature is considered ready for review.

---

## Requirements

- [ ] Product requirements are understood.
- [ ] Acceptance criteria are defined.
- [ ] Edge cases are identified.
- [ ] Dependencies are documented.

---

## Architecture

- [ ] Follows project architecture.
- [ ] No unnecessary abstractions.
- [ ] Reuses existing components.
- [ ] No duplicated logic.

---

## Backend

- [ ] API endpoint implemented.
- [ ] Request validation added.
- [ ] Response schema created.
- [ ] Service layer implemented.
- [ ] Repository layer implemented.
- [ ] Database migration created (if required).

---

## AI (if applicable)

- [ ] Prompt reviewed.
- [ ] RAG retrieval implemented.
- [ ] Hallucination risks considered.
- [ ] Confidence handling implemented.
- [ ] Escalation logic implemented.

---

## Security

- [ ] Authentication enforced.
- [ ] Authorization verified.
- [ ] Input validation complete.
- [ ] Secrets not exposed.
- [ ] Sensitive data protected.

---

## Testing

- [ ] Unit tests added.
- [ ] Integration tests added.
- [ ] Regression tests updated.
- [ ] Manual testing completed.

---

## Performance

- [ ] No unnecessary database queries.
- [ ] Async operations used where appropriate.
- [ ] No blocking code.
- [ ] Large responses paginated.

---

## Documentation

- [ ] API documentation updated.
- [ ] Architecture updated (if required).
- [ ] README updated (if required).

---

## Ready for Review

- [ ] All tests pass.
- [ ] Lint passes.
- [ ] No TODOs remain.
- [ ] Feature is production ready.