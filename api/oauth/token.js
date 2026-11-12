// POST /api/oauth/token — OAuth 2.0 token endpoint (client_credentials grant).
const L = require('../_lib');
const O = require('../_oauth');

async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString('utf8');
  if (!raw) return {};
  const ct = (req.headers['content-type'] || '');
  if (ct.includes('application/x-www-form-urlencoded')) return Object.fromEntries(new URLSearchParams(raw));
  try { return JSON.parse(raw); } catch { return Object.fromEntries(new URLSearchParams(raw)); }
}
module.exports = async (req, res) => {
  if (req.method !== 'POST') { L.send(res, 405, { error: 'method_not_allowed' }); return; }
  if (!L.storageReady()) { L.send(res, 503, { error: 'temporarily_unavailable' }); return; }
  try {
    const body = await readBody(req);
    if (body.grant_type !== 'client_credentials') { L.send(res, 400, { error: 'unsupported_grant_type' }); return; }
    const client = await O.authenticateClient(req, body);
    if (!client) {
      res.setHeader('WWW-Authenticate', 'Basic realm="younis-travel-oauth"');
      L.send(res, 401, { error: 'invalid_client' });
      return;
    }
    const t = await O.issueToken(client, body.scope);
    if (t.error) { L.send(res, 400, { error: t.error }); return; }
    L.send(res, 200, t);
  } catch (e) { L.send(res, 500, { error: 'server_error' }); }
};
