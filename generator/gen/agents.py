"""Younis Travel — v3.4 agent-readiness layer (from the isitagentready fix list Amged pasted).
Implements only what is TRUE for this static site:
- Markdown for Agents: pre-generated markdown copies + Accept-based rewrites on Vercel.
- Agent Skills discovery index + two real SKILL.md guides for agents.
- WebMCP: registerTool() tools wired to the real request form + declarative form attributes.
- ARD ai-catalog.json describing the site's real resources.
Deliberately NOT implemented (would be fabrication — no such systems exist on this site):
API catalog, OAuth/OIDC metadata, auth.md, MCP server card.
Runs the v3.3 build first, then post-processes site_v3/."""
import os, sys, json, re, html as htmllib, hashlib
from gen import base as B
from gen import layout as V3
from gen import publish_fixes as V33
from gen import countries as V32

OUT = V3.OUT
BASE = B.BASE

WEBMCP_JS = """
<script>
(function(){var mc=document.modelContext||(window.navigator&&navigator.modelContext);if(!mc||typeof mc.registerTool!=='function')return;
var en=(document.documentElement.lang||'').indexOf('en')===0;
function reqUrl(svc,dest){var p=new URLSearchParams();if(svc)p.set('s',svc);if(dest)p.set('d',dest);var q=p.toString();return (en?'/en/request.html':'/request.html')+(q?('?'+q):'');}
var tools=[
{name:'prepare_travel_request',description:'Open the Younis Travel request form prefilled with a service and destination so the traveller can review it and send a booking request. Younis Travel is request-based: no online payment and no prices on the website; the team replies on Facebook Messenger with exact prices and next steps.',inputSchema:{type:'object',properties:{service:{type:'string',enum:['visa','flight','hotel','trip','insurance'],description:'The requested service'},destination:{type:'string',description:'Destination country or city'}},required:['service']},execute:function(a){var u=reqUrl(a&&a.service,a&&a.destination);window.location.href=u;return{opened:u,next:'The traveller reviews the prefilled form, adds name, dates and travellers, then sends the request to the team via Facebook Messenger.'};}},
{name:'younis_travel_services',description:'List the services Younis Travel offers and how requesting works.',inputSchema:{type:'object',properties:{}},execute:function(){return{services:['e-Visas: Turkey, Vietnam, Albania, Kenya, United Arab Emirates','Embassy and Tasheer appointment booking: USA, Schengen countries, United Kingdom, Saudi Arabia','Flights: comparison across 500+ airlines; payment by cash, bank transfer or electronic payment; ticket delivered by WhatsApp and email','Hotels: closed B2B rates, official receipts accepted by embassies and airports','Trips and travel insurance'],how:'Prepare a request on the website request form; it is sent to the team via Facebook Messenger, and the team replies with exact prices and steps.'};}}
];
tools.forEach(function(t){try{var r=mc.registerTool(t);if(r&&r.catch)r.catch(function(){});}catch(e){}});
})();
</script>
"""

_orig_v33_layout = V3.layout3  # already wrapped by v33 (adds <main>)
def layout34(title, desc, path, body, lang='ar', extra_head=''):
    out = _orig_v33_layout(title, desc, path, body, lang=lang, extra_head=extra_head)
    out = out.replace('</head>', '<link rel="ai-catalog" href="/.well-known/ai-catalog.json">\n</head>', 1)
    return out.replace('</body>', WEBMCP_JS + '</body>', 1)
V3.layout3 = layout34

# ---------------------------------------------------------------- markdown copies
def html_to_md(page_html, url):
    t = re.search(r'<title>(.*?)</title>', page_html, re.S)
    title = htmllib.unescape(t.group(1)).split(' | ')[0] if t else 'Younis Travel'
    m = re.search(r'<main>(.*?)</main>', page_html, re.S)
    body = m.group(1) if m else page_html
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
    body = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n# \1\n', body, flags=re.S)
    body = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', body, flags=re.S)
    body = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', body, flags=re.S)
    body = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', body, flags=re.S)
    body = re.sub(r'<strong>(.*?)</strong>', r'**\1**', body, flags=re.S)
    body = re.sub(r'<li[^>]*>', '\n- ', body)
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'</(p|div|section|article|ul|ol|details|summary|figure|figcaption)>', '\n', body)
    body = re.sub(r'<[^>]+>', '', body)
    body = htmllib.unescape(body)
    body = re.sub(r'[ \t]+', ' ', body)
    body = re.sub(r'\n\s*\n\s*\n+', '\n\n', body).strip()
    return f'# {title}\n\nSource: {url}\n\n{body}\n'

PAGES = (['index.html', 'visas.html', 'flights.html', 'hotels.html', 'trips.html', 'request.html']
         + ['en/' + p for p in ('index.html', 'visas.html', 'flights.html', 'hotels.html', 'trips.html', 'request.html')]
         + [f'visas/{c}.html' for c in V32.COUNTRIES] + [f'en/visas/{c}.html' for c in V32.COUNTRIES])

# ---------------------------------------------------------------- agent skills
SKILL_SERVICES = """---
name: younis-travel-services
description: Factual guide to Younis Travel's services (visas, flights, hotels, trips, insurance) for agents answering traveller questions or preparing a booking request.
---

# Younis Travel — services guide for agents

Younis Travel is an Egyptian travel service. The website (https://www.younistravel.site)
is request-based: it publishes NO prices, takes NO online payment, and confirms nothing
automatically. Every request is reviewed by the human team, who reply on Facebook
Messenger with exact prices and next steps.

## Services (only state these — never invent prices, durations, fees or requirements)

- **e-Visas** (applied for online): Turkey, Vietnam, Albania, Kenya, United Arab Emirates.
  Per-country pages: https://www.younistravel.site/visas/turkey.html (and /uae, /vietnam,
  /kenya, /albania). Arabic and English versions exist under the same paths.
- **Embassy / Tasheer appointment booking**: USA, Schengen countries, United Kingdom,
  and Saudi Arabia (Saudi appointments are booked through Tasheer centres).
  Saudi page: https://www.younistravel.site/visas/saudi.html
- **Flights**: comparison across 500+ airlines; payment by cash, bank transfer or
  electronic payment; the ticket is delivered by WhatsApp and by email.
- **Hotels**: closed B2B rates; official receipts that embassies and airports accept.
- **Trips & travel insurance**: organised trips and travel insurance policies.

## How a request works

1. The traveller fills the request form at https://www.younistravel.site/request.html
   (service, destination, dates, travellers, name, notes).
2. The form composes a summary and opens Facebook Messenger to the Younis Travel Page.
3. The team replies with exact prices, required documents and the next steps.
4. The traveller pays by the agreed method; tickets/receipts are delivered as above.

## Rules for agents

- Never quote a price, discount, visa fee, processing time or document list — the site
  does not publish them; the team provides them per request.
- Direct every booking intent to the request form above or the Facebook Page:
  https://www.facebook.com/profile.php?id=61596173995345
- A fuller machine-readable brief lives at https://www.younistravel.site/llms-full.txt
"""

SKILL_REQUEST = """---
name: prepare-booking-request
description: How an agent prepares a Younis Travel booking request for a traveller using the website request form (fields, prefill parameters, and what happens after sending).
---

# Prepare a Younis Travel booking request

Younis Travel takes requests, not instant bookings. Your job is to prepare a complete,
accurate request; the human team prices it and replies on Facebook Messenger.

## Prefill the form with URL parameters

Open: https://www.younistravel.site/request.html?s=<service>&d=<destination>
(English: https://www.younistravel.site/en/request.html)

- `s` — one of: `visa`, `flight`, `hotel`, `trip`, `insurance`
- `d` — destination country or city, free text (e.g. `Turkey`, `تركيا`)

## Fields the traveller completes

- Full name
- Destination (prefilled from `d`)
- From / to dates (as applicable to the service)
- Number of travellers
- Free-text notes: hotel area or class, flight times, visa purpose — anything the
  team needs to price the request correctly.

## After the traveller presses send

1. The form composes a text summary of the request.
2. It opens the Younis Travel Facebook Page messages with the summary ready to send.
3. The team replies there with exact prices and the next steps.
4. Payment (when agreed) is by cash, bank transfer or electronic payment — never
   through the website itself.

## Accuracy rules

- Do not add prices, offers or deadlines to the request that the traveller did not state.
- If the traveller has no fixed dates yet, leave the date fields empty and say so in notes.
- One request per service: a flight + hotel trip is two requests or one `trip` request
  that mentions both in the notes.
"""

ARD = {
    "specVersion": "1.0",
    "host": {"displayName": "Younis Travel", "identifier": "did:web:younistravel.site"},
    "entries": [
        {"identifier": "urn:air:younistravel.site:site:main",
         "displayName": "Younis Travel website (Arabic & English)",
         "type": "text/html", "url": BASE + "/",
         "representativeQueries": ["احجز تأشيرة لتركيا", "book a flight to Dubai with Younis Travel",
                                   "hotels in Istanbul with official receipts"]},
        {"identifier": "urn:air:younistravel.site:docs:llms-full",
         "displayName": "Younis Travel factual brief for AI systems (llms-full.txt)",
         "type": "text/plain", "url": BASE + "/llms-full.txt",
         "representativeQueries": ["what services does Younis Travel offer",
                                   "ما هي خدمات يونس ترافيل للتأشيرات"]},
        {"identifier": "urn:air:younistravel.site:skills:index",
         "displayName": "Younis Travel agent skills index",
         "type": "application/json", "url": BASE + "/.well-known/agent-skills/index.json",
         "representativeQueries": ["how can an agent prepare a booking request with Younis Travel",
                                   "agent skill for Younis Travel services"]},
        {"identifier": "urn:air:younistravel.site:form:request",
         "displayName": "Younis Travel booking request form",
         "type": "text/html", "url": BASE + "/request.html",
         "representativeQueries": ["اطلب حجز طيران", "request a Saudi Tasheer appointment",
                                   "احجز فندق عن طريق يونس ترافيل"]},
    ],
}

def main():
    V33.main()

    # --- markdown copies + negotiation metadata
    md_tokens = {}
    for rel in PAGES:
        src = os.path.join(OUT, rel)
        with open(src, encoding='utf-8') as fh:
            page = fh.read()
        url = BASE + '/' + ('' if rel == 'index.html' else rel)
        md = html_to_md(page, url)
        dst = os.path.join(OUT, 'md', rel[:-5] + '.md')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'w', encoding='utf-8') as fh:
            fh.write(md)
        md_tokens['/md/' + rel[:-5] + '.md'] = str(max(1, len(md.split())))

    # --- agent skills + index
    skills_dir = os.path.join(OUT, 'skills')
    specs = [('younis-travel-services', SKILL_SERVICES,
              'Factual guide to Younis Travel services (e-visas, Tasheer/embassy appointments, flights, hotels, trips, insurance), what the site does and does not publish, and how requests work.'),
             ('prepare-booking-request', SKILL_REQUEST,
              'How an agent prepares a Younis Travel booking request: request-form fields, URL prefill parameters, and the Facebook Messenger hand-off that follows.')]
    index_skills = []
    for name, content, desc in specs:
        d = os.path.join(skills_dir, name)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, 'SKILL.md')
        data = content.encode('utf-8')
        with open(p, 'wb') as fh:
            fh.write(data)
        index_skills.append({'name': name, 'type': 'skill-md', 'description': desc,
                             'url': f'{BASE}/skills/{name}/SKILL.md',
                             'digest': 'sha256:' + hashlib.sha256(data).hexdigest()})
    wk = os.path.join(OUT, '.well-known')
    os.makedirs(wk, exist_ok=True)
    os.makedirs(os.path.join(wk, 'agent-skills'), exist_ok=True)
    with open(os.path.join(wk, 'agent-skills', 'index.json'), 'w', encoding='utf-8') as fh:
        json.dump({'$schema': 'https://schemas.agentskills.io/discovery/0.2.0/schema.json',
                   'skills': index_skills}, fh, ensure_ascii=False, indent=2)

    # --- ARD catalog
    with open(os.path.join(wk, 'ai-catalog.json'), 'w', encoding='utf-8') as fh:
        json.dump(ARD, fh, ensure_ascii=False, indent=2)

    # --- robots: Agentmap pointer to the catalog
    rp = os.path.join(OUT, 'robots.txt')
    with open(rp, encoding='utf-8') as fh:
        robots = fh.read()
    with open(rp, 'w', encoding='utf-8') as fh:
        fh.write(robots.rstrip() + f'\n\nAgentmap: {BASE}/.well-known/ai-catalog.json\n')

    # --- declarative WebMCP attributes on the request form
    for rel in ('request.html', 'en/request.html'):
        p = os.path.join(OUT, rel)
        with open(p, encoding='utf-8') as fh:
            h = fh.read()
        h = h.replace('<form id="reqForm">',
                      '<form id="reqForm" toolname="prepare_travel_request" tooldescription="Prepare a Younis Travel booking request: choose a service, destination, dates and travellers; the request is sent to the team via Facebook Messenger, which replies with exact prices and steps.">')
        for fid, desc in (('name', 'Traveller full name'), ('dest', 'Destination country or city'),
                          ('dates', 'Travel dates and duration'), ('people', 'Number of travellers'),
                          ('service', 'Requested service: visa, flight, hotel, trip or insurance'),
                          ('notes', 'Notes for the team: hotel area or class, preferred times, visa purpose')):
            h = h.replace(f'id="{fid}"', f'id="{fid}" toolparamdescription="{desc}"')
        with open(p, 'w', encoding='utf-8') as fh:
            fh.write(h)

    # --- vercel.json: markdown negotiation rewrites + headers
    vj_path = os.path.join(OUT, 'vercel.json')
    vj = json.load(open(vj_path))
    ACC = [{'type': 'header', 'key': 'accept', 'value': '.*text/markdown.*'}]
    # redirects (307) rather than rewrites: on Vercel rewrites run after the static
    # filesystem, so existing .html files shadow them; redirects run first.
    vj['redirects'] = [dict(r, statusCode=307) for r in [
        {'source': '/', 'has': ACC, 'destination': '/md/index.md'},
        {'source': '/index.html', 'has': ACC, 'destination': '/md/index.md'},
        {'source': '/en', 'has': ACC, 'destination': '/md/en/index.md'},
        {'source': '/en/', 'has': ACC, 'destination': '/md/en/index.md'},
        {'source': '/en/index.html', 'has': ACC, 'destination': '/md/en/index.md'},
        {'source': '/visas/:c.html', 'has': ACC, 'destination': '/md/visas/:c.md'},
        {'source': '/en/visas/:c.html', 'has': ACC, 'destination': '/md/en/visas/:c.md'},
        {'source': '/en/:p.html', 'has': ACC, 'destination': '/md/en/:p.md'},
        {'source': '/:p.html', 'has': ACC, 'destination': '/md/:p.md'},
    ]]
    for path, tokens in md_tokens.items():
        vj['headers'].append({'source': path, 'headers': [
            {'key': 'Content-Type', 'value': 'text/markdown; charset=utf-8'},
            {'key': 'x-markdown-tokens', 'value': tokens}]})
    vj['headers'].append({'source': '/.well-known/ai-catalog.json', 'headers': [
        {'key': 'Access-Control-Allow-Origin', 'value': '*'},
        {'key': 'Content-Type', 'value': 'application/json'}]})
    vj['headers'].append({'source': '/.well-known/agent-skills/index.json', 'headers': [
        {'key': 'Access-Control-Allow-Origin', 'value': '*'}]})
    with open(vj_path, 'w', encoding='utf-8') as fh:
        json.dump(vj, fh, indent=2)
    print('built v3.4 ->', OUT, '| md pages:', len(md_tokens), '| skills:', len(index_skills))

if __name__ == '__main__':
    main()
