"""Younis Travel — v3.5 REAL BOOKING SYSTEM (Amged chose option A, 2026-11-12).
Upgrades the request page into a structured booking flow backed by Vercel
serverless functions + Upstash Redis: booking reference, status tracking page,
admin dashboard. Adds the now-real API layer artifacts: OpenAPI spec, RFC 9727
API catalog, MCP server + server card. Runs the v3.4 build first, then overlays.
API sources live in api_src/ and are copied into site_v3/api/."""
import os, sys, json, hashlib, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as B
import build_site_v3 as V3
import build_site_v34 as V34

OUT = V3.OUT
BASE = B.BASE
FB = B.FB_PAGE
STYLE = """<style>
.sbar{display:flex;gap:6px;margin:18px 0}
.sbar div{flex:1;text-align:center;padding:9px 4px;border-radius:10px;background:#efe9dc;color:#7a6a45;font-weight:700;font-size:.86rem}
.sbar div.on{background:#0f2b46;color:#fff}
.bstep{display:none}.bstep.on{display:block}
.refbig{font-size:2rem;font-weight:800;letter-spacing:2px;color:#0f2b46;text-align:center;margin:8px 0}
.tl{display:flex;gap:0;margin:16px 0}
.tl div{flex:1;text-align:center;font-size:.8rem;color:#999;padding-top:16px;position:relative}
.tl div:before{content:'';position:absolute;top:4px;inset-inline-start:calc(50% - 7px);width:14px;height:14px;border-radius:50%;background:#ddd}
.tl div.done{color:#0f2b46;font-weight:700}.tl div.done:before{background:#c9a24d}
.msg{display:none;border-radius:10px;padding:12px 14px;margin:12px 0;font-size:.95rem}
.msg.err{display:block;background:#fdecec;color:#8c1d1d}
.msg.ok{display:block;background:#e9f7ee;color:#14532d}
.kv{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;margin:10px 0}
.kv dt{color:#777}.kv dd{margin:0;font-weight:600}
.abk{border:1px solid #e5ddc9;border-radius:12px;padding:14px;margin:10px 0;background:#fff}
.abk select,.abk input{padding:8px;border:1px solid #d8d2c2;border-radius:8px}
</style>"""

BOOK_AR = """<section class="page-hero"><div class="wrap"><h1>احجز طلبك</h1><p>٣ خطوات بسيطة ويبقى عندك رقم حجز تتابع بيه حالة طلبك لحظة بلحظة. الفريق بيراجع الحجز ويتواصل معاك بالسعر النهائي وخطوات التنفيذ.</p></div></section>
<section class="section"><div class="wrap"><div class="card">
<div class="sbar"><div id="sb1" class="on">١ · الخدمة والتفاصيل</div><div id="sb2">٢ · بياناتك</div><div id="sb3">٣ · المراجعة والتأكيد</div></div>
<div class="bstep on" id="st1">
<div class="field-grid">
<div class="fg"><label for="service">الخدمة</label><select id="service"><option value="visa">تأشيرة</option><option value="flight">طيران</option><option value="hotel">فندق</option><option value="trip">رحلة سياحية</option><option value="insurance">تأمين سفر</option></select></div>
<div class="fg"><label for="dest">الوجهة</label><input id="dest" placeholder="مثال: السعودية، دبي، تركيا..."></div>
<div class="fg"><label for="dates">التواريخ والمدة</label><input id="dates" placeholder="مثال: أول ديسمبر، 5 أيام"></div>
<div class="fg"><label for="people">عدد المسافرين</label><input id="people" type="number" min="1" max="50" value="1"></div>
</div>
<div class="msg err" id="e1"></div>
<button class="btn btn-gold" onclick="goStep(2)">التالي ←</button>
</div>
<div class="bstep" id="st2">
<div class="field-grid">
<div class="fg"><label for="name">الاسم بالكامل</label><input id="name" placeholder="اسمك الكريم"></div>
<div class="fg"><label for="phone">رقم الموبايل (واتساب)</label><input id="phone" inputmode="tel" placeholder="01xxxxxxxxx"></div>
</div>
<div class="fg"><label for="notes">ملاحظات للفريق</label><textarea id="notes" rows="3" placeholder="منطقة أو فئة الفندق، مواعيد مفضلة، غرض التأشيرة..."></textarea></div>
<p style="color:#777;font-size:.9rem">بياناتك بتستخدم لتنفيذ الحجز والتواصل معاك بس، ومش بتتشارك مع أي طرف تاني.</p>
<div class="msg err" id="e2"></div>
<button class="btn" onclick="goStep(1)">→ رجوع</button> <button class="btn btn-gold" onclick="goStep(3)">مراجعة الحجز ←</button>
</div>
<div class="bstep" id="st3">
<h3 style="margin-top:0">راجع بيانات حجزك</h3>
<dl class="kv" id="review"></dl>
<div class="msg err" id="e3"></div>
<button class="btn" onclick="goStep(2)">→ تعديل</button> <button class="btn btn-gold" id="confirmBtn" onclick="submitBooking()">تأكيد الحجز ✓</button>
</div>
<div class="bstep" id="stDone">
<div class="msg ok" style="display:block">تم استلام حجزك بنجاح ✅</div>
<p style="text-align:center">رقم الحجز بتاعك — احفظه عندك:</p>
<div class="refbig" id="refOut"></div>
<p style="text-align:center">الحالة دلوقتي: <strong>جديد</strong> — الفريق هيراجع الحجز ويتواصل معاك على رقمك بالسعر النهائي والخطوات.</p>
<div style="text-align:center;display:flex;gap:8px;justify-content:center;flex-wrap:wrap">
<a class="btn btn-gold" id="trackLink" href="/track.html">تابع حالة حجزك</a>
<button class="btn" onclick="copySummary()">انسخ ملخص الحجز</button>
<a class="btn" href="https://m.me/61596173995345" target="_blank" rel="noopener">ابعت نسخة على فيسبوك</a>
</div>
</div>
<div class="bstep" id="stFallback">
<div class="msg err" style="display:block">نظام الحجز الأونلاين بيتم تفعيله دلوقتي — طلبك مش هيضيع: ابعته للفريق على فيسبوك وهيتسجل بنفس الطريقة.</div>
<dl class="kv" id="review2"></dl>
<a class="btn btn-gold" href="__FB__" target="_blank" rel="noopener">ابعت الطلب على فيسبوك</a>
</div>
</div></div></section>
<script>
var SVC={visa:'تأشيرة',flight:'طيران',hotel:'فندق',trip:'رحلة سياحية',insurance:'تأمين سفر'};
var q=new URLSearchParams(location.search);
if(q.get('s'))document.getElementById('service').value=q.get('s');
if(q.get('d'))document.getElementById('dest').value=q.get('d');
function val(id){return document.getElementById(id).value.trim();}
function showErr(id,txt){var e=document.getElementById(id);if(txt){e.textContent=txt;e.style.display='block';}else{e.style.display='none';}}
function goStep(n){
  if(n===2){ if(!val('dest')){showErr('e1','من فضلك اكتب الوجهة');return;} showErr('e1',''); }
  if(n===3){ if(val('name').length<3){showErr('e2','من فضلك اكتب الاسم بالكامل');return;}
    var ph=val('phone').replace(/[\\s-]/g,''); if(ph.replace(/\\D/g,'').length<9){showErr('e2','من فضلك اكتب رقم موبايل صحيح — الفريق هيتواصل معاك عليه');return;} showErr('e2',''); fillReview(); }
  [1,2,3].forEach(function(i){document.getElementById('st'+i).classList.toggle('on',i===n);document.getElementById('sb'+i).classList.toggle('on',i===n);});
  window.scrollTo({top:0,behavior:'smooth'});
}
function bookingData(){return {service:val('service'),destination:val('dest'),dates:val('dates'),people:parseInt(val('people')||'1',10),name:val('name'),phone:val('phone'),notes:val('notes')};}
function summaryText(b,ref){return 'حجز يونس ترافيل'+(ref?' — رقم الحجز: '+ref:'')+'\\nالخدمة: '+SVC[b.service]+'\\nالوجهة: '+b.destination+'\\nالتواريخ: '+(b.dates||'—')+'\\nعدد المسافرين: '+b.people+'\\nالاسم: '+b.name+'\\nالموبايل: '+b.phone+(b.notes?'\\nملاحظات: '+b.notes:'');}
function fillReview(){var b=bookingData();document.getElementById('review').innerHTML='<dt>الخدمة</dt><dd>'+SVC[b.service]+'</dd><dt>الوجهة</dt><dd>'+b.destination+'</dd><dt>التواريخ</dt><dd>'+(b.dates||'—')+'</dd><dt>المسافرون</dt><dd>'+b.people+'</dd><dt>الاسم</dt><dd>'+b.name+'</dd><dt>الموبايل</dt><dd>'+b.phone+'</dd>'+(b.notes?'<dt>ملاحظات</dt><dd>'+b.notes+'</dd>':'');}
var lastRef='';
function submitBooking(){
  var b=bookingData();var btn=document.getElementById('confirmBtn');btn.disabled=true;btn.textContent='جاري تسجيل الحجز...';
  fetch('/api/bookings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)})
  .then(function(r){return r.json().then(function(j){return {s:r.status,j:j};});})
  .then(function(x){
    if(x.s===201){ lastRef=x.j.ref; document.getElementById('refOut').textContent=x.j.ref;
      document.getElementById('trackLink').href='/track.html?ref='+x.j.ref;
      [1,2,3].forEach(function(i){document.getElementById('st'+i).classList.remove('on');});
      document.getElementById('stDone').classList.add('on'); window.scrollTo({top:0,behavior:'smooth'});
    } else { fallback(b); }
  }).catch(function(){ fallback(b); });
}
function fallback(b){ [1,2,3].forEach(function(i){document.getElementById('st'+i).classList.remove('on');});
  document.getElementById('review2').innerHTML=document.getElementById('review').innerHTML;
  document.getElementById('stFallback').classList.add('on'); window.scrollTo({top:0,behavior:'smooth'}); }
function copySummary(){ if(lastRef&&navigator.clipboard){navigator.clipboard.writeText(summaryText(bookingData(),lastRef)); alert('اتنسخ ملخص الحجز ✓');} }
</script>"""

TRACK_AR = """<section class="page-hero"><div class="wrap"><h1>تابع حالة حجزك</h1><p>اكتب رقم الحجز اللي جالك وقت التأكيد ورقم الموبايل اللي حجزت بيه.</p></div></section>
<section class="section"><div class="wrap"><div class="card">
<div class="field-grid">
<div class="fg"><label for="ref">رقم الحجز</label><input id="ref" placeholder="YT-XXXXXX" style="text-transform:uppercase"></div>
<div class="fg"><label for="phone">رقم الموبايل</label><input id="phone" inputmode="tel" placeholder="01xxxxxxxxx"></div>
</div>
<div class="msg err" id="terr"></div>
<button class="btn btn-gold" onclick="doTrack()">شوف الحالة</button>
<div id="tres" style="display:none">
<div class="tl" id="ttl"><div data-s="NEW">تم الاستلام</div><div data-s="CONTACTED">تم التواصل</div><div data-s="CONFIRMED">الحجز مؤكد</div><div data-s="COMPLETED">مكتمل</div></div>
<dl class="kv" id="tdet"></dl>
<p id="tnext" style="font-weight:600"></p>
</div>
</div></div></section>
<script>
var SVC={visa:'تأشيرة',flight:'طيران',hotel:'فندق',trip:'رحلة سياحية',insurance:'تأمين سفر'};
var NEXT={NEW:'طلبك وصل والفريق هيراجعه ويتواصل معاك في أقرب وقت.',CONTACTED:'الفريق تواصل معاك (أو بيحاول يوصلك) — راجع موبايلك وواتساب.',CONFIRMED:'حجزك مؤكد — الفريق بيجهز التنفيذ وهيبعتلك التفاصيل النهائية.',COMPLETED:'الحجز اكتمل — سفر سعيد! لو احتجت أي حاجة إحنا موجودين.',CANCELLED:'الحجز ده ملغي. لو ده مش بطلبك، كلمنا على صفحة فيسبوك.'};
var q=new URLSearchParams(location.search); if(q.get('ref'))document.getElementById('ref').value=q.get('ref');
function doTrack(){
  var ref=document.getElementById('ref').value.trim(), ph=document.getElementById('phone').value.trim();
  var e=document.getElementById('terr');
  if(!ref||!ph){e.textContent='اكتب رقم الحجز والموبايل';e.style.display='block';return;}
  e.style.display='none';
  fetch('/api/track?ref='+encodeURIComponent(ref)+'&phone='+encodeURIComponent(ph))
  .then(function(r){return r.json().then(function(j){return {s:r.status,j:j};});})
  .then(function(x){
    if(x.s!==200){e.textContent='ملقيناش حجز بالبيانات دي — اتأكد من رقم الحجز والموبايل اللي حجزت بيه';e.style.display='block';document.getElementById('tres').style.display='none';return;}
    var b=x.j.booking; var order=['NEW','CONTACTED','CONFIRMED','COMPLETED']; var idx=order.indexOf(b.status);
    document.querySelectorAll('#ttl div').forEach(function(d,i){d.classList.toggle('done', idx>=i && b.status!=='CANCELLED');});
    document.getElementById('tdet').innerHTML='<dt>رقم الحجز</dt><dd>'+b.ref+'</dd><dt>الخدمة</dt><dd>'+SVC[b.service]+'</dd><dt>الوجهة</dt><dd>'+b.destination+'</dd><dt>التواريخ</dt><dd>'+(b.dates||'—')+'</dd><dt>المسافرون</dt><dd>'+b.people+'</dd><dt>تاريخ الحجز</dt><dd>'+b.created_at.slice(0,10)+'</dd><dt>آخر تحديث</dt><dd>'+b.updated_at.slice(0,10)+'</dd>';
    document.getElementById('tnext').textContent=NEXT[b.status]||'';
    document.getElementById('tres').style.display='block';
  }).catch(function(){e.textContent='حصلت مشكلة في الاتصال — حاول تاني';e.style.display='block';});
}
</script>"""

ADMIN_AR = """<section class="page-hero"><div class="wrap"><h1>لوحة إدارة الحجوزات</h1><p>خاصة بفريق يونس ترافيل.</p></div></section>
<section class="section"><div class="wrap">
<div class="card" id="gate"><div class="fg"><label for="tok">رمز الإدارة</label><input id="tok" type="password" placeholder="ADMIN TOKEN"></div>
<button class="btn btn-gold" onclick="unlock()">دخول</button><div class="msg err" id="gerr"></div></div>
<div id="panel" style="display:none">
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
<select id="fstatus" onchange="render()"><option value="">كل الحالات</option><option>NEW</option><option>CONTACTED</option><option>CONFIRMED</option><option>COMPLETED</option><option>CANCELLED</option></select>
<button class="btn" onclick="load()">تحديث ↻</button>
<span id="count" style="align-self:center;font-weight:700"></span>
</div>
<div id="list"></div>
</div>
</div></section>
<script>
var SVC={visa:'تأشيرة',flight:'طيران',hotel:'فندق',trip:'رحلة',insurance:'تأمين'};
var STL={NEW:'جديد',CONTACTED:'تم التواصل',CONFIRMED:'مؤكد',COMPLETED:'مكتمل',CANCELLED:'ملغي'};
var TOK=sessionStorage.getItem('yt_admin')||''; var DATA=[];
function tok(){return document.getElementById('tok').value.trim()||TOK;}
function unlock(){TOK=tok();sessionStorage.setItem('yt_admin',TOK);load();}
function api(method,body){var o={method:method,headers:{'x-admin-token':TOK,'Content-Type':'application/json'}};if(body)o.body=JSON.stringify(body);return fetch('/api/bookings',o).then(function(r){return r.json().then(function(j){return {s:r.status,j:j};});});}
function load(){ api('GET').then(function(x){ if(x.s!==200){document.getElementById('gerr').textContent='الرمز غير صحيح أو النظام غير مفعّل';document.getElementById('gerr').style.display='block';return;}
  document.getElementById('gate').style.display='none';document.getElementById('panel').style.display='block'; DATA=x.j.bookings; render(); }); }
function render(){ var f=document.getElementById('fstatus').value; var rows=DATA.filter(function(b){return !f||b.status===f;});
  document.getElementById('count').textContent=rows.length+' حجز';
  document.getElementById('list').innerHTML=rows.map(function(b){return '<div class="abk"><strong>'+b.ref+'</strong> · '+SVC[b.service]+' · '+b.destination+' · '+(b.dates||'—')+' · '+b.people+' مسافر<br>'+b.name+' — '+b.phone+(b.notes?'<br>ملاحظات العميل: '+b.notes:'')+'<br><span style="color:#777">'+b.created_at.slice(0,16).replace('T',' ')+'</span><br>'+
  '<select id="st-'+b.ref+'">'+['NEW','CONTACTED','CONFIRMED','COMPLETED','CANCELLED'].map(function(s){return '<option value="'+s+'"'+(b.status===s?' selected':'')+'>'+STL[s]+'</option>';}).join('')+'</select> '+
  '<input id="nt-'+b.ref+'" placeholder="ملاحظة داخلية" value="'+(b.admin_notes||'').replace(/"/g,'&quot;')+'" style="min-width:220px"> '+
  '<button class="btn" onclick="save(\''+b.ref+'\')">حفظ</button> <button class="btn" onclick="del(\''+b.ref+'\')">حذف</button></div>';}).join('')||'<p>لا توجد حجوزات مطابقة.</p>'; }
function save(ref){ api('PATCH',{ref:ref,status:document.getElementById('st-'+ref).value,admin_notes:document.getElementById('nt-'+ref).value}).then(function(x){ if(x.s===200){alert('اتحفظ ✓');load();} else alert('حصلت مشكلة'); }); }
function del(ref){ if(confirm('حذف الحجز '+ref+' نهائيًا؟')){ fetch('/api/bookings?ref='+ref,{method:'DELETE',headers:{'x-admin-token':TOK}}).then(function(){load();}); } }
if(TOK){document.getElementById('tok').value=TOK;load();}
</script>"""

BOOK_EN = """<section class="page-hero"><div class="wrap"><h1>Book your request</h1><p>Three simple steps and you get a booking reference to track your request. The team reviews every booking and contacts you with the final price and next steps.</p></div></section>
<section class="section"><div class="wrap"><div class="card">
<div class="sbar"><div id="sb1" class="on">1 · Service & details</div><div id="sb2">2 · Your details</div><div id="sb3">3 · Review & confirm</div></div>
<div class="bstep on" id="st1">
<div class="field-grid">
<div class="fg"><label for="service">Service</label><select id="service"><option value="visa">Visa</option><option value="flight">Flight</option><option value="hotel">Hotel</option><option value="trip">Trip</option><option value="insurance">Travel insurance</option></select></div>
<div class="fg"><label for="dest">Destination</label><input id="dest" placeholder="e.g. Saudi Arabia, Dubai, Turkey..."></div>
<div class="fg"><label for="dates">Dates & duration</label><input id="dates" placeholder="e.g. early December, 5 days"></div>
<div class="fg"><label for="people">Travellers</label><input id="people" type="number" min="1" max="50" value="1"></div>
</div>
<div class="msg err" id="e1"></div>
<button class="btn btn-gold" onclick="goStep(2)">Next →</button>
</div>
<div class="bstep" id="st2">
<div class="field-grid">
<div class="fg"><label for="name">Full name</label><input id="name" placeholder="Your full name"></div>
<div class="fg"><label for="phone">Mobile (WhatsApp)</label><input id="phone" inputmode="tel" placeholder="+20 1x xxxx xxxx"></div>
</div>
<div class="fg"><label for="notes">Notes for the team</label><textarea id="notes" rows="3" placeholder="Hotel area or class, preferred times, visa purpose..."></textarea></div>
<p style="color:#777;font-size:.9rem">Your details are used only to process the booking and contact you; they are never shared.</p>
<div class="msg err" id="e2"></div>
<button class="btn" onclick="goStep(1)">← Back</button> <button class="btn btn-gold" onclick="goStep(3)">Review booking →</button>
</div>
<div class="bstep" id="st3">
<h3 style="margin-top:0">Review your booking</h3>
<dl class="kv" id="review"></dl>
<div class="msg err" id="e3"></div>
<button class="btn" onclick="goStep(2)">← Edit</button> <button class="btn btn-gold" id="confirmBtn" onclick="submitBooking()">Confirm booking ✓</button>
</div>
<div class="bstep" id="stDone">
<div class="msg ok" style="display:block">Booking received ✅</div>
<p style="text-align:center">Your booking reference — keep it safe:</p>
<div class="refbig" id="refOut"></div>
<p style="text-align:center">Status now: <strong>New</strong> — the team will review it and contact you on your number with the final price and steps.</p>
<div style="text-align:center;display:flex;gap:8px;justify-content:center;flex-wrap:wrap">
<a class="btn btn-gold" id="trackLink" href="/en/track.html">Track your booking</a>
<button class="btn" onclick="copySummary()">Copy booking summary</button>
<a class="btn" href="https://m.me/61596173995345" target="_blank" rel="noopener">Send a copy on Facebook</a>
</div>
</div>
<div class="bstep" id="stFallback">
<div class="msg err" style="display:block">The online booking system is being activated right now — your request is not lost: send it to the team on Facebook and it will be registered the same way.</div>
<dl class="kv" id="review2"></dl>
<a class="btn btn-gold" href="__FB__" target="_blank" rel="noopener">Send the request on Facebook</a>
</div>
</div></div></section>
<script>
var SVC={visa:'Visa',flight:'Flight',hotel:'Hotel',trip:'Trip',insurance:'Travel insurance'};
var q=new URLSearchParams(location.search);
if(q.get('s'))document.getElementById('service').value=q.get('s');
if(q.get('d'))document.getElementById('dest').value=q.get('d');
function val(id){return document.getElementById(id).value.trim();}
function showErr(id,txt){var e=document.getElementById(id);if(txt){e.textContent=txt;e.style.display='block';}else{e.style.display='none';}}
function goStep(n){
  if(n===2){ if(!val('dest')){showErr('e1','Please enter the destination');return;} showErr('e1',''); }
  if(n===3){ if(val('name').length<3){showErr('e2','Please enter your full name');return;}
    var ph=val('phone').replace(/[\\s-]/g,''); if(ph.replace(/\\D/g,'').length<9){showErr('e2','Please enter a valid mobile number — the team will contact you on it');return;} showErr('e2',''); fillReview(); }
  [1,2,3].forEach(function(i){document.getElementById('st'+i).classList.toggle('on',i===n);document.getElementById('sb'+i).classList.toggle('on',i===n);});
  window.scrollTo({top:0,behavior:'smooth'});
}
function bookingData(){return {service:val('service'),destination:val('dest'),dates:val('dates'),people:parseInt(val('people')||'1',10),name:val('name'),phone:val('phone'),notes:val('notes')};}
function summaryText(b,ref){return 'Younis Travel booking'+(ref?' — reference: '+ref:'')+'\\nService: '+SVC[b.service]+'\\nDestination: '+b.destination+'\\nDates: '+(b.dates||'—')+'\\nTravellers: '+b.people+'\\nName: '+b.name+'\\nMobile: '+b.phone+(b.notes?'\\nNotes: '+b.notes:'');}
function fillReview(){var b=bookingData();document.getElementById('review').innerHTML='<dt>Service</dt><dd>'+SVC[b.service]+'</dd><dt>Destination</dt><dd>'+b.destination+'</dd><dt>Dates</dt><dd>'+(b.dates||'—')+'</dd><dt>Travellers</dt><dd>'+b.people+'</dd><dt>Name</dt><dd>'+b.name+'</dd><dt>Mobile</dt><dd>'+b.phone+'</dd>'+(b.notes?'<dt>Notes</dt><dd>'+b.notes+'</dd>':'');}
var lastRef='';
function submitBooking(){
  var b=bookingData();var btn=document.getElementById('confirmBtn');btn.disabled=true;btn.textContent='Saving your booking...';
  fetch('/api/bookings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)})
  .then(function(r){return r.json().then(function(j){return {s:r.status,j:j};});})
  .then(function(x){
    if(x.s===201){ lastRef=x.j.ref; document.getElementById('refOut').textContent=x.j.ref;
      document.getElementById('trackLink').href='/en/track.html?ref='+x.j.ref;
      [1,2,3].forEach(function(i){document.getElementById('st'+i).classList.remove('on');});
      document.getElementById('stDone').classList.add('on'); window.scrollTo({top:0,behavior:'smooth'});
    } else { fallback(b); }
  }).catch(function(){ fallback(b); });
}
function fallback(b){ [1,2,3].forEach(function(i){document.getElementById('st'+i).classList.remove('on');});
  document.getElementById('review2').innerHTML=document.getElementById('review').innerHTML;
  document.getElementById('stFallback').classList.add('on'); window.scrollTo({top:0,behavior:'smooth'}); }
function copySummary(){ if(lastRef&&navigator.clipboard){navigator.clipboard.writeText(summaryText(bookingData(),lastRef)); alert('Booking summary copied ✓');} }
</script>"""

TRACK_EN = """<section class="page-hero"><div class="wrap"><h1>Track your booking</h1><p>Enter the booking reference you received at confirmation and the mobile number you booked with.</p></div></section>
<section class="section"><div class="wrap"><div class="card">
<div class="field-grid">
<div class="fg"><label for="ref">Booking reference</label><input id="ref" placeholder="YT-XXXXXX" style="text-transform:uppercase"></div>
<div class="fg"><label for="phone">Mobile number</label><input id="phone" inputmode="tel" placeholder="+20 1x xxxx xxxx"></div>
</div>
<div class="msg err" id="terr"></div>
<button class="btn btn-gold" onclick="doTrack()">Check status</button>
<div id="tres" style="display:none">
<div class="tl" id="ttl"><div data-s="NEW">Received</div><div data-s="CONTACTED">Contacted</div><div data-s="CONFIRMED">Confirmed</div><div data-s="COMPLETED">Completed</div></div>
<dl class="kv" id="tdet"></dl>
<p id="tnext" style="font-weight:600"></p>
</div>
</div></div></section>
<script>
var SVC={visa:'Visa',flight:'Flight',hotel:'Hotel',trip:'Trip',insurance:'Travel insurance'};
var NEXT={NEW:'Your request arrived; the team will review it and contact you shortly.',CONTACTED:'The team has contacted you (or is trying to reach you) — check your phone and WhatsApp.',CONFIRMED:'Your booking is confirmed — the team is preparing execution and will send the final details.',COMPLETED:'Booking completed — safe travels! We are here if you need anything.',CANCELLED:'This booking is cancelled. If that was not at your request, message us on the Facebook Page.'};
var q=new URLSearchParams(location.search); if(q.get('ref'))document.getElementById('ref').value=q.get('ref');
function doTrack(){
  var ref=document.getElementById('ref').value.trim(), ph=document.getElementById('phone').value.trim();
  var e=document.getElementById('terr');
  if(!ref||!ph){e.textContent='Enter the reference and mobile number';e.style.display='block';return;}
  e.style.display='none';
  fetch('/api/track?ref='+encodeURIComponent(ref)+'&phone='+encodeURIComponent(ph))
  .then(function(r){return r.json().then(function(j){return {s:r.status,j:j};});})
  .then(function(x){
    if(x.s!==200){e.textContent='No booking matches those details — check the reference and the mobile you booked with';e.style.display='block';document.getElementById('tres').style.display='none';return;}
    var b=x.j.booking; var order=['NEW','CONTACTED','CONFIRMED','COMPLETED']; var idx=order.indexOf(b.status);
    document.querySelectorAll('#ttl div').forEach(function(d,i){d.classList.toggle('done', idx>=i && b.status!=='CANCELLED');});
    document.getElementById('tdet').innerHTML='<dt>Reference</dt><dd>'+b.ref+'</dd><dt>Service</dt><dd>'+SVC[b.service]+'</dd><dt>Destination</dt><dd>'+b.destination+'</dd><dt>Dates</dt><dd>'+(b.dates||'—')+'</dd><dt>Travellers</dt><dd>'+b.people+'</dd><dt>Booked on</dt><dd>'+b.created_at.slice(0,10)+'</dd><dt>Last update</dt><dd>'+b.updated_at.slice(0,10)+'</dd>';
    document.getElementById('tnext').textContent=NEXT[b.status]||'';
    document.getElementById('tres').style.display='block';
  }).catch(function(){e.textContent='Connection problem — please try again';e.style.display='block';});
}
</script>"""

SKILL_REQUEST_V2 = """---
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
"""

MCP_CARD = {
    "serverInfo": {"name": "younis-travel", "version": "1.0.0"},
    "transport": {"type": "streamable-http", "endpoint": "https://younistravel.site/api/mcp"},
    "capabilities": {"tools": True, "resources": False, "prompts": False},
    "description": "Younis Travel booking tools for AI agents: list services, create real booking requests, and track booking status. Bookings are reviewed by the human team; no prices are published.",
    "tools": ["younis_travel_services", "create_booking", "track_booking"],
}

API_CATALOG = {"linkset": [{
    "anchor": "https://younistravel.site/api",
    "service-desc": [{"href": "https://younistravel.site/api/openapi", "type": "application/vnd.oai.openapi+json"}],
    "service-doc": [{"href": "https://younistravel.site/llms-full.txt", "type": "text/plain"}],
    "status": [{"href": "https://younistravel.site/api/health", "type": "application/json"}],
}]}

def _write(rel, content):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(content)

def main():
    V34.main()

    # --- API functions + package marker
    api_out = os.path.join(OUT, 'api')
    os.makedirs(api_out, exist_ok=True)
    for fn in ('_lib.js', 'bookings.js', 'track.js', 'health.js', 'openapi.js', 'mcp.js'):
        shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_src', fn),
                    os.path.join(api_out, fn))
    _write('package.json', json.dumps({"name": "younistravel-site", "private": True}, indent=2))

    # --- booking / track / admin pages (full chrome via the current layout)
    _write('request.html', V3.layout3('احجز طلبك', 'احجز تأشيرتك أو رحلتك أو فندقك في ٣ خطوات واحصل على رقم حجز لمتابعة حالة طلبك.', '/request.html',
                                      BOOK_AR.replace('__FB__', FB), extra_head=STYLE))
    _write('en/request.html', V3.layout3('Book your request', 'Book your visa, flight or hotel in three steps and get a booking reference to track your request.', '/en/request.html',
                                         BOOK_EN.replace('__FB__', FB), lang='en', extra_head=STYLE))
    _write('track.html', V3.layout3('تابع حالة حجزك', 'تابع حالة حجزك في يونس ترافيل برقم الحجز ورقم الموبايل.', '/track.html', TRACK_AR, extra_head=STYLE))
    _write('en/track.html', V3.layout3('Track your booking', 'Track your Younis Travel booking status with your reference and mobile number.', '/en/track.html', TRACK_EN, lang='en', extra_head=STYLE))
    _write('admin.html', V3.layout3('لوحة إدارة الحجوزات', 'لوحة إدارة حجوزات يونس ترافيل — للفريق فقط.', '/admin.html',
                                    ADMIN_AR, extra_head=STYLE + '<meta name="robots" content="noindex,nofollow">'))
    # refresh the request pages' markdown copies from the new HTML
    for rel in ('request.html', 'en/request.html', 'track.html', 'en/track.html'):
        with open(os.path.join(OUT, rel), encoding='utf-8') as fh:
            page = fh.read()
        md = V34.html_to_md(page, BASE + '/' + rel)
        _write('md/' + rel[:-5] + '.md', md)

    # --- API discovery artifacts (now backed by a real API)
    wk = os.path.join(OUT, '.well-known')
    with open(os.path.join(wk, 'api-catalog'), 'w', encoding='utf-8') as fh:
        json.dump(API_CATALOG, fh, indent=2)
    os.makedirs(os.path.join(wk, 'mcp'), exist_ok=True)
    with open(os.path.join(wk, 'mcp', 'server-card.json'), 'w', encoding='utf-8') as fh:
        json.dump(MCP_CARD, fh, ensure_ascii=False, indent=2)

    # --- update the booking skill to the real flow + refresh index digests
    sk = os.path.join(OUT, 'skills', 'prepare-booking-request', 'SKILL.md')
    with open(sk, 'wb') as fh:
        fh.write(SKILL_REQUEST_V2.encode('utf-8'))
    idx_path = os.path.join(wk, 'agent-skills', 'index.json')
    idx = json.load(open(idx_path))
    for s in idx['skills']:
        p = os.path.join(OUT, 'skills', s['name'], 'SKILL.md')
        s['digest'] = 'sha256:' + hashlib.sha256(open(p, 'rb').read()).hexdigest()
        if s['name'] == 'prepare-booking-request':
            s['description'] = 'How an agent creates and tracks a real Younis Travel booking: the booking API and MCP tools, booking references, and status tracking.'
    with open(idx_path, 'w', encoding='utf-8') as fh:
        json.dump(idx, fh, ensure_ascii=False, indent=2)

    # --- ARD: add the booking API entry
    ard_path = os.path.join(wk, 'ai-catalog.json')
    ard = json.load(open(ard_path))
    ard['entries'].append({"identifier": "urn:air:younistravel.site:api:bookings",
                           "displayName": "Younis Travel Booking API (OpenAPI)",
                           "type": "application/vnd.oai.openapi+json", "url": BASE + "/api/openapi",
                           "representativeQueries": ["create a booking with Younis Travel via API",
                                                     "track a Younis Travel booking"]})
    with open(ard_path, 'w', encoding='utf-8') as fh:
        json.dump(ard, fh, ensure_ascii=False, indent=2)

    # --- llms files: describe the booking system
    for f in ('llms.txt', 'llms-full.txt'):
        p = os.path.join(OUT, f)
        txt = open(p, encoding='utf-8').read()
        txt += ('\n## Booking system\n\nTravellers book on the site and receive a booking reference '
                '(e.g. YT-AB12CD): book at ' + BASE + '/request.html (English: ' + BASE + '/en/request.html), '
                'track status at ' + BASE + '/track.html with the reference and the booking phone number. '
                'Agents may use the Booking API (OpenAPI: ' + BASE + '/api/openapi) or the MCP server at '
                + BASE + '/api/mcp. The team reviews every booking and replies with exact prices — no prices are published and no payment is taken online.\n')
        with open(p, 'w', encoding='utf-8') as fh:
            fh.write(txt)

    # --- vercel.json: API catalog headers + Link header gains the api-catalog relation
    vj_path = os.path.join(OUT, 'vercel.json')
    vj = json.load(open(vj_path))
    for rule in vj['headers']:
        if rule['source'] == '/(.*)':
            for h in rule['headers']:
                if h['key'] == 'Link':
                    h['value'] += f', <{BASE}/.well-known/api-catalog>; rel="api-catalog"; type="application/linkset+json"'
    vj['headers'].append({'source': '/.well-known/api-catalog', 'headers': [
        {'key': 'Content-Type', 'value': 'application/linkset+json'},
        {'key': 'Access-Control-Allow-Origin', 'value': '*'}]})
    vj['headers'].append({'source': '/admin.html', 'headers': [
        {'key': 'X-Robots-Tag', 'value': 'noindex, nofollow'}]})
    for rel in ('track.html', 'en/track.html'):
        with open(os.path.join(OUT, 'md', rel[:-5] + '.md'), encoding='utf-8') as fh:
            toks = str(max(1, len(fh.read().split())))
        vj['headers'].append({'source': '/md/' + rel[:-5] + '.md', 'headers': [
            {'key': 'Content-Type', 'value': 'text/markdown; charset=utf-8'},
            {'key': 'x-markdown-tokens', 'value': toks}]})
    with open(vj_path, 'w', encoding='utf-8') as fh:
        json.dump(vj, fh, indent=2)
    print('built v3.5 ->', OUT, '| api functions copied, booking/track/admin pages written')

if __name__ == '__main__':
    main()
