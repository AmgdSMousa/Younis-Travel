// POST /api/oauth/revoke — RFC 7009 token revocation (client-authenticated).
const L = require('../_lib');
const O = require('../_oauth');
module.exports = async (req, res) => {
  if (req.method !== 'POST') { L.send(res, 405, { error: 'method_not_allowed' }); return; }
  if (!L.storageReady()) { L.send(res, 503, { error: 'temporarily_unavailable' }); return; }
  try {
    const body = await L.readJson(req);
    const client = await O.authenticateClient(req, body);
    if (!client) { L.send(res, 401, { error: 'invalid_client' }); return; }
    if (body.token) await O.revokeToken(String(body.token));
    L.send(res, 200, {});
  } catch (e) { L.send(res, 500, { error: 'server_error' }); }
};
