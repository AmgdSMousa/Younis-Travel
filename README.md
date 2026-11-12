# Younis Travel — younistravel.site

The production website of **Younis Travel** (visas, flights, hotels, trips & travel
insurance), deployed on Vercel and linked to this repository. Arabic + English,
static pages plus a serverless booking API.

## Structure

- Root = the deployable site: static HTML pages (AR at root, EN under `en/`,
  per-country visa pages under `visas/`), `md/` markdown copies served to AI
  agents via content negotiation, `skills/` agent skill guides, `.well-known/`
  discovery artifacts (API catalog, MCP server card, agent-skills index, ARD
  catalog), `vercel.json` (headers, markdown-negotiation redirects).
- `api/` — Vercel serverless functions (zero-dependency Node):
  - `bookings.js` — create/list/update/delete bookings (admin ops need the
    `x-admin-token` header matching the `ADMIN_TOKEN` env var)
  - `track.js` — public status lookup by booking reference + phone
  - `health.js`, `openapi.js` — status + OpenAPI description
  - `mcp.js` — MCP server (tools: `younis_travel_services`, `create_booking`,
    `track_booking`)
  - `_lib.js` — Upstash Redis storage + validation
- `generator/` — the Python site generators (`build_site*.py`, each version runs
  the previous chain and overlays its layer; `build_site_v35.py` is current),
  the API sources in `api_src/` (copied into `api/` at build time), and
  `test_api.js` (local end-to-end test of the API with an in-memory driver:
  `node generator/test_api.js`, run from the generator folder's parent).

## Booking system

Travellers book at `/request.html` (3 steps) and receive a reference
(`YT-XXXXXX`); status is tracked at `/track.html`; the team manages bookings at
`/admin.html`. Data lives in Upstash Redis, configured through the Vercel
project env vars `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN` and
`ADMIN_TOKEN` (values are NOT stored in this repo). No prices are published and
no payment is taken online — the team replies per booking.

## Notes

- `images/` and `fonts/` contain binary assets. The fonts are committed here;
  the images are uploaded through the GitHub web UI when they change, because
  the automated sync only carries text files.
- Rebuilding: run `python3 generator/build_site_v35.py` in the workspace, which
  regenerates the deployable tree, then deploy to Vercel.
