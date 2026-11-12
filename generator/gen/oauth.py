"""Younis Travel — v3.6 OAuth layer (Amged pasted the remaining isitagentready goals).
Everything here is REAL: a working OAuth 2.0 client-credentials authorization
server (JWT RS256 + JWKS + revocation) protects the booking API's admin
operations alongside the team token; agents register via a real endpoint and
the team provisions credentials after review. Metadata documents describe
exactly this system — nothing more. Runs the v3.5 build first."""
import os, sys, json, shutil
from gen import layout as V3
from gen import booking as V35

OUT = V3.OUT
BASE = 'https://younistravel.site'

AS_METADATA = {
    "issuer": BASE,
    "token_endpoint": BASE + "/api/oauth/token",
    "jwks_uri": BASE + "/api/oauth/jwks",
    "revocation_endpoint": BASE + "/api/oauth/revoke",
    "grant_types_supported": ["client_credentials"],
    "response_types_supported": [],
    "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"],
    "scopes_supported": ["bookings:read", "bookings:write"],
    "agent_auth": {
        "skill": BASE + "/auth.md",
        "register_uri": BASE + "/api/oauth/register",
        "identity_types_supported": ["identity_assertion"],
        "identity_assertion": {"assertion_types_supported": ["verified_email"],
                               "credential_types_supported": ["client_secret"]},
        "claim_uri": BASE + "/auth.md",
    },
}
PRM = {
    "resource": "https://www.younistravel.site",
    "authorization_servers": [BASE],
    "scopes_supported": ["bookings:read", "bookings:write"],
    "bearer_methods_supported": ["header"],
    "resource_documentation": BASE + "/llms-full.txt",
}
AUTH_MD = """# auth.md — Younis Travel agent authentication

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
curl -X POST https://younistravel.site/api/oauth/token \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
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
"""

def main():
    V35.main()
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api_src')
    api_out = os.path.join(OUT, 'api')
    shutil.copy(os.path.join(src, '_oauth.js'), os.path.join(api_out, '_oauth.js'))
    os.makedirs(os.path.join(api_out, 'oauth'), exist_ok=True)
    for fn in ('token.js', 'jwks.js', 'revoke.js', 'clients.js', 'register.js'):
        shutil.copy(os.path.join(src, 'oauth', fn), os.path.join(api_out, 'oauth', fn))

    wk = os.path.join(OUT, '.well-known')
    with open(os.path.join(wk, 'oauth-authorization-server'), 'w', encoding='utf-8') as fh:
        json.dump(AS_METADATA, fh, indent=2)
    with open(os.path.join(wk, 'oauth-protected-resource'), 'w', encoding='utf-8') as fh:
        json.dump(PRM, fh, indent=2)
    with open(os.path.join(OUT, 'auth.md'), 'w', encoding='utf-8') as fh:
        fh.write(AUTH_MD)

    p = os.path.join(OUT, 'llms-full.txt')
    txt = open(p, encoding='utf-8').read()
    txt += ('\n## API authentication\n\nProtected booking operations accept OAuth 2.0 client-credentials '
            'tokens (scopes: bookings:read, bookings:write). Discovery: ' + BASE + '/.well-known/oauth-authorization-server '
            'and ' + BASE + '/.well-known/oauth-protected-resource. Agent registration is documented at '
            + BASE + '/auth.md (team-reviewed provisioning — no instant signup).\n')
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(txt)

    vj_path = os.path.join(OUT, 'vercel.json')
    vj = json.load(open(vj_path))
    for path in ('/.well-known/oauth-authorization-server', '/.well-known/oauth-protected-resource'):
        vj['headers'].append({'source': path, 'headers': [
            {'key': 'Content-Type', 'value': 'application/json'},
            {'key': 'Access-Control-Allow-Origin', 'value': '*'}]})
    with open(vj_path, 'w', encoding='utf-8') as fh:
        json.dump(vj, fh, indent=2)
    print('built v3.6 ->', OUT, '| oauth endpoints + metadata + auth.md written')

if __name__ == '__main__':
    main()
