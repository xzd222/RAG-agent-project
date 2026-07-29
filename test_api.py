import os, io, json
from api import app
from fastapi.testclient import TestClient

client = TestClient(app)

# ── 1. Health ──
r = client.get('/api/health')
assert r.status_code == 200
assert r.json()['status'] == 'ok'
print('OK GET /api/health')

# ── 2. Documents list (empty) ──
r = client.get('/api/documents')
assert r.status_code == 200
assert r.json() == {'documents': []}
print('OK GET /api/documents (empty)')

# ── 3. Chat SSE stream ──
r = client.post('/api/chat', json={'query': 'hello'})
assert r.status_code == 200
assert 'text/event-stream' in r.headers['content-type']
lines = [l for l in r.text.split('\n') if l.startswith('data: ')]
assert len(lines) >= 2
content_line = json.loads(lines[0][6:])
assert 'content' in content_line
done_line = json.loads(lines[-1][6:])
assert done_line.get('done') == True
print(f'OK POST /api/chat (SSE, {len(lines)} events)')

# ── 4. Upload a test txt file ──
test_content = b'This is a test knowledge base document.\nWith some test content.'
r = client.post('/api/documents/upload', files={'file': ('test_kb.txt', io.BytesIO(test_content), 'text/plain')})
assert r.status_code == 200
assert r.json()['status'] == 'ok'
assert r.json()['filename'] == 'test_kb.txt'
print('OK POST /api/documents/upload (test_kb.txt)')

# ── 5. Upload should be idempotent (MD5 dedup) ──
r2 = client.post('/api/documents/upload', files={'file': ('test_kb.txt', io.BytesIO(test_content), 'text/plain')})
assert r2.status_code == 200
print('OK POST /api/documents/upload (duplicate, idempotent)')

# ── 6. Documents list (should have test_kb.txt) ──
r = client.get('/api/documents')
assert r.status_code == 200
docs = r.json()['documents']
assert len(docs) >= 1
test_doc = [d for d in docs if d['filename'] == 'test_kb.txt'][0]
assert test_doc['ingested'] == True
print(f'OK GET /api/documents ({len(docs)} files, ingested={test_doc["ingested"]})')

# ── 7. Reingest ──
r = client.post('/api/documents/reingest')
assert r.status_code == 200
print('OK POST /api/documents/reingest')

# ── 8. Delete ──
r = client.delete('/api/documents/test_kb.txt')
assert r.status_code == 200
print('OK DELETE /api/documents/test_kb.txt')

# ── 9. Delete nonexistent ──
r = client.delete('/api/documents/nonexistent.txt')
assert r.status_code == 404
print('OK DELETE /api/documents/nonexistent.txt (404)')

# ── 10. Upload unsupported type ──
r = client.post('/api/documents/upload', files={'file': ('test.jpg', io.BytesIO(b'nope'), 'image/jpeg')})
assert r.status_code == 400
print('OK POST /api/documents/upload (reject .jpg, 400)')

# ── 11. Verify test file was cleaned up ──
from utils.path_tool import get_abs_path
data_path = get_abs_path('data')
remains = [f for f in os.listdir(data_path) if f == 'test_kb.txt']
assert len(remains) == 0, f'file not cleaned: {remains}'
print('OK File cleanup confirmed')

print()
print('ALL 11 tests passed')
