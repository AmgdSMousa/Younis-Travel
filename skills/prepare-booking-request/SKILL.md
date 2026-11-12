---
name: prepare-booking-request
description: How an agent creates and tracks a real Younis Travel booking (booking API, references, status tracking) on behalf of a traveller.
---

# Create and track a Younis Travel booking

Younis Travel runs a real booking system. A booking is a structured request that the
human team reviews; the traveller receives a booking reference and can track its
status. No prices are published and no payment is taken online — the team replies
with exact prices and next steps.

## Create a booking

Either guide the traveller through the form:
- Arabic: https://www.younistravel.site/request.html?s=<service>&d=<destination>
- English: https://www.younistravel.site/en/request.html

or call the API directly:
`POST https://younistravel.site/api/bookings` with JSON
`{"service": "visa|flight|hotel|trip|insurance", "destination": "...", "dates": "...", "people": 1, "name": "...", "phone": "...", "notes": "..."}`
A 201 response returns `{"ref": "YT-XXXXXX", "status": "NEW", "track_url": "..."}`.
An MCP server exposing the same operations lives at https://younistravel.site/api/mcp
(tools: younis_travel_services, create_booking, track_booking). The OpenAPI document
is at https://younistravel.site/api/openapi.

## Track a booking

The traveller opens https://www.younistravel.site/track.html (English: /en/track.html)
and enters the reference plus the phone number used when booking — or call
`GET https://younistravel.site/api/track?ref=YT-XXXXXX&phone=...`.
Statuses: NEW (received) → CONTACTED → CONFIRMED → COMPLETED, or CANCELLED.

## Accuracy rules

- Never add prices, offers or deadlines the traveller did not state.
- The phone number is required: the team contacts the traveller on it, and it is the
  key for status tracking.
- One booking per service; a combined flight + hotel trip can be one `trip` booking
  that mentions both in the notes.
