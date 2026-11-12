"""Younis Travel — v3.2: per-country visa landing pages + IndexNow key.
Runs v3.1 build first, then adds /visas/<country>.html and /en/visas/<country>.html
for saudi, turkey, uae, vietnam, kenya, albania; links them from the visas pages;
extends sitemap.xml and llms files. Copy: Amged's approved service texts only —
no invented visa durations, fees or requirements; country specifics stay at the
level of his approved copy (service type + destination highlights he published)."""
import os, json, sys, secrets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as B
import build_site_v3 as V3
import build_site_v31 as V31

OUT = V3.OUT
BASE = B.BASE

VFAQ = V31.FAQ_PAGES['/visas.html']
# faq subsets: e-visa pages use items 0,2,3,4 ; saudi uses 1,2,3,4
def faq_subset(lang, kind):
    data = VFAQ[lang]
    idx = (0, 2, 3, 4) if kind == 'evisa' else (1, 2, 3, 4)
    return [data[i] for i in idx]

COUNTRIES = {
 'saudi': {
   'kind': 'tasheer', 'img': 'saudi',
   'ar': {'name': 'السعودية', 'title': 'تأشيرة السعودية — مواعيد تأشير ومراجعة وتجهيز الملف',
          'desc': 'حجز مواعيد مراكز تأشير السعودية مع يونس ترافيل: مراجعة وتجهيز كامل لملف التأشيرة، حجوزات طيران وفنادق مبدئية مؤكدة متوافقة مع شروط التقديم، وخطوات واضحة من أول رسالة حتى استلام التأشيرة.',
          'h1': 'تأشيرة السعودية',
          'lead': 'بنحجزلك موعد مركز تأشير وبنراجع ملفك ونجهزه بالكامل قبل التقديم — عشان غلطة صغيرة في الأبلكيشن أو حجز مش مظبوط هي غالبًا سبب الرفض.',
          'answer': 'مع يونس ترافيل، تأشيرة السعودية تبدأ بحجز موعد في مراكز تأشير ومراجعة ملفك بالكامل: تعبئة الأبلكيشن باحترافية، تجهيز خطابات العمل والترجمة المعتمدة، وحجوزات طيران وفنادق مبدئية مؤكدة متوافقة مع شروط التقديم — وبنبعتلك قايمة الأوراق الدقيقة حسب نوع تأشيرتك وحالتك.',
          'extra_h': 'أماكن تبدأ بيها في السعودية',
          'extra_p': 'أول مرة تروح السعودية؟ دي 5 أماكن تبدأ بيهم: العلا (آثار وتاريخ)، جدة البلد (تراث وأسواق قديمة)، الرياض (العاصمة — متاحف وأبراج)، أبها (جبال وجو مختلف)، والبحر الأحمر (شواطئ وجزر).'},
   'en': {'name': 'Saudi Arabia', 'title': 'Saudi Arabia Visa — Tasheer Appointments & File Preparation',
          'desc': 'Book your Saudi Tasheer center appointment with Younis Travel: full visa file review and preparation, confirmed preliminary flight and hotel bookings compliant with submission requirements, and clear steps from the first message to receiving your visa.',
          'h1': 'Saudi Arabia Visa',
          'lead': 'We book your Tasheer center appointment and review and prepare your complete file before submission — because a small mistake in the application or a booking that is not right is usually why visas get rejected.',
          'answer': 'With Younis Travel, a Saudi visa starts with booking your Tasheer center appointment and a full review of your file: professional application filling, employment letters and certified translation, and confirmed preliminary flight and hotel bookings compliant with submission requirements — and we send you the exact document list for your visa type and case.',
          'extra_h': 'Places to Start With in Saudi Arabia',
          'extra_p': 'Going to Saudi Arabia for the first time? Here are 5 places to start with: AlUla (archaeology and history), Historic Jeddah — Al-Balad (heritage and old markets), Riyadh (the capital — museums and towers), Abha (mountains and a different climate), and the Red Sea (beaches and islands).'}},
 'turkey': {
   'kind': 'evisa', 'img': 'turkey',
   'ar': {'name': 'تركيا', 'title': 'تأشيرة تركيا الإلكترونية — إصدار فوري',
          'desc': 'إصدار فوري لتأشيرة تركيا الإلكترونية (e-Visa) مع يونس ترافيل، مع مراجعة ملفك وتجهيز حجوزات طيران وفنادق مبدئية مؤكدة متوافقة مع شروط التقديم.',
          'h1': 'تأشيرة تركيا الإلكترونية',
          'lead': 'بنصدر تأشيرة تركيا إلكترونيًا بشكل فوري، وبنراجع ملفك قبل الإصدار عشان تتجنب أخطاء الرفض الشائعة.',
          'answer': 'يونس ترافيل يصدر تأشيرة تركيا الإلكترونية (e-Visa) بشكل فوري ضمن خدمة التأشيرات الإلكترونية، ومع الإصدار بنراجع ملفك وبنجهز حجوزات طيران وفنادق مبدئية مؤكدة متوافقة 100% مع شروط التقديم — وإسطنبول، مدينة بين قارتين بتاريخ عريق وأسواق وتسوق، هي بداية مثالية لرحلتك.',
          'extra_h': 'ليه تركيا؟', 'extra_p': 'إسطنبول مدينة بين قارتين: تاريخ عريق وأسواق قديمة وتسوق حديث — وجهة بيحبها مسافرينا وبيطلبوا برامجها باستمرار.'},
   'en': {'name': 'Turkey', 'title': 'Turkey e-Visa — Instant Issuance',
          'desc': 'Instant issuance of the Turkey electronic visa (e-Visa) with Younis Travel, with your file reviewed and confirmed preliminary flight and hotel bookings prepared in line with submission requirements.',
          'h1': 'Turkey Electronic Visa',
          'lead': 'We issue the Turkey visa electronically and instantly, and review your file before issuance so you avoid the common rejection mistakes.',
          'answer': 'Younis Travel issues the Turkey electronic visa (e-Visa) instantly as part of its e-visa service, and with the issuance we review your file and prepare confirmed preliminary flight and hotel bookings, 100% compliant with submission requirements — and Istanbul, a city between two continents with deep history, markets and shopping, is a perfect start to your trip.',
          'extra_h': 'Why Turkey?', 'extra_p': 'Istanbul is a city between two continents: deep history, old markets and modern shopping — a destination our travelers love and keep asking about.'}},
 'uae': {
   'kind': 'evisa', 'img': 'uae',
   'ar': {'name': 'الإمارات', 'title': 'تأشيرة الإمارات الإلكترونية — إصدار فوري',
          'desc': 'إصدار فوري لتأشيرة الإمارات الإلكترونية مع يونس ترافيل، مع مراجعة ملفك وتجهيز حجوزات الطيران والفنادق بأسعار شركات وحجوزات مبدئية مؤكدة.',
          'h1': 'تأشيرة الإمارات الإلكترونية',
          'lead': 'بنصدر تأشيرة الإمارات إلكترونيًا بشكل فوري، ونكمل رحلتك بحجوزات طيران وفنادق بأسعار شركات.',
          'answer': 'يونس ترافيل يصدر تأشيرة الإمارات الإلكترونية (e-Visa) بشكل فوري ضمن خدمة التأشيرات الإلكترونية، وبنكمل ملف رحلتك بحجوزات طيران بمقارنة بين أكثر من 500 شركة طيران وفنادق بأسعار B2B أرخص من بوابات الحجز المفتوحة — ودبي بأبراجها وتسوقها وترفيهها وجهة تناسب كل العيلة.',
          'extra_h': 'ليه الإمارات؟', 'extra_p': 'دبي مدينة الأبراج والتسوق والترفيه العائلي — من أكتر الوجهات طلبًا عند مسافرينا في الإجازات القصيرة والطويلة.'},
   'en': {'name': 'UAE', 'title': 'UAE e-Visa — Instant Issuance',
          'desc': 'Instant issuance of the UAE electronic visa with Younis Travel, with your file reviewed and flight and hotel bookings prepared at corporate rates with confirmed preliminary bookings.',
          'h1': 'UAE Electronic Visa',
          'lead': 'We issue the UAE visa electronically and instantly, and complete your trip with flight and hotel bookings at corporate rates.',
          'answer': 'Younis Travel issues the UAE electronic visa (e-Visa) instantly as part of its e-visa service, and completes your trip file with flight bookings compared across more than 500 airlines and hotels at B2B rates cheaper than the open booking portals — and Dubai, with its towers, shopping and entertainment, suits the whole family.',
          'extra_h': 'Why the UAE?', 'extra_p': 'Dubai is a city of towers, shopping and family entertainment — one of the most requested destinations among our travelers for short and long breaks alike.'}},
 'vietnam': {
   'kind': 'evisa', 'img': 'vietnam',
   'ar': {'name': 'فيتنام', 'title': 'تأشيرة فيتنام الإلكترونية — إصدار فوري',
          'desc': 'إصدار فوري لتأشيرة فيتنام الإلكترونية مع يونس ترافيل، مع مراجعة ملفك وتجهيز حجوزات مبدئية مؤكدة وبرامج لخليج ها لونج وأجمل مدن فيتنام.',
          'h1': 'تأشيرة فيتنام الإلكترونية',
          'lead': 'بنصدر تأشيرة فيتنام إلكترونيًا بشكل فوري، وبنجهزلك برنامج رحلة لطبيعة آسيا الهادية.',
          'answer': 'يونس ترافيل يصدر تأشيرة فيتنام الإلكترونية (e-Visa) بشكل فوري ضمن خدمة التأشيرات الإلكترونية، ومع الإصدار بنراجع ملفك وبنجهز حجوزات طيران وفنادق مبدئية مؤكدة — وخليج ها لونج بجُزره الخضراء وطبيعته الهادية من أجمل محطات أي رحلة لفيتنام.',
          'extra_h': 'ليه فيتنام؟', 'extra_p': 'خليج ها لونج — جزر خضراء طالعة من البحر وهدوء آسيوي مختلف — تجربة طبيعة من أجمل ما يكون.'},
   'en': {'name': 'Vietnam', 'title': 'Vietnam e-Visa — Instant Issuance',
          'desc': 'Instant issuance of the Vietnam electronic visa with Younis Travel, with your file reviewed, confirmed preliminary bookings prepared, and programs for Ha Long Bay and Vietnam’s finest cities.',
          'h1': 'Vietnam Electronic Visa',
          'lead': 'We issue the Vietnam visa electronically and instantly, and prepare a trip program for Asia’s calm nature.',
          'answer': 'Younis Travel issues the Vietnam electronic visa (e-Visa) instantly as part of its e-visa service, and with the issuance we review your file and prepare confirmed preliminary flight and hotel bookings — and Ha Long Bay, with its green islands and calm nature, is one of the finest stops on any Vietnam trip.',
          'extra_h': 'Why Vietnam?', 'extra_p': 'Ha Long Bay — green islands rising from the sea and a distinct Asian calm — is one of the most beautiful nature experiences there is.'}},
 'kenya': {
   'kind': 'evisa', 'img': 'kenya',
   'ar': {'name': 'كينيا', 'title': 'تأشيرة كينيا الإلكترونية — إصدار فوري',
          'desc': 'إصدار فوري لتأشيرة كينيا الإلكترونية مع يونس ترافيل، مع مراجعة ملفك وتجهيز برامج سفاري أفريقية حقيقية وحجوزات مبدئية مؤكدة.',
          'h1': 'تأشيرة كينيا الإلكترونية',
          'lead': 'بنصدر تأشيرة كينيا إلكترونيًا بشكل فوري، وبنجهزلك سفاري أفريقية حقيقية.',
          'answer': 'يونس ترافيل يصدر تأشيرة كينيا الإلكترونية (e-Visa) بشكل فوري ضمن خدمة التأشيرات الإلكترونية، ومع الإصدار بنراجع ملفك وبنجهز حجوزات طيران وفنادق مبدئية مؤكدة — وكينيا هي بوابة السفاري الأفريقية: حياة برية حقيقية وتجربة مختلفة عن أي رحلة تانية.',
          'extra_h': 'ليه كينيا؟', 'extra_p': 'سفاري أفريقية حقيقية وسط الحياة البرية — وجهة المغامرة الأولى عند مسافرينا الباحثين عن تجربة مختلفة.'},
   'en': {'name': 'Kenya', 'title': 'Kenya e-Visa — Instant Issuance',
          'desc': 'Instant issuance of the Kenya electronic visa with Younis Travel, with your file reviewed and real African safari programs prepared with confirmed preliminary bookings.',
          'h1': 'Kenya Electronic Visa',
          'lead': 'We issue the Kenya visa electronically and instantly, and prepare a real African safari for you.',
          'answer': 'Younis Travel issues the Kenya electronic visa (e-Visa) instantly as part of its e-visa service, and with the issuance we review your file and prepare confirmed preliminary flight and hotel bookings — and Kenya is the gateway to the African safari: real wildlife and an experience unlike any other trip.',
          'extra_h': 'Why Kenya?', 'extra_p': 'A real African safari among the wildlife — the top adventure destination for our travelers looking for something different.'}},
 'albania': {
   'kind': 'evisa', 'img': 'albania',
   'ar': {'name': 'ألبانيا', 'title': 'تأشيرة ألبانيا الإلكترونية — إصدار فوري',
          'desc': 'إصدار فوري لتأشيرة ألبانيا الإلكترونية مع يونس ترافيل، مع مراجعة ملفك وتجهيز حجوزات مبدئية مؤكدة وبرامج لشواطئ الريفييرا الألبانية.',
          'h1': 'تأشيرة ألبانيا الإلكترونية',
          'lead': 'بنصدر تأشيرة ألبانيا إلكترونيًا بشكل فوري — بوابتك لشواطئ أوروبية بسعر أخف.',
          'answer': 'يونس ترافيل يصدر تأشيرة ألبانيا الإلكترونية (e-Visa) بشكل فوري ضمن خدمة التأشيرات الإلكترونية، ومع الإصدار بنراجع ملفك وبنجهز حجوزات طيران وفنادق مبدئية مؤكدة — وألبانيا بشواطئها على البحر الأدرياتيكي بتقدم تجربة أوروبية كاملة بروح أخف وأسعار أهدى.',
          'extra_h': 'ليه ألبانيا؟', 'extra_p': 'الريفييرا الألبانية — شواطئ أوروبية على البحر الأدرياتيكي بمياه صافية وأجواء هادية، وجهة صاعدة بيحبها مسافرينا.'},
   'en': {'name': 'Albania', 'title': 'Albania e-Visa — Instant Issuance',
          'desc': 'Instant issuance of the Albania electronic visa with Younis Travel, with your file reviewed, confirmed preliminary bookings prepared, and programs for the Albanian Riviera beaches.',
          'h1': 'Albania Electronic Visa',
          'lead': 'We issue the Albania visa electronically and instantly — your gateway to European beaches at a lighter cost.',
          'answer': 'Younis Travel issues the Albania electronic visa (e-Visa) instantly as part of its e-visa service, and with the issuance we review your file and prepare confirmed preliminary flight and hotel bookings — and Albania, with its Adriatic beaches, offers a complete European experience with a lighter spirit and calmer prices.',
          'extra_h': 'Why Albania?', 'extra_p': 'The Albanian Riviera — European beaches on the Adriatic Sea with clear water and a calm atmosphere, a rising destination our travelers love.'}},
}

def crumb3(path, country_name, lang):
    en = (lang == 'en')
    prefix = '/en' if en else ''
    items = [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home' if en else 'الرئيسية', 'item': BASE + prefix + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Visas' if en else 'التأشيرات', 'item': BASE + prefix + '/visas.html'},
        {'@type': 'ListItem', 'position': 3, 'name': country_name, 'item': BASE + prefix + path}]
    s = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': items}
    return f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'

def country_body(slug, c, lang):
    d = c[lang]
    en = (lang == 'en')
    prefix = '/en' if en else ''
    kind = c['kind']
    if en:
        svc_h = 'What We Do For You'
        svc = [('Electronic visa issuance', '<p>Instant issuance of the electronic visa as part of our e-visa service.</p>'),
               ('File review & preparation', B.ul(['Professional application writing and filling', 'Employment letter preparation', 'Certified translation'])),
               ('Confirmed preliminary bookings', '<p>Confirmed preliminary flight and hotel bookings, 100% compliant with embassy requirements, to keep your file safe.</p>')] if kind == 'evisa' else \
              [('Tasheer appointment booking', '<p>We book your appointment at the Saudi visa centers (Tasheer) as part of our embassy and visa-center appointment service.</p>'),
               ('File review & preparation', B.ul(['Professional application writing and filling', 'Employment letter preparation', 'Certified translation'])),
               ('Confirmed preliminary bookings', '<p>Confirmed preliminary flight and hotel bookings, 100% compliant with submission requirements, to keep your file safe.</p>')]
        steps_h = 'How It Works'
        steps = [('1', 'Send us a message with the country and visa type.'), ('2', 'We review your file and prepare the documents and application.'), ('3', 'We issue the e-visa or book your appointment.'), ('4', 'You receive your visa before travel.')]
        cta_h, cta_p = f'Ready to Apply for Your {d["name"]} Visa?', 'Send your request with the country and expected travel date, and we will get started with you right away.'
        cta = B.cta_band_en(cta_h, cta_p)
    else:
        svc_h = 'بنقدملك إيه؟'
        svc = [('إصدار التأشيرة الإلكترونية', '<p>إصدار فوري للتأشيرة الإلكترونية ضمن خدمة التأشيرات الإلكترونية بتاعتنا.</p>'),
               ('مراجعة وتجهيز الملف', B.ul(['كتابة وتعبئة الأبلكيشن باحترافية', 'تجهيز خطابات العمل', 'الترجمة المعتمدة'])),
               ('حجوزات مبدئية مؤكدة', '<p>حجوزات طيران وفنادق مبدئية مؤكدة، متوافقة 100% مع شروط السفارات لضمان سلامة الملف.</p>')] if kind == 'evisa' else \
              [('حجز موعد تأشير', '<p>بنحجزلك موعدك في مراكز التأشيرات السعودية (تأشير) ضمن خدمة حجز مواعيد السفارات ومراكز التأشيرات.</p>'),
               ('مراجعة وتجهيز الملف', B.ul(['كتابة وتعبئة الأبلكيشن باحترافية', 'تجهيز خطابات العمل', 'الترجمة المعتمدة'])),
               ('حجوزات مبدئية مؤكدة', '<p>حجوزات طيران وفنادق مبدئية مؤكدة، متوافقة 100% مع شروط التقديم لضمان سلامة الملف.</p>')]
        steps_h = 'إزاي بنشتغل؟'
        steps = [('١', 'بتبعتلنا رسالة بالدولة ونوع التأشيرة.'), ('٢', 'بنراجع ملفك وبنجهز الأوراق والأبلكيشن.'), ('٣', 'بنصدر التأشيرة الإلكترونية أو بنحجز موعدك.'), ('٤', 'بتستلم تأشيرتك قبل السفر.')]
        cta_h, cta_p = f'جاهز تقدم على تأشيرة {d["name"]}؟', 'ابعت طلبك بالدولة وتاريخ السفر المتوقع، وهنبدأ معاك على طول.'
        cta = B.cta_band(cta_h, cta_p)
    body = f"""
<section class="page-hero"><div class="wrap">
<h1>{d['h1']}</h1>
<p>{d['lead']}</p>
</div></section>
<section style="padding:28px 0 0"><div class="wrap">
<div class="band" style="text-align:start;margin-top:0"><p style="font-size:18px">{d['answer']}</p></div>
</div></section>
<section><div class="wrap">
<h2>{svc_h}</h2>
""" + B.cards(svc) + f"""
<div class="dcard" style="margin-top:18px"><img src="/images/{c['img']}.webp" alt="{d['name']}" loading="lazy"><div class="db"><h3>{d['extra_h']}</h3><p>{d['extra_p']}</p></div></div>
</div></section>
<section><div class="wrap">
<h2>{steps_h}</h2>
""" + ''.join(f'<div class="step"><div class="n">{n}</div><p>{t}</p></div>' for n, t in steps) + """
</div></section>
""" + V31.faq_section_for(faq_subset(lang, kind), lang) + f"""
<section><div class="wrap">
{cta}
</div></section>
"""
    return body

def country_grid(lang):
    en = (lang == 'en')
    prefix = '/en' if en else ''
    h = 'Visa Pages by Country' if en else 'صفحات التأشيرات حسب الدولة'
    lead = 'Pick your country for the full service details:' if en else 'اختر دولتك لصفحة الخدمة الكاملة:'
    items = []
    for slug, c in COUNTRIES.items():
        d = c[lang]
        badge = 'Electronic visa' if c['kind'] == 'evisa' else 'Tasheer appointments'
        if not en:
            badge = 'تأشيرة إلكترونية' if c['kind'] == 'evisa' else 'مواعيد تأشير'
        more = 'Details →' if en else 'التفاصيل ←'
        items.append((d['name'], f'<span class="badge">{badge}</span><p><a href="{prefix}/visas/{slug}.html">{more}</a></p>'))
    return f'<section><div class="wrap"><h2>{h}</h2><p class="lead">{lead}</p>' + B.cards(items) + '</div></section>'

def main():
    V31.main()
    visas_dir = os.path.join(OUT, 'visas')
    en_visas_dir = os.path.join(OUT, 'en', 'visas')
    os.makedirs(visas_dir, exist_ok=True)
    os.makedirs(en_visas_dir, exist_ok=True)
    for slug, c in COUNTRIES.items():
        path = f'/visas/{slug}.html'
        for lang, out_dir in (('ar', visas_dir), ('en', en_visas_dir)):
            d = c[lang]
            extra = crumb3(path, d['name'], lang) + V31.faq_schema_for(faq_subset(lang, c['kind'])) + V31.howto_schema(lang)
            meta = [pg for pg in (B.PAGES if lang == 'ar' else B.PAGES_EN) if pg[3] == '/visas.html'][0]
            html = V3.layout3(d['title'], d['desc'], path, country_body(slug, c, lang),
                              lang=lang, extra_head=extra)
            with open(os.path.join(out_dir, slug + '.html'), 'w', encoding='utf-8') as fh:
                fh.write(html)
    # visas index pages: add country grid before FAQ
    for lang, fname, base_body in (('ar', os.path.join(OUT, 'visas.html'), B.visas_body),
                                   ('en', os.path.join(OUT, 'en', 'visas.html'), B.visas_body_en)):
        body = V31.inject_answer(base_body, V31.ANSWERS['/visas.html'][lang]) \
            + country_grid(lang) + V31.faq_section_for(V31.FAQ_PAGES['/visas.html'][lang], lang)
        extra = V31.breadcrumb_schema('/visas.html', lang) \
            + V31.faq_schema_for(V31.FAQ_PAGES['/visas.html'][lang]) + V31.howto_schema(lang)
        meta = [pg for pg in (B.PAGES if lang == 'ar' else B.PAGES_EN) if pg[3] == '/visas.html'][0]
        with open(fname, 'w', encoding='utf-8') as fh:
            fh.write(V3.layout3(meta[1], meta[2], '/visas.html', body, lang=lang, extra_head=extra))
    # sitemap: base 12 + country 12
    all_paths = [pg[3] for pg in B.PAGES] + [('/en' + pg[3] if pg[3] != '/' else '/en/') for pg in B.PAGES_EN]
    all_paths += [f'/visas/{s}.html' for s in COUNTRIES] + [f'/en/visas/{s}.html' for s in COUNTRIES]
    urls = '\n'.join(f'  <url><loc>{BASE}{u}</loc></url>' for u in all_paths)
    with open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8') as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '\n</urlset>\n')
    # llms: append country landing pages
    extra_llms = '\n## Visa landing pages\n\n' + ''.join(f'- {c["en"]["name"]}: {BASE}/visas/{s}.html\n' for s, c in COUNTRIES.items())
    for f in ('llms.txt', 'llms-full.txt'):
        with open(os.path.join(OUT, f), 'a', encoding='utf-8') as fh:
            fh.write(extra_llms)
    # IndexNow key file
    key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'indexnow-key.txt')
    if os.path.exists(key_file):
        key = open(key_file).read().strip()
    else:
        key = secrets.token_hex(16)
        with open(key_file, 'w') as fh:
            fh.write(key)
    with open(os.path.join(OUT, key + '.txt'), 'w') as fh:
        fh.write(key)
    print('built v3.2 ->', OUT, '| sitemap urls:', len(all_paths), '| indexnow key file:', key + '.txt')

if __name__ == '__main__':
    main()
