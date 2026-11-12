# Younis Travel — site generator

One entry point: `build_site.py` (runs the whole pipeline into `../site_v3/`).

## Layout
- `gen/base.py` — v1 content model: services, destinations, FAQ, copy blocks.
- `gen/layout.py` — the single page layout (header/footer/nav rendered once,
  used by every page) + homepage, visa directory, static pages.
- `gen/seo.py` — llms.txt, per-page FAQ schema, image WebP optimization.
- `gen/countries.py` — per-country visa pages (AR/EN) + IndexNow submission.
- `gen/publish_fixes.py` — audit fixes: image resizing, landmarks, robots
  content signals, security headers.
- `gen/agents.py` — agent layer: Markdown-for-Agents, Agent Skills index,
  WebMCP tools, AI catalog (ARD).
- `gen/booking.py` — booking system pages + Vercel serverless API sources
  (copied from `api_src/`).
- `gen/oauth.py` — OAuth 2.0 layer (real client-credentials server) +
  discovery metadata + auth.md.
- `api_src/` — the serverless functions (bookings, tracking, MCP, OAuth).
- `assets/` — master inputs the build consumes: destination photos (`images/`, JPG masters; WebP/resized variants are derived) and the IBM Plex Sans Arabic fonts (`fonts/`).
- `test_api.js`, `test_oauth.js`, `test_security.js` — local test suites
  (in-memory storage driver; run with plain `node`).

History of every stage is tracked in git — the stage files are the current
pipeline, not versioned copies.
