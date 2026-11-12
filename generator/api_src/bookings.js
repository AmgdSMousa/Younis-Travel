// POST /api/bookings — create a booking (public)
// GET  /api/bookings — list bookings (admin, x-admin-token)
// PATCH /api/bookings — update status/admin notes (admin)
// DELETE /api/bookings?ref=YT-XXXXXX — remove a booking (admin)
const L = require('./_lib');

module.exports = async (req, res) => {
  if (req.method === 'OPTIONS') { L.send(res, 204, {}); return; }
  if (!L.storageReady()) { L.send(res, 503, { error: 'storage_not_configured', message: 'Booking storage is being activated.' }); return; }
  try {
    if (req.method === 'POST') {
      const input = await L.readJson(req);
      const r = await L.createBooking(input);
      if (!r.ok) { L.send(res, 400, { error: 'validation', fields: r.errors }); return; }
      L.send(res, 201, { ref: r.booking.ref, status: r.booking.status, created_at: r.booking.created_at,
                         track_url: '/track.html?ref=' + r.booking.ref });
      return;
    }
    if (!L.isAdmin(req)) { L.send(res, 401, { error: 'admin_token_required' }); return; }
    if (req.method === 'GET') {
      L.send(res, 200, { bookings: await L.listBookings(100) });
      return;
    }
    if (req.method === 'PATCH') {
      const p = await L.readJson(req);
      const u = await L.updateBooking(L.clean(p.ref, 12).toUpperCase(), p);
      if (!u) { L.send(res, 404, { error: 'not_found' }); return; }
      L.send(res, 200, { booking: u });
      return;
    }
    if (req.method === 'DELETE') {
      const ref = L.clean((req.query && req.query.ref) || '', 12).toUpperCase();
      const ok = await L.deleteBooking(ref);
      L.send(res, ok ? 200 : 404, ok ? { deleted: ref } : { error: 'not_found' });
      return;
    }
    L.send(res, 405, { error: 'method_not_allowed' });
  } catch (e) {
    L.send(res, 500, { error: 'server_error' });
  }
};
