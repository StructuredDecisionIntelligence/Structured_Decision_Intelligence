import json, sys, hashlib

# recompute_entry_hash.py
# SDI Protocol v1. Records at seq 355 and forward.
#
# Recomputes a record's entry_hash from the record's own contents and
# compares it against the declared value. Nothing outside the record is
# needed.
#
# Two of the nine packet fields are derived rather than read directly:
#   der_hash    never stored, computed here over meta.SDI_DER
#   audit_hash  always stored at meta.audit_hash, read as-is
#
# Usage:
#   curl -s https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/355 \
#     | python3 recompute_entry_hash.py

d = json.load(sys.stdin)
event = d.get('event', {})
entry = event.get('ENTRY', {})
meta = entry.get('meta', {}) if isinstance(entry.get('meta'), dict) else {}


def canon_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha384_hex_upper(s):
    return hashlib.sha384(s.encode('utf-8')).hexdigest().upper()


declared_entry_hash = entry.get('entry_hash')

# der_hash: SHA-384 over the canonically serialized reasoning record.
der_obj = meta.get('SDI_DER') if isinstance(meta.get('SDI_DER'), dict) else {}
der_hash = '0x' + sha384_hex_upper(canon_json(der_obj))

# The nine-field chain packet. Written in an arbitrary order deliberately:
# canon_json's sort_keys=True makes the order below irrelevant.
chain_packet = {
    'v':           entry.get('v', 'SDI_CHAIN_v1'),
    'hash_alg':    entry.get('hash_alg', 'SHA-384'),
    'agent_id':    entry.get('agent_id'),
    'seq':         entry.get('seq'),
    'parent_hash': entry.get('parent_hash'),
    'type':        entry.get('type'),
    'der_hash':    der_hash,
    'audit_hash':  meta.get('audit_hash'),
    'success_met': meta.get('success_met'),
}

computed_entry_hash = '0x' + sha384_hex_upper(canon_json(chain_packet))

print("=== entry_hash, recomputed from this record's own contents ===")
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
