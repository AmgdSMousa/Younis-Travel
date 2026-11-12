"""Younis Travel — v3 generator. Upgrades over v2 (per competitor research 2026-11-12):
hero photo + tabbed request widget (flights/hotels/visas/trips-insurance), USP strip,
photo destination cards, visa-facts band, FAQ accordion + FAQPage schema, floating
message button + mobile sticky CTA. Copy stays Amged's approved texts only — no
invented prices, stats, or testimonials. Images: Wikimedia Commons (free licenses).
Output: site_v3/ (v2 site/ untouched)."""
import os, json, sys, shutil
from gen import base as B

OUT = os.path.join(B.PROJECT_DIR, 'site_v3')
FB_PAGE = B.FB_PAGE
BASE = B.BASE

CSS = B.CSS + """
.hero3{position:relative;padding:96px 0 120px;text-align:center;background:url('/images/hero.jpg') center 30%/cover no-repeat}
.hero3::before{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,22,38,.72),rgba(7,22,38,.88))}
.hero3 .wrap{position:relative}
.hero3 h1{font-size:46px;line-height:1.7;color:var(--goldlt);text-shadow:0 2px 18px rgba(0,0,0,.5)}
.hero3 p{font-size:20px;max-width:780px;margin:14px auto 0;color:var(--cream)}
.widget{position:relative;max-width:960px;margin:-84px auto 0;background:#fdfbf5;color:#12242f;border-radius:18px;box-shadow:0 24px 60px rgba(0,0,0,.45);padding:22px 22px 26px;text-align:start}
.widget h2{color:#0b2237;font-size:22px;margin-bottom:4px;line-height:1.6}
.widget .wsub{color:#5a7182;font-size:15px;margin-bottom:14px}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.tab{border:2px solid rgba(11,34,55,.18);background:transparent;color:#0b2237;font-family:inherit;font-weight:700;font-size:16px;padding:8px 18px;border-radius:999px;cursor:pointer}
.tab.on{background:var(--gold);border-color:var(--gold);color:#1a1405}
.panel{display:none}
.panel.on{display:block}
.wgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.widget label{color:#40586b;font-size:14.5px;display:block;margin-bottom:4px}
.widget input,.widget select{width:100%;background:#fff;border:1px solid #c9d6de;border-radius:10px;color:#12242f;padding:11px 12px;font-family:inherit;font-size:16px}
.widget .chk{display:flex;align-items:center;gap:8px;font-size:15px;color:#40586b}
.widget .chk input{width:auto}
.wsum{display:none;margin-top:16px;background:#0d2a42;color:var(--cream);border-radius:12px;padding:18px}
.wsum h3{color:var(--gold);margin-bottom:6px;font-size:19px}
.usps{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:26px}
.usp{display:flex;gap:12px;align-items:flex-start;background:var(--card);border:1px solid rgba(94,200,190,.2);border-radius:14px;padding:16px 18px}
.usp .ic{font-size:24px;line-height:1.4}
.usp p{font-size:16px}
.dgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;margin-top:28px}
.dcard{background:var(--card);border:1px solid rgba(232,184,75,.18);border-radius:16px;overflow:hidden}
.dcard img{width:100%;height:190px;object-fit:cover;display:block}
.dcard .db{padding:18px 20px 20px}
.dcard h3{color:var(--gold);font-size:21px;margin-bottom:4px}
.badge{display:inline-block;background:rgba(94,200,190,.16);color:var(--teal);border:1px solid rgba(94,200,190,.4);font-size:13.5px;padding:2px 10px;border-radius:999px;margin-bottom:8px}
.dcard p{font-size:16px;color:var(--cream)}
.dcard a{font-weight:700}
details.faq{background:var(--card);border:1px solid rgba(232,184,75,.18);border-radius:12px;padding:16px 20px;margin-top:12px}
details.faq summary{cursor:pointer;font-weight:700;color:var(--goldlt);font-size:17.5px}
details.faq p{margin-top:8px;color:var(--cream);font-size:16.5px}
.floatmsg{position:fixed;bottom:20px;inset-inline-end:20px;z-index:50;background:var(--gold);color:#1a1405;font-weight:700;padding:12px 20px;border-radius:999px;box-shadow:0 10px 30px rgba(0,0,0,.4)}
.floatmsg:hover{background:var(--goldlt);color:#1a1405}
.stickybar{display:none}
@media(max-width:640px){.hero3 h1{font-size:31px}.hero3{padding:64px 0 104px}
.stickybar{display:flex;position:fixed;bottom:0;left:0;right:0;z-index:49;background:rgba(7,22,38,.97);border-top:1px solid rgba(232,184,75,.35);padding:10px 14px;gap:10px}
.stickybar a{flex:1;text-align:center}
.floatmsg{bottom:76px}
body{padding-bottom:64px}}
"""

def layout3(title, desc, path, body, lang='ar', extra_head=''):
    en = (lang == 'en')
    prefix = '/en' if en else ''
    en_path = '/en' + path if path != '/' else '/en/'
    if en:
        nav = [('Home', '/'), ('Visas', '/visas.html'), ('Flights', '/flights.html'),
               ('Hotels', '/hotels.html'), ('Trips & Insurance', '/trips.html')]
        cta = 'Book Now'
        foot = 'Younis Travel — visas, flights, hotels, and tour programs.'
        fb_label = 'Our Facebook Page'
        req_label = 'Book Your Trip'
        switch_href, switch_label = path, 'العربية'
        og_locale, in_lang = 'en_US', 'en'
        float_label = '💬 Message Us'
    else:
        nav = [('الرئيسية', '/'), ('التأشيرات', '/visas.html'), ('الطيران', '/flights.html'),
               ('الفنادق', '/hotels.html'), ('الرحلات والتأمين', '/trips.html')]
        cta = 'اطلب حجزك'
        foot = 'Younis Travel — تأشيرات، طيران، فنادق، وبرامج سياحية.'
        fb_label = 'صفحتنا على فيسبوك'
        req_label = 'اطلب حجزك'
        switch_href, switch_label = en_path, 'English'
        og_locale, in_lang = 'ar_EG', 'ar'
        float_label = '💬 ابعتلنا رسالة'
    links = ''.join(f'<a href="{prefix}{u}">{t}</a>' for t, u in nav)
    canonical = BASE + (en_path if en else path)
    schema = {
        '@context': 'https://schema.org', '@type': 'TravelAgency',
        'name': 'Younis Travel', 'url': BASE + '/',
        'description': desc, 'sameAs': [FB_PAGE],
        'areaServed': 'EG', 'inLanguage': in_lang,
    }
    alternates = (f'<link rel="alternate" hreflang="ar" href="{BASE}{path}">\n'
                  f'<link rel="alternate" hreflang="en" href="{BASE}{en_path}">\n'
                  f'<link rel="alternate" hreflang="x-default" href="{BASE}{path}">')
    return f"""<!DOCTYPE html>
<html lang="{'en' if en else 'ar'}" dir="{'ltr' if en else 'rtl'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Younis Travel</title>
<meta name="description" content="{desc}">
<meta name="google-site-verification" content="zL5GI78-wG1QwSc5pazIywubl7DFkN_UbVySmW5A-Us">
<link rel="canonical" href="{canonical}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:title" content="{title} | Younis Travel">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="{og_locale}">
<meta property="og:image" content="{BASE}/images/hero.jpg">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect x='28' y='28' width='44' height='44' fill='none' stroke='%23e8b84b' stroke-width='8' transform='rotate(45 50 50)'/></svg>">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
{extra_head}
</head>
<body>
<header><div class="wrap nav">
<a class="logo" href="{prefix}/"><span class="diamond"></span> Younis Travel</a>
<nav class="links">{links}</nav>
<a class="cta-btn" href="{prefix}/request.html">{cta}</a>
</div></header>
{body}
<footer><div class="wrap">
<p>{foot}</p>
<p><a href="{FB_PAGE}" target="_blank" rel="noopener">{fb_label}</a> · <a href="{prefix}/request.html">{req_label}</a> · <a href="{switch_href}">{switch_label}</a></p>
</div></footer>
<a class="floatmsg" href="{FB_PAGE}" target="_blank" rel="noopener">{float_label}</a>
<div class="stickybar"><a class="cta-btn" href="{prefix}/request.html">{cta}</a></div>
</body>
</html>"""

# ---------- Request widget (hero) ----------
def field(fid, label, kind='text', opts=None, ph=''):
    if kind == 'select':
        o = ''.join(f'<option>{x}</option>' for x in opts)
        return f'<div><label for="{fid}">{label}</label><select id="{fid}" data-label="{label}">{o}</select></div>'
    if kind == 'chk':
        return f'<div class="chk"><input type="checkbox" id="{fid}" data-label="{label}"><label for="{fid}" style="margin:0">{label}</label></div>'
    return f'<div><label for="{fid}">{label}</label><input id="{fid}" data-label="{label}" type="{kind}" placeholder="{ph}"></div>'

def widget(lang='ar'):
    en = (lang == 'en')
    if en:
        tabs = [('flights', '✈ Flights'), ('hotels', '🏨 Hotels'), ('visas', '🛂 Visas'), ('trips', '🧳 Trips & Insurance')]
        title, sub = 'Plan Your Trip Now', 'Fill in your trip details and we will reply with the best options — no payment now, this is a request only.'
        name_l, btn = 'Your name (optional)', 'Prepare My Request'
        panels = {
            'flights': field('f-type', 'Trip type', 'select', ['Round trip', 'One way']) + field('f-from', 'From', 'text', ph='City') + field('f-to', 'To', 'text', ph='City') + field('f-dep', 'Departure date', 'date') + field('f-ret', 'Return date', 'date') + field('f-pax', 'Travelers', 'number', ph='2') + field('f-class', 'Class', 'select', ['Economy', 'Business']) + field('f-flex', 'My dates are flexible — find me the cheapest date', 'chk'),
            'hotels': field('h-city', 'City / destination', 'text', ph='e.g. Dubai') + field('h-in', 'Check-in date', 'date') + field('h-out', 'Check-out date', 'date') + field('h-rooms', 'Rooms', 'number', ph='1') + field('h-guests', 'Guests', 'number', ph='2') + field('h-stars', 'Preferred hotel class', 'select', ['Any', '3 stars', '4 stars', '5 stars']),
            'visas': field('v-country', 'Country', 'text', ph='e.g. Turkey') + field('v-type', 'Visa type', 'select', ['Tourist', 'Visit', 'Business', 'Umrah']) + field('v-date', 'Expected travel date', 'date') + field('v-pax', 'Number of applicants', 'number', ph='1'),
            'trips': field('t-dest', 'Destination', 'text', ph='e.g. Saudi Arabia') + field('t-type', 'Request type', 'select', ['Travel insurance', 'Complete tour program']) + field('t-start', 'Trip start date', 'date') + field('t-end', 'Trip end date', 'date') + field('t-pax', 'Travelers', 'number', ph='2'),
        }
        svc_names = {'flights': 'Flight', 'hotels': 'Hotel', 'visas': 'Visa', 'trips': 'Trip / Insurance'}
        sum_h, send_l = 'Your Request Is Ready', 'Send via Page Messages'
        head = 'Booking request — Younis Travel website'
    else:
        tabs = [('flights', '✈ طيران'), ('hotels', '🏨 فنادق'), ('visas', '🛂 تأشيرات'), ('trips', '🧳 رحلات وتأمين')]
        title, sub = 'خطط رحلتك دلوقتي', 'املى بيانات رحلتك وهنرد عليك بأنسب الخيارات — ده طلب بس، مفيش دفع دلوقتي.'
        name_l, btn = 'اسمك (اختياري)', 'جهز طلبي'
        panels = {
            'flights': field('f-type', 'نوع الرحلة', 'select', ['ذهاب وعودة', 'ذهاب فقط']) + field('f-from', 'من', 'text', ph='المدينة') + field('f-to', 'إلى', 'text', ph='المدينة') + field('f-dep', 'تاريخ الذهاب', 'date') + field('f-ret', 'تاريخ العودة', 'date') + field('f-pax', 'عدد المسافرين', 'number', ph='2') + field('f-class', 'الدرجة', 'select', ['اقتصادية', 'رجال أعمال']) + field('f-flex', 'تواريخي مرنة — هات أرخص تاريخ', 'chk'),
            'hotels': field('h-city', 'المدينة / الوجهة', 'text', ph='مثال: دبي') + field('h-in', 'تاريخ الوصول', 'date') + field('h-out', 'تاريخ المغادرة', 'date') + field('h-rooms', 'عدد الغرف', 'number', ph='1') + field('h-guests', 'عدد النزلاء', 'number', ph='2') + field('h-stars', 'فئة الفندق المفضلة', 'select', ['أي فئة', '3 نجوم', '4 نجوم', '5 نجوم']),
            'visas': field('v-country', 'الدولة', 'text', ph='مثال: تركيا') + field('v-type', 'نوع التأشيرة', 'select', ['سياحية', 'زيارة', 'عمل', 'عمرة']) + field('v-date', 'تاريخ السفر المتوقع', 'date') + field('v-pax', 'عدد المتقدمين', 'number', ph='1'),
            'trips': field('t-dest', 'الوجهة', 'text', ph='مثال: السعودية') + field('t-type', 'نوع الطلب', 'select', ['تأمين سفر', 'برنامج سياحي متكامل']) + field('t-start', 'تاريخ بداية الرحلة', 'date') + field('t-end', 'تاريخ نهاية الرحلة', 'date') + field('t-pax', 'عدد المسافرين', 'number', ph='2'),
        }
        svc_names = {'flights': 'طيران', 'hotels': 'فندق', 'visas': 'تأشيرة', 'trips': 'رحلة / تأمين'}
        sum_h, send_l = 'طلبك جاهز', 'إرسال عبر رسائل الصفحة'
        head = 'طلب حجز — موقع Younis Travel'
    tabs_html = ''.join(f'<button type="button" class="tab{" on" if i == 0 else ""}" data-tab="{k}">{v}</button>' for i, (k, v) in enumerate(tabs))
    panels_html = ''.join(f'<div class="panel{" on" if i == 0 else ""}" id="panel-{k}"><div class="wgrid">{panels[k]}</div></div>' for i, (k, v) in enumerate(tabs))
    svc_json = json.dumps(svc_names, ensure_ascii=False)
    html = f"""
<div class="widget" id="widget">
<h2>{title}</h2><p class="wsub">{sub}</p>
<div class="tabs">{tabs_html}</div>
<div style="margin-bottom:12px"><label for="w-name">{name_l}</label><input id="w-name" data-label="{name_l}"></div>
{panels_html}
<p style="margin-top:16px"><button type="button" class="cta-btn" id="w-go" style="border:none;cursor:pointer;font-family:inherit;font-size:17px">{btn}</button></p>
<div class="wsum" id="w-sum"><h3>{sum_h}</h3><p id="w-sum-text" style="white-space:pre-line"></p>
<p style="margin-top:12px"><a class="cta-btn" href="FBURL" target="_blank" rel="noopener">{send_l}</a></p></div>
</div>
<script>
var SVC = {svc_json};
var curTab = 'flights';
document.querySelectorAll('.tab').forEach(function(b){{ b.addEventListener('click', function(){{
  document.querySelectorAll('.tab').forEach(function(x){{ x.classList.remove('on'); }});
  document.querySelectorAll('.panel').forEach(function(x){{ x.classList.remove('on'); }});
  b.classList.add('on'); curTab = b.getAttribute('data-tab');
  document.getElementById('panel-' + curTab).classList.add('on');
}}); }});
document.getElementById('w-go').addEventListener('click', function(){{
  var lines = ['{head}', 'Service: ' + SVC[curTab]];
  var nm = document.getElementById('w-name');
  if (nm.value.trim()) lines.push(nm.getAttribute('data-label') + ': ' + nm.value.trim());
  document.querySelectorAll('#panel-' + curTab + ' [data-label]').forEach(function(el){{
    if (el.type === 'checkbox') {{ if (el.checked) lines.push(el.getAttribute('data-label') + ': ✓'); }}
    else if (el.value && el.value.trim()) lines.push(el.getAttribute('data-label') + ': ' + el.value.trim());
  }});
  document.getElementById('w-sum-text').textContent = lines.join('\\n');
  var s = document.getElementById('w-sum'); s.style.display = 'block'; s.scrollIntoView({{behavior:'smooth'}});
}});
</script>
"""
    return html.replace('FBURL', FB_PAGE)

def usps(lang='ar'):
    if lang == 'en':
        items = [('🔍', 'Instant comparison across 500+ airlines in one place'),
                 ('🏷️', 'B2B hotel rates — cheaper than the open booking portals'),
                 ('🧾', 'Official receipts accepted at embassies and airports'),
                 ('🛟', 'Change & cancellation support — with you until you are back')]
    else:
        items = [('🔍', 'مقارنة فورية بين أكثر من 500 شركة طيران في مكان واحد'),
                 ('🏷️', 'أسعار فنادق B2B أرخص من بوابات الحجز المفتوحة'),
                 ('🧾', 'إيصالات رسمية مقبولة في السفارات والمطارات'),
                 ('🛟', 'دعم في التعديل والإلغاء — معاك لحد ما ترجع بالسلامة')]
    return '<div class="usps">' + ''.join(f'<div class="usp"><div class="ic">{i}</div><p>{t}</p></div>' for i, t in items) + '</div>'

def destinations(lang='ar'):
    if lang == 'en':
        data = [('saudi', 'Saudi Arabia — AlUla', 'Tasheer & embassy appointments', 'Archaeology, history and desert nature — from AlUla to Historic Jeddah and Abha.', 'Saudi Arabia', 'visa'),
                ('turkey', 'Turkey — Istanbul', 'Electronic visa', 'A city between two continents: history, markets and shopping.', 'Turkey', 'visa'),
                ('uae', 'UAE — Dubai', 'Electronic visa', 'Towers, shopping and entertainment for the whole family.', 'UAE', 'visa'),
                ('vietnam', 'Vietnam — Ha Long Bay', 'Electronic visa', 'A bay of green islands and calm nature.', 'Vietnam', 'visa'),
                ('kenya', 'Kenya — Safari', 'Electronic visa', 'Wildlife and a real African safari.', 'Kenya', 'trip'),
                ('albania', 'Albania — The Riviera', 'Electronic visa', 'European beaches on the Adriatic Sea.', 'Albania', 'visa')]
        h, lead, ask = 'Destinations Our Travelers Love', 'Real places we build trips and visas for — pick a destination and ask us about its program.', 'Ask about this destination →'
        base = '/en/request.html'
    else:
        data = [('saudi', 'السعودية — العلا', 'مواعيد تأشير والسفارات', 'آثار وتاريخ وطبيعة صحراوية مختلفة — من العلا لجدة البلد والرياض وأبها.', 'السعودية', 'visa'),
                ('turkey', 'تركيا — إسطنبول', 'تأشيرة إلكترونية', 'مدينة بين قارتين: تاريخ عريق وأسواق وتسوق.', 'تركيا', 'visa'),
                ('uae', 'الإمارات — دبي', 'تأشيرة إلكترونية', 'أبراج وتسوق وترفيه يناسب كل العيلة.', 'الإمارات', 'visa'),
                ('vietnam', 'فيتنام — خليج ها لونج', 'تأشيرة إلكترونية', 'خليج وجزر خضراء وطبيعة آسيوية هادية.', 'فيتنام', 'visa'),
                ('kenya', 'كينيا — سفاري', 'تأشيرة إلكترونية', 'حياة برية وسفاري أفريقية حقيقية.', 'كينيا', 'trip'),
                ('albania', 'ألبانيا — الريفييرا', 'تأشيرة إلكترونية', 'شواطئ أوروبية على البحر الأدرياتيكي.', 'ألبانيا', 'visa')]
        h, lead, ask = 'وجهات بيحبها مسافرينا', 'أماكن حقيقية بنجهز لها رحلات وتأشيرات — اختر وجهتك واسألنا عن برنامجها.', 'اسأل عن الوجهة دي ←'
        base = '/request.html'
    cards_html = ''.join(
        f'<div class="dcard"><img src="/images/{img}.jpg" alt="{t}" loading="lazy"><div class="db">'
        f'<span class="badge">{b}</span><h3>{t}</h3><p>{d}</p>'
        f'<p style="margin-top:8px"><a href="{base}?d={dest}&s={svc}">{ask}</a></p></div></div>'
        for img, t, b, d, dest, svc in data)
    return f'<section><div class="wrap"><h2>{h}</h2><p class="lead">{lead}</p><div class="dgrid">{cards_html}</div></div></section>'

FAQ_AR = [
    ('إزاي أبدأ الحجز؟', 'بتبعتلنا رسالة على صفحة الفيسبوك أو بتملا نموذج الطلب هنا بالوجهة والتواريخ وعدد المسافرين، وهنرد عليك بالتفاصيل والخيارات المتاحة.'),
    ('إيه الأوراق المطلوبة للتأشيرة؟', 'بتختلف حسب الدولة ونوع التأشيرة، لكن الأساس غالبًا: جواز سفر سارٍ وصور شخصية حديثة، وحجوزات مبدئية مؤكدة للطيران والفندق. ابعتلنا الدولة اللي ناوي عليها وهنبعتلك قايمة الأوراق الدقيقة لملفك.'),
    ('الدفع بيتم إزاي؟', 'بعد ما تأكد العرض المناسب لك، الدفع متاح بطرق متعددة وسهلة: كاش، تحويل بنكي، أو دفع إلكتروني — وبتستلم تذكرتك في دقايق على الواتساب والإيميل.'),
    ('أقدر أعدّل أو ألغي حجزي؟', 'بنقدملك دعم كامل في تغيير المواعيد أو ترقية المقاعد أو الإلغاء، حسب شروط شركة الطيران أو الفندق — ومن غير تعقيدات التعامل المباشر معاهم.'),
    ('إيصالات الفنادق تنفع تتقدم للسفارة؟', 'أيوه — بنصدر إيصالات حجز وفواتير رسمية مقبولة بالكامل في السفارات والمطارات.'),
    ('تأمين السفر مهم فعلًا؟', 'هو مطلوب في سفارات كتير، وكمان من الأوراق اللي بتقوي ملف التأشيرة — غير إنه بيغطيك بتغطية شاملة طول رحلتك.'),
]
FAQ_EN = [
    ('How do I start booking?', 'Send us a message on the Facebook Page, or fill in the request form here with the destination, dates and number of travelers, and we will reply with the details and available options.'),
    ('What documents does a visa need?', 'It depends on the country and visa type, but the basics are usually: a valid passport, recent personal photos, and confirmed preliminary flight and hotel bookings. Send us your destination country and we will send you the exact document list for your file.'),
    ('How does payment work?', 'Once you confirm the offer that suits you, payment is available through easy, multiple methods: cash, bank transfer, or electronic payment — and you receive your ticket in minutes on WhatsApp and email.'),
    ('Can I change or cancel my booking?', 'We give you full support for changing dates, upgrading seats or cancelling, under the airline or hotel conditions — without the complications of dealing with them directly.'),
    ('Do the hotel receipts work for embassies?', 'Yes — we issue booking receipts and official invoices that are fully accepted at embassies and airports.'),
    ('Is travel insurance really important?', 'It is required by many embassies, and it is also one of the documents that strengthens your visa file — besides covering you comprehensively throughout your trip.'),
]

def faq_section(lang='ar'):
    data = FAQ_EN if lang == 'en' else FAQ_AR
    h = 'Frequently Asked Questions' if lang == 'en' else 'الأسئلة الشائعة'
    items = ''.join(f'<details class="faq"><summary>{q}</summary><p>{a}</p></details>' for q, a in data)
    return f'<section><div class="wrap"><h2>{h}</h2>{items}</div></section>'

def faq_schema(lang='ar'):
    data = FAQ_EN if lang == 'en' else FAQ_AR
    s = {'@context': 'https://schema.org', '@type': 'FAQPage',
         'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in data]}
    return f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'

# ---------- Home v3 ----------
def steps_html(steps):
    return ''.join(f'<div class="step"><div class="n">{n}</div><p>{t}</p></div>' for n, t in steps)

home3 = """
<section class="hero3"><div class="wrap">
<h1>سفرك يبدأ من هنا — من غير لف ودوران</h1>
<p>من أول خطوة للتفكير في السفر لحد ما ترجع بالسلامة، إحنا معاك بباقة خدمات سياحية متكاملة: تأشيرات، طيران، فنادق، تأمين سفر وبرامج سياحية — بالراحة وأحسن سعر.</p>
</div></section>
<section style="padding-top:0"><div class="wrap">
""" + widget('ar') + usps('ar') + """
</div></section>
<section><div class="wrap">
<h2>خدماتنا</h2>
<p class="lead">أربع خدمات أساسية بنقدمها من مكان واحد، عشان رحلتك تبقى متظبطة من أولها لآخرها.</p>
""" + B.cards([
    ('إصدار التأشيرات', '<p>تأشيرات إلكترونية وعادية، ومساعدة في تجهيز كل الأوراق وحجز المواعيد — بدون أخطاء أو رفض.</p><p><a href="/visas.html">اعرف أكتر ←</a></p>'),
    ('حجوزات الطيران', '<p>بنقارن بين مئات خطوط الطيران عشان نجيبلك أقل سعر تذكرة وأنسب مسار لرحلتك.</p><p><a href="/flights.html">اعرف أكتر ←</a></p>'),
    ('حجوزات الفنادق', '<p>خصومات حصرية وتأكيدات فورية في أفخم وأنسب الفنادق والمنتجعات حول العالم.</p><p><a href="/hotels.html">اعرف أكتر ←</a></p>'),
    ('تأمين وبرامج سياحية', '<p>تأمين سفر بتغطية شاملة، وجولات وبرامج ترفيهية بتناسب ميزانيتك.</p><p><a href="/trips.html">اعرف أكتر ←</a></p>'),
]) + """
</div></section>
""" + destinations('ar') + """
<section><div class="wrap">
<h2>التأشيرات على طول — من غير لف على السفارات</h2>
<p class="lead">دول بنصدر تأشيراتها إلكترونيًا، ودول بنحجزلك مواعيد سفاراتها ومراكز التأشيرات — وملفك بيتراجع قبل التقديم.</p>
""" + B.cards([
    ('تأشيرات إلكترونية فورية', B.ul(['تركيا', 'فيتنام', 'ألبانيا', 'كينيا', 'الإمارات', 'وغيرها'])),
    ('مواعيد سفارات ومراكز تأشيرات', B.ul(['أمريكا', 'الشنغن', 'بريطانيا', 'السعودية — تأشير'])),
]) + """
<p style="margin-top:16px"><a href="/visas.html">كل تفاصيل خدمات التأشيرات ←</a></p>
</div></section>
<section><div class="wrap">
<h2>إزاي بنشتغل؟ من أول رسالة لحد ركوب الطيارة</h2>
""" + steps_html([
    ('١', 'بتبعتلنا رسالة بالوجهة والتواريخ.'),
    ('٢', 'بنبعتلك عرض الطيران + الفندق + التأشيرة.'),
    ('٣', 'بتأكد الحجز وبتدفع.'),
    ('٤', 'بتستلم التذاكر والتأشيرة قبل السفر.'),
    ('٥', 'بتسافر — واحنا معاك لحد ما ترجع.'),
]) + """
</div></section>
""" + faq_section('ar') + """
<section><div class="wrap">
""" + B.cta_band('بتفكر تسافر فين في رحلتك الجاية؟', 'سيب طلبك في صفحة الحجز بالوجهة والتواريخ، وهنبدأ معاك على طول.') + """
</div></section>
"""

home3_en = """
<section class="hero3"><div class="wrap">
<h1>Your Trip Starts Here — No Running Around</h1>
<p>From the first step of thinking about travel until you're back home safe, we're with you with a complete travel service package: visas, flights, hotels, travel insurance and tour programs — comfortably and at the best price.</p>
</div></section>
<section style="padding-top:0"><div class="wrap">
""" + widget('en') + usps('en') + """
</div></section>
<section><div class="wrap">
<h2>Our Services</h2>
<p class="lead">Four core services from one place, so your trip is sorted from start to finish.</p>
""" + B.cards([
    ('Visa Issuance', '<p>Electronic and regular visas, with help preparing all the documents and booking appointments — no mistakes, no rejections.</p><p><a href="/en/visas.html">Learn more →</a></p>'),
    ('Flight Bookings', '<p>We compare hundreds of airlines to get you the lowest ticket price and the best route for your trip.</p><p><a href="/en/flights.html">Learn more →</a></p>'),
    ('Hotel Bookings', '<p>Exclusive discounts and instant confirmations at the finest and most suitable hotels and resorts around the world.</p><p><a href="/en/hotels.html">Learn more →</a></p>'),
    ('Insurance & Tour Programs', '<p>Travel insurance with comprehensive coverage, plus tours and leisure programs that fit your budget.</p><p><a href="/en/trips.html">Learn more →</a></p>'),
]) + """
</div></section>
""" + destinations('en') + """
<section><div class="wrap">
<h2>Visas, Sorted — Without Embassy Queues</h2>
<p class="lead">Countries whose visas we issue electronically, and countries whose embassy and visa-center appointments we book for you — with your file reviewed before submission.</p>
""" + B.cards([
    ('Instant Electronic Visas', B.ul(['Turkey', 'Vietnam', 'Albania', 'Kenya', 'UAE', 'and more'])),
    ('Embassy & Visa Center Appointments', B.ul(['USA', 'Schengen', 'United Kingdom', 'Saudi Arabia — Tasheer'])),
]) + """
<p style="margin-top:16px"><a href="/en/visas.html">All visa service details →</a></p>
</div></section>
<section><div class="wrap">
<h2>How We Work — From the First Message to Boarding the Plane</h2>
""" + steps_html([
    ('1', 'You send us a message with the destination and dates.'),
    ('2', 'We send you the flight + hotel + visa offer.'),
    ('3', 'You confirm the booking and pay.'),
    ('4', 'You receive your tickets and visa before travel.'),
    ('5', 'You travel — and we are with you until you are back.'),
]) + """
</div></section>
""" + faq_section('en') + """
<section><div class="wrap">
""" + B.cta_band_en('Where Are You Thinking of Traveling Next?', 'Leave your request on the booking page with the destination and dates, and we will get started with you right away.') + """
</div></section>
"""

PREFILL_AR = """
<script>
(function(){ var q = new URLSearchParams(location.search);
  var d = q.get('d'), s = q.get('s');
  var map = {visa:'تأشيرة', flight:'طيران', hotel:'فندق', trip:'برنامج سياحي متكامل', insurance:'تأمين سفر'};
  if (d) document.getElementById('dest').value = d;
  if (s && map[s]) document.getElementById('service').value = map[s];
})();
</script>
"""
PREFILL_EN = """
<script>
(function(){ var q = new URLSearchParams(location.search);
  var d = q.get('d'), s = q.get('s');
  var map = {visa:'Visa', flight:'Flight', hotel:'Hotel', trip:'Complete tour program', insurance:'Travel insurance'};
  if (d) document.getElementById('dest').value = d;
  if (s && map[s]) document.getElementById('service').value = map[s];
})();
</script>
"""

def _seed_images():
    # Master destination photos live in generator/assets/images/; later stages
    # derive WebP copies and resized variants from the JPGs inside the output
    # tree, so seed any missing JPG before they run.
    import glob as _glob
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'images')
    dst = os.path.join(OUT, 'images')
    os.makedirs(dst, exist_ok=True)
    for f in _glob.glob(os.path.join(src, '*.jpg')):
        t = os.path.join(dst, os.path.basename(f))
        if not os.path.exists(t):
            shutil.copy(f, t)

def main():
    os.makedirs(OUT, exist_ok=True)
    _seed_images()
    os.makedirs(os.path.join(OUT, 'fonts'), exist_ok=True)
    src_fonts = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'fonts')
    for f in ('IBMPlexSansArabic-Regular.woff2', 'IBMPlexSansArabic-Bold.woff2'):
        shutil.copy(os.path.join(src_fonts, f), os.path.join(OUT, 'fonts', f))
    bodies_ar = {'/': home3, '/visas.html': B.visas_body, '/flights.html': B.flights_body,
                 '/hotels.html': B.hotels_body, '/trips.html': B.trips_body,
                 '/request.html': B.request_body + PREFILL_AR}
    bodies_en = {'/': home3_en, '/visas.html': B.visas_body_en, '/flights.html': B.flights_body_en,
                 '/hotels.html': B.hotels_body_en, '/trips.html': B.trips_body_en,
                 '/request.html': B.request_body_en + PREFILL_EN}
    for fname, title, desc, path, _b in B.PAGES:
        extra = faq_schema('ar') if path == '/' else ''
        with open(os.path.join(OUT, fname), 'w', encoding='utf-8') as fh:
            fh.write(layout3(title, desc, path, bodies_ar[path], extra_head=extra))
    en_dir = os.path.join(OUT, 'en')
    os.makedirs(en_dir, exist_ok=True)
    for fname, title, desc, path, _b in B.PAGES_EN:
        extra = faq_schema('en') if path == '/' else ''
        with open(os.path.join(en_dir, fname), 'w', encoding='utf-8') as fh:
            fh.write(layout3(title, desc, path, bodies_en[path], lang='en', extra_head=extra))
    all_paths = [pg[3] for pg in B.PAGES] + [('/en' + pg[3] if pg[3] != '/' else '/en/') for pg in B.PAGES_EN]
    urls = '\n'.join(f'  <url><loc>{BASE}{u}</loc></url>' for u in all_paths)
    with open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8') as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '\n</urlset>\n')
    with open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8') as fh:
        fh.write(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    with open(os.path.join(OUT, 'vercel.json'), 'w', encoding='utf-8') as fh:
        json.dump({'cleanUrls': False, 'headers': [{'source': '/fonts/(.*)',
                   'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=31536000, immutable'}]}]}, fh, indent=2)
    print('built v3 ->', OUT)

if __name__ == '__main__':
    main()
