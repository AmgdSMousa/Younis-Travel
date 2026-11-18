// GET /api/flights — indicative flight prices in EGP.
// Source: Travelpayouts (Aviasales) data API, fares requested in EUR and
// converted at the daily rate from open.er-api.com, plus the agency margin
// (10%), rounded up to the nearest 5 EGP. Env: TRAVELPAYOUTS_TOKEN.
// Prices are indicative — the final fare is confirmed when the team books
// manually through the request flow. The provider booking link returned by
// the upstream API is deliberately never exposed to clients.
const L = require('./_lib');

const MARKUP = 1.10;
const ceil5 = n => Math.ceil(n / 5) * 5;

async function fxEurEgp() {
  try {
    const c = await L.redis(['GET', 'fx:eur:egp']);
    if (c) return parseFloat(c);
  } catch (e) { /* fall through to a live fetch */ }
  const r = await fetch('https://open.er-api.com/v6/latest/EUR');
  const j = await r.json();
  const rate = j && j.rates && j.rates.EGP;
  if (!rate) throw new Error('fx_unavailable');
  try { await L.redis(['SET', 'fx:eur:egp', String(rate), 'EX', 21600]); } catch (e) {}
  return rate;
}

module.exports = async (req, res) => {
  if (req.method === 'OPTIONS') { L.send(res, 204, {}, L.browserCors(req)); return; }
  if (req.method !== 'GET') { L.send(res, 405, { error: 'method_not_allowed' }, L.browserCors(req)); return; }
  const token = process.env.TRAVELPAYOUTS_TOKEN;
  if (!token) {
    L.send(res, 503, { error: 'not_configured', message: 'Flight price search is being activated.' }, L.browserCors(req));
    return;
  }
  if (!(await L.rateLimit('flsearch', req, 60, 3600))) {
    res.setHeader('Retry-After', '3600');
    L.send(res, 429, { error: 'rate_limited', message: 'Too many searches — please try again later.' }, L.browserCors(req));
    return;
  }
  const q = new URL(req.url, 'https://younistravel.site').searchParams;
  const iata = v => (/^[A-Za-z]{3}$/.test(v || '') ? v.toUpperCase() : null);
  const dateOk = v => /^\d{4}-\d{2}-\d{2}$/.test(v || '');
  const origin = iata(q.get('origin'));
  const destination = iata(q.get('destination'));
  const dep = q.get('departure_at') || '';
  const ret = q.get('return_at') || '';
  if (!origin || !destination || !dateOk(dep) || (ret && !dateOk(ret))) {
    L.send(res, 400, { error: 'validation', message: 'origin, destination (IATA) and departure_at (YYYY-MM-DD) are required.' }, L.browserCors(req));
    return;
  }
  const pax = Math.min(9, Math.max(1, parseInt(q.get('passengers') || '1', 10) || 1));
  const tclass = q.get('class') === 'business' ? '1' : '0';
  const cacheKey = 'fl3:' + [origin, destination, dep, ret, pax, tclass].join(':');
  try {
    const c = await L.redis(['GET', cacheKey]);
    if (c) { L.send(res, 200, JSON.parse(c), L.browserCors(req)); return; }
  } catch (e) { /* cache is best-effort */ }
  try {
    // The upstream data API holds cached fares, so an exact date pair is often
    // empty even on busy routes. Fall back: same month (round trip), then the
    // month one-way — and flag the answer as approximate so the page can say
    // these are the cheapest fares around the requested dates.
    const fetchFares = async (depAt, retAt, oneWay) => {
      const u = new URL('https://api.travelpayouts.com/aviasales/v3/prices_for_dates');
      u.searchParams.set('origin', origin);
      u.searchParams.set('destination', destination);
      u.searchParams.set('departure_at', depAt);
      if (retAt) u.searchParams.set('return_at', retAt);
      u.searchParams.set('one_way', oneWay ? 'true' : 'false');
      u.searchParams.set('currency', 'eur');
      u.searchParams.set('sorting', 'price');
      u.searchParams.set('limit', '30');
      u.searchParams.set('trip_class', tclass);
      u.searchParams.set('token', token);
      const r = await fetch(u);
      const j = await r.json();
      if (!j || !j.success) throw new Error('upstream_error');
      return j.data || [];
    };
    let data = await fetchFares(dep, ret || null, !ret);
    let approximate = false;
    if (!data.length) {
      data = await fetchFares(dep.slice(0, 7), ret ? ret.slice(0, 7) : null, !ret);
      approximate = data.length > 0;
    }
    if (!data.length && ret) {
      data = await fetchFares(dep.slice(0, 7), null, true);
      approximate = data.length > 0;
    }
    const rate = await fxEurEgp();
    const seen = new Set();
    const results = [];
    for (const f of data) {
      const key = [f.airline, f.flight_number, f.departure_at].join('|');
      if (seen.has(key)) continue;
      seen.add(key);
      const perPerson = ceil5(Math.round(Number(f.price) * rate * MARKUP * 100) / 100);
      results.push({
        airline: f.airline || '',
        flight_number: f.flight_number || '',
        departure_at: f.departure_at || null,
        return_at: f.return_at || null,
        transfers: f.transfers || 0,
        return_transfers: f.return_transfers || 0,
        origin_airport: f.origin_airport || origin,
        destination_airport: f.destination_airport || destination,
        duration_min: f.duration_to || f.duration || null,
        duration_back_min: f.duration_back || null,
        price_egp_per_person: perPerson,
        price_egp_total: perPerson * pax,
      });
      if (results.length >= 10) break;
    }
    const out = { currency: 'EGP', origin, destination, departure_at: dep, return_at: ret || null, passengers: pax, approximate, results };
    if (results.length) { try { await L.redis(['SET', cacheKey, JSON.stringify(out), 'EX', 1200]); } catch (e) {} }
    L.send(res, 200, out, L.browserCors(req));
  } catch (e) {
    L.send(res, 502, { error: 'upstream', message: 'Price search is unavailable right now.' }, L.browserCors(req));
  }
};
