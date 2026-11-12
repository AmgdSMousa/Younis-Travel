// Younis Travel OAuth 2.0 (client-credentials) — real authorization-server logic.
// JWT access tokens (RS256) signed with an RSA keypair generated once and stored
// in Redis; JWKS publishes the public key. Clients are provisioned by the admin;
// agents may file registration requests that the team approves manually.
const crypto = require('crypto');
const L = require('./_lib');

const ISSUER = 'https://younistravel.site';
const AUDIENCE = 'https://www.younistravel.site'; // matches the PRM "resource" identifier
const SCOPES = ['bookings:read', 'bookings:write'];
const TOKEN_TTL = 3600;

const sha256 = (s) => crypto.createHash('sha256').update(String(s)).digest('hex');
const b64u = (buf) => Buffer.from(buf).toString('base64url');

// ---------------------------------------------------------------- key management
async function getKeys() {
  const raw = await L.redis(['GET', 'oauth:keys']);
  if (raw) return JSON.parse(raw);
  const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', { modulusLength: 2048 });
  const jwk = publicKey.export({ format: 'jwk' });
  const kid = sha256(jwk.n).slice(0, 16);
  const rec = { kid, privatePem: privateKey.export({ format: 'pem', type: 'pkcs8' }),
                jwk: { kty: 'RSA', kid, use: 'sig', alg: 'RS256', n: jwk.n, e: jwk.e } };
  const set = await L.redis(['SET', 'oauth:keys', JSON.stringify(rec), 'NX']);
  if (set !== 'OK') { const again = await L.redis(['GET', 'oauth:keys']); if (again) return JSON.parse(again); }
  return rec;
}

// ---------------------------------------------------------------- clients
async function createClient(name, scopes) {
  const client_id = 'ytc_' + crypto.randomBytes(6).toString('hex');
  const secret = crypto.randomBytes(24).toString('hex');
  const rec = { client_id, name: L.clean(name, 80) || 'agent', secret_hash: sha256(secret),
                scopes: (scopes || []).filter(s => SCOPES.includes(s)), created_at: new Date().toISOString(), disabled: false };
  if (!rec.scopes.length) rec.scopes = ['bookings:read'];
  await L.redis(['SET', 'oauth:client:' + client_id, JSON.stringify(rec)]);
  await L.redis(['ZADD', 'oauth:clients', String(Date.now()), client_id]);
  return { client_id, client_secret: secret, scopes: rec.scopes };
}
async function getClient(id) {
  const raw = await L.redis(['GET', 'oauth:client:' + L.clean(id, 40)]);
  return raw ? JSON.parse(raw) : null;
}
async function listClients() {
  const ids = (await L.redis(['ZREVRANGE', 'oauth:clients', '0', '99'])) || [];
  const out = [];
  for (const id of ids) { const c = await getClient(id); if (c) { delete c.secret_hash; out.push(c); } }
  return out;
}
async function deleteClient(id) {
  const c = await getClient(id);
  if (!c) return false;
  await L.redis(['DEL', 'oauth:client:' + c.client_id]);
  await L.redis(['ZREM', 'oauth:clients', c.client_id]);
  return true;
}
function clientAuth(req, body) {
  // client_secret_basic (Authorization) or client_secret_post (body fields)
  const h = req.headers['authorization'] || '';
  if (h.startsWith('Basic ')) {
    const dec = Buffer.from(h.slice(6), 'base64').toString('utf8');
    const i = dec.indexOf(':');
    if (i > 0) return { id: dec.slice(0, i), secret: dec.slice(i + 1) };
  }
  if (body && body.client_id) return { id: String(body.client_id), secret: String(body.client_secret || '') };
  return null;
}
async function authenticateClient(req, body) {
  const creds = clientAuth(req, body);
  if (!creds) return null;
  const c = await getClient(creds.id);
  if (!c || c.disabled) return null;
  const given = Buffer.from(sha256(creds.secret));
  const stored = Buffer.from(c.secret_hash);
  if (given.length !== stored.length || !crypto.timingSafeEqual(given, stored)) return null;
  return c;
}

// ---------------------------------------------------------------- tokens (JWT RS256)
async function issueToken(client, scopeStr) {
  const want = scopeStr ? String(scopeStr).split(/\s+/).filter(Boolean) : client.scopes;
  const granted = want.filter(s => client.scopes.includes(s));
  if (scopeStr && granted.length !== want.length) return { error: 'invalid_scope' };
  const keys = await getKeys();
  const now = Math.floor(Date.now() / 1000);
  const payload = { iss: ISSUER, sub: client.client_id, aud: AUDIENCE, scope: granted.join(' '),
                    iat: now, exp: now + TOKEN_TTL, jti: crypto.randomBytes(12).toString('hex') };
  const header = { alg: 'RS256', typ: 'JWT', kid: keys.kid };
  const data = b64u(JSON.stringify(header)) + '.' + b64u(JSON.stringify(payload));
  const sig = crypto.sign('RSA-SHA256', Buffer.from(data), keys.privatePem);
  return { access_token: data + '.' + b64u(sig), token_type: 'Bearer', expires_in: TOKEN_TTL, scope: granted.join(' ') };
}
async function verifyToken(token) {
  const parts = String(token || '').split('.');
  if (parts.length !== 3) return null;
  let header, payload;
  try { header = JSON.parse(Buffer.from(parts[0], 'base64url')); payload = JSON.parse(Buffer.from(parts[1], 'base64url')); }
  catch { return null; }
  if (header.alg !== 'RS256') return null;
  const keys = await getKeys();
  if (header.kid !== keys.kid) return null;
  const pub = crypto.createPublicKey({ key: keys.jwk, format: 'jwk' });
  const ok = crypto.verify('RSA-SHA256', Buffer.from(parts[0] + '.' + parts[1]), pub, Buffer.from(parts[2], 'base64url'));
  if (!ok) return null;
  const now = Math.floor(Date.now() / 1000);
  if (payload.iss !== ISSUER || payload.aud !== AUDIENCE || !payload.exp || payload.exp < now) return null;
  const denied = await L.redis(['GET', 'oauth:deny:' + payload.jti]);
  if (denied) return null;
  return payload;
}
async function revokeToken(token) {
  const parts = String(token || '').split('.');
  if (parts.length !== 3) return false;
  let payload;
  try { payload = JSON.parse(Buffer.from(parts[1], 'base64url')); } catch { return false; }
  if (!payload.jti || !payload.exp) return false;
  const ttl = Math.max(1, payload.exp - Math.floor(Date.now() / 1000));
  await L.redis(['SET', 'oauth:deny:' + payload.jti, '1', 'EX', String(ttl)]);
  return true;
}
// Bearer authorization for protected API operations. Returns payload or null.
async function bearerAuth(req, scope) {
  const h = req.headers['authorization'] || '';
  if (!h.startsWith('Bearer ')) return null;
  const p = await verifyToken(h.slice(7));
  if (!p) return null;
  if (scope && !(p.scope || '').split(' ').includes(scope)) return null;
  return p;
}

// ---------------------------------------------------------------- registration requests
async function createRegistrationRequest(input) {
  const r = { name: L.clean(input.name, 80), contact: L.clean(input.contact, 120),
              use_case: L.clean(input.use_case, 500), status: 'pending', created_at: new Date().toISOString() };
  if (r.name.length < 2 || r.contact.length < 5) return { ok: false };
  const id = 'reg_' + crypto.randomBytes(6).toString('hex');
  r.id = id;
  await L.redis(['SET', 'oauth:regreq:' + id, JSON.stringify(r)]);
  await L.redis(['ZADD', 'oauth:regreqs', String(Date.now()), id]);
  return { ok: true, request: r };
}
async function listRegistrationRequests() {
  const ids = (await L.redis(['ZREVRANGE', 'oauth:regreqs', '0', '99'])) || [];
  const out = [];
  for (const id of ids) { const raw = await L.redis(['GET', 'oauth:regreq:' + id]); if (raw) out.push(JSON.parse(raw)); }
  return out;
}

module.exports = { ISSUER, AUDIENCE, SCOPES, getKeys, createClient, getClient, listClients,
                   deleteClient, authenticateClient, issueToken, verifyToken, revokeToken,
                   bearerAuth, createRegistrationRequest, listRegistrationRequests, sha256 };
