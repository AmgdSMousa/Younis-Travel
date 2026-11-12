// POST /api/oauth/register — an agent (or its operator) requests API credentials.
// Requests are stored for the Younis Travel team, who review them and provision
// an OAuth client manually. GET (admin) lists pending requests.
const L = require('../_lib');
const O = require('../_oauth');
module.exports = async (req, res) => {
  if (!L.storageReady()) { L.send(res, 503, { error: 'storage_not_configured' }); return; }
  try {
    if (req.method === 'POST') {
      const b = await L.readJson(req);
      const r = await O.createRegistrationRequest(b);
      if (!r.ok) { L.send(res, 400, { error: 'validation', message: 'name and a contact (email or phone) are required' }); return; }
      L.send(res, 201, { request_id: r.request.id, status: r.request.status,
                         message: 'Request received. The Younis Travel team reviews requests and replies with client credentials if approved.' });
      return;
    }
    if (req.method === 'GET' && L.isAdmin(req)) {
      L.send(res, 200, { requests: await O.listRegistrationRequests() });
      return;
    }
    L.send(res, 405, { error: 'method_not_allowed' });
  } catch (e) { L.send(res, 500, { error: 'server_error' }); }
};
