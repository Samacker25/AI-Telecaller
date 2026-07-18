# 07 — Security

**Project:** AI Telecaller for Hospitals (MVP)

**Version:** 1.0

**Status:** Approved

**Owner:** Security Architecture Team

---

# 1. Purpose

This document defines the minimum security requirements for the AI Telecaller MVP.

The objective is to ensure that the application is secure by design while remaining simple enough for rapid MVP development.

Security is treated as a product requirement rather than a post-development activity.

---

# 2. Security Objectives

The MVP must protect:

- Hospital knowledge
- Administrator accounts
- AI services
- User conversations
- Uploaded documents
- Infrastructure
- API endpoints

The system must remain available, trustworthy, and resistant to common attack vectors.

---

# 3. Security Principles

The application follows these principles.

## Secure by Default

All components must be secure without requiring additional configuration.

---

## Least Privilege

Users, administrators, APIs, and services receive only the permissions required to perform their tasks.

---

## Defense in Depth

Security controls exist at multiple layers.

- Frontend
- API
- AI Pipeline
- Database
- Infrastructure

---

## Zero Trust

No request is trusted automatically.

Every request is authenticated, validated, and authorized.

---

## Fail Securely

If a component fails, it must fail safely without exposing sensitive information.

---

# 4. Threat Model

Primary threats include:

- Unauthorized administrator access
- Credential theft
- API abuse
- Prompt injection
- Jailbreak attempts
- Hallucinated medical responses
- Malicious document uploads
- Data leakage
- Denial of Service (DoS)
- Cost abuse of AI APIs

---

# 5. Authentication

Administrator authentication requirements:

- JWT-based authentication
- Secure password hashing (Argon2id or bcrypt)
- Strong password policy
- Token expiration
- Token revocation support
- HTTPS only

Patients use the chatbot anonymously during the MVP.

---

# 6. Authorization

Protected operations include:

- Upload documents
- Delete documents
- Manage FAQs
- View audit logs
- Trigger re-indexing

Public users must never access administrative endpoints.

---

# 7. API Security

All APIs must implement:

- HTTPS
- JWT verification
- Input validation
- Output encoding
- Request size limits
- Rate limiting
- Structured error responses

No internal stack traces should be returned to clients.

---

# 8. Input Validation

Every request must be validated.

Examples

- Empty values
- Invalid UUIDs
- Invalid email formats
- Oversized payloads
- Unsupported file types
- Invalid JSON

Reject malformed requests before business logic executes.

---

# 9. File Upload Security

Accepted formats:

- PDF
- DOCX
- TXT

Requirements:

- MIME type validation
- File size limits
- Filename sanitization
- Malware scanning (future)
- Storage outside the web root
- Randomized storage paths

Executable files must never be accepted.

---

# 10. AI Security

The AI assistant must never:

- Diagnose diseases
- Prescribe medication
- Invent doctor schedules
- Invent hospital policies
- Guess unavailable information

All responses must be grounded in retrieved knowledge.

If sufficient context is unavailable, the AI must escalate to a human.

---

# 11. Prompt Injection Protection

The AI pipeline must defend against:

- Instruction overrides
- Role manipulation
- Prompt leakage
- Context poisoning
- Jailbreak attempts

User prompts must never replace or modify system prompts.

---

# 12. RAG Security

Knowledge retrieval rules:

- Retrieve only approved documents
- Ignore inactive knowledge
- Respect metadata filters
- Never expose hidden documents
- Never retrieve deleted content

The AI should answer only from verified knowledge sources.

---

# 13. Conversation Security

Conversation history should:

- Remain isolated per session
- Never leak between users
- Be stored securely
- Exclude sensitive internal metadata

Session identifiers must be unpredictable UUIDs.

---

# 14. Data Protection

Sensitive data includes:

- Administrator credentials
- Conversation history
- Audit logs
- Uploaded documents

Requirements:

- Encryption in transit (TLS)
- Secure storage
- Principle of least privilege
- Regular backups

Passwords must never be stored in plaintext.

---

# 15. Secrets Management

Secrets include:

- Gemini API Key
- Pinecone API Key
- JWT Secret
- Database URL

Requirements:

- Environment variables only
- Never commit secrets to Git
- Rotate secrets periodically
- Separate development and production credentials

---

# 16. Database Security

Requirements:

- Parameterized queries
- ORM protection against SQL injection
- Least-privilege database user
- Encrypted connections
- Regular backups

Direct SQL string concatenation is prohibited.

---

# 17. Logging & Auditing

Security-relevant events must be logged.

Examples:

- Login attempts
- Failed authentication
- Document uploads
- Document deletions
- FAQ changes
- AI escalation events
- Administrative actions

Sensitive data must not appear in logs.

---

# 18. Rate Limiting

Apply limits to public endpoints.

Examples:

| Endpoint | Limit |
|----------|-------|
| Chat | 30 requests/minute/IP |
| Login | 5 attempts/minute/IP |
| Document Upload | 10 uploads/hour |
| Admin APIs | Configurable |

Rate limits protect both infrastructure and AI usage costs.

---

# 19. AI Cost Protection

Protect external AI APIs through:

- Request rate limiting
- Input size limits
- Maximum conversation length
- Request timeouts
- Daily usage monitoring

The system should reject abusive requests before invoking the LLM.

---

# 20. Error Handling

Error responses must:

- Be consistent
- Avoid internal implementation details
- Avoid exposing stack traces
- Use standardized error codes

Example:

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required."
  }
}
```

---

# 21. Security Headers

Recommended HTTP headers:

- Strict-Transport-Security
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Content-Security-Policy
- Permissions-Policy

These should be configured by the backend and reverse proxy.

---

# 22. Infrastructure Security

Deployment requirements:

- HTTPS enabled
- Automatic TLS renewal
- Firewall rules
- Principle of least privilege
- Managed cloud services
- Environment isolation

Development and production environments must remain separate.

---

# 23. Backup & Recovery

Minimum requirements:

- Daily PostgreSQL backup
- Versioned document storage
- Secure backup retention
- Recovery procedure documentation

Recovery procedures should be tested periodically.

---

# 24. Incident Response

In the event of a security incident:

1. Detect
2. Contain
3. Investigate
4. Recover
5. Document
6. Review

Every incident should produce a post-incident report.

---

# 25. Security Testing

Before production release, perform:

- Authentication testing
- Authorization testing
- API validation testing
- Prompt injection testing
- File upload testing
- SQL injection testing
- XSS testing
- Rate limit testing
- Dependency vulnerability scanning

Security testing is part of the release checklist.

---

# 26. Compliance Considerations

The MVP is designed with future healthcare compliance in mind.

Future releases may align with:

- HIPAA
- GDPR
- ISO 27001
- SOC 2

The MVP itself is not certified for these standards.

---

# 27. Security Checklist

Before every deployment:

- All dependencies updated
- No known critical vulnerabilities
- Secrets stored securely
- HTTPS enabled
- JWT functioning
- Rate limiting enabled
- Audit logging enabled
- Prompt injection protections verified
- File upload restrictions verified
- Backup process verified

---

# 28. Future Enhancements

Phase 2:

- Malware scanning
- MFA for administrators
- Voice security
- Advanced monitoring

Phase 3:

- AI red-team automation
- Automated threat detection
- Continuous compliance monitoring
- Zero-trust network architecture

Phase 4:

- RBAC
- Tenant isolation
- SIEM integration
- Security dashboards


---

# 29. Security Principles Summary

Every engineer working on this project must follow these rules:

- Validate all inputs
- Authenticate every privileged request
- Authorize every protected operation
- Encrypt sensitive data
- Never hardcode secrets
- Never trust AI output without retrieval
- Never expose internal errors
- Log security-relevant events
- Prefer safe failure over risky success

---

# 30. Summary

The AI Telecaller MVP adopts a practical, security-first architecture suitable for handling hospital operational information while remaining lightweight enough for rapid product development.

Key characteristics include:

- Secure-by-default architecture
- JWT-protected administration
- AI guardrails against hallucination
- Retrieval-based response generation
- Protected document ingestion
- Least-privilege access control
- Rate limiting and cost protection
- Audit-ready operational logging

This baseline establishes a strong security foundation that can evolve into enterprise-grade controls as the platform grows into a multi-tenant SaaS solution.