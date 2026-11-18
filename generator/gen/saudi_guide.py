"""Younis Travel — Saudi tourist visa guide page (owner-supplied requirements,
2026-11-18). The requirements stated here are exactly the owner's own rules for
the Saudi tourist visa file: a high profession shown in the passport, a bank
balance of at least EGP 70,000, and a 3-month bank statement showing account
activity (deposits/withdrawals) over that period. Nothing else is claimed:
no processing time, no fees, no approval promise. Service framing reuses the
approved Saudi copy (Tasheer appointment + full file review/preparation +
confirmed preliminary bookings). Runs the flight-search stage (whole chain)
first, then adds /saudi-visa-guide.html + /en/saudi-visa-guide.html, Markdown
copies, sitemap + llms entries, and an IndexNow submission."""
import os, sys, json, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gen import layout as V3
from gen import flights_search as PREV

OUT = V3.OUT
BASE = 'https://younistravel.site'
GEN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQ_AR = [
    'مهنة عالية مثبتة في جواز السفر.',
    'حساب بنكي برصيد 70,000 جنيه على الأقل.',
    'كشف حساب بنكي عن آخر 3 شهور، ويكون على الحساب خلال الشهور دي حركة سحب وإيداع — الحساب الراكد من غير حركة ما بيكفيش.',
]
REQ_EN = [
    'A high profession shown in your passport.',
    'A bank account with a balance of at least EGP 70,000.',
    'A bank statement covering the last 3 months, with deposit and withdrawal activity on the account during that period — a dormant account with no transactions is not enough.',
]
FAQ_AR = [
    ('إيه ضوابط التأشيرة السياحية السعودية؟',
     'الضوابط الأساسية: مهنة عالية مثبتة في جواز السفر، وحساب بنكي برصيد 70,000 جنيه على الأقل، مع كشف حساب بنكي عن آخر 3 شهور يكون عليه حركة سحب وإيداع خلال المدة دي.'),
    ('كشف الحساب البنكي المطلوب شكله إيه؟',
     'كشف حساب بنكي عن آخر 3 شهور، الرصيد فيه 70,000 جنيه أو أكتر، وبيوضح حركات سحب وإيداع على الحساب خلال الشهور دي — الحساب اللي مفيهوش حركة ما بينفعش.'),
    ('يونس ترافيل بيساعدني في إيه في تأشيرة السعودية؟',
     'بنحجزلك موعدك في مراكز تأشير، وبنراجع ملفك وبنجهزه بالكامل قبل التقديم: تعبئة الأبلكيشن باحترافية، وتجهيز خطابات العمل والترجمة المعتمدة، وحجوزات طيران وفنادق مبدئية مؤكدة متوافقة مع شروط التقديم.'),
]
FAQ_EN = [
    ('What are the requirements for a Saudi tourist visa?',
     'The core requirements: a high profession shown in your passport, a bank account with a balance of at least EGP 70,000, and a bank statement covering the last 3 months showing deposit and withdrawal activity over that period.'),
    ('What exactly is required from the bank statement?',
     'A bank statement for the last 3 months with a balance of EGP 70,000 or more, showing deposits and withdrawals on the account during those months — an account with no transactions does not work.'),
    ('How does Younis Travel help with a Saudi visa?',
     'We book your Tasheer center appointment and review and prepare your complete file before submission: professional application filling, employment letters and certified translation, and confirmed preliminary flight and hotel bookings compliant with submission requirements.'),
]
STYLE = ('<style>.faq-item{border-bottom:1px solid #e7e2d9;padding:18px 0}'
         '.faq-item h3{margin:0 0 8px;font-size:1.12rem;color:#003262}.faq-item p{margin:0;color:#3d5a75}'
         '.req-list{margin:0;padding-inline-start:22px;color:#3d5a75;font-size:17px;line-height:1.9}</style>')

def _schema(faqs):
    data = {'@context': 'https://schema.org', '@type': 'FAQPage',
            'mainEntity': [{'@type': 'Question', 'name': q,
                            'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'

def _body(lang):
    if lang == 'ar':
        reqs = ''.join(f'<li>{r}</li>' for r in REQ_AR)
        items = ''.join(f'<div class="faq-item"><h3>{q}</h3><p>{a}</p></div>' for q, a in FAQ_AR)
        return f"""
<section class="page-hero"><div class="wrap">
<h1>التأشيرة السياحية السعودية: الضوابط والأوراق المطلوبة</h1>
<p>دي ضوابط التأشيرة السياحية السعودية والأوراق الأساسية المطلوبة في ملف التقديم، مجمعة في صفحة واحدة عشان تجهز ملفك صح من الأول.</p>
</div></section>
<section class="section"><div class="wrap">
<h2>الضوابط الأساسية</h2>
<div class="card"><ul class="req-list">{reqs}</ul>
<p style="margin-top:14px;color:#3d5a75">دي الضوابط الأساسية للتأشيرة السياحية؛ وقايمة الأوراق الدقيقة بتتحدد حسب حالتك ونوع تأشيرتك، وبنبعتها لك كاملة مع مراجعة الملف.</p></div>
<h2 style="margin-top:34px">أسئلة شائعة</h2>
<div class="card">{items}</div>
<div style="text-align:center;margin-top:30px"><a class="cta-btn" href="/request.html">ابعت طلبك وابدأ ملفك</a>
<p style="margin-top:12px"><a href="/visas/saudi.html">صفحة تأشيرة السعودية: مواعيد تأشير وتجهيز الملف</a></p></div>
</div></section>
"""
    reqs = ''.join(f'<li>{r}</li>' for r in REQ_EN)
    items = ''.join(f'<div class="faq-item"><h3>{q}</h3><p>{a}</p></div>' for q, a in FAQ_EN)
    return f"""
<section class="page-hero"><div class="wrap">
<h1>Saudi Tourist Visa: Requirements &amp; Documents</h1>
<p>These are the requirements for a Saudi tourist visa and the core documents your application file needs, gathered on one page so you prepare your file correctly from the start.</p>
</div></section>
<section class="section"><div class="wrap">
<h2>Core Requirements</h2>
<div class="card"><ul class="req-list">{reqs}</ul>
<p style="margin-top:14px;color:#3d5a75">These are the core requirements for the tourist visa; the exact document list depends on your case and visa type, and we send it to you in full when we review your file.</p></div>
<h2 style="margin-top:34px">Frequently Asked Questions</h2>
<div class="card">{items}</div>
<div style="text-align:center;margin-top:30px"><a class="cta-btn" href="/en/request.html">Send Your Request and Start Your File</a>
<p style="margin-top:12px"><a href="/en/visas/saudi.html">Saudi visa page: Tasheer appointments &amp; file preparation</a></p></div>
</div></section>
"""

def _md(lang):
    if lang == 'ar':
        out = ['# التأشيرة السياحية السعودية: الضوابط والأوراق المطلوبة — يونس ترافيل', '', '## الضوابط الأساسية', '']
        out += [f'- {r}' for r in REQ_AR] + ['']
        for q, a in FAQ_AR:
            out += [f'## {q}', '', a, '']
        return '\n'.join(out)
    out = ['# Saudi Tourist Visa: Requirements & Documents — Younis Travel', '', '## Core Requirements', '']
    out += [f'- {r}' for r in REQ_EN] + ['']
    for q, a in FAQ_EN:
        out += [f'## {q}', '', a, '']
    return '\n'.join(out)

def _write(rel, content):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(content)

def main():
    PREV.main()
    _write('saudi-visa-guide.html', V3.layout3('دليل التأشيرة السياحية السعودية — الضوابط والأوراق المطلوبة',
           'ضوابط التأشيرة السياحية السعودية: مهنة عالية في الجواز، حساب بنكي برصيد 70,000 جنيه على الأقل، وكشف حساب بنكي عن آخر 3 شهور عليه حركة — مع حجز موعد تأشير وتجهيز الملف من يونس ترافيل.',
           '/saudi-visa-guide.html', _body('ar'), extra_head=STYLE + _schema(FAQ_AR)))
    _write('en/saudi-visa-guide.html', V3.layout3('Saudi Tourist Visa Guide — Requirements & Documents',
           'Saudi tourist visa requirements: a high profession in the passport, a bank balance of at least EGP 70,000, and a 3-month bank statement with account activity — with Tasheer appointment booking and file preparation by Younis Travel.',
           '/en/saudi-visa-guide.html', _body('en'), lang='en', extra_head=STYLE + _schema(FAQ_EN)))
    _write('md/saudi-visa-guide.md', _md('ar'))
    _write('md/en/saudi-visa-guide.md', _md('en'))

    sm_path = os.path.join(OUT, 'sitemap.xml')
    sm = open(sm_path, encoding='utf-8').read()
    if '/saudi-visa-guide.html' not in sm:
        add = ('<url><loc>' + BASE + '/saudi-visa-guide.html</loc><lastmod>2026-11-18</lastmod></url>'
               '<url><loc>' + BASE + '/en/saudi-visa-guide.html</loc><lastmod>2026-11-18</lastmod></url>')
        sm = sm.replace('</urlset>', add + '</urlset>')
        _write('sitemap.xml', sm)

    llms_path = os.path.join(OUT, 'llms.txt')
    llms = open(llms_path, encoding='utf-8').read()
    if '/saudi-visa-guide.html' not in llms:
        _write('llms.txt', llms.rstrip() + '\n- [Saudi Tourist Visa Guide](' + BASE + '/saudi-visa-guide.html): Saudi tourist visa requirements — profession in passport, EGP 70,000 bank balance, 3-month active bank statement\n')

    full_path = os.path.join(OUT, 'llms-full.txt')
    full = open(full_path, encoding='utf-8').read()
    if 'Saudi Tourist Visa' not in full:
        block = '\n## Saudi Tourist Visa Requirements\n\n' + '\n'.join(f'Q: {q}\nA: {a}\n' for q, a in FAQ_EN)
        _write('llms-full.txt', full.rstrip() + '\n' + block)

    try:
        key = open(os.path.join(GEN_DIR, 'indexnow-key.txt'), encoding='utf-8').read().strip()
        payload = json.dumps({'host': 'younistravel.site', 'key': key,
                              'keyLocation': BASE + '/' + key + '.txt',
                              'urlList': [BASE + '/saudi-visa-guide.html', BASE + '/en/saudi-visa-guide.html']}).encode()
        req = urllib.request.Request('https://api.indexnow.org/indexnow', data=payload,
                                     headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=20) as r:
            print('IndexNow Saudi guide submit:', r.status)
    except Exception as e:
        print('IndexNow Saudi guide submit skipped:', e)
    print('built Saudi visa guide -> saudi-visa-guide.html, en/saudi-visa-guide.html (+ sitemap, llms)')

if __name__ == '__main__':
    main()
