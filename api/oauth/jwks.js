// GET /api/oauth/jwks — public keys for verifying issued JWTs (RS256).
const L = require('../_lib');
const O = require('../_oauth');
module.exports = async (req, res) => {
  if (!L.storageReady()) { L.send(res, 503, { error: 'temporarily_unavailable' }); return; }
  try {
    const keys = await O.getKeys();
    L.send(res, 200, { keys: [keys.jwk] });
  } catch (e) { L.send(res, 500, { error: 'server_error' }); }
};
