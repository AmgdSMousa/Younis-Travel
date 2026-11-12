// Local end-to-end test of the OAuth layer + protected bookings (in-memory driver).
process.env.YT_ALLOW_MOCK = '1';
process.env.ADMIN_TOKEN = 'test-admin-token';
const A = '/home/hatch/workspace/younis-website/api_src/';
const bookings = require(A + 'bookings.js');
const clients = require(A + 'oauth/clients.js');
const tokenEp = require(A + 'oauth/token.js');
const jwks = require(A + 'oauth/jwks.js');
const revoke = require(A + 'oauth/revoke.js');
const register = require(A + 'oauth/register.js');

function call(handler, { method = 'GET', body = null, query = {}, headers = {} } = {}) {
  return new Promise((resolve) => {
    const req = { method, body, query, headers,
                  async *[Symbol.asyncIterator]() { if (body) yield Buffer.from(JSON.stringify(body)); } };
    const res = { statusCode: 200, headers: {},
                  setHeader(k, v) { this.headers[k] = v; },
                  end(data) { let json = null; try { json = JSON.parse(data); } catch {}
                              resolve({ status: this.statusCode, json, headers: this.headers }); } };
    handler(req, res);
  });
}
let fails = 0;
function check(name, cond, extra = '') { console.log((cond ? 'PASS' : 'FAIL'), name, extra); if (!cond) fails++; }
const ADMIN = { 'x-admin-token': 'test-admin-token' };

(async () => {
  let r = await call(clients, { method: 'POST', body: { name: 'x', scopes: ['bookings:read'] } });
  check('clients without admin 401', r.status === 401);

  r = await call(clients, { method: 'POST', headers: ADMIN, body: { name: 'Read Agent', scopes: ['bookings:read'] } });
  check('create read client', r.status === 201 && r.json.client_id && r.json.client_secret);
  const rc = r.json;

  r = await call(clients, { method: 'POST', headers: ADMIN, body: { name: 'Full Agent', scopes: ['bookings:read', 'bookings:write'] } });
  const fc = r.json;
  check('create full client', r.status === 201);

  r = await call(tokenEp, { method: 'POST', body: { grant_type: 'client_credentials', client_id: rc.client_id, client_secret: 'wrong' } });
  check('wrong secret 401', r.status === 401 && r.json.error === 'invalid_client');

  r = await call(tokenEp, { method: 'POST', body: { grant_type: 'client_credentials', client_id: rc.client_id, client_secret: rc.client_secret, scope: 'bookings:write' } });
  check('scope beyond client 400', r.status === 400 && r.json.error === 'invalid_scope');

  r = await call(tokenEp, { method: 'POST', body: { grant_type: 'client_credentials', client_id: rc.client_id, client_secret: rc.client_secret } });
  check('issue read token', r.status === 200 && (r.json.access_token || '').split('.').length === 3);
  const readTok = r.json.access_token;

  r = await call(tokenEp, { method: 'POST', body: { grant_type: 'client_credentials', client_id: fc.client_id, client_secret: fc.client_secret } });
  const fullTok = r.json.access_token;
  check('issue full token', r.status === 200 && !!fullTok);

  r = await call(jwks);
  check('jwks RSA key', r.status === 200 && r.json.keys[0].kty === 'RSA' && !!r.json.keys[0].n);

  // a booking to protect
  r = await call(bookings, { method: 'POST', body: { service: 'visa', destination: 'Turkey', name: 'OAuth Test', phone: '01001234567' } });
  const ref = r.json.ref;
  check('create booking', r.status === 201 && !!ref);

  r = await call(bookings, { method: 'GET', headers: { authorization: 'Bearer ' + readTok } });
  check('GET bookings with read token', r.status === 200 && r.json.bookings.length >= 1);

  r = await call(bookings, { method: 'PATCH', headers: { authorization: 'Bearer ' + readTok }, body: { ref, status: 'CONFIRMED' } });
  check('PATCH with read-only token 401', r.status === 401 && (r.headers['WWW-Authenticate'] || '').includes('resource_metadata'));

  r = await call(bookings, { method: 'PATCH', headers: { authorization: 'Bearer ' + fullTok }, body: { ref, status: 'CONFIRMED' } });
  check('PATCH with write token', r.status === 200 && r.json.booking.status === 'CONFIRMED');

  const tampered = fullTok.slice(0, -2) + 'xx';
  r = await call(bookings, { method: 'GET', headers: { authorization: 'Bearer ' + tampered } });
  check('tampered token 401', r.status === 401);

  r = await call(revoke, { method: 'POST', body: { client_id: fc.client_id, client_secret: fc.client_secret, token: fullTok } });
  check('revoke ok', r.status === 200);
  r = await call(bookings, { method: 'GET', headers: { authorization: 'Bearer ' + fullTok } });
  check('revoked token 401', r.status === 401);

  r = await call(register, { method: 'POST', body: { name: 'Agent Co', contact: 'ops@agent.example', use_case: 'booking status sync' } });
  check('register request 201', r.status === 201 && r.json.status === 'pending');
  r = await call(register, { method: 'GET', headers: ADMIN });
  check('admin lists register requests', r.status === 200 && r.json.requests.length === 1);

  r = await call(clients, { method: 'DELETE', headers: ADMIN, query: { id: rc.client_id } });
  check('delete client', r.status === 200);
  r = await call(tokenEp, { method: 'POST', body: { grant_type: 'client_credentials', client_id: rc.client_id, client_secret: rc.client_secret } });
  check('deleted client cannot get token', r.status === 401);

  console.log(fails === 0 ? 'ALL PASS' : fails + ' FAILURES');
  process.exit(fails ? 1 : 0);
})();
