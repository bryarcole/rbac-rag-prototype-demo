import { test, expect } from '@playwright/test';

test.describe('RAG API Contract & Schema Validation', () => {
  test('GET /health returns valid service metadata', async ({ request }) => {
    const res = await request.get('/health');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('status', 'ok');
    expect(typeof body.indexed_docs).toBe('number');
    expect(typeof body.model_id).toBe('string');
  });

  test('POST /query rejects spoofed/invalid roles with HTTP 403', async ({ request }) => {
    const res = await request.post('/query', {
      headers: { 'X-User-Role': 'root_admin' },
      data: { question: 'Show me Project Titan' },
    });
    expect(res.status()).toBe(403);
    const body = await res.json();
    expect(body.detail).toContain('Invalid role');
  });

  test('POST /query rejects short/empty questions with HTTP 422', async ({ request }) => {
    const res = await request.post('/query', {
      headers: { 'X-User-Role': 'employee' },
      data: { question: 'hi' },
    });
    expect(res.status()).toBe(422);
  });
});
