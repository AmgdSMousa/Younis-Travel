// GET /api/health — service status for the API catalog "status" relation.
const L = require('./_lib');

module.exports = async (req, res) => {
  let storage = 'not_configured';
  if (L.storageReady()) {
    try { await L.redis(['PING']); storage = 'ok'; } catch { storage = 'error'; }
  }
  L.send(res, 200, { status: storage === 'ok' ? 'ok' : 'degraded', service: 'younis-travel-booking-api',
                     storage, time: new Date().toISOString() });
};
