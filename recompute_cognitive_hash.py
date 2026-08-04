import json, sys, hashlib

def canon_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha384_hex_upper(s):
    return hashlib.sha384(s.encode('utf-8')).hexdigest().upper()

d = json.load(sys.stdin)
event = d.get('event', {})
audit = event.get('AUDIT', {})
metrics = audit.get('metrics', {})

operands = metrics.get('cognitive_hash_operands', {})
declared_cognitive_hash = metrics.get('cognitive_hash')

computed = '0x' + sha384_hex_upper(canon_json(operands))

print('=== cognitive_hash, recomputed independently from declared operands ===')
print()
print('seven operands (AL, CE, RS, SC, SQ, T, U), canonically')
print('serialized with sorted keys:')
print(canon_json(operands))
print()
print('computed cognitive_hash:', computed)
print('declared cognitive_hash:', declared_cognitive_hash)
print('match                  :', computed == declared_cognitive_hash)
