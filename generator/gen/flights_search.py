"""Younis Travel — flight price search results pages (approved 2026-11-17).

The homepage widget's Flights tab lands here with IATA codes; the page calls
/api/flights (Travelpayouts fares in EUR -> EGP at the daily rate + 10% agency
margin, computed server-side) and renders indicative prices in EGP. Booking a
result pre-fills the standard request form (service/destination/passengers/
notes) — the team confirms the final fare personally, as everywhere on the
site. If the price API is not configured or has no fares, the page degrades
to the manual request flow. Runs the FAQ stage (the whole chain) first."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gen import layout as V3
from gen import faq_page as PREV

OUT = V3.OUT
BASE = 'https://younistravel.site'

def _write(rel, text):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(text)

STYLE = """
<style>
.fcard{background:#fff;border:1px solid var(--line);border-radius:18px;box-shadow:var(--sh-card);padding:20px 22px;margin-top:14px;display:flex;gap:18px;flex-wrap:wrap;align-items:center;justify-content:space-between}
.fmain{flex:1 1 330px}
.fair{font-weight:700;color:var(--ink);font-size:19px}
.fmeta{color:var(--mute);font-size:15.5px;margin-top:2px}
.fstop{display:inline-block;background:var(--field);color:var(--ink);border-radius:999px;padding:1px 12px;font-size:13.5px;font-weight:700;margin-inline-start:8px}
.fprice{text-align:end}
.fprice .amt{font-size:27px;font-weight:700;color:var(--ink)}
.fprice .cur{color:var(--golddk);font-weight:700;font-size:17px}
.fbox{background:#fff;border:1px solid var(--line);border-radius:18px;padding:28px;text-align:center;box-shadow:var(--sh-card);margin-top:16px}
.fspin{color:var(--mute);text-align:center;padding:34px 0;font-size:18px}
.fdisc{color:var(--mute);font-size:14.5px;margin-top:18px;text-align:center}
.fnote{background:var(--field);border-radius:14px;padding:12px 18px;color:var(--ink);font-size:15.5px;margin-top:16px;text-align:center}
.fleg{margin-top:10px;padding-top:10px;border-top:1px dashed var(--line)}
.frow{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:17px;color:var(--ink);margin-top:3px}
.farrow{color:var(--gold);font-weight:700}
</style>
"""

STR = {
 'ar': {
  'loading': 'بنبحث عن أرخص الأسعار دلوقتي…',
  'summary': 'رحلات {oname} ← {dname}',
  'dep': 'ذهاب', 'ret': 'عودة', 'pax1': 'مسافر واحد', 'paxn': '{n} مسافر',
  'direct': 'مباشرة', 'stop1': 'توقف واحد', 'stop2': 'توقفان', 'stopn': '{n} توقفات',
  'dur': 'مدة الرحلة', 'per': 'للفرد', 'total': 'الإجمالي',
  'book': 'اطلب حجز الرحلة دي',
  'disc': 'أسعار استرشادية بالجنيه المصري شاملة الضرائب والرسوم — السعر النهائي بيتم تأكيده معاك شخصيًا عند تأكيد الحجز حسب التوافر في وقتها.',
  'notready_h': 'البحث بالأسعار المباشرة بيتفعّل دلوقتي',
  'notready_p': 'ابعت طلبك بالوجهة والتواريخ وهنبحثلك يدويًا ونرد عليك بأحسن سعر متاح.',
  'empty_h': 'مفيش أسعار متاحة للتواريخ دي حاليًا',
  'empty_p': 'جرّب تواريخ مختلفة، أو ابعت طلبك وهنشوفلك بدائل مناسبة.',
  'err_h': 'البحث مش متاح في اللحظة دي',
  'err_p': 'حصلت مشكلة مؤقتة — ابعت طلبك وهنبحثلك يدويًا على طول.',
  'cta': 'ابعت طلب حجز',
  'note': 'رحلة مختارة من بحث الأسعار: {air} {fno} — من {oname} ({oc}) إلى {dname} ({dc})، ذهاب {dep}{retpart}، السعر المعروض {total} ج.م لـ{pax} مسافر ({per} ج.م للفرد).',
  'note_ret': '، عودة {ret}',
  'approx': 'التواريخ دي بالذات مفيهاش أسعار متاحة حاليًا — دي أرخص الأسعار المتاحة في نفس الشهر حوالين تواريخك، وتاريخ كل رحلة مكتوب عليها بالظبط.',
  'kiwi': 'احجز أونلاين فورًا',
  'nextday': '+1 يوم',
  'bag': 'الأمتعة والوزن المسموح بيتم تأكيدهم عند الحجز حسب شركة الطيران ودرجة التذكرة — وبيظهروا بالتفصيل في صفحة Kiwi لو حجزت أونلاين.',
 },
 'en': {
  'loading': 'Searching for the cheapest fares…',
  'summary': 'Flights {oname} → {dname}',
  'dep': 'Outbound', 'ret': 'Return', 'pax1': '1 traveler', 'paxn': '{n} travelers',
  'direct': 'Non-stop', 'stop1': '1 stop', 'stop2': '2 stops', 'stopn': '{n} stops',
  'dur': 'Duration', 'per': 'per person', 'total': 'Total',
  'book': 'Request This Flight',
  'disc': 'Indicative prices in Egyptian Pounds, including taxes and fees — the final fare is confirmed with you personally when the booking is confirmed, subject to availability at that time.',
  'notready_h': 'Live price search is being activated',
  'notready_p': 'Send your request with the destination and dates and we will search manually and reply with the best available fare.',
  'empty_h': 'No fares available for these dates right now',
  'empty_p': 'Try different dates, or send a request and we will look for suitable alternatives.',
  'err_h': 'Search is unavailable at the moment',
  'err_p': 'A temporary problem occurred — send a request and we will search manually right away.',
  'cta': 'Send a Booking Request',
  'note': 'Flight picked from price search: {air} {fno} — from {oname} ({oc}) to {dname} ({dc}), outbound {dep}{retpart}, displayed price EGP {total} for {pax} traveler(s) (EGP {per} per person).',
  'note_ret': ', return {ret}',
  'approx': 'No fares are available for those exact dates right now — these are the cheapest fares in the same month around your dates, and each card shows its exact dates.',
  'kiwi': 'Book Online Instantly',
  'nextday': '+1 day',
  'bag': 'Baggage allowance is confirmed at booking — it depends on the airline and fare class, and Kiwi shows the exact allowance on its booking page.',
 },
}

AIRLINES = {
 'MS': ('مصر للطيران', 'Egyptair'), 'EK': ('طيران الإمارات', 'Emirates'),
 'EY': ('الاتحاد للطيران', 'Etihad'), 'QR': ('الخطوط القطرية', 'Qatar Airways'),
 'FZ': ('فلاي دبي', 'flydubai'), 'G9': ('العربية للطيران', 'Air Arabia'),
 'E5': ('العربية للطيران مصر', 'Air Arabia Egypt'), 'XY': ('طيران ناس', 'flynas'),
 'SV': ('الخطوط السعودية', 'Saudia'), 'KU': ('الخطوط الكويتية', 'Kuwait Airways'),
 'GF': ('طيران الخليج', 'Gulf Air'), 'WY': ('الطيران العُماني', 'Oman Air'),
 'RJ': ('الملكية الأردنية', 'Royal Jordanian'), 'ME': ('طيران الشرق الأوسط', 'MEA'),
 'TK': ('الخطوط التركية', 'Turkish Airlines'), 'LH': ('لوفتهانزا', 'Lufthansa'),
 'AF': ('الخطوط الفرنسية', 'Air France'), 'KL': ('كي إل إم', 'KLM'),
 'BA': ('الخطوط البريطانية', 'British Airways'), 'SM': ('إير كايرو', 'Air Cairo'),
 'J9': ('طيران الجزيرة', 'Jazeera Airways'), 'F3': ('فلاي إيجيبت', 'FlyEgypt'),
 'NE': ('طيران نسما', 'Nesma Airlines'), 'AT': ('الخطوط الملكية المغربية', 'Royal Air Maroc'),
 'TU': ('الخطوط التونسية', 'Tunisair'), 'AH': ('الخطوط الجزائرية', 'Air Algérie'),
}

SCRIPT = """
<script>
var S = __STRINGS__, AL = __AIRLINES__;
function esc(t){ return String(t == null ? '' : t).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
function fmt(n){ return Number(n).toLocaleString('en-US'); }
function fdate(iso){ if(!iso) return ''; var d = new Date(iso); if(isNaN(d)) return esc(iso); return d.toLocaleDateString(document.documentElement.lang === 'ar' ? 'ar-EG' : 'en-GB', {weekday:'short', day:'numeric', month:'short', year:'numeric'}) + ' · ' + d.toLocaleTimeString('en-GB', {hour:'2-digit', minute:'2-digit'}); }
function fdur(m){ if(!m) return ''; var h = Math.floor(m/60), r = m%60; return h + ':' + (r<10?'0':'') + r; }
function stops(n){ return n===0 ? S.direct : n===1 ? S.stop1 : n===2 ? S.stop2 : S.stopn.replace('{n}', n); }
var TZ = {CAI:'Africa/Cairo',HRG:'Africa/Cairo',SSH:'Africa/Cairo',LXR:'Africa/Cairo',ASW:'Africa/Cairo',ALY:'Africa/Cairo',
JED:'Asia/Riyadh',RUH:'Asia/Riyadh',DMM:'Asia/Riyadh',MED:'Asia/Riyadh',AHB:'Asia/Riyadh',TIF:'Asia/Riyadh',
DXB:'Asia/Dubai',AUH:'Asia/Dubai',SHJ:'Asia/Dubai',DOH:'Asia/Qatar',KWI:'Asia/Kuwait',BAH:'Asia/Bahrain',MCT:'Asia/Muscat',
AMM:'Asia/Amman',BEY:'Asia/Beirut',IST:'Europe/Istanbul',SAW:'Europe/Istanbul',ATH:'Europe/Athens',LCA:'Asia/Nicosia',
LHR:'Europe/London',CDG:'Europe/Paris',FRA:'Europe/Berlin',MUC:'Europe/Berlin',BER:'Europe/Berlin',AMS:'Europe/Amsterdam',
FCO:'Europe/Rome',MAD:'Europe/Madrid',BCN:'Europe/Madrid',VIE:'Europe/Vienna',ZRH:'Europe/Zurich',
JFK:'America/New_York',EWR:'America/New_York',IAD:'America/New_York',ORD:'America/Chicago',LAX:'America/Los_Angeles',
BOM:'Asia/Kolkata',DEL:'Asia/Kolkata',KUL:'Asia/Kuala_Lumpur',SIN:'Asia/Singapore',BKK:'Asia/Bangkok',
HAN:'Asia/Ho_Chi_Minh',SGN:'Asia/Ho_Chi_Minh',MLE:'Indian/Maldives',TBS:'Asia/Tbilisi',EVN:'Asia/Yerevan',GYD:'Asia/Baku',
TUN:'Africa/Tunis',ALG:'Africa/Algiers',CMN:'Africa/Casablanca',ADD:'Africa/Addis_Ababa',NBO:'Africa/Nairobi',DAR:'Africa/Dar_es_Salaam'};
function arrTime(iso, durMin, tz){
  if (!iso || !durMin || !tz) return '';
  var dep = new Date(iso); if (isNaN(dep)) return '';
  var arr = new Date(dep.getTime() + durMin * 60000);
  var tf = new Intl.DateTimeFormat('en-GB', {hour:'2-digit', minute:'2-digit', timeZone: tz});
  var df = new Intl.DateTimeFormat('en-CA', {year:'numeric', month:'2-digit', day:'2-digit', timeZone: tz});
  return tf.format(arr) + (df.format(arr) > df.format(dep) ? ' ' + S.nextday : '');
}
function dstr(iso){ var d = new Date(iso); if (isNaN(d)) return String(iso || ''); return d.toLocaleDateString(document.documentElement.lang === 'ar' ? 'ar-EG' : 'en-GB', {weekday:'short', day:'numeric', month:'short'}); }
function leg(label, fromN, fromC, toN, toC, depIso, durMin, stopsN){
  var arr = arrTime(depIso, durMin, TZ[toC]);
  var arrow = document.documentElement.lang === 'ar' ? '←' : '→';
  return '<div class="fleg"><div class="fmeta" style="font-weight:700;color:var(--ink)">' + esc(label) + ' · ' + esc(dstr(depIso)) + '<span class="fstop">' + esc(stops(stopsN)) + '</span></div>' +
    '<div class="frow"><span><b>' + esc(String(depIso).slice(11, 16)) + '</b> ' + esc(fromN) + ' (' + esc(fromC) + ')</span><span class="farrow">' + arrow + '</span>' +
    '<span>' + (arr ? '<b>' + esc(arr) + '</b> ' : '') + esc(toN) + ' (' + esc(toC) + ')</span></div>' +
    (durMin ? '<div class="fmeta">' + esc(S.dur) + ' ' + esc(fdur(durMin)) + '</div>' : '') + '</div>';
}
(function(){
  var q = new URLSearchParams(location.search);
  var origin = (q.get('origin')||'').toUpperCase(), dest = (q.get('destination')||'').toUpperCase();
  var dep = q.get('departure_at')||'', ret = q.get('return_at')||'';
  var pax = Math.max(1, parseInt(q.get('passengers')||'1', 10) || 1), cls = q.get('class')||'economy';
  var oname = q.get('oname') || origin, dname = q.get('dname') || dest;
  var sum = document.getElementById('fsum'), box = document.getElementById('fresults'), st = document.getElementById('fstatus');
  sum.textContent = S.summary.replace('{oname}', oname).replace('{dname}', dname) + ' — ' + S.dep + ': ' + fdate(dep) + (ret ? ' · ' + S.ret + ': ' + fdate(ret) : '') + ' · ' + (pax === 1 ? S.pax1 : S.paxn.replace('{n}', pax));
  var reqBase = (document.documentElement.lang === 'ar' ? '/request.html' : '/en/request.html');
  var AFFIL = 'travelpayoutsdeeplink_www.younistravel.site_0174eed9e1904e2a9e5be2ea2-807576';
  function ddmmyyyy(iso){ if (!iso) return ''; var p = String(iso).slice(0, 10).split('-'); return p[2] + '-' + p[1] + '-' + p[0]; }
  function kiwiLink(depIso, retIso){
    var u = 'https://www.kiwi.com/deep?affilid=' + AFFIL + '&from=' + origin + '&to=' + dest + '&departure=' + ddmmyyyy(depIso);
    if (retIso) u += '&return=' + ddmmyyyy(retIso);
    return u;
  }
  function reqLink(note){
    return reqBase + '?s=flight&d=' + encodeURIComponent(dname) + '&p=' + pax + '&n=' + encodeURIComponent(note);
  }
  function fallback(h, p){
    st.style.display = 'none';
    box.innerHTML = '<div class="fbox"><h2>' + esc(h) + '</h2><p class="lead" style="margin:8px auto 18px">' + esc(p) + '</p>' +
      '<a class="cta-btn" href="' + reqLink(S.summary.replace('{oname}', oname).replace('{dname}', dname) + ' — ' + dep + (ret ? ' / ' + ret : '')) + '">' + esc(S.cta) + '</a>' +
      '<p style="margin-top:10px"><a class="btn-gold" target="_blank" rel="noopener" href="' + kiwiLink(dep, ret) + '">' + esc(S.kiwi) + '</a></p></div>';
  }
  if (!/^[A-Z]{3}$/.test(origin) || !/^[A-Z]{3}$/.test(dest) || !dep) { fallback(S.err_h, S.err_p); return; }
  var u = '/api/flights?origin=' + origin + '&destination=' + dest + '&departure_at=' + encodeURIComponent(dep) + '&passengers=' + pax + '&class=' + encodeURIComponent(cls);
  if (ret) u += '&return_at=' + encodeURIComponent(ret);
  fetch(u).then(function(r){ return r.json().then(function(j){ return {s: r.status, j: j}; }); }).then(function(x){
    if (x.s === 503) { fallback(S.notready_h, S.notready_p); return; }
    if (x.s !== 200 || !x.j.results) { fallback(S.err_h, S.err_p); return; }
    if (!x.j.results.length) { fallback(S.empty_h, S.empty_p); return; }
    st.style.display = 'none';
    var html = x.j.approximate ? '<div class="fnote">' + esc(S.approx) + '</div>' : '';
    x.j.results.forEach(function(f){
      var an = (AL[f.airline] || [f.airline, f.airline])[document.documentElement.lang === 'ar' ? 0 : 1];
      var note = S.note.replace('{air}', an).replace('{fno}', f.flight_number).replace('{oname}', oname).replace('{oc}', origin)
        .replace('{dname}', dname).replace('{dc}', dest).replace('{dep}', fdate(f.departure_at))
        .replace('{retpart}', f.return_at ? S.note_ret.replace('{ret}', fdate(f.return_at)) : '')
        .replace('{total}', fmt(f.price_egp_total)).replace('{pax}', pax).replace('{per}', fmt(f.price_egp_per_person));
      html += '<div class="fcard"><div class="fmain"><div class="fair">' + esc(an) + (f.flight_number ? ' · ' + esc(f.flight_number) : '') + '</div>' +
        leg(S.dep, oname, f.origin_airport || origin, dname, f.destination_airport || dest, f.departure_at, f.duration_min, f.transfers) +
        (f.return_at ? leg(S.ret, dname, f.destination_airport || dest, oname, f.origin_airport || origin, f.return_at, f.duration_back_min, f.return_transfers) : '') +
        '<div class="fmeta" style="margin-top:8px">🧳 ' + esc(S.bag) + '</div>' +
        '</div><div class="fprice"><div><span class="amt">' + fmt(f.price_egp_total) + '</span> <span class="cur">EGP</span></div>' +
        '<div class="fmeta">' + esc(S.total) + ' · ' + fmt(f.price_egp_per_person) + ' ' + esc(S.per) + '</div>' +
        '<p style="margin-top:10px"><a class="cta-btn" href="' + reqLink(note) + '">' + esc(S.book) + '</a></p>' +
        '<p style="margin-top:8px"><a class="btn-gold" target="_blank" rel="noopener" href="' + kiwiLink(f.departure_at, f.return_at) + '">' + esc(S.kiwi) + '</a></p></div></div>';
    });
    box.innerHTML = html + '<p class="fdisc">' + esc(S.disc) + '</p>';
  }).catch(function(){ fallback(S.err_h, S.err_p); });
})();
</script>
"""

def _body(lang):
    s = STR[lang]
    al = {k: list(v) for k, v in AIRLINES.items()}
    script = SCRIPT.replace('__STRINGS__', json.dumps(s, ensure_ascii=False)).replace('__AIRLINES__', json.dumps(al, ensure_ascii=False))
    h1 = 'نتائج بحث الطيران' if lang == 'ar' else 'Flight Search Results'
    return f"""
<section style="padding-top:44px"><div class="wrap">
<h1 style="font-size:34px;color:var(--ink);line-height:1.5">{h1}</h1>
<p class="lead" id="fsum" style="margin-top:6px"></p>
<div id="fstatus" class="fspin">{s['loading']}</div>
<div id="fresults"></div>
</div></section>
""" + script

def main():
    PREV.main()
    _write('flight-results.html', V3.layout3('نتائج بحث الطيران', 'أرخص أسعار الطيران بالجنيه المصري — أسعار استرشادية وسعر نهائي مؤكد عند الحجز مع يونس ترافيل.', '/flight-results.html', _body('ar'), extra_head=STYLE))
    _write('en/flight-results.html', V3.layout3('Flight Search Results', 'Cheapest flight prices in Egyptian Pounds — indicative fares, final price confirmed on booking with Younis Travel.', '/en/flight-results.html', _body('en'), lang='en', extra_head=STYLE))
    sm_path = os.path.join(OUT, 'sitemap.xml')
    sm = open(sm_path, encoding='utf-8').read()
    if '/flight-results.html' not in sm:
        add = ('<url><loc>' + BASE + '/flight-results.html</loc><lastmod>2026-11-17</lastmod></url>'
               '<url><loc>' + BASE + '/en/flight-results.html</loc><lastmod>2026-11-17</lastmod></url>')
        sm = sm.replace('</urlset>', add + '</urlset>')
        _write('sitemap.xml', sm)
    print('built flight search pages -> flight-results.html, en/flight-results.html (+ sitemap)')

if __name__ == '__main__':
    main()
