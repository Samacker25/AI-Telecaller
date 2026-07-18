# Security Skill

## Purpose

This document defines the secure development standards for the AI Telecaller project.

Security is a fundamental engineering requirement, not an optional feature.

Every component must be designed following the principle of **Secure by Default**.

---

# Core Security Principles

Always prioritize:

- Confidentiality
- Integrity
- Availability
- Least Privilege
- Defense in Depth
- Zero Trust
- Fail Secure

Never trade security for convenience.

---

# Secure Development Lifecycle

Every feature should consider:

```
Design

↓

Threat Modeling

↓

Implementation

↓

Testing

↓

Review

↓

Deployment

↓

Monitoring
```

Security is continuous throughout the software lifecycle.

---

# Authentication

Protect every administrative endpoint.

Current authentication:

- JWT Access Tokens

Future:

- Refresh Tokens
- OAuth
- Multi-Factor Authentication (MFA)

Never trust client-provided authentication data.

---

# Authorization

Authentication identifies a user.

Authorization determines what they can do.

Always verify permissions on the server.

Never rely on frontend restrictions.

---

# Principle of Least Privilege

Every user, service, and process should have only the permissions required to perform its function.

Avoid overly permissive roles.

---

# Password Security

Passwords must:

- Be hashed
- Never be encrypted for storage
- Never be logged
- Never be returned in API responses

Never store plaintext passwords.

---

# Secrets Management

Never hardcode:

- API Keys
- JWT Secrets
- Database URLs
- Credentials
- Tokens

Use environment variables or a secrets manager.

Secrets must never be committed to version control.

---

# Input Validation

Validate every external input.

Examples:

- JSON payloads
- Query parameters
- Path parameters
- Form data
- File uploads

Never trust user input.

---

# Output Encoding

Return only the data required.

Avoid exposing:

- Internal IDs (when unnecessary)
- Stack traces
- SQL errors
- Configuration details

---

# File Upload Security

Always validate:

- File type
- MIME type
- Extension
- File size

Reject unsupported files.

Future enhancements:

- Malware scanning
- Content validation

Never execute uploaded files.

---

# SQL Injection Prevention

Always use ORM queries or parameterized SQL.

Never build SQL queries using string concatenation.

---

# XSS Prevention

Never trust user-generated HTML.

Escape or sanitize content before rendering.

Avoid rendering raw HTML unless explicitly required.

---

# CSRF

For cookie-based authentication:

- Enable CSRF protection

For JWT Authorization headers:

- Use appropriate token handling
- Validate token origin where applicable

---

# Rate Limiting

Protect public endpoints against abuse.

Apply rate limiting to:

- Login
- Chat
- File Upload
- Password Reset

Future:

- Per-user limits
- Per-IP limits
- Adaptive throttling

---

# API Security

Every endpoint should:

- Validate authentication
- Validate authorization
- Validate input
- Return consistent error responses

Avoid exposing internal implementation details.

---

# AI Security Principles

The AI assistant must:

- Answer only from retrieved knowledge
- Reject unsafe requests
- Escalate when uncertain
- Refuse unsupported medical advice

Safety takes precedence over completeness.

---

# Prompt Injection Defense

Never allow user prompts to override system instructions.

Reject attempts to:

- Ignore previous instructions
- Reveal system prompts
- Bypass safety policies
- Fabricate answers

System instructions always have the highest priority.

---

# Retrieval Security

Only retrieve:

- Approved knowledge
- Authorized documents

Never expose hidden or unpublished content.

Future multi-tenant systems must isolate retrieval by tenant.

---

# Sensitive Data

Avoid collecting or storing unnecessary sensitive information.

Never log:

- Passwords
- Tokens
- Secrets
- Personal medical details
- API Keys

Mask sensitive values in logs.

---

# Logging

Log security-relevant events such as:

- Authentication failures
- Authorization failures
- Document uploads
- Permission changes
- AI escalation events

Logs should support auditing without exposing sensitive data.

---

# Error Handling

Return generic client-facing errors.

Log detailed internal errors separately.

Never expose:

- Stack traces
- SQL queries
- Internal exceptions

---

# Session Security

Use short-lived access tokens.

Invalidate sessions on logout when supported.

Future:

- Refresh token rotation
- Session revocation

---

# HTTPS

All production traffic must use HTTPS.

Never transmit credentials over insecure connections.

---

# CORS

Allow only trusted origins.

Do not use wildcard origins in production.

Keep CORS policies as restrictive as possible.

---

# Dependencies

Use maintained dependencies.

Regularly:

- Update packages
- Review vulnerabilities
- Remove unused libraries

Never ignore critical security advisories.

---

# Infrastructure Security

Production systems should:

- Run behind a reverse proxy
- Restrict unnecessary ports
- Use secure environment variables
- Enable automated backups
- Monitor system health

---

# Database Security

Use:

- Parameterized queries
- Least-privilege database users
- Encrypted connections

Never expose database credentials.

---

# Redis Security (Future)

When Redis is introduced:

- Require authentication
- Encrypt connections
- Disable public access
- Set expiration for temporary data

Never store secrets in Redis.

---

# Multi-Tenant Security (Future)

When SaaS is introduced:

- Enforce tenant isolation
- Validate tenant ownership
- Prevent cross-tenant access
- Scope every query by tenant

Tenant isolation is mandatory.

---

# Monitoring

Continuously monitor:

- Failed logins
- Suspicious API usage
- Rate limit violations
- AI abuse attempts
- Upload failures

Security monitoring should enable rapid incident response.

---

# Security Testing

Every release should include:

- Authentication testing
- Authorization testing
- Input validation testing
- File upload testing
- Prompt injection testing
- API security testing

Future:

- Penetration testing
- Dependency scanning
- Container scanning

---

# Incident Response

When a security issue is identified:

1. Contain the issue
2. Assess impact
3. Fix the vulnerability
4. Validate the fix
5. Document the incident
6. Add regression tests

Every incident should improve the system.

---

# Definition of Done

A feature is security-complete only if:

- Authentication is implemented where required.
- Authorization is enforced.
- Inputs are validated.
- Sensitive data is protected.
- Errors are handled safely.
- Logging is appropriate.
- Security tests pass.
- Documentation is updated.

---

# Anti-Patterns

Never:

- Hardcode secrets.
- Trust client input.
- Return internal errors.
- Log sensitive data.
- Disable authentication.
- Skip authorization checks.
- Execute uploaded files.
- Answer unsupported medical questions.
- Ignore prompt injection risks.

---

# Security Philosophy

Security is everyone's responsibility.

The AI Telecaller must be designed so that the safest behavior is the default behavior.

When uncertainty exists, prefer:

- Deny over Allow
- Escalate over Guess
- Validate over Trust
- Log over Ignore

Every line of code should preserve the confidentiality, integrity, and availability of hospital data while protecting users from unsafe AI behavior.