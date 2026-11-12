"""Younis Travel — static site generator (Arabic RTL, Vercel-ready, zero build step).
Copy comes from Amged's own approved Page post texts (2026-11-04 batch) — no invented
prices, offers or durations. Saudi-visa Q&A waits for his two lines (see PLAN)."""
import os, json

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
FB_PAGE = 'https://www.facebook.com/profile.php?id=61596173995345'
BASE = 'https://younistravel.site'

CSS = """
@font-face{font-family:'Plex';src:url('/fonts/IBMPlexSansArabic-Regular.woff2') format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:'Plex';src:url('/fonts/IBMPlexSansArabic-Bold.woff2') format('woff2');font-weight:700;font-display:swap}
:root{--navy:#071626;--navy2:#0b2237;--gold:#e8b84b;--goldlt:#f5d078;--teal:#5ec8be;--cream:#f7f3ea;--gray:#aebcc8;--card:#0d2a42}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Plex',system-ui,sans-serif;background:var(--navy);color:var(--cream);line-height:1.9}
a{color:var(--goldlt);text-decoration:none}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
header{position:sticky;top:0;background:rgba(7,22,38,.92);backdrop-filter:blur(8px);border-bottom:1px solid rgba(232,184,75,.25);z-index:10}
.nav{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 0;flex-wrap:wrap}
.logo{display:flex;align-items:center;gap:10px;font-weight:700;font-size:20px;color:var(--cream)}
.diamond{width:16px;height:16px;border:3px solid var(--gold);transform:rotate(45deg);display:inline-block}
nav.links{display:flex;gap:22px;flex-wrap:wrap}
nav.links a{color:var(--cream);font-size:16px}
nav.links a:hover{color:var(--goldlt)}
.cta-btn{background:var(--gold);color:#1a1405;font-weight:700;padding:10px 22px;border-radius:999px;display:inline-block}
.cta-btn:hover{background:var(--goldlt);color:#1a1405}
.hero{padding:84px 0 64px;text-align:center;background:radial-gradient(ellipse 700px 340px at 50% -60px,rgba(94,200,190,.28),transparent)}
.hero h1{font-size:44px;line-height:1.7;color:var(--goldlt)}
.hero p{font-size:20px;color:var(--cream);max-width:760px;margin:14px auto 26px}
section{padding:52px 0}
h2{font-size:30px;color:var(--goldlt);margin-bottom:10px;line-height:1.7}
.lead{color:var(--gray);font-size:18px;max-width:820px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;margin-top:28px}
.card{background:var(--card);border:1px solid rgba(232,184,75,.18);border-radius:16px;padding:24px}
.card h3{color:var(--gold);font-size:21px;margin-bottom:8px}
.card p,.card li{color:var(--cream);font-size:16.5px}
.card ul{list-style:none}
.card li{padding:4px 0}
.card li::before{content:'• ';color:var(--teal);font-weight:700}
.steps{counter-reset:step}
.step{display:flex;gap:16px;align-items:flex-start;background:var(--card);border-radius:14px;padding:18px 20px;margin-top:12px;border:1px solid rgba(94,200,190,.16)}
.step .n{flex:0 0 auto;width:44px;height:44px;border:2px solid var(--teal);border-radius:50%;color:var(--teal);font-weight:700;display:flex;align-items:center;justify-content:center;font-size:19px}
.page-hero{padding:64px 0 10px;text-align:center}
.page-hero h1{font-size:38px;color:var(--goldlt);line-height:1.7}
.page-hero p{color:var(--gray);font-size:19px;max-width:780px;margin:10px auto 0}
.band{background:var(--navy2);border-radius:18px;padding:30px;margin-top:26px;text-align:center}
.band h2{margin-bottom:6px}
form{display:grid;gap:14px;max-width:640px;margin:26px auto 0;text-align:start}
label{font-size:15.5px;color:var(--gray)}
input,select,textarea{width:100%;background:var(--card);border:1px solid rgba(232,184,75,.3);border-radius:10px;color:var(--cream);padding:12px 14px;font-family:inherit;font-size:16.5px}
textarea{min-height:110px}
button.cta-btn{border:none;cursor:pointer;font-family:inherit;font-size:17px}
.note{color:var(--gray);font-size:15px;text-align:center;margin-top:12px}
footer{border-top:1px solid rgba(232,184,75,.22);padding:30px 0;margin-top:30px;text-align:center;color:var(--gray);font-size:15.5px}
footer a{color:var(--goldlt)}
@media(max-width:640px){.hero h1{font-size:32px}.page-hero h1{font-size:29px}h2{font-size:25px}}
"""

def layout(title, desc, path, body, lang='ar', extra_head=''):
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
    else:
        nav = [('الرئيسية', '/'), ('التأشيرات', '/visas.html'), ('الطيران', '/flights.html'),
               ('الفنادق', '/hotels.html'), ('الرحلات والتأمين', '/trips.html')]
        cta = 'اطلب حجزك'
        foot = 'Younis Travel — تأشيرات، طيران، فنادق، وبرامج سياحية.'
        fb_label = 'صفحتنا على فيسبوك'
        req_label = 'اطلب حجزك'
        switch_href, switch_label = en_path, 'English'
        og_locale, in_lang = 'ar_EG', 'ar'
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
<link rel="canonical" href="{canonical}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:title" content="{title} | Younis Travel">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="{og_locale}">
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
</body>
</html>"""

def cards(items):
    out = '<div class="grid">'
    for h, body in items:
        out += f'<div class="card"><h3>{h}</h3>{body}</div>'
    return out + '</div>'

def ul(items):
    return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'

def cta_band(h, p):
    return (f'<div class="band"><h2>{h}</h2><p class="lead" style="margin:0 auto">{p}</p>'
            f'<p style="margin-top:18px"><a class="cta-btn" href="/request.html">اطلب حجزك دلوقتي</a></p></div>')

def cta_band_en(h, p):
    return (f'<div class="band"><h2>{h}</h2><p class="lead" style="margin:0 auto">{p}</p>'
            f'<p style="margin-top:18px"><a class="cta-btn" href="/en/request.html">Book Now</a></p></div>')

# ---------- Home ----------
home_body = """
<section class="hero"><div class="wrap">
<h1>سفرك يبدأ من هنا — من غير لف ودوران</h1>
<p>من أول خطوة للتفكير في السفر لحد ما ترجع بالسلامة، إحنا معاك بباقة خدمات سياحية متكاملة: تأشيرات، طيران، فنادق، تأمين سفر وبرامج سياحية — بالراحة وأحسن سعر.</p>
<a class="cta-btn" href="/request.html">اطلب حجزك</a>
<a class="cta-btn" href="/visas.html" style="background:transparent;border:2px solid var(--gold);color:var(--goldlt);margin-right:10px">خدمات التأشيرات</a>
</div></section>
<section><div class="wrap">
<h2>خدماتنا</h2>
<p class="lead">أربع خدمات أساسية بنقدمها من مكان واحد، عشان رحلتك تبقى متظبطة من أولها لآخرها.</p>
""" + cards([
    ('إصدار التأشيرات', '<p>تأشيرات إلكترونية وعادية، ومساعدة في تجهيز كل الأوراق وحجز المواعيد — بدون أخطاء أو رفض.</p><p><a href="/visas.html">اعرف أكتر ←</a></p>'),
    ('حجوزات الطيران', '<p>بنقارن بين مئات خطوط الطيران عشان نجيبلك أقل سعر تذكرة وأنسب مسار لرحلتك.</p><p><a href="/flights.html">اعرف أكتر ←</a></p>'),
    ('حجوزات الفنادق', '<p>خصومات حصرية وتأكيدات فورية في أفخم وأنسب الفنادق والمنتجعات حول العالم.</p><p><a href="/hotels.html">اعرف أكتر ←</a></p>'),
    ('تأمين وبرامج سياحية', '<p>تأمين سفر بتغطية شاملة، وجولات وبرامج ترفيهية بتناسب ميزانيتك.</p><p><a href="/trips.html">اعرف أكتر ←</a></p>'),
]) + """
</div></section>
<section><div class="wrap">
<h2>إزاي بنشتغل؟ من أول رسالة لحد ركوب الطيارة</h2>
""" + ''.join(f'<div class="step"><div class="n">{n}</div><p>{t}</p></div>' for n, t in [
    ('١', 'بتبعتلنا رسالة بالوجهة والتواريخ.'),
    ('٢', 'بنبعتلك عرض الطيران + الفندق + التأشيرة.'),
    ('٣', 'بتأكد الحجز وبتدفع.'),
    ('٤', 'بتستلم التذاكر والتأشيرة قبل السفر.'),
    ('٥', 'بتسافر — واحنا معاك لحد ما ترجع.'),
]) + cta_band('بتفكر تسافر فين في رحلتك الجاية؟',
             'سيب طلبك في صفحة الحجز بالوجهة والتواريخ، وهنبدأ معاك على طول.') + """
</div></section>
"""

# ---------- Visas ----------
visas_body = """
<section class="page-hero"><div class="wrap">
<h1>خدمات التأشيرات</h1>
<p>رفض التأشيرة غالبًا بيكون بسبب غلطة صغيرة في الأبلكيشن أو حجز مش مظبوط. فريقنا المتخصص بيجهز ملفك صح عشان أعلى نسب قبول.</p>
</div></section>
<section><div class="wrap">
<h2>بنقدملك إيه في خدمة التأشيرات؟</h2>
""" + cards([
    ('تأشيرات إلكترونية فورية (e-Visa)', '<p>إصدار فوري للتأشيرات الإلكترونية لدول منها:</p>' + ul(['تركيا', 'فيتنام', 'ألبانيا', 'كينيا', 'الإمارات', 'وغيرها'])),
    ('مواعيد السفارات ومراكز التأشيرات', '<p>حجز مواعيد السفارات ومراكز التأشيرات لدول منها:</p>' + ul(['أمريكا', 'الشنغن', 'بريطانيا', 'السعودية — تأشير'])),
    ('مراجعة وتجهيز الملف', ul(['كتابة وتعبئة الأبلكيشن باحترافية', 'تجهيز خطابات العمل', 'الترجمة المعتمدة'])),
    ('حجوزات مبدئية مؤكدة', '<p>حجوزات طيران وفنادق مبدئية مؤكدة، متوافقة 100% مع شروط السفارات لضمان سلامة الملف.</p>'),
]) + cta_band('سيب قلق الرفض',
             'ابعتلنا الدولة اللي حابب تسافر لها، وهنوضحلك كل الشروط والأوراق المطلوبة بالتفصيل.') + """
</div></section>
"""

# ---------- Flights ----------
flights_body = """
<section class="page-hero"><div class="wrap">
<h1>حجوزات الطيران</h1>
<p>أسعار الطيران بتزيد كل ثانية؟ مع سيستم الحجوزات المباشر بتاعنا بنطلعلك أرخص تذكرة بأفضل امتيازات.</p>
</div></section>
<section><div class="wrap">
<h2>ليه تحجز طيرانك من خلالنا؟</h2>
""" + cards([
    ('مقارنة فورية', '<p>مقارنة فورية بين أكثر من 500 شركة طيران — بنفاضل بين الطيران الاقتصادي والتجاري عشان نطلع بأوفر سعر لرحلتك.</p>'),
    ('أفضل أوزان وأنسب أوقات', '<p>بنختار مواعيد ترانزيت مريحة وباقات أمتعة تناسبك — بدون رسوم مخفية.</p>'),
    ('مرونة التعديل والإلغاء', '<p>دعم كامل في تغيير المواعيد أو ترقية المقاعد، بدون تعقيدات الخطوط المباشرة.</p>'),
    ('دفع متعدد واستلام فوري', '<p>طرق دفع متعددة وسهلة: كاش، تحويل بنكي، أو دفع إلكتروني — مع استلام التذكرة في دقايق على الواتساب والإيميل.</p>'),
]) + cta_band('جاهز تعرف أرخص خيارات رحلتك؟',
             'سيب مسار رحلتك (منين لفين) وتاريخ السفر في صفحة الحجز، وهنرد عليك بأرخص 3 خيارات متاحة حاليًا.') + """
</div></section>
"""

# ---------- Hotels ----------
hotels_body = """
<section class="page-hero"><div class="wrap">
<h1>حجوزات الفنادق</h1>
<p>أصعب حاجة في السفر إنك تختار فندق وتتفاجأ على الواقع إنه مش شبه الصور أو في مكان بعيد عن كل حاجة. إحنا بنضمنلك إقامة مثالية ومريحة.</p>
</div></section>
<section><div class="wrap">
<h2>مميزات الحجز الفندقي معانا</h2>
""" + cards([
    ('أسعار B2B وخصومات خاصة', '<p>أسعار شركات مغلقة أرخص من البوابات المفتوحة على الإنترنت.</p>'),
    ('مواقع استراتيجية', '<p>فنادق قريبة من السناتر ومحطات المترو وأهم المعالم السياحية — لتوفير تكاليف المواصلات.</p>'),
    ('خيارات مرنة', ul(['شامل الإفطار', 'شامل كليًا (All-inclusive)', 'غرف عائلية', 'شقق فندقية مجهزة'])),
    ('إيصالات رسمية', '<p>إيصالات حجز وفواتير رسمية مقبولة بالكامل في السفارات والمطارات، لتجنب أي استفسارات عند الوصول.</p>'),
]) + """
<h2 style="margin-top:44px">قبل ما تحجز: إزاي تختار فندقك صح؟</h2>
""" + ''.join(f'<div class="step"><div class="n">{n}</div><p>{t}</p></div>' for n, t in [
    ('١', 'القرب من المعالم أو الحرم.'),
    ('٢', 'الإفطار مشمول ولا لأ.'),
    ('٣', 'تقييم النزلاء الحقيقي.'),
    ('٤', 'سياسة الإلغاء — اقرأها قبل ما تدفع.'),
]) + cta_band('ناوي تقضي إجازتك فين؟',
             'سيب اسم المدينة وعدد الأفراد في صفحة الحجز، وهنبعتلك ترشيحات الفنادق الأكتر تقييمًا بأفضل سعر.') + """
</div></section>
"""

# ---------- Trips & insurance ----------
trips_body = """
<section class="page-hero"><div class="wrap">
<h1>الرحلات والتأمين</h1>
<p>برامج سياحية وجولات ترفيهية بتناسب ميزانيتك، وتأمين سفر بتغطية شاملة يخليك مسافر وانت مطمن.</p>
</div></section>
<section><div class="wrap">
""" + cards([
    ('برامج سياحية متكاملة', '<p>من أول خطوة للتفكير في السفر لحد ما ترجع بالسلامة: طيران + فندق + تأشيرة + جولات، في عرض واحد متكامل يناسب طلبك وميزانيتك.</p>'),
    ('تأمين سفر', '<p>تغطية شاملة أثناء رحلتك — وهو كمان من الأوراق اللي بتقوي ملف التأشيرة في سفارات كتير.</p>'),
    ('أماكن تبدأ بيها في السعودية', '<p>أول مرة تروح السعودية؟ دي 5 أماكن تبدأ بيهم: العلا (آثار وتاريخ)، جدة البلد (تراث وأسواق قديمة)، الرياض (العاصمة — متاحف وأبراج)، أبها (جبال وجو مختلف)، والبحر الأحمر (شواطئ وجزر).</p>'),
]) + cta_band('عايز برنامج رحلة يناسبك؟',
             'سيب الوجهة والتواريخ في صفحة الحجز، وهنجهزلك عرض متكامل.') + """
</div></section>
"""

# ---------- Request ----------
request_body = """
<section class="page-hero"><div class="wrap">
<h1>اطلب حجزك</h1>
<p>املى البيانات دي، وفي الآخر هتلاقي ملخص طلبك جاهز — ابعته لنا برسالة على صفحة الفيسبوك وهنبدأ معاك على طول.</p>
</div></section>
<section><div class="wrap">
<form id="reqForm">
<div><label for="name">الاسم</label><input id="name" required placeholder="اسمك الكريم"></div>
<div><label for="service">الخدمة المطلوبة</label>
<select id="service">
<option>تأشيرة</option><option>طيران</option><option>فندق</option>
<option>برنامج سياحي متكامل</option><option>تأمين سفر</option>
</select></div>
<div><label for="dest">الوجهة</label><input id="dest" required placeholder="مثال: السعودية، دبي، تركيا..."></div>
<div><label for="dates">تواريخ السفر التقريبية</label><input id="dates" placeholder="مثال: أول ديسمبر، 5 أيام"></div>
<div><label for="people">عدد المسافرين</label><input id="people" inputmode="numeric" placeholder="مثال: 2"></div>
<div><label for="notes">تفاصيل إضافية</label><textarea id="notes" placeholder="أي حاجة عايزنا نعرفها عن طلبك"></textarea></div>
<button class="cta-btn" type="submit">جهز ملخص الطلب</button>
</form>
<div id="summary" style="display:none;max-width:640px;margin:22px auto 0" class="card">
<h3>ملخص طلبك جاهز</h3>
<p id="summaryText" style="white-space:pre-line"></p>
<p style="margin-top:14px"><a class="cta-btn" id="fbSend" href="#" target="_blank" rel="noopener">إرسال عبر رسائل الصفحة</a></p>
</div>
<p class="note">أو ابعتلنا رسالة مباشرة على <a href="FBURL" target="_blank" rel="noopener">صفحتنا على فيسبوك</a>.</p>
</div></section>
<script>
document.getElementById('reqForm').addEventListener('submit', function(e){
  e.preventDefault();
  var v = function(id){ return document.getElementById(id).value.trim(); };
  var lines = ['طلب حجز — موقع Younis Travel','الاسم: ' + v('name'),'الخدمة: ' + v('service'),'الوجهة: ' + v('dest')];
  if (v('dates')) lines.push('التواريخ: ' + v('dates'));
  if (v('people')) lines.push('عدد المسافرين: ' + v('people'));
  if (v('notes')) lines.push('تفاصيل: ' + v('notes'));
  document.getElementById('summaryText').textContent = lines.join('\\n');
  document.getElementById('fbSend').href = 'FBURL';
  var s = document.getElementById('summary'); s.style.display = 'block';
  s.scrollIntoView({behavior:'smooth'});
});
</script>
""".replace('FBURL', FB_PAGE)

PAGES = [
    ('index.html', 'يونس ترافيل — تأشيرات وطيران وفنادق وبرامج سياحية',
     'Younis Travel: إصدار التأشيرات، حجوزات الطيران والفنادق، تأمين سفر وبرامج سياحية متكاملة — من أول رسالة لحد ركوب الطيارة.', '/', home_body),
    ('visas.html', 'خدمات التأشيرات — تأشيرات إلكترونية ومواعيد سفارات',
     'إصدار فوري للتأشيرات الإلكترونية (تركيا، فيتنام، ألبانيا، كينيا، الإمارات)، حجز مواعيد سفارات أمريكا والشنغن وبريطانيا والسعودية، ومراجعة وتجهيز ملف التأشيرة.', '/visas.html', visas_body),
    ('flights.html', 'حجوزات الطيران — مقارنة بين أكثر من 500 شركة طيران',
     'مقارنة فورية بين أكثر من 500 شركة طيران، أفضل أوزان ومواعيد ترانزيت، مرونة تعديل وإلغاء، ودفع متعدد مع استلام التذكرة في دقايق.', '/flights.html', flights_body),
    ('hotels.html', 'حجوزات الفنادق — أسعار B2B ومواقع استراتيجية',
     'أسعار شركات مغلقة أرخص من البوابات المفتوحة، فنادق في مواقع استراتيجية، خيارات إقامة مرنة، وإيصالات رسمية مقبولة في السفارات والمطارات.', '/hotels.html', hotels_body),
    ('trips.html', 'الرحلات والتأمين — برامج سياحية وتأمين سفر',
     'برامج سياحية وجولات ترفيهية بتناسب ميزانيتك، وتأمين سفر بتغطية شاملة — رحلتك متظبطة من أولها لآخرها.', '/trips.html', trips_body),
    ('request.html', 'اطلب حجزك',
     'اطلب تأشيرتك أو تذكرة طيرانك أو فندقك من Younis Travel — سيب الوجهة والتواريخ وهنبدأ معاك.', '/request.html', request_body),
]

# ---------- English bodies (faithful translations of Amged's approved Arabic copy) ----------
home_body_en = """
<section class="hero"><div class="wrap">
<h1>Your Trip Starts Here — No Running Around</h1>
<p>From the first step of thinking about travel until you're back home safe, we're with you with a complete travel service package: visas, flights, hotels, travel insurance and tour programs — comfortably and at the best price.</p>
<a class="cta-btn" href="/en/request.html">Book Now</a>
<a class="cta-btn" href="/en/visas.html" style="background:transparent;border:2px solid var(--gold);color:var(--goldlt);margin-inline-start:10px">Visa Services</a>
</div></section>
<section><div class="wrap">
<h2>Our Services</h2>
<p class="lead">Four core services from one place, so your trip is sorted from start to finish.</p>
""" + cards([
    ('Visa Issuance', '<p>Electronic and regular visas, with help preparing all the documents and booking appointments — no mistakes, no rejections.</p><p><a href="/en/visas.html">Learn more →</a></p>'),
    ('Flight Bookings', '<p>We compare hundreds of airlines to get you the lowest ticket price and the best route for your trip.</p><p><a href="/en/flights.html">Learn more →</a></p>'),
    ('Hotel Bookings', '<p>Exclusive discounts and instant confirmations at the finest and most suitable hotels and resorts around the world.</p><p><a href="/en/hotels.html">Learn more →</a></p>'),
    ('Insurance & Tour Programs', '<p>Travel insurance with comprehensive coverage, plus tours and leisure programs that fit your budget.</p><p><a href="/en/trips.html">Learn more →</a></p>'),
]) + """
</div></section>
<section><div class="wrap">
<h2>How We Work — From the First Message to Boarding the Plane</h2>
""" + ''.join(f'<div class="step"><div class="n">{n}</div><p>{t}</p></div>' for n, t in [
    ('1', 'You send us a message with the destination and dates.'),
    ('2', 'We send you the flight + hotel + visa offer.'),
    ('3', 'You confirm the booking and pay.'),
    ('4', 'You receive your tickets and visa before travel.'),
    ('5', 'You travel — and we are with you until you are back.'),
]) + cta_band_en('Where Are You Thinking of Traveling Next?',
             'Leave your request on the booking page with the destination and dates, and we will get started with you right away.') + """
</div></section>
"""

visas_body_en = """
<section class="page-hero"><div class="wrap">
<h1>Visa Services</h1>
<p>A visa rejection usually happens because of a small mistake in the application or a booking that is not right. Our specialist team prepares your file properly, for the highest acceptance rates.</p>
</div></section>
<section><div class="wrap">
<h2>What We Offer in Visa Services</h2>
""" + cards([
    ('Instant Electronic Visas (e-Visa)', '<p>Instant issuance of electronic visas for countries including:</p>' + ul(['Turkey', 'Vietnam', 'Albania', 'Kenya', 'UAE', 'and more'])),
    ('Embassy & Visa Center Appointments', '<p>Booking embassy and visa-center appointments for countries including:</p>' + ul(['USA', 'Schengen', 'United Kingdom', 'Saudi Arabia — Tasheer'])),
    ('File Review & Preparation', ul(['Professional application writing and filling', 'Employment letter preparation', 'Certified translation'])),
    ('Confirmed Preliminary Bookings', '<p>Confirmed preliminary flight and hotel bookings, 100% compliant with embassy requirements, to keep your file safe.</p>'),
]) + cta_band_en('Leave the Rejection Worry Behind',
             'Send us the country you want to travel to, and we will explain all the conditions and required documents in detail.') + """
</div></section>
"""

flights_body_en = """
<section class="page-hero"><div class="wrap">
<h1>Flight Bookings</h1>
<p>Flight prices go up every second? With our direct booking system, we get you the cheapest ticket with the best perks.</p>
</div></section>
<section><div class="wrap">
<h2>Why Book Your Flight With Us?</h2>
""" + cards([
    ('Instant Comparison', '<p>Instant comparison across more than 500 airlines — we weigh budget and full-service carriers to land the best price for your trip.</p>'),
    ('Best Baggage & Most Convenient Times', '<p>We choose comfortable layover times and baggage packages that suit you — with no hidden fees.</p>'),
    ('Flexible Changes & Cancellations', '<p>Full support for changing dates or upgrading seats, without the complications of dealing with airlines directly.</p>'),
    ('Multiple Payment & Instant Delivery', '<p>Easy, multiple payment methods: cash, bank transfer, or electronic payment — with your ticket delivered in minutes on WhatsApp and email.</p>'),
]) + cta_band_en('Ready to See the Cheapest Options for Your Trip?',
             'Leave your route (from where to where) and travel date on the booking page, and we will reply with the 3 cheapest options currently available.') + """
</div></section>
"""

hotels_body_en = """
<section class="page-hero"><div class="wrap">
<h1>Hotel Bookings</h1>
<p>The hardest part of traveling is choosing a hotel and then finding on arrival that it does not look like the photos, or that it is far from everything. We guarantee you an ideal, comfortable stay.</p>
</div></section>
<section><div class="wrap">
<h2>Hotel Booking Advantages With Us</h2>
""" + cards([
    ('B2B Rates & Special Discounts', '<p>Closed corporate rates, cheaper than the open booking portals on the internet.</p>'),
    ('Strategic Locations', '<p>Hotels close to city centers, metro stations and the top attractions — saving you transport costs.</p>'),
    ('Flexible Options', ul(['Breakfast included', 'All-inclusive', 'Family rooms', 'Fully equipped hotel apartments'])),
    ('Official Receipts', '<p>Booking receipts and official invoices, fully accepted at embassies and airports, to avoid any questions on arrival.</p>'),
]) + """
<h2 style="margin-top:44px">Before You Book: How to Choose Your Hotel Right</h2>
""" + ''.join(f'<div class="step"><div class="n">{n}</div><p>{t}</p></div>' for n, t in [
    ('1', 'Proximity to the attractions or the Haram.'),
    ('2', 'Whether breakfast is included or not.'),
    ('3', 'Real guest ratings.'),
    ('4', 'The cancellation policy — read it before you pay.'),
]) + cta_band_en('Where Are You Spending Your Vacation?',
             'Leave the city name and number of travelers on the booking page, and we will send you the top-rated hotel recommendations at the best price.') + """
</div></section>
"""

trips_body_en = """
<section class="page-hero"><div class="wrap">
<h1>Trips & Insurance</h1>
<p>Tour programs and leisure tours that fit your budget, and travel insurance with comprehensive coverage, so you travel with peace of mind.</p>
</div></section>
<section><div class="wrap">
""" + cards([
    ('Complete Tour Programs', '<p>From the first step of thinking about travel until you are back home safe: flight + hotel + visa + tours, in one complete offer tailored to your request and budget.</p>'),
    ('Travel Insurance', '<p>Comprehensive coverage during your trip — and it is also one of the documents that strengthens your visa file at many embassies.</p>'),
    ('Places to Start With in Saudi Arabia', '<p>Going to Saudi Arabia for the first time? Here are 5 places to start with: AlUla (archaeology and history), Historic Jeddah — Al-Balad (heritage and old markets), Riyadh (the capital — museums and towers), Abha (mountains and a different climate), and the Red Sea (beaches and islands).</p>'),
]) + cta_band_en('Want a Trip Program That Fits You?',
             'Leave the destination and dates on the booking page, and we will prepare a complete offer for you.') + """
</div></section>
"""

request_body_en = """
<section class="page-hero"><div class="wrap">
<h1>Book Your Trip</h1>
<p>Fill in these details, and at the end you will find a summary of your request ready — send it to us in a message on the Facebook Page and we will get started with you right away.</p>
</div></section>
<section><div class="wrap">
<form id="reqForm">
<div><label for="name">Name</label><input id="name" required placeholder="Your name"></div>
<div><label for="service">Service needed</label>
<select id="service">
<option>Visa</option><option>Flight</option><option>Hotel</option>
<option>Complete tour program</option><option>Travel insurance</option>
</select></div>
<div><label for="dest">Destination</label><input id="dest" required placeholder="e.g. Saudi Arabia, Dubai, Turkey..."></div>
<div><label for="dates">Approximate travel dates</label><input id="dates" placeholder="e.g. early December, 5 days"></div>
<div><label for="people">Number of travelers</label><input id="people" inputmode="numeric" placeholder="e.g. 2"></div>
<div><label for="notes">Additional details</label><textarea id="notes" placeholder="Anything you want us to know about your request"></textarea></div>
<button class="cta-btn" type="submit">Prepare Request Summary</button>
</form>
<div id="summary" style="display:none;max-width:640px;margin:22px auto 0" class="card">
<h3>Your Request Summary Is Ready</h3>
<p id="summaryText" style="white-space:pre-line"></p>
<p style="margin-top:14px"><a class="cta-btn" id="fbSend" href="#" target="_blank" rel="noopener">Send via Page Messages</a></p>
</div>
<p class="note">Or message us directly on <a href="FBURL" target="_blank" rel="noopener">our Facebook Page</a>.</p>
</div></section>
<script>
document.getElementById('reqForm').addEventListener('submit', function(e){
  e.preventDefault();
  var v = function(id){ return document.getElementById(id).value.trim(); };
  var lines = ['Booking request — Younis Travel website','Name: ' + v('name'),'Service: ' + v('service'),'Destination: ' + v('dest')];
  if (v('dates')) lines.push('Dates: ' + v('dates'));
  if (v('people')) lines.push('Travelers: ' + v('people'));
  if (v('notes')) lines.push('Details: ' + v('notes'));
  document.getElementById('summaryText').textContent = lines.join('\\n');
  document.getElementById('fbSend').href = 'FBURL';
  var s = document.getElementById('summary'); s.style.display = 'block';
  s.scrollIntoView({behavior:'smooth'});
});
</script>
""".replace('FBURL', FB_PAGE)

PAGES_EN = [
    ('index.html', 'Younis Travel — Visas, Flights, Hotels & Tour Programs',
     'Younis Travel: visa issuance, flight and hotel bookings, travel insurance and complete tour programs — from the first message to boarding the plane.', '/', home_body_en),
    ('visas.html', 'Visa Services — e-Visas & Embassy Appointments',
     'Instant e-visa issuance (Turkey, Vietnam, Albania, Kenya, UAE), embassy appointment booking for the USA, Schengen, the UK and Saudi Arabia, and professional visa file review and preparation.', '/visas.html', visas_body_en),
    ('flights.html', 'Flight Bookings — Comparing 500+ Airlines',
     'Instant comparison across more than 500 airlines, the best baggage and layover options, flexible changes and cancellations, multiple payment methods, and ticket delivery in minutes.', '/flights.html', flights_body_en),
    ('hotels.html', 'Hotel Bookings — B2B Rates & Strategic Locations',
     'Closed corporate rates cheaper than open portals, hotels in strategic locations, flexible stay options, and official receipts accepted at embassies and airports.', '/hotels.html', hotels_body_en),
    ('trips.html', 'Trips & Insurance — Tour Programs & Travel Insurance',
     'Tour programs and leisure tours that fit your budget, plus comprehensive travel insurance — your trip sorted from start to finish.', '/trips.html', trips_body_en),
    ('request.html', 'Book Your Trip',
     'Request your visa, flight ticket or hotel from Younis Travel — leave the destination and dates and we will get started.', '/request.html', request_body_en),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, 'fonts'), exist_ok=True)
    import shutil
    src_fonts = os.path.expanduser('~/workspace/lead-gen/fonts')
    for f in ('IBMPlexSansArabic-Regular.woff2', 'IBMPlexSansArabic-Bold.woff2'):
        shutil.copy(os.path.join(src_fonts, f), os.path.join(OUT, 'fonts', f))
    for fname, title, desc, path, body in PAGES:
        with open(os.path.join(OUT, fname), 'w', encoding='utf-8') as fh:
            fh.write(layout(title, desc, path, body))
    en_dir = os.path.join(OUT, 'en')
    os.makedirs(en_dir, exist_ok=True)
    for fname, title, desc, path, body in PAGES_EN:
        with open(os.path.join(en_dir, fname), 'w', encoding='utf-8') as fh:
            fh.write(layout(title, desc, path, body, lang='en'))
    all_paths = [pg[3] for pg in PAGES] + [('/en' + pg[3] if pg[3] != '/' else '/en/') for pg in PAGES_EN]
    urls = '\n'.join(f'  <url><loc>{BASE}{u}</loc></url>' for u in all_paths)
    with open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8') as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '\n</urlset>\n')
    with open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8') as fh:
        fh.write(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    with open(os.path.join(OUT, 'vercel.json'), 'w', encoding='utf-8') as fh:
        json.dump({'cleanUrls': False, 'headers': [{'source': '/fonts/(.*)',
                   'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=31536000, immutable'}]}]}, fh, indent=2)
    print('built', len(PAGES), 'AR +', len(PAGES_EN), 'EN pages ->', OUT)

if __name__ == '__main__':
    main()
