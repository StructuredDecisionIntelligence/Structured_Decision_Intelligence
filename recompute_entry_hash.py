import json, sys, hashlib

# recompute_entry_hash.py
# Protocol v1, seq 355 and forward.
#
# CHANGED from the prior version: the ninth packet field is audit_hash,
# not the challenge block. The prior version matched under the prototype
# construction and fails from 355 forward.
#
# UNTESTED against a live record. Verify before publishing:
#   curl -s https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/355 \
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

# Step 1: der_hash. Stored at the top level of AUDIT, a sibling of ENTRY,
# not nested inside ENTRY.meta. Read it rather than recomputing it.
stored_der_hash = audit.get('der_hash') or meta.get('der_hash')
if stored_der_hash:
    der_hash = stored_der_hash
    der_hash_source = 'stored on record (AUDIT.der_hash), used as-is'
else:
    full_der = meta.get('SDI_DER', {})
    der_hash = '0x' + sha384_hex_upper(canon_json(full_der))
    der_hash_source = 'computed from full SDI_DER, not present on record'

# Step 2: audit_hash. Stored under ENTRY.meta. Read it, do not recompute.
stored_audit_hash = meta.get('audit_hash') or audit.get('audit_hash')
if stored_audit_hash:
    audit_hash = stored_audit_hash
    audit_hash_source = 'stored on record (meta.audit_hash), used as-is'
else:
    audit_hash = None
    audit_hash_source = 'NOT FOUND on record, packet will not match'

# Step 3: the nine-field chain packet. Written here in an arbitrary order
# deliberately, to demonstrate the point: canon_json's own sort_keys=True
# makes the order below irrelevant to the result.
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

computed_entry_hash = '0x' + sha384_hex_upper(canon_json(chain_packet))

print("=== entry_hash, recomputed independently from this record's own declared fields ===")
print()
print('der_hash source  :', der_hash_source)
print('der_hash         :', der_hash)
print('audit_hash source:', audit_hash_source)
print('audit_hash       :', audit_hash)
print()
print('chain packet, nine fields, canonically serialized with sorted keys')
print('(the order the fields are listed in this script is irrelevant,')
print('canon_json sorts them alphabetically regardless):')
print(canon_json(chain_packet))
print()
print('computed entry_hash :', computed_entry_hash)
print('declared entry_hash :', declared_entry_hash)
print('match               :', computed_entry_hash == declared_entry_hash)
print()
print('=== chain continuity, against a later record ===')
print("To confirm continuity, pull the next record on the chain (this")
print("record's seq + 1). Its declared parent_hash should equal this")
print("record's entry_hash, computed above. This script only computes")
print("one record's own entry_hash; comparing it to a later record's")
print("declared parent_hash is the final, manual step.")
