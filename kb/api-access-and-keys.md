# API access and developer keys

**api_access** is a Pro and Enterprise entitlement, enabling programmatic access to your
Northbeam account via our REST API. See "What each plan includes" if you're unsure of your
plan.

## Generating an API key

1. Go to Account → Developer → API Keys → Generate New Key.
2. Name the key descriptively (e.g., "CI pipeline," "internal dashboard") — this helps you
   identify and revoke the right key later.
3. The full key is shown **once**, at creation. Copy it immediately and store it in a secrets
   manager or environment variable — Northbeam never displays the full key again.
4. Keys inherit your account's plan-level rate limits (see below); they do not have separate
   permissions from your account.

## Rate limits

- Pro: 60 requests/minute, 20,000 requests/day.
- Enterprise: 300 requests/minute, unlimited daily requests, plus the option of a **dedicated
  IP** for API traffic (Enterprise-only — see "What each plan includes").
- Exceeding the limit returns HTTP 429; back off and retry after the `Retry-After` header
  duration.

## Revoking or rotating keys

Go to Account → Developer → API Keys and click Revoke next to any key. Revocation is
immediate and cannot be undone — generate a new key if you still need access. Rotate keys
periodically and immediately if you suspect one was exposed (see "Reporting a security
concern").

## Common issues

- **401 Unauthorized**: key is invalid, revoked, or was copied with extra whitespace.
- **403 Forbidden on a specific endpoint**: your plan doesn't include that endpoint's
  feature (e.g., calling a dedicated-IP-only endpoint on Pro).
- **429 Too Many Requests**: you've hit your plan's rate limit — see above.

## When to contact support

Contact support if: a newly generated key returns 401 immediately, you're consistently
hitting rate limits below your plan's stated threshold, or you need to discuss a custom rate
limit for a legitimate high-volume use case.
