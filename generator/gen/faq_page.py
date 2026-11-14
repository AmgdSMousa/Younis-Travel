"""Younis Travel — expanded FAQ pages (GEO/AEO plan, Phase 2, approved 2026-11-14).
One FAQ page per language with FAQPage schema, written ONLY from the approved
service copy (e-visas: Turkey, Vietnam, Albania, Kenya, UAE; embassy/Tasheer
appointments: USA, Schengen, UK, Saudi; flights compared across 500+ airlines,
ticket via WhatsApp + email; hotels at closed B2B rates with official receipts;
no prices published — the team confirms the final price personally).
Also: sitemap + llms entries, Markdown copies, IndexNow submission.
Runs the OAuth stage (the whole chain) first."""
import os, sys, json, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gen import layout as V3
from gen import oauth as V36

OUT = V3.OUT
BASE = 'https://younistravel.site'
GEN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAQ_AR = [
    ('إيه الخدمات اللي بيقدمها يونس ترافيل؟',
     'يونس ترافيل بيقدم تأشيرات إلكترونية وعادية مع حجز مواعيد السفارات، وحجوزات طيران، وحجوزات فنادق، وبرامج رحلات سياحية، وتأمين سفر.'),
    ('أي دول تأشيرتها إلكترونية؟',
     'التأشيرات الإلكترونية متاحة لتركيا وفيتنام وألبانيا وكينيا والإمارات — بتتقدم أونلاين من غير ما تحتاج تروح سفارة.'),
    ('أي تأشيرات بتحتاج موعد سفارة أو مراكز تأشير؟',
     'تأشيرات أمريكا وشنجن وبريطانيا والسعودية بتحتاج موعد سفارة أو مركز تأشير (تشير)، وإحنا بنساعدك في تجهيز الأوراق وحجز الموعد.'),
    ('إزاي أطلب خدمة أو أحجز؟',
     'املأ نموذج الطلب على الموقع في ٣ خطوات: الخدمة والتفاصيل، وبعدين بياناتك، وبعدين المراجعة والتأكيد. هتستلم رقم حجز فورًا، والفريق بيراجع طلبك وبيتواصل معاك بالتأكيد والسعر النهائي.'),
    ('هل الأسعار النهائية موجودة على الموقع؟',
     'لا. الأسعار بتتغير حسب التاريخ والتوفر، فالفريق بيأكد السعر النهائي معاك شخصيًا قبل أي دفع، ومفيش أي مبلغ بيتدفع أونلاين على الموقع.'),
    ('إزاي أتابع حالة طلبي؟',
     'من صفحة «تابع حالة حجزك» على الموقع، برقم الحجز ورقم الموبايل اللي سجلت بيه. الحالات: جديد، تم التواصل، مؤكد، مكتمل، أو ملغي.'),
    ('بتحجزوا طيران لأي وجهة؟',
     'أيوه. بنقارن بين أكتر من 500 شركة طيران عشان نوصّل لأنسب سعر ومسار لرحلتك، والتذكرة بتوصلك على واتساب والإيميل.'),
    ('أسعار الفنادق عندكم إزاي؟',
     'بنشتغل بأسعار B2B خاصة مش متاحة للجمهور، وكل حجز فندق بيطلع بإيصال رسمي.'),
    ('هل فيه تأمين سفر؟',
     'أيوه، تأمين السفر من ضمن خدمات يونس ترافيل وبيتضاف لأي رحلة عند الطلب.'),
    ('إزاي أتواصل مع الفريق؟',
     'ابعت رسالة لصفحتنا على فيسبوك، أو املأ نموذج الطلب على الموقع، والفريق هيرد عليك ويراجع طلبك.'),
]
FAQ_EN = [
    ('What services does Younis Travel offer?',
     'Younis Travel offers electronic and regular visas with embassy appointment booking, flight bookings, hotel bookings, tour programs, and travel insurance.'),
    ('Which countries have electronic visas?',
     'E-visas are available for Turkey, Vietnam, Albania, Kenya, and the UAE — you apply online without visiting an embassy.'),
    ('Which visas need an embassy or Tasheer appointment?',
     'USA, Schengen, UK, and Saudi visas need an embassy or visa-centre (Tasheer) appointment, and we help you prepare the documents and book the appointment.'),
    ('How do I place a request or book?',
     'Fill in the request form on the website in three steps: service and details, then your details, then review and confirm. You receive a booking reference immediately, and the team reviews your request and contacts you with the confirmation and final price.'),
    ('Are final prices shown on the website?',
     'No. Prices change with dates and availability, so the team confirms the final price with you personally before any payment, and nothing is paid online on the website.'),
    ('How do I track my request?',
     'Use the "Track your booking" page on the website with your booking reference and the mobile number you registered with. Statuses: New, Contacted, Confirmed, Completed, or Cancelled.'),
    ('Do you book flights to any destination?',
     'Yes. We compare more than 500 airlines to find the best price and route for your trip, and your ticket is delivered via WhatsApp and email.'),
    ('How do your hotel rates work?',
     'We work with closed B2B rates that are not available to the public, and every hotel booking comes with an official receipt.'),
    ('Do you offer travel insurance?',
     'Yes, travel insurance is one of Younis Travel\'s services and can be added to any trip on request.'),
    ('How do I contact the team?',
     'Message our Facebook Page, or fill in the request form on the website, and the team will reply and review your request.'),
]
STYLE = ('<style>.faq-item{border-bottom:1px solid #e7e2d9;padding:18px 0}'
         '.faq-item h3{margin:0 0 8px;font-size:1.12rem}.faq-item p{margin:0;color:#444}</style>')

def _schema(faqs):
    data = {'@context': 'https://schema.org', '@type': 'FAQPage',
            'mainEntity': [{'@type': 'Question', 'name': q,
                            'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'

def _body(faqs, heading, intro):
    items = ''.join(f'<div class="faq-item"><h3>{q}</h3><p>{a}</p></div>' for q, a in faqs)
    return (f'<section class="page-hero"><div class="wrap"><h1>{heading}</h1><p>{intro}</p></div></section>'
            f'<section class="section"><div class="wrap"><div class="card">{items}</div></div></section>')

def _md(faqs, heading):
    out = [f'# {heading}', '']
    for q, a in faqs:
        out += [f'## {q}', '', a, '']
    return '\n'.join(out)

def _write(rel, content):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(content)

def main():
    V36.main()
    ar = _body(FAQ_AR, 'الأسئلة الشائعة', 'إجابات مباشرة عن خدمات يونس ترافيل: التأشيرات والطيران والفنادق وطريقة الحجز والمتابعة.')
    en = _body(FAQ_EN, 'Frequently Asked Questions', 'Direct answers about Younis Travel services: visas, flights, hotels, and how booking and tracking work.')
    _write('faq.html', V3.layout3('الأسئلة الشائعة', 'إجابات مباشرة عن خدمات يونس ترافيل: التأشيرات الإلكترونية ومواعيد السفارات والطيران والفنادق وطريقة الحجز والمتابعة.', '/faq.html', ar, extra_head=STYLE + _schema(FAQ_AR)))
    _write('en/faq.html', V3.layout3('Frequently Asked Questions', 'Direct answers about Younis Travel services: e-visas, embassy appointments, flights, hotels, and how booking and tracking work.', '/faq.html', en, lang='en', extra_head=STYLE + _schema(FAQ_EN)))
    _write('md/faq.md', _md(FAQ_AR, 'الأسئلة الشائعة — يونس ترافيل'))
    _write('md/en/faq.md', _md(FAQ_EN, 'Frequently Asked Questions — Younis Travel'))

    # sitemap: add the two URLs once
    sm_path = os.path.join(OUT, 'sitemap.xml')
    sm = open(sm_path, encoding='utf-8').read()
    if '/faq.html' not in sm:
        add = ('<url><loc>' + BASE + '/faq.html</loc><lastmod>2026-11-14</lastmod></url>'
               '<url><loc>' + BASE + '/en/faq.html</loc><lastmod>2026-11-14</lastmod></url>')
        sm = sm.replace('</urlset>', add + '</urlset>')
        _write('sitemap.xml', sm)

    # llms.txt: one discoverable link per language
    llms_path = os.path.join(OUT, 'llms.txt')
    llms = open(llms_path, encoding='utf-8').read()
    if '/faq.html' not in llms:
        _write('llms.txt', llms.rstrip() + '\n- [Frequently Asked Questions](' + BASE + '/faq.html): direct answers about visas, flights, hotels, booking and tracking\n')

    # llms-full.txt: the full Q&A text — the quotable answer source for models
    full_path = os.path.join(OUT, 'llms-full.txt')
    full = open(full_path, encoding='utf-8').read()
    if 'Frequently Asked Questions' not in full:
        block = '\n## Frequently Asked Questions\n\n' + '\n'.join(f'Q: {q}\nA: {a}\n' for q, a in FAQ_EN)
        _write('llms-full.txt', full.rstrip() + '\n' + block)

    # IndexNow: submit the two new URLs
    try:
        key = open(os.path.join(GEN_DIR, 'indexnow-key.txt'), encoding='utf-8').read().strip()
        payload = json.dumps({'host': 'younistravel.site', 'key': key,
                              'keyLocation': BASE + '/' + key + '.txt',
                              'urlList': [BASE + '/faq.html', BASE + '/en/faq.html']}).encode()
        req = urllib.request.Request('https://api.indexnow.org/indexnow', data=payload,
                                     headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=20) as r:
            print('IndexNow FAQ submit:', r.status)
    except Exception as e:
        print('IndexNow FAQ submit skipped:', e)
    print('built faq pages -> faq.html, en/faq.html (+ sitemap, llms, md)')

if __name__ == '__main__':
    main()
