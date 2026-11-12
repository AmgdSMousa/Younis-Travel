# auth.md — Younis Travel agent authentication

This document describes how AI agents and partner systems authenticate to the
Younis Travel Booking API. Everything below is live and describes the real
system.

## Who this is for

Agents and partner tools that need programmatic access to booking operations
beyond the public ones. Public operations need NO credentials:

- Create a booking: `POST https://younistravel.site/api/bookings`
- Track a booking: `GET https://younistravel.site/api/track?ref=YT-XXXXXX&phone=...`
- MCP tools at `https://younistravel.site/api/mcp` (services, create, track)

Protected operations (listing bookings, changing status, deleting) require
either the team admin token or an OAuth 2.0 access token with the right scope.

## Discovery

- Authorization server metadata: https://younistravel.site/.well-known/oauth-authorization-server
- Protected resource metadata: https://younistravel.site/.well-known/oauth-protected-resource
- OpenAPI: https://younistravel.site/api/openapi

## Registration

Credentials are provisioned by the Younis Travel team after a short review —
there is no instant self-service signup.

1. File a registration request:
   `POST https://younistravel.site/api/oauth/register`
   with JSON `{"name": "<your system or company>", "contact": "<email or phone>", "use_case": "<what you will do with booking access>"}`
   You receive a `request_id` with status `pending`.
2. The team reviews the request and verifies control of the contact email by
   sending the issued credentials only to that address — receiving them there
   is the identity claim step. If approved, you get a `client_id` and
   `client_secret`.
3. Keep the secret private; it is shown only once. Ask the team to rotate or
   revoke it if it leaks.

## Getting a token

OAuth 2.0 client-credentials grant at `POST https://younistravel.site/api/oauth/token`:

```
curl -X POST https://younistravel.site/api/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_ID&client_secret=YOUR_SECRET&scope=bookings:read"
```

The response is a Bearer JWT (RS256, 1 hour) — verify signatures with the JWKS
at https://younistravel.site/api/oauth/jwks.

## Scopes

- `bookings:read` — list bookings (GET /api/bookings)
- `bookings:write` — update status/notes and delete bookings (PATCH/DELETE /api/bookings)

## Using and revoking tokens

Send `Authorization: Bearer <token>` on protected calls. Revoke a token at
`POST https://younistravel.site/api/oauth/revoke` with your client credentials
and `{"token": "<access token>"}`.

## Contact

Younis Travel team via the Facebook Page: https://www.facebook.com/profile.php?id=61596173995345
