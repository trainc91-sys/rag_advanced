import json, pathlib
path = pathlib.Path('test_chunks.json')
print('path exists', path.exists())
with path.open('r', encoding='utf-8') as f:
    data = json.load(f)

chunks_with_next = 0
next_ids = set()
chunk_ids = set()
for item in data:
    for chunk in item.get('chunks', []):
        chunk_ids.add(chunk['id'])
        if 'next_id' in chunk and chunk['next_id'] not in (None, ''):
            chunks_with_next += 1
            next_ids.add(chunk['next_id'])

print('documents', len(data))
print('total_chunks', len(chunk_ids))
print('chunks_with_next', chunks_with_next)
print('unique_next_ids', len(next_ids))
print('sample_next_ids', list(next_ids)[:20])
print('missing next ids count', sum(1 for nid in next_ids if nid not in chunk_ids))
print('first chunk sample', next(iter(data[0]['chunks'])))
