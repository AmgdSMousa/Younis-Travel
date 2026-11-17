// Local test of the flight price API handler (mock storage + stubbed upstreams).
process.env.YT_ALLOW_MOCK = '1';
const A = '/home/hatch/workspace/younis-website/generator/api_src/';
const flights = require(A + 'flights.js');

let fetchCalls = [];
global.fetch = async (url) => {
  const u = String(url);
  fetchCalls.push(u);
  if (u.includes('prices_for_dates')) {
    return { json: async () => ({ success: true, currency: 'eur', data: [
      { airline: 'MS', flight_number: 'MS964', departure_at: '2026-12-10T06:30:00', return_at: '2026-12-17T11:05:00', price: 100, transfers: 0, return_transfers: 1, duration_to: 240, link: '/search/SECRET' },
      { airline: 'MS', flight_number: 'MS964', departure_at: '2026-12-10T06:30:00', return_at: '2026-12-17T11:05:00', price: 100, transfers: 0, return_transfers: 1, duration_to: 240, link: '/search/SECRET' },
      { airline: 'FZ', flight_number: 'FZ578', departure_at: '2026-12-10T09:15:00', return_at: '2026-12-17T14:20:00', price: 121, transfers: 1, return_transfers: 0, duration_to: 300, link: '/search/SECRET2' },
    ] }) };
  }
  if (u.includes('open.er-api.com')) return { json: async () => ({ result: 'success', rates: { EGP: 50 } }) };
  throw new Error('unexpected fetch ' + u);
};

function call({ method = 'GET', url = '/api/flights', headers = {} } = {}) {
  return new Promise((resolve) => {
    const req = { method, url, headers };
    const res = { statusCode: 200, headers: {},
                  setHeader(k, v) { this.headers[k] = v; },
                  end(data) { let json = null; try { json = JSON.parse(data); } catch {}
                              resolve({ status: this.statusCode, json, raw: data }); } };
    flights(req, res);
  });
}
let fails = 0;
function check(name, cond, extra = '') { console.log((cond ? 'PASS' : 'FAIL'), name, extra); if (!cond) fails++; }

(async () => {
  delete process.env.TRAVELPAYOUTS_TOKEN;
  let r = await call({ url: '/api/flights?origin=CAI&destination=DXB&departure_at=2026-12-10' });
  check('no token -> 503 not_configured', r.status === 503 && r.json.error === 'not_configured', JSON.stringify(r.json));

  process.env.TRAVELPAYOUTS_TOKEN = 'test-token';
  r = await call({ url: '/api/flights?origin=CAI&destination=DXB' });
  check('missing date -> 400', r.status === 400, JSON.stringify(r.json));

  r = await call({ url: '/api/flights?origin=CAI&destination=DXB&departure_at=2026-12-10&return_at=2026-12-17&passengers=2' });
  check('search ok', r.status === 200 && r.json.currency === 'EGP', JSON.stringify(r.json).slice(0, 200));
  check('dedupe -> 2 results', r.json.results.length === 2, 'got ' + r.json.results.length);
  const f0 = r.json.results[0];
  check('markup math: 100 EUR x 50 x 1.10 = 5500/person', f0.price_egp_per_person === 5500, String(f0.price_egp_per_person));
  check('total for 2 pax = 11000', f0.price_egp_total === 11000, String(f0.price_egp_total));
  check('ceil5: 121 EUR -> 6655/person', r.json.results[1].price_egp_per_person === 6655, String(r.json.results[1].price_egp_per_person));
  check('provider link never exposed', !JSON.stringify(r.json).includes('SECRET') && !('link' in f0));
  check('token sent upstream, currency eur', fetchCalls.some(u => u.includes('token=test-token') && u.includes('currency=eur')));

  console.log(fails === 0 ? 'ALL PASS' : fails + ' FAILURES');
  process.exit(fails ? 1 : 0);
})();
