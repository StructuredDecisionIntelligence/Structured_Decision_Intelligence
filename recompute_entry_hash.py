import json, sys, hashlib

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

# Step 1: der_hash. This lives at the top level of the record,
# under AUDIT, a sibling of ENTRY, not nested inside ENTRY.meta.
# Check there first, and only compute from the full DER if
# genuinely absent from both locations.
stored_der_hash = audit.get('der_hash') or meta.get('der_hash')
if stored_der_hash:
    der_hash = stored_der_hash
    der_hash_source = 'stored on record (AUDIT.der_hash), used as-is'
else:
    full_der = meta.get('SDI_DER', {})
    der_hash = '0x' + sha384_hex_upper(canon_json(full_der))
    der_hash_source = 'computed from full SDI_DER, not present on record'

# Step 2: the nine-field chain packet. Written here in an arbitrary
# order deliberately, to demonstrate the point: canon_json's own
# sort_keys=True makes the order below irrelevant to the result.
chain_packet = {
    'v': 'SDI_CHAIN_v1',
    'hash_alg': 'SHA-384',
    'agent_id': entry.get('agent_id'),
    'seq': entry.get('seq'),
    'parent_hash': declared_parent_hash,
    'type': entry.get('type'),
    'der_hash': der_hash,
    'success_met': meta.get('success_met'),
    'challenge': {
        'nonce': meta.get('challenge_nonce'),
        'proof_prefix16': meta.get('proof_prefix16'),
        'expires_utc': meta.get('expires_utc'),
    },
}

computed_entry_hash = '0x' + sha384_hex_upper(canon_json(chain_packet))

print('=== entry_hash, recomputed independently from this record\'s own declared fields ===')
print()
print('der_hash source:', der_hash_source)
print('der_hash        :', der_hash)
print()
print('chain packet, nine fields, canonically serialized with sorted keys')
print('(the order the fields are listed in this script is irrelevant,')
print('canon_json sorts them alphabetically regardless):')
print(canon_json(chain_packet))
print()
print('computed entry_hash :', computed_entry_hash)
print('declared entry_hash :', declared_entry_hash)
print('match                :', computed_entry_hash == declared_entry_hash)
print()
print('=== chain continuity, against a later record ===')
print('To confirm continuity, pull the next record on the chain (this')
print('record\'s seq + 1). Its declared parent_hash should equal this')
print('record\'s entry_hash, computed above. This script only computes')
print('one record\'s own entry_hash; comparing it to a later record\'s')
print('declared parent_hash is the final, manual step.')
