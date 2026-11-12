// Younis Travel booking API — shared library (storage, validation, booking ops).
// Storage: Upstash Redis over its REST API (zero dependencies, plain fetch).
// Env: UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN (or Vercel KV equivalents
// KV_REST_API_URL / KV_REST_API_TOKEN). ADMIN_TOKEN gates admin operations.
// YT_ALLOW_MOCK=1 enables an in-memory driver for LOCAL TESTS ONLY.
const UP_URL = process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL || '';
const UP_TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN || '';
const MOCK = process.env.YT_ALLOW_MOCK === '1' && !UP_URL;

const mem = new Map(); const memIndex = []; // mock-only state
async function redis(cmd) {
  if (MOCK) return mockCmd(cmd);
  const r = await fetch(UP_URL, {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + UP_TOKEN, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd),
  });
  const j = await r.json();
  if (j.error) throw new Error('storage: ' + j.error);
  return j.result;
}
function mockCmd([op, ...a]) {
  if (op === 'GET') return mem.has(a[0]) ? mem.get(a[0]) : null;
  if (op === 'SET') {
    if (a[2] === 'NX' && mem.has(a[0])) return null;
    mem.set(a[0], a[1]); return 'OK';
  }
  if (op === 'DEL') { const had = mem.delete(a[0]); return had ? 1 : 0; }
  if (op === 'ZADD') { if (!memIndex.includes(a[2])) memIndex.push(a[2]); return 1; }
  if (op === 'ZREVRANGE') { const s = [...memIndex].reverse(); return s.slice(Number(a[0]), Number(a[1]) + 1); }
  if (op === 'ZREM') { const i = memIndex.indexOf(a[0]); if (i >= 0) memIndex.splice(i, 1); return 1; }
  if (op === 'INCR') { const v = (parseInt(mem.get(a[0]) || '0', 10) || 0) + 1; mem.set(a[0], String(v)); return v; }
  if (op === 'EXPIRE') return 1;
  if (op === 'PING') return 'PONG';
  throw new Error('mock: unsupported ' + op);
}
const storageReady = () => Boolean(UP_URL && UP_TOKEN) || MOCK;

const SERVICES = ['visa', 'flight', 'hotel', 'trip', 'insurance'];
const STATUSES = ['NEW', 'CONTACTED', 'CONFIRMED', 'COMPLETED', 'CANCELLED'];
const REF_ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
function genRef() {
  let s = '';
  for (let i = 0; i < 6; i++) s += REF_ALPHABET[Math.floor(Math.random() * REF_ALPHABET.length)];
  return 'YT-' + s;
}
// Normalize whitespace, then strip markup-significant and control characters:
// stored values are later rendered in the team dashboard, so nothing that can
// become HTML ever reaches storage (the dashboard also escapes on render).
const clean = (v, max) => String(v == null ? '' : v).replace(/\s+/g, ' ').trim()
  .replace(/[<>"'`]/g, '').replace(/[\u0000-\u001f\u007f]/g, '').slice(0, max);
function digits(v) { return String(v || '').replace(/\D/g, ''); }
function phoneKey(v) { const d = digits(v); return d.length > 9 ? d.slice(-9) : d; }

function validateBooking(input) {
  const b = {
    service: clean(input.service, 20),
    destination: clean(input.destination, 80),
    dates: clean(input.dates, 80),
    people: Math.max(1, Math.min(50, parseInt(input.people, 10) || 1)),
    name: clean(input.name, 80),
    phone: clean(input.phone, 25),
    notes: clean(input.notes, 1000),
  };
  const errors = [];
  if (!SERVICES.includes(b.service)) errors.push('service');
  if (b.destination.length < 2) errors.push('destination');
  if (b.name.length < 3) errors.push('name');
  if (!/^[+\d][\d\s-]{7,16}$/.test(b.phone) || digits(b.phone).length < 9) errors.push('phone');
  return { b, errors };
}

async function createBooking(input) {
  const { b, errors } = validateBooking(input || {});
  if (errors.length) return { ok: false, errors };
  const now = new Date().toISOString();
  for (let tries = 0; tries < 5; tries++) {
    const ref = genRef();
    const rec = { ref, ...b, status: 'NEW', admin_notes: '', created_at: now, updated_at: now };
    const set = await redis(['SET', 'bk:' + ref, JSON.stringify(rec), 'NX']);
    if (set === 'OK') {
      await redis(['ZADD', 'bk:index', String(Date.now()), ref]);
      return { ok: true, booking: rec };
    }
  }
  return { ok: false, errors: ['ref_collision'] };
}
async function getBooking(ref) {
  const raw = await redis(['GET', 'bk:' + clean(ref, 12).toUpperCase()]);
  return raw ? JSON.parse(raw) : null;
}
async function listBookings(limit = 100) {
  const refs = (await redis(['ZREVRANGE', 'bk:index', '0', String(limit - 1)])) || [];
  const out = [];
  for (const ref of refs) { const b = await getBooking(ref); if (b) out.push(b); }
  return out;
}
async function updateBooking(ref, patch) {
  const b = await getBooking(ref);
  if (!b) return null;
  if (patch.status && STATUSES.includes(patch.status)) b.status = patch.status;
  if (typeof patch.admin_notes === 'string') b.admin_notes = clean(patch.admin_notes, 1000);
  b.updated_at = new Date().toISOString();
  await redis(['SET', 'bk:' + b.ref, JSON.stringify(b)]);
  return b;
}
async function deleteBooking(ref) {
  const b = await getBooking(ref);
  if (!b) return false;
  await redis(['DEL', 'bk:' + b.ref]);
  await redis(['ZREM', 'bk:index', b.ref]);
  return true;
}
function publicView(b) {
  return { ref: b.ref, service: b.service, destination: b.destination, dates: b.dates,
           people: b.people, status: b.status, created_at: b.created_at, updated_at: b.updated_at };
}
function isAdmin(req) {
  const t = process.env.ADMIN_TOKEN || '';
  return Boolean(t) && (req.headers['x-admin-token'] || '') === t;
}
function send(res, code, obj, corsOrigin) {
  res.statusCode = code;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Access-Control-Allow-Origin', corsOrigin || '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-admin-token, Authorization');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(obj));
}
// Browser-facing endpoints (booking form, tracking page) accept browser calls
// only from the site's own origins. Machine clients send no Origin header and
// are unaffected; the agent APIs (MCP/OAuth/discovery) keep the open default.
const SITE_ORIGINS = ['https://younistravel.site', 'https://www.younistravel.site'];
function browserCors(req) {
  const o = (req.headers && (req.headers.origin || req.headers.Origin)) || '';
  if (!o) return '*';
  return SITE_ORIGINS.includes(o) ? o : SITE_ORIGINS[1];
}
function clientIp(req) {
  const xff = (req.headers && req.headers['x-forwarded-for']) || '';
  return (String(xff).split(',')[0] || 'unknown').trim().slice(0, 64);
}
// Fixed-window rate limit in the shared store. Resolves true when allowed.
async function rateLimit(name, req, limit, windowSec) {
  const bucket = Math.floor(Date.now() / 1000 / windowSec);
  const key = 'rl:' + name + ':' + clientIp(req) + ':' + bucket;
  const n = await redis(['INCR', key]);
  if (Number(n) === 1) { try { await redis(['EXPIRE', key, String(windowSec + 60)]); } catch {} }
  return Number(n) <= limit;
}
async function readJson(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string' && req.body) { try { return JSON.parse(req.body); } catch { return {}; } }
  const chunks = [];
  for await (const c of req) chunks.push(c);
  if (!chunks.length) return {};
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); } catch { return {}; }
}
module.exports = { redis, storageReady, SERVICES, STATUSES, createBooking, getBooking,
                   listBookings, updateBooking, deleteBooking, publicView, isAdmin, send,
                   readJson, phoneKey, clean, browserCors, clientIp, rateLimit };
