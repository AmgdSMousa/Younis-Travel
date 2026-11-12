"""Younis Travel — v3.3 fixes from the 2026-11-12 PageSpeed + isitagentready audits
(approved by Amged): destination images resized to display size, <main> landmark,
descriptive service link names, llms.txt links in markdown form, robots.txt
Content Signals + explicit AI-bot rules, Link + basic security headers.
Runs the v3.2 build, then post-processes its output in site_v3/."""
import os, json, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as B
import build_site_v3 as V3
import build_site_v31 as V31
import build_site_v32 as V32
from PIL import Image

OUT = V3.OUT
BASE = B.BASE

# 1) descriptive "learn more" link names on the home services cards
AR_LINKS = [('/visas.html', 'اعرف أكتر عن التأشيرات ←'), ('/flights.html', 'اعرف أكتر عن الطيران ←'),
            ('/hotels.html', 'اعرف أكتر عن الفنادق ←'), ('/trips.html', 'اعرف أكتر عن الرحلات والتأمين ←')]
EN_LINKS = [('/en/visas.html', 'Learn more about visas →'), ('/en/flights.html', 'Learn more about flights →'),
            ('/en/hotels.html', 'Learn more about hotels →'), ('/en/trips.html', 'Learn more about trips & insurance →')]
for href, label in AR_LINKS:
    V3.home3 = V3.home3.replace(f'<a href="{href}">اعرف أكتر ←</a>', f'<a href="{href}">{label}</a>')
for href, label in EN_LINKS:
    V3.home3_en = V3.home3_en.replace(f'<a href="{href}">Learn more →</a>', f'<a href="{href}">{label}</a>')

# 2) <main> landmark around page body
_orig_layout3 = V3.layout3
def layout3_main(title, desc, path, body, lang='ar', extra_head=''):
    html = _orig_layout3(title, desc, path, body, lang=lang, extra_head=extra_head)
    return html.replace('</header>', '</header><main>', 1).replace('<footer>', '</main><footer>', 1)
V3.layout3 = layout3_main

ROBOTS = f"""# Younis Travel — robots.txt
# Content signals: we welcome search indexing and AI answers that cite and link to our pages.
User-agent: *
Content-Signal: search=yes, ai-input=yes, ai-train=yes
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: CCBot
Allow: /

Sitemap: {BASE}/sitemap.xml
"""

def md_links(text):
    # "- Label: https://x" or "- https://x" -> markdown link form
    def rep(m):
        label, url = m.group(1).strip(' :'), m.group(2)
        if not label or label.lower() in ('home (arabic)', 'home (english)'):
            label = label or url
        return f'- [{label}]({url})'
    text = re.sub(r'^-\s+([^:\n]{0,60}?):\s+(https://\S+)$', rep, text, flags=re.M)
    text = re.sub(r'^-\s+(https://\S+)$', lambda m: f'- [{m.group(1)}]({m.group(1)})', text, flags=re.M)
    text = text.replace('Facebook Page: https://www.facebook.com/profile.php?id=61596173995345',
                        'Facebook Page: [Younis Travel on Facebook](https://www.facebook.com/profile.php?id=61596173995345)')
    return text

def main():
    V32.main()
    # images: destination cards display ~360-1080px wide; 900w is plenty and much lighter
    for n in ('saudi', 'turkey', 'uae', 'vietnam', 'kenya', 'albania'):
        jpg = os.path.join(OUT, 'images', n + '.jpg')
        webp = os.path.join(OUT, 'images', n + '.webp')
        im = Image.open(jpg).convert('RGB')
        if im.width > 900:
            im = im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS)
        im.save(webp, 'WEBP', quality=75)
    # robots.txt with content signals
    with open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8') as fh:
        fh.write(ROBOTS)
    # llms files: links in markdown form
    for f in ('llms.txt', 'llms-full.txt'):
        p = os.path.join(OUT, f)
        with open(p, encoding='utf-8') as fh:
            txt = fh.read()
        with open(p, 'w', encoding='utf-8') as fh:
            fh.write(md_links(txt))
    # vercel.json: Link headers + basic security headers on all paths
    vj_path = os.path.join(OUT, 'vercel.json')
    vj = json.load(open(vj_path))
    vj['headers'].append({
        'source': '/(.*)',
        'headers': [
            {'key': 'Link', 'value': f'<{BASE}/sitemap.xml>; rel="sitemap", <{BASE}/llms.txt>; rel="describedby"; type="text/plain"'},
            {'key': 'X-Content-Type-Options', 'value': 'nosniff'},
            {'key': 'Referrer-Policy', 'value': 'strict-origin-when-cross-origin'},
            {'key': 'X-Frame-Options', 'value': 'SAMEORIGIN'},
        ]})
    with open(vj_path, 'w', encoding='utf-8') as fh:
        json.dump(vj, fh, indent=2)
    print('built v3.3 ->', OUT)

if __name__ == '__main__':
    main()
