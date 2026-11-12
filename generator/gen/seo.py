"""Younis Travel — v3.1 SEO/AEO/GEO layer on top of v3 (approved by Amged 2026-11-12).
Adds: llms.txt + llms-full.txt, per-service-page FAQ sections + FAQPage schema,
direct-answer lead blocks, BreadcrumbList on subpages, HowTo schema on the visas
page, WebP images + hero preload. All copy from Amged's approved texts only.
Output: regenerates site_v3/ (same folder v3 deploys from)."""
import os, json, sys, shutil
from gen import base as B
from gen import layout as V3
from PIL import Image

OUT = V3.OUT
BASE = B.BASE
FB_PAGE = B.FB_PAGE
V3.CSS = V3.CSS.replace("/images/hero.jpg", "/images/hero.webp")

ANSWERS = {
 '/visas.html': {
  'ar': 'يونس ترافيل يصدر التأشيرات إلكترونيًا لدول مثل تركيا وفيتنام وألبانيا وكينيا والإمارات، ويحجز مواعيد السفارات ومراكز التأشيرات لأمريكا والشنغن وبريطانيا والسعودية (تأشير). فريق متخصص يراجع ملفك ويجهزه بالكامل — أبلكيشن وخطابات عمل وترجمة معتمدة وحجوزات مبدئية مؤكدة — لأن رفض التأشيرة غالبًا سببه خطأ صغير يمكن تجنّبه.',
  'en': 'Younis Travel issues electronic visas for countries such as Turkey, Vietnam, Albania, Kenya and the UAE, and books embassy and visa-center appointments for the USA, Schengen, the United Kingdom and Saudi Arabia (Tasheer). A specialist team reviews and fully prepares your file — application, employment letters, certified translation and confirmed preliminary bookings — because a visa rejection usually comes down to one small avoidable mistake.'},
 '/flights.html': {
  'ar': 'احجز طيرانك مع يونس ترافيل بمقارنة فورية بين أكثر من 500 شركة طيران للوصول إلى أوفر سعر، بأنسب أوزان ومواعيد ترانزيت مريحة وبدون رسوم مخفية — مع مرونة في التعديل والإلغاء، ودفع كاش أو تحويل بنكي أو إلكتروني، واستلام تذكرتك في دقائق على الواتساب والإيميل.',
  'en': 'Book your flight with Younis Travel through an instant comparison across more than 500 airlines to land the best price, with baggage packages and comfortable layover times and no hidden fees — plus flexible changes and cancellations, payment by cash, bank transfer or electronic payment, and your ticket delivered in minutes on WhatsApp and email.'},
 '/hotels.html': {
  'ar': 'يونس ترافيل يحجز فندقك بأسعار شركات (B2B) مغلقة أرخص من بوابات الحجز المفتوحة على الإنترنت، في مواقع استراتيجية قريبة من السناتر ومحطات المترو وأهم المعالم، وبخيارات مرنة من الإفطار المشمول إلى الشامل كليًا والغرف العائلية — مع إيصالات وفواتير رسمية مقبولة بالكامل في السفارات والمطارات.',
  'en': 'Younis Travel books your hotel at closed corporate (B2B) rates, cheaper than the open booking portals, in strategic locations close to city centers, metro stations and the top attractions — with flexible options from breakfast included to all-inclusive and family rooms, plus official receipts and invoices fully accepted at embassies and airports.'},
 '/trips.html': {
  'ar': 'مع يونس ترافيل تحصل على برنامج سياحي متكامل — طيران وفندق وتأشيرة وجولات — في عرض واحد يناسب طلبك وميزانيتك، من أول خطوة للتفكير في السفر حتى الرجوع بالسلامة، بالإضافة إلى تأمين سفر بتغطية شاملة يحميك طوال رحلتك ويُعد من الأوراق التي تقوّي ملف التأشيرة في سفارات كثيرة.',
  'en': 'With Younis Travel you get a complete tour program — flight, hotel, visa and tours — in one offer tailored to your request and budget, from the first step of thinking about travel until you are back home safe, plus travel insurance with comprehensive coverage that protects you throughout your trip and strengthens your visa file at many embassies.'},
}

FAQ_PAGES = {
 '/visas.html': {
  'ar': [('ما الدول التي تصدرون تأشيراتها إلكترونيًا؟', 'إصدار فوري للتأشيرات الإلكترونية لدول منها: تركيا، فيتنام، ألبانيا، كينيا، الإمارات، وغيرها.'),
         ('ما الدول التي تحجزون مواعيد سفاراتها؟', 'بنحجز مواعيد السفارات ومراكز التأشيرات لدول منها: أمريكا، الشنغن، بريطانيا، والسعودية عبر مراكز تأشير.'),
         ('لماذا تُرفض التأشيرات غالبًا؟', 'رفض التأشيرة غالبًا بيكون بسبب غلطة صغيرة في الأبلكيشن أو حجز مش مظبوط — فريقنا المتخصص بيجهز ملفك صح عشان أعلى نسب قبول.'),
         ('ما هي الحجوزات المبدئية المؤكدة؟', 'حجوزات طيران وفنادق مبدئية مؤكدة، متوافقة 100% مع شروط السفارات لضمان سلامة الملف.'),
         ('هل تساعدون في تجهيز ملف التأشيرة؟', 'أيوه: كتابة وتعبئة الأبلكيشن باحترافية، تجهيز خطابات العمل، والترجمة المعتمدة.')],
  'en': [('Which countries do you issue e-visas for?', 'Instant issuance of electronic visas for countries including: Turkey, Vietnam, Albania, Kenya, the UAE, and more.'),
         ('Which countries do you book embassy appointments for?', 'We book embassy and visa-center appointments for countries including: the USA, Schengen, the United Kingdom, and Saudi Arabia through Tasheer centers.'),
         ('Why are visas usually rejected?', 'A visa rejection usually happens because of a small mistake in the application or a booking that is not right — our specialist team prepares your file properly, for the highest acceptance rates.'),
         ('What are confirmed preliminary bookings?', 'Confirmed preliminary flight and hotel bookings, 100% compliant with embassy requirements, to keep your file safe.'),
         ('Do you help prepare the visa file?', 'Yes: professional application writing and filling, employment letter preparation, and certified translation.')]},
 '/flights.html': {
  'ar': [('إزاي بتوصلوا لأرخص تذكرة؟', 'بمقارنة فورية بين أكثر من 500 شركة طيران — بنفاضل بين الطيران الاقتصادي والتجاري عشان نطلع بأوفر سعر لرحلتك.'),
         ('هل فيه رسوم مخفية؟', 'لا — بنختار مواعيد ترانزيت مريحة وباقات أمتعة تناسبك، وكل التكلفة واضحة قبل التأكيد، بدون رسوم مخفية.'),
         ('إزاي هستلم تذكرتي؟', 'بتستلم التذكرة في دقايق على الواتساب والإيميل بعد تأكيد الحجز والدفع.'),
         ('إيه طرق الدفع المتاحة؟', 'طرق دفع متعددة وسهلة: كاش، تحويل بنكي، أو دفع إلكتروني.'),
         ('أقدر أعدّل أو ألغي الحجز؟', 'بنقدملك دعم كامل في تغيير المواعيد أو ترقية المقاعد أو الإلغاء حسب شروط شركة الطيران — بدون تعقيدات الخطوط المباشرة.')],
  'en': [('How do you find the cheapest ticket?', 'Through an instant comparison across more than 500 airlines — we weigh budget and full-service carriers to land the best price for your trip.'),
         ('Are there hidden fees?', 'No — we choose comfortable layover times and baggage packages that suit you, with the full cost clear before confirmation and no hidden fees.'),
         ('How do I receive my ticket?', 'You receive your ticket in minutes on WhatsApp and email after confirming the booking and payment.'),
         ('What payment methods are available?', 'Easy, multiple payment methods: cash, bank transfer, or electronic payment.'),
         ('Can I change or cancel my booking?', 'We give you full support for changing dates, upgrading seats or cancelling, under the airline conditions — without the complications of dealing with airlines directly.')]},
 '/hotels.html': {
  'ar': [('ليه أسعاركم أرخص من مواقع الحجز؟', 'لأننا بنشتغل بأسعار شركات مغلقة (B2B) وخصومات خاصة، أرخص من البوابات المفتوحة على الإنترنت.'),
         ('هل إيصالات الحجز مقبولة في السفارات؟', 'أيوه — إيصالات حجز وفواتير رسمية مقبولة بالكامل في السفارات والمطارات، لتجنب أي استفسارات عند الوصول.'),
         ('إزاي أختار الفندق الصح؟', 'راعِ أربعة حاجات: القرب من المعالم أو الحرم، الإفطار مشمول ولا لأ، تقييم النزلاء الحقيقي، وسياسة الإلغاء قبل ما تدفع — أو سيب الترشيح علينا وابعت طلبك.'),
         ('إيه خيارات الإقامة المتاحة؟', 'شامل الإفطار، شامل كليًا (All-inclusive)، غرف عائلية، وشقق فندقية مجهزة — في فنادق قريبة من السناتر ومحطات المترو وأهم المعالم.')],
  'en': [('Why are your prices cheaper than booking sites?', 'Because we work with closed corporate (B2B) rates and special discounts, cheaper than the open booking portals on the internet.'),
         ('Are the booking receipts accepted at embassies?', 'Yes — booking receipts and official invoices, fully accepted at embassies and airports, to avoid any questions on arrival.'),
         ('How do I choose the right hotel?', 'Mind four things: proximity to the attractions or the Haram, whether breakfast is included, real guest ratings, and the cancellation policy before you pay — or leave the recommendation to us and send your request.'),
         ('What stay options are available?', 'Breakfast included, all-inclusive, family rooms, and fully equipped hotel apartments — in hotels close to city centers, metro stations and the top attractions.')]},
 '/trips.html': {
  'ar': [('إيه اللي بيشمله البرنامج السياحي المتكامل؟', 'طيران + فندق + تأشيرة + جولات، في عرض واحد متكامل يناسب طلبك وميزانيتك — من أول خطوة للتفكير في السفر لحد ما ترجع بالسلامة.'),
         ('ليه أحتاج تأمين سفر؟', 'لأنه بيمنحك تغطية شاملة أثناء رحلتك، وهو كمان من الأوراق اللي بتقوي ملف التأشيرة في سفارات كتير.'),
         ('أول مرة أروح السعودية — أبدأ بإيه؟', 'دي 5 أماكن تبدأ بيهم: العلا (آثار وتاريخ)، جدة البلد (تراث وأسواق قديمة)، الرياض (العاصمة — متاحف وأبراج)، أبها (جبال وجو مختلف)، والبحر الأحمر (شواطئ وجزر).')],
  'en': [('What does a complete tour program include?', 'Flight + hotel + visa + tours, in one complete offer tailored to your request and budget — from the first step of thinking about travel until you are back home safe.'),
         ('Why do I need travel insurance?', 'It gives you comprehensive coverage during your trip, and it is also one of the documents that strengthens your visa file at many embassies.'),
         ('Going to Saudi Arabia for the first time — where do I start?', 'Here are 5 places to start with: AlUla (archaeology and history), Historic Jeddah — Al-Balad (heritage and old markets), Riyadh (the capital — museums and towers), Abha (mountains and a different climate), and the Red Sea (beaches and islands).')]},
}

CRUMB_NAMES = {
 '/visas.html': ('التأشيرات', 'Visas'), '/flights.html': ('الطيران', 'Flights'),
 '/hotels.html': ('الفنادق', 'Hotels'), '/trips.html': ('الرحلات والتأمين', 'Trips & Insurance'),
 '/request.html': ('اطلب حجزك', 'Book Your Trip')}

def faq_schema_for(data):
    s = {'@context': 'https://schema.org', '@type': 'FAQPage',
         'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in data]}
    return f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'

def faq_section_for(data, lang):
    h = 'Frequently Asked Questions' if lang == 'en' else 'الأسئلة الشائعة'
    items = ''.join(f'<details class="faq"><summary>{q}</summary><p>{a}</p></details>' for q, a in data)
    return f'<section><div class="wrap"><h2>{h}</h2>{items}</div></section>'

def breadcrumb_schema(path, lang):
    en = (lang == 'en')
    home_name = 'Home' if en else 'الرئيسية'
    prefix = '/en' if en else ''
    name = CRUMB_NAMES[path][1 if en else 0]
    s = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': home_name, 'item': BASE + prefix + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': name, 'item': BASE + prefix + path}]}
    return f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'

def howto_schema(lang):
    if lang == 'en':
        name, steps = 'How to apply for a visa with Younis Travel', [
            'Choose the country and visa type',
            'Send us a message on the Facebook Page or fill in the request form',
            'We review your file and prepare the documents and application',
            'We issue the electronic visa or book your embassy / Tasheer appointment',
            'You receive your visa before travel']
    else:
        name, steps = 'إزاي تقدم على تأشيرة مع يونس ترافيل', [
            'اختر الدولة ونوع التأشيرة',
            'ابعتلنا رسالة على صفحة الفيسبوك أو املأ نموذج الطلب',
            'بنراجع ملفك وبنجهز الأوراق والأبلكيشن',
            'بنصدر التأشيرة الإلكترونية أو بنحجز موعد السفارة / تأشير',
            'بتستلم تأشيرتك قبل السفر']
    s = {'@context': 'https://schema.org', '@type': 'HowTo', 'name': name,
         'step': [{'@type': 'HowToStep', 'position': i + 1, 'text': t} for i, t in enumerate(steps)]}
    return f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'

def inject_answer(body, text):
    block = ('<section style="padding:28px 0 0"><div class="wrap">'
             f'<div class="band" style="text-align:start;margin-top:0"><p style="font-size:18px">{text}</p></div>'
             '</div></section>')
    return body.replace('</section>', '</section>' + block, 1)

LLMS = """# Younis Travel

> Younis Travel is an Egyptian travel agency offering visa issuance, flight bookings, hotel bookings, travel insurance and complete tour programs. The website is available in Arabic (default) and English. Bookings start with a request: the traveler sends a message on the agency's Facebook Page or fills in the request form on the website, receives an offer, confirms and pays, then receives the tickets and visa before travel. There are no prices published on the website.

## Services

- Visa issuance: instant electronic visas (e-Visa) and embassy / visa-center appointment booking, with full file review and preparation.
- Flight bookings: instant comparison across more than 500 airlines, flexible changes and cancellations, multiple payment methods, ticket delivered in minutes on WhatsApp and email.
- Hotel bookings: closed corporate (B2B) rates cheaper than open booking portals, strategic locations, official receipts accepted at embassies and airports.
- Trips & insurance: complete tour programs (flight + hotel + visa + tours) and travel insurance with comprehensive coverage.

## Visa coverage

- Electronic visas (e-Visa): Turkey, Vietnam, Albania, Kenya, UAE, and more.
- Embassy and visa-center appointments: USA, Schengen, United Kingdom, Saudi Arabia (Tasheer centers).
- File preparation: professional application filling, employment letters, certified translation, and confirmed preliminary flight and hotel bookings that comply with embassy requirements.

## Key pages

- Home (Arabic): https://younistravel.site/
- Home (English): https://younistravel.site/en/
- Visa services: https://younistravel.site/visas.html
- Flight bookings: https://younistravel.site/flights.html
- Hotel bookings: https://younistravel.site/hotels.html
- Trips & insurance: https://younistravel.site/trips.html
- Request form: https://younistravel.site/request.html

## Contact

- Facebook Page: https://www.facebook.com/profile.php?id=61596173995345
- All booking requests go through the Facebook Page messages or the website request form.
"""

LLMS_FULL_EXTRA = """

## Frequently asked questions

- How do I start booking? Send a message on the Facebook Page, or fill in the request form with the destination, dates and number of travelers; the agency replies with the details and available options.
- Why are visas usually rejected? Usually because of a small mistake in the application or a booking that is not right; the agency's specialist team prepares the file properly for the highest acceptance rates.
- What documents does a visa need? It depends on the country and visa type; the basics are usually a valid passport, recent personal photos, and confirmed preliminary flight and hotel bookings. The agency sends the exact document list for each file.
- How does payment work? After confirming the offer: cash, bank transfer, or electronic payment.
- Can I change or cancel a booking? Full support for changing dates, upgrading seats or cancelling, under the airline or hotel conditions.
- Do hotel receipts work for embassies? Yes, the agency issues booking receipts and official invoices fully accepted at embassies and airports.
- Why travel insurance? It is required by many embassies, strengthens the visa file, and provides comprehensive coverage during the trip.

## أسئلة شائعة

- إزاي أبدأ الحجز؟ ابعتلنا رسالة على صفحة الفيسبوك أو املأ نموذج الطلب بالوجهة والتواريخ وعدد المسافرين، وهنرد عليك بالتفاصيل والخيارات المتاحة.
- لماذا تُرفض التأشيرات غالبًا؟ غالبًا بسبب غلطة صغيرة في الأبلكيشن أو حجز مش مظبوط؛ فريقنا المتخصص بيجهز ملفك صح عشان أعلى نسب قبول.
- إيه الأوراق المطلوبة للتأشيرة؟ بتختلف حسب الدولة ونوع التأشيرة، والأساس غالبًا: جواز سفر سارٍ وصور شخصية حديثة وحجوزات مبدئية مؤكدة للطيران والفندق — وبنبعتلك قايمة الأوراق الدقيقة لملفك.
- الدفع بيتم إزاي؟ بعد تأكيد العرض: كاش، تحويل بنكي، أو دفع إلكتروني.
- أقدر أعدّل أو ألغي حجزي؟ بنقدملك دعم كامل في تغيير المواعيد أو ترقية المقاعد أو الإلغاء، حسب شروط شركة الطيران أو الفندق.
- إيصالات الفنادق تنفع للسفارة؟ أيوه — إيصالات وفواتير رسمية مقبولة بالكامل في السفارات والمطارات.
- ليه تأمين السفر؟ مطلوب في سفارات كتير، وبيقوي ملف التأشيرة، وبيغطيك بتغطية شاملة طول رحلتك.

## How booking works (5 steps)

1. The traveler sends a message with the destination and dates.
2. The agency sends the flight + hotel + visa offer.
3. The traveler confirms the booking and pays.
4. The traveler receives the tickets and visa before travel.
5. The traveler travels — the agency stays with them until they are back.
"""

def webp_images(body):
    out = body
    for n in ('hero', 'saudi', 'turkey', 'uae', 'vietnam', 'kenya', 'albania'):
        out = out.replace(f'/images/{n}.jpg', f'/images/{n}.webp')
    return out

def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, 'fonts'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'images'), exist_ok=True)
    src_fonts = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'fonts')
    for f in ('IBMPlexSansArabic-Regular.woff2', 'IBMPlexSansArabic-Bold.woff2'):
        shutil.copy(os.path.join(src_fonts, f), os.path.join(OUT, 'fonts', f))
    for n in ('hero', 'saudi', 'turkey', 'uae', 'vietnam', 'kenya', 'albania'):
        jpg = os.path.join(OUT, 'images', n + '.jpg')
        webp = os.path.join(OUT, 'images', n + '.webp')
        if os.path.exists(jpg):
            Image.open(jpg).convert('RGB').save(webp, 'WEBP', quality=78)
    bodies_ar = {'/': V3.home3, '/visas.html': B.visas_body, '/flights.html': B.flights_body,
                 '/hotels.html': B.hotels_body, '/trips.html': B.trips_body,
                 '/request.html': B.request_body + V3.PREFILL_AR}
    bodies_en = {'/': V3.home3_en, '/visas.html': B.visas_body_en, '/flights.html': B.flights_body_en,
                 '/hotels.html': B.hotels_body_en, '/trips.html': B.trips_body_en,
                 '/request.html': B.request_body_en + V3.PREFILL_EN}
    for fname, title, desc, path, _b in B.PAGES:
        body, extra = bodies_ar[path], ''
        if path == '/':
            extra = V3.faq_schema('ar') + '<link rel="preload" as="image" href="/images/hero.webp">'
        else:
            extra = breadcrumb_schema(path, 'ar')
            if path in FAQ_PAGES:
                body = inject_answer(body, ANSWERS[path]['ar']) + faq_section_for(FAQ_PAGES[path]['ar'], 'ar')
                extra += faq_schema_for(FAQ_PAGES[path]['ar'])
            if path == '/visas.html':
                extra += howto_schema('ar')
        with open(os.path.join(OUT, fname), 'w', encoding='utf-8') as fh:
            fh.write(V3.layout3(title, desc, path, webp_images(body), extra_head=extra))
    en_dir = os.path.join(OUT, 'en')
    os.makedirs(en_dir, exist_ok=True)
    for fname, title, desc, path, _b in B.PAGES_EN:
        body, extra = bodies_en[path], ''
        if path == '/':
            extra = V3.faq_schema('en') + '<link rel="preload" as="image" href="/images/hero.webp">'
        else:
            extra = breadcrumb_schema(path, 'en')
            if path in FAQ_PAGES:
                body = inject_answer(body, ANSWERS[path]['en']) + faq_section_for(FAQ_PAGES[path]['en'], 'en')
                extra += faq_schema_for(FAQ_PAGES[path]['en'])
            if path == '/visas.html':
                extra += howto_schema('en')
        with open(os.path.join(en_dir, fname), 'w', encoding='utf-8') as fh:
            fh.write(V3.layout3(title, desc, path, webp_images(body), lang='en', extra_head=extra))
    all_paths = [pg[3] for pg in B.PAGES] + [('/en' + pg[3] if pg[3] != '/' else '/en/') for pg in B.PAGES_EN]
    urls = '\n'.join(f'  <url><loc>{BASE}{u}</loc></url>' for u in all_paths)
    with open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8') as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '\n</urlset>\n')
    with open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8') as fh:
        fh.write(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    with open(os.path.join(OUT, 'vercel.json'), 'w', encoding='utf-8') as fh:
        json.dump({'cleanUrls': False, 'headers': [{'source': '/fonts/(.*)',
                   'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=31536000, immutable'}]}]}, fh, indent=2)
    with open(os.path.join(OUT, 'llms.txt'), 'w', encoding='utf-8') as fh:
        fh.write(LLMS)
    with open(os.path.join(OUT, 'llms-full.txt'), 'w', encoding='utf-8') as fh:
        fh.write(LLMS + LLMS_FULL_EXTRA)
    print('built v3.1 ->', OUT)

if __name__ == '__main__':
    main()
