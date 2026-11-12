// OAuth client provisioning — admin only (x-admin-token).
// POST {name, scopes[]} -> {client_id, client_secret (shown once), scopes}
// GET -> list (no secrets). DELETE ?id=ytc_... -> remove client.
const L = require('../_lib');
const O = require('../_oauth');
module.exports = async (req, res) => {
  if (!L.storageReady()) { L.send(res, 503, { error: 'storage_not_configured' }); return; }
  if (!L.isAdmin(req)) { L.send(res, 401, { error: 'admin_token_required' }); return; }
  try {
    if (req.method === 'POST') {
      const b = await L.readJson(req);
      const c = await O.createClient(b.name, Array.isArray(b.scopes) ? b.scopes : []);
      L.send(res, 201, c);
      return;
    }
    if (req.method === 'GET') { L.send(res, 200, { clients: await O.listClients() }); return; }
    if (req.method === 'DELETE') {
      const ok = await O.deleteClient((req.query && req.query.id) || '');
      L.send(res, ok ? 200 : 404, ok ? { deleted: true } : { error: 'not_found' });
      return;
    }
    L.send(res, 405, { error: 'method_not_allowed' });
  } catch (e) { L.send(res, 500, { error: 'server_error' }); }
};
