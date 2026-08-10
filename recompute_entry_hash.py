import json, sys, hashlib

# recompute_entry_hash.py
# Protocol v1.
#
# Schema boundary: records sealed before the challenge-removal build
# include a challenge block in the chain packet. Records from seq 355
# forward do NOT include challenge but DO include audit_hash.
# This script detects which version a given record uses automatically.
#
# Test against seq 355 and a post-removal record:
#   curl -s https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/355 \
#     | python3 recompute_entry_hash.py
#   curl -s https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/360 \
#     | python3 recompute_entry_hash.py

d = json.load(sys.stdin)
event = d.get('event', {})
entry = event.get('ENTRY', {})
meta = entry.get('meta', {})
audit = event.get('AUDIT', {})

def canon_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha384_hex_upper(s):
    return hashlib.sha384(s.encode('utf-8')).hexdigest().upper()

declared_entry_hash = entry.get('entry_hash')
declared_parent_hash = entry.get('parent_hash')

# Step 1: der_hash. Stored at AUDIT.der_hash, not inside ENTRY.meta.
stored_der_hash = audit.get('der_hash') or meta.get('der_hash')
if stored_der_hash:
    der_hash = stored_der_hash
    der_hash_source = 'stored on record (AUDIT.der_hash), used as-is'
else:
    full_der = meta.get('SDI_DER', {})
    der_hash = '0x' + sha384_hex_upper(canon_json(full_der))
    der_hash_source = 'computed from full SDI_DER, not present on record'

# Step 2: audit_hash. Present on records from the audit_hash build forward.
stored_audit_hash = meta.get('audit_hash') or audit.get('audit_hash')
if stored_audit_hash:
    audit_hash = stored_audit_hash
    audit_hash_source = 'stored on record (meta.audit_hash), used as-is'
else:
    audit_hash = None
    audit_hash_source = 'NOT FOUND — this is a pre-audit_hash record'

# Step 3: chain packet. Core nine fields.
chain_packet = {
    'v': entry.get('v', 'SDI_CHAIN_v1'),
    'hash_alg': entry.get('hash_alg', 'SHA-384'),
    'agent_id': entry.get('agent_id'),
    'seq': entry.get('seq'),
    'parent_hash': declared_parent_hash,
    'type': entry.get('type'),
    'der_hash': der_hash,
    'audit_hash': audit_hash,
    'success_met': entry.get('success_met', meta.get('success_met')),
}

# Schema boundary: if challenge is present on this record (even as null
# values), include it. The original entry_hash was computed with it.
# Records where challenge is absent were sealed after the removal build.
challenge_note = ''
if 'challenge' in entry:
    chain_packet['challenge'] = entry.get('challenge')
    challenge_note = 'challenge present on record, included (pre-removal schema)'
else:
    challenge_note = 'challenge absent from record (post-removal schema)'

computed_entry_hash = '0x' + sha384_hex_upper(canon_json(chain_packet))

print("=== entry_hash, recomputed independently from this record's own declared fields ===")
print()
print('der_hash source  :', der_hash_source)
print('der_hash         :', der_hash)
print('audit_hash source:', audit_hash_source)
print('audit_hash       :', audit_hash)
print('schema boundary  :', challenge_note)
print()
print('chain packet, canonically serialized with sorted keys:')
print(canon_json(chain_packet))
print()
print('computed entry_hash :', computed_entry_hash)
print('declared entry_hash :', declared_entry_hash)
print('match               :', computed_entry_hash == declared_entry_hash)
print()
print('=== chain continuity ===')
print('Pull the next record (seq + 1). Its parent_hash should equal')
print('the computed entry_hash above.')
