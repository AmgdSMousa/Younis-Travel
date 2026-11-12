// Security regression tests: stored-XSS sanitization, rate limiting, CORS policy.
process.env.YT_ALLOW_MOCK = '1';
process.env.ADMIN_TOKEN = 'test-admin-token';
const A = '/home/hatch/workspace/younis-website/generator/api_src/';
const bookings = require(A + 'bookings.js');

function call(handler, { method = 'GET', body = null, query = {}, headers = {} } = {}) {
  return new Promise((resolve) => {
    const req = { method, body, query, headers,
                  async *[Symbol.asyncIterator]() { if (body) yield Buffer.from(JSON.stringify(body)); } };
    const res = { statusCode: 200, headers: {},
                  setHeader(k, v) { this.headers[k.toLowerCase()] = v; },
                  end(data) { let json = null; try { json = JSON.parse(data); } catch {}
                              resolve({ status: this.statusCode, json, headers: this.headers }); } };
    handler(req, res);
  });
}
let fails = 0;
function check(name, cond, extra = '') { console.log((cond ? 'PASS' : 'FAIL'), name, extra); if (!cond) fails++; }
const ADMIN = { 'x-admin-token': 'test-admin-token' };
const good = { service: 'visa', destination: 'Turkey', name: 'Normal Name', phone: '01001234567' };

(async () => {
  // 1) stored-XSS: markup must never reach storage
  let r = await call(bookings, { method: 'POST', headers: { 'x-forwarded-for': '9.9.9.9' },
    body: { ...good, name: '<script>alert(1)</script>', destination: '<img src=x onerror=alert(2)>', notes: 'a"b<c>d' } });
  check('xss booking accepted (cleaned)', r.status === 201);
  const ref = r.json.ref;
  r = await call(bookings, { method: 'GET', headers: ADMIN });
  const stored = r.json.bookings.find(b => b.ref === ref);
  check('stored name has no < >', stored && !/[<>]/.test(stored.name), stored && stored.name);
  check('stored destination has no < >', stored && !/[<>]/.test(stored.destination));
  check('stored notes sanitized', stored && !/[<>"]/.test(stored.notes), stored && stored.notes);

  // 2) rate limiting: 10 creates/hour/IP allowed, the 11th is refused
  let last = null;
  for (let i = 0; i < 11; i++) {
    last = await call(bookings, { method: 'POST', headers: { 'x-forwarded-for': '8.8.8.8' }, body: good });
  }
  check('11th create in an hour -> 429', last.status === 429 && last.json.error === 'rate_limited', 'status ' + last.status);
  r = await call(bookings, { method: 'POST', headers: { 'x-forwarded-for': '7.7.7.7' }, body: good });
  check('different IP unaffected', r.status === 201);

  // 3) CORS policy on the browser-facing endpoint
  r = await call(bookings, { method: 'POST', headers: { 'x-forwarded-for': '6.6.6.6', origin: 'https://evil.example' }, body: good });
  check('foreign origin not reflected', r.headers['access-control-allow-origin'] === 'https://www.younistravel.site',
        r.headers['access-control-allow-origin']);
  r = await call(bookings, { method: 'POST', headers: { 'x-forwarded-for': '6.6.6.6', origin: 'https://www.younistravel.site' }, body: good });
  check('own origin echoed', r.headers['access-control-allow-origin'] === 'https://www.younistravel.site');

  // 4) MCP create_booking shares the same 10/hour/IP bucket as REST POST
  const mcp = require(A + 'mcp.js');
  async function mcpCall(body, ip) {
    return new Promise((resolve) => {
      const req = { method: 'POST', body, query: {}, headers: { 'x-forwarded-for': ip },
                    async *[Symbol.asyncIterator]() { yield Buffer.from(JSON.stringify(body)); } };
      const res = { statusCode: 200, headers: {},
                    setHeader(k, v) { this.headers[k.toLowerCase()] = v; },
                    end(data) { let json = null; try { json = JSON.parse(data); } catch {}
                                resolve({ status: this.statusCode, json, headers: this.headers }); } };
      mcp(req, res);
    });
  }
  let mcpLast = null;
  for (let i = 0; i < 11; i++) {
    mcpLast = await mcpCall({ jsonrpc: '2.0', id: i, method: 'tools/call',
      params: { name: 'create_booking', arguments: good } }, '5.5.5.5');
  }
  check('MCP 11th create in an hour -> isError rate limited',
        mcpLast.json && mcpLast.json.result && mcpLast.json.result.isError === true &&
        /Rate limited/.test(mcpLast.json.result.content[0].text),
        mcpLast.json && mcpLast.json.result && mcpLast.json.result.content[0].text);
  // MCP track_booking still returns no PII (no name/phone in public view)
  const created = await mcpCall({ jsonrpc: '2.0', id: 99, method: 'tools/call',
    params: { name: 'create_booking', arguments: good } }, '4.4.4.4');
  const mcpRef = JSON.parse(created.json.result.content[0].text).ref;
  const tracked = await mcpCall({ jsonrpc: '2.0', id: 100, method: 'tools/call',
    params: { name: 'track_booking', arguments: { ref: mcpRef, phone: '01001234567' } } }, '4.4.4.4');
  const tv = JSON.parse(tracked.json.result.content[0].text);
  check('MCP track_booking exposes no name/phone', tv.name === undefined && tv.phone === undefined, JSON.stringify(tv));

  console.log(fails === 0 ? 'ALL PASS' : fails + ' FAILURES');
  process.exit(fails ? 1 : 0);
})();
