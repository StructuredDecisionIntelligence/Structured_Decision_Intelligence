import json, sys, hashlib

# recompute_entry_hash.py
# Protocol v1, seq 355 and forward.
#
# This mirrors the kernel's canonical_entry_string() exactly: same field
# set, same source paths, same fallbacks. Notable differences from the
# prior published version:
#
#   1. der_hash is read from entry["meta"]["der_hash"], NOT from AUDIT.
#      The prior script read AUDIT first. A value exists in both places
#      on a pulled record; the kernel uses meta.
#   2. audit_hash is the ninth field. The challenge block is gone,
#      removed because its three values were permanently null on every
#      episodic act.
#   3. success_met is read from meta, not from entry.
#
# Verify before publishing:
#   curl -s https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/355 \
#     | python3 recompute_entry_hash.py

d = json.load(sys.stdin)
event = d.get('event', {})
entry = event.get('ENTRY', {})
meta = entry.get('meta', {}) if isinstance(entry.get('meta'), dict) else {}
audit = event.get('AUDIT', {})


def canon_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha384_hex_upper(s):
    return hashlib.sha384(s.encode('utf-8')).hexdigest().upper()


declared_entry_hash = entry.get('entry_hash')

# Step 1: der_hash. The kernel reads meta["der_hash"] and computes from
# the full SDI_DER only if that is absent. It does not read AUDIT.
der_obj = meta.get('SDI_DER') if isinstance(meta.get('SDI_DER'), dict) else None
der_hash = meta.get('der_hash')
if not der_hash and der_obj:
    der_hash = '0x' + sha384_hex_upper(canon_json(der_obj))
    der_hash_source = 'computed from meta.SDI_DER, absent from meta.der_hash'
elif der_hash:
    der_hash_source = 'stored at meta.der_hash, used as-is'
else:
    der_hash_source = 'NOT FOUND, packet will not match'

# Step 2: the nine-field chain packet, field for field as the kernel
# builds it. Written in an arbitrary order deliberately: canon_json's
# sort_keys=True makes the order below irrelevant to the result.
chain_packet = {
    'v':           entry.get('v', 'SDI_CHAIN_v1'),
    'hash_alg':    entry.get('hash_alg', 'SHA-384'),
    'agent_id':    entry.get('agent_id'),
    'seq':         entry.get('seq'),
    'parent_hash': entry.get('parent_hash'),
    'type':        entry.get('type'),
    'der_hash':    der_hash or None,
    'audit_hash':  meta.get('audit_hash', None),
    'success_met': meta.get('success_met', None),
}

computed_entry_hash = '0x' + sha384_hex_upper(canon_json(chain_packet))

print("=== entry_hash, recomputed independently from this record's own declared fields ===")
print()
print('der_hash source :', der_hash_source)
print()

# Diagnostic: if a der_hash also exists under AUDIT and differs from the
# one the kernel uses, that is the mismatch, and it is worth seeing.
audit_der = audit.get('der_hash')
if audit_der and audit_der != der_hash:
    print('NOTE: AUDIT.der_hash differs from meta.der_hash.')
    print('  meta.der_hash  :', der_hash)
    print('  AUDIT.der_hash :', audit_der)
    print('  The kernel uses meta. AUDIT is not the packet input.')
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
