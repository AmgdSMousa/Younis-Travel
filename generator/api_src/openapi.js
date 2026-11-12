// GET /api/openapi — OpenAPI 3.1 description of the Younis Travel booking API.
const L = require('./_lib');
const BASE = 'https://younistravel.site';
const SPEC = {
  openapi: '3.1.0',
  info: { title: 'Younis Travel Booking API', version: '1.0.0',
          description: 'Structured booking requests for Younis Travel (visas, flights, hotels, trips, insurance). Bookings are requests reviewed by the human team — no prices are published and no payment is taken through the API. A successful POST returns a booking reference the traveller uses to track status.' },
  servers: [{ url: BASE }],
  paths: {
    '/api/bookings': {
      post: { summary: 'Create a booking request',
              requestBody: { required: true, content: { 'application/json': { schema: { $ref: '#/components/schemas/BookingInput' } } } },
              responses: { '201': { description: 'Booking created', content: { 'application/json': { schema: { type: 'object', properties: { ref: { type: 'string', example: 'YT-AB12CD' }, status: { type: 'string', example: 'NEW' }, track_url: { type: 'string' } } } } } },
                           '400': { description: 'Validation error — response lists the invalid fields' },
                           '503': { description: 'Booking storage not yet activated' } } },
      get: { summary: 'List bookings (admin only, x-admin-token header)', security: [{ adminToken: [] }],
             responses: { '200': { description: 'Newest bookings first' }, '401': { description: 'Missing or wrong admin token' } } },
      patch: { summary: 'Update booking status or admin notes (admin only)', security: [{ adminToken: [] }],
               responses: { '200': { description: 'Updated booking' }, '401': { description: 'Missing or wrong admin token' }, '404': { description: 'Unknown reference' } } },
    },
    '/api/track': {
      get: { summary: 'Track a booking by reference + phone number',
             parameters: [{ name: 'ref', in: 'query', required: true, schema: { type: 'string' } },
                          { name: 'phone', in: 'query', required: true, schema: { type: 'string' } }],
             responses: { '200': { description: 'Public booking view (no personal data beyond what the traveller entered)' },
                          '404': { description: 'Unknown reference or phone mismatch' } } },
    },
    '/api/health': { get: { summary: 'Service and storage status', responses: { '200': { description: 'Status object' } } } },
  },
  components: {
    securitySchemes: { adminToken: { type: 'apiKey', in: 'header', name: 'x-admin-token' } },
    schemas: { BookingInput: { type: 'object', required: ['service', 'destination', 'name', 'phone'],
      properties: { service: { type: 'string', enum: ['visa', 'flight', 'hotel', 'trip', 'insurance'] },
                    destination: { type: 'string' }, dates: { type: 'string' },
                    people: { type: 'integer', minimum: 1, maximum: 50 },
                    name: { type: 'string' }, phone: { type: 'string' }, notes: { type: 'string' } } } },
  },
};
module.exports = (req, res) => { L.send(res, 200, SPEC); };
