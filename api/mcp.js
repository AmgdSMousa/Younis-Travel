// /api/mcp — minimal MCP (Model Context Protocol) server over HTTP JSON-RPC 2.0.
// Tools wrap the same booking library as the REST API, so everything they report
// is real: services info, booking creation, booking tracking.
const L = require('./_lib');

const TOOLS = [
  { name: 'younis_travel_services',
    description: 'List Younis Travel services and how booking works. The site publishes no prices; the human team replies per request.',
    inputSchema: { type: 'object', properties: {} } },
  { name: 'create_booking',
    description: 'Create a real booking request with Younis Travel and return its booking reference. The team reviews it and contacts the traveller.',
    inputSchema: { type: 'object', required: ['service', 'destination', 'name', 'phone'],
      properties: { service: { type: 'string', enum: L.SERVICES }, destination: { type: 'string' },
                    dates: { type: 'string' }, people: { type: 'integer', minimum: 1, maximum: 50 },
                    name: { type: 'string' }, phone: { type: 'string' }, notes: { type: 'string' } } } },
  { name: 'track_booking',
    description: 'Get the current status of a booking by its reference and the phone number used when booking.',
    inputSchema: { type: 'object', required: ['ref', 'phone'],
      properties: { ref: { type: 'string' }, phone: { type: 'string' } } } },
];
const SERVICES_INFO = {
  services: ['e-Visas: Turkey, Vietnam, Albania, Kenya, United Arab Emirates',
             'Embassy and Tasheer appointment booking: USA, Schengen countries, United Kingdom, Saudi Arabia',
             'Flights: comparison across 500+ airlines; payment by cash, bank transfer or electronic payment; ticket by WhatsApp and email',
             'Hotels: closed B2B rates with official receipts accepted by embassies and airports',
             'Trips and travel insurance'],
  how: 'Create a booking with the create_booking tool or at https://younistravel.site/request.html. The traveller receives a reference (e.g. YT-AB12CD) and can track it at https://younistravel.site/track.html. The team replies with exact prices and next steps.',
};
function rpc(res, id, result) { L.send(res, 200, { jsonrpc: '2.0', id: id == null ? null : id, result }); }
function rpcErr(res, id, code, message) { L.send(res, 200, { jsonrpc: '2.0', id: id == null ? null : id, error: { code, message } }); }

module.exports = async (req, res) => {
  if (req.method === 'GET') {
    L.send(res, 200, { name: 'younis-travel', version: '1.0.0', protocol: 'mcp', transport: 'http-jsonrpc',
                       endpoint: 'https://younistravel.site/api/mcp', tools: TOOLS.map(t => t.name) });
    return;
  }
  if (req.method !== 'POST') { L.send(res, 405, { error: 'method_not_allowed' }); return; }
  const m = await L.readJson(req);
  const id = m.id == null ? null : m.id;
  try {
    if (m.method === 'initialize') {
      rpc(res, id, { protocolVersion: '2025-03-26', capabilities: { tools: {} },
                     serverInfo: { name: 'younis-travel', version: '1.0.0' } });
      return;
    }
    if (m.method === 'ping') { rpc(res, id, {}); return; }
    if (String(m.method || '').startsWith('notifications/')) { res.statusCode = 202; res.end(); return; }
    if (m.method === 'tools/list') { rpc(res, id, { tools: TOOLS }); return; }
    if (m.method === 'tools/call') {
      const name = m.params && m.params.name;
      const args = (m.params && m.params.arguments) || {};
      if (!L.storageReady() && name !== 'younis_travel_services') {
        rpc(res, id, { content: [{ type: 'text', text: 'Booking storage is being activated; please use https://younistravel.site/request.html meanwhile.' }], isError: true });
        return;
      }
      if (name === 'younis_travel_services') {
        rpc(res, id, { content: [{ type: 'text', text: JSON.stringify(SERVICES_INFO, null, 2) }] });
        return;
      }
      if (name === 'create_booking') {
        // Same 10/hour/IP bucket as POST /api/bookings ('bkcreate') — without
        // this, the MCP tool would bypass the REST rate limit entirely.
        if (!(await L.rateLimit('bkcreate', req, 10, 3600))) {
          rpc(res, id, { content: [{ type: 'text', text: 'Rate limited: too many booking requests — please try again later, or message the team on Facebook.' }], isError: true });
          return;
        }
        const r = await L.createBooking(args);
        if (!r.ok) { rpc(res, id, { content: [{ type: 'text', text: 'Validation failed for fields: ' + r.errors.join(', ') }], isError: true }); return; }
        rpc(res, id, { content: [{ type: 'text', text: JSON.stringify({ ref: r.booking.ref, status: r.booking.status, track_url: 'https://younistravel.site/track.html?ref=' + r.booking.ref }, null, 2) }] });
        return;
      }
      if (name === 'track_booking') {
        const b = await L.getBooking(L.clean(args.ref || '', 12).toUpperCase());
        if (!b || L.phoneKey(b.phone) !== L.phoneKey(args.phone || '')) {
          rpc(res, id, { content: [{ type: 'text', text: 'Booking not found (check the reference and phone number).' }], isError: true });
          return;
        }
        rpc(res, id, { content: [{ type: 'text', text: JSON.stringify(L.publicView(b), null, 2) }] });
        return;
      }
      rpcErr(res, id, -32602, 'Unknown tool: ' + name);
      return;
    }
    rpcErr(res, id, -32601, 'Method not found: ' + m.method);
  } catch (e) {
    rpcErr(res, id, -32603, 'Internal error');
  }
};
