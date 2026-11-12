// GET /api/track?ref=YT-XXXXXX&phone=01xxxxxxxxx — public booking status lookup.
// Requires the phone number used in the booking; a wrong phone returns the same
// 404 as an unknown reference so references cannot be probed.
const L = require('./_lib');

module.exports = async (req, res) => {
  if (req.method === 'OPTIONS') { L.send(res, 204, {}); return; }
  if (req.method !== 'GET') { L.send(res, 405, { error: 'method_not_allowed' }); return; }
  if (!L.storageReady()) { L.send(res, 503, { error: 'storage_not_configured' }); return; }
  try {
    const q = req.query || {};
    const ref = L.clean(q.ref || '', 12).toUpperCase();
    const b = ref ? await L.getBooking(ref) : null;
    if (!b || L.phoneKey(b.phone) !== L.phoneKey(q.phone || '')) {
      L.send(res, 404, { error: 'not_found' });
      return;
    }
    L.send(res, 200, { booking: L.publicView(b) });
  } catch (e) {
    L.send(res, 500, { error: 'server_error' });
  }
};
