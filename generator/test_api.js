// Local end-to-end test of the booking API handlers with the in-memory driver.
process.env.YT_ALLOW_MOCK = '1';
process.env.ADMIN_TOKEN = 'test-admin-token';
const A = '/home/hatch/workspace/younis-website/generator/api_src/';
const bookings = require(A + 'bookings.js');
const track = require(A + 'track.js');
const health = require(A + 'health.js');
const mcp = require(A + 'mcp.js');

function call(handler, { method = 'GET', body = null, query = {}, headers = {} } = {}) {
  return new Promise((resolve) => {
    const req = { method, body, query, headers,
                  async *[Symbol.asyncIterator]() { if (body) yield Buffer.from(JSON.stringify(body)); } };
    const res = { statusCode: 200, headers: {},
                  setHeader(k, v) { this.headers[k] = v; },
                  end(data) { let json = null; try { json = JSON.parse(data); } catch {}
                              resolve({ status: this.statusCode, json, raw: data }); } };
    handler(req, res);
  });
}
let fails = 0;
function check(name, cond, extra = '') {
  console.log((cond ? 'PASS' : 'FAIL'), name, extra);
  if (!cond) fails++;
}
(async () => {
  let r = await call(health);
  check('health ok', r.status === 200 && r.json.storage === 'ok', JSON.stringify(r.json));

  r = await call(bookings, { method: 'POST', body: { service: 'visa', destination: 'تركيا', dates: 'أول ديسمبر، 5 أيام', people: 2, name: 'أحمد محمد', phone: '01001234567', notes: 'تأشيرة سياحية' } });
  check('create booking 201', r.status === 201 && /^YT-[A-Z0-9]{6}$/.test(r.json.ref || ''), JSON.stringify(r.json));
  const ref = r.json.ref;

  r = await call(bookings, { method: 'POST', body: { service: 'visa', destination: 'تركيا', name: 'أحمد', phone: '123' } });
  check('invalid phone 400', r.status === 400 && (r.json.fields || []).includes('phone'), JSON.stringify(r.json));

  r = await call(track, { query: { ref, phone: '01001234567' } });
  check('track ok NEW', r.status === 200 && r.json.booking.status === 'NEW', JSON.stringify(r.json));

  r = await call(track, { query: { ref, phone: '01099999999' } });
  check('track wrong phone 404', r.status === 404);

  r = await call(bookings, { method: 'GET' });
  check('admin list without token 401', r.status === 401);

  r = await call(bookings, { method: 'GET', headers: { 'x-admin-token': 'test-admin-token' } });
  check('admin list ok', r.status === 200 && r.json.bookings.length === 1 && r.json.bookings[0].ref === ref);

  r = await call(bookings, { method: 'PATCH', headers: { 'x-admin-token': 'test-admin-token' }, body: { ref, status: 'CONFIRMED', admin_notes: 'تم التواصل' } });
  check('patch status', r.status === 200 && r.json.booking.status === 'CONFIRMED');

  r = await call(track, { query: { ref, phone: '+20 100 123 4567' } });
  check('track phone formats + confirmed', r.status === 200 && r.json.booking.status === 'CONFIRMED');

  r = await call(mcp, { method: 'POST', body: { jsonrpc: '2.0', id: 1, method: 'tools/list' } });
  check('mcp tools/list', r.status === 200 && r.json.result.tools.length === 3);

  r = await call(mcp, { method: 'POST', body: { jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: 'create_booking', arguments: { service: 'flight', destination: 'Dubai', name: 'Sara Ali', phone: '01112223334' } } } });
  check('mcp create_booking', r.status === 200 && /YT-[A-Z0-9]{6}/.test(r.json.result.content[0].text), r.json.result.content[0].text.replace(/\n/g, ' ').slice(0, 120));

  r = await call(bookings, { method: 'DELETE', query: { ref }, headers: { 'x-admin-token': 'test-admin-token' } });
  check('admin delete', r.status === 200);
  r = await call(track, { query: { ref, phone: '01001234567' } });
  check('track after delete 404', r.status === 404);

  console.log(fails === 0 ? 'ALL PASS' : fails + ' FAILURES');
  process.exit(fails ? 1 : 0);
})();
