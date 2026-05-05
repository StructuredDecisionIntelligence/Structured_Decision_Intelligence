import urllib.request, json, hashlib

SEQ = 154  # Replace with any SEQ from 154 onward for full metrics

def fetch(seq):
    url = f'https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/{seq}'
    return json.loads(urllib.request.urlopen(url).read())

def check(label, expected, recomputed):
    e = str(expected)
    r = str(recomputed)
    if '.' in e:
        match = abs(float(e) - float(r)) < 0.0001
    else:
        match = e == r
    status = 'MATCH' if match else 'MISMATCH'
    print(f'{status:8} {label}')
    if not match:
        print(f'         expected:   {e[:80]}')
        print(f'         recomputed: {r[:80]}')

d       = fetch(SEQ)
entry   = d['event']['ENTRY']
metrics = d['event']['AUDIT']['metrics']

print(f'\n=== REASONING VERIFICATION: SEQ {SEQ} ===\n')

# 1. cognitive_hash — proof of reasoning cost fingerprint
ops = metrics.get('cognitive_hash_operands', {})
if ops:
    cog_input = json.dumps(
        {k: ops[k] for k in sorted(ops)},
        sort_keys=True, separators=(',',':')
    )
    recomputed_cog = '0x' + hashlib.sha384(cog_input.encode()).hexdigest().upper()
    check('cognitive_hash    (reasoning cost fingerprint)', metrics.get('cognitive_hash'), recomputed_cog)
else:
    print('SKIP     cognitive_hash    (pre-RAI_v3 entry — use SEQ 154+)')

# 2. Jc_clt — cognitive work density
jops = metrics.get('Jc_clt_operands', {})
if jops:
    SQ = jops.get('SQ', 0)
    SC = jops.get('SC', 0)
    CE = jops.get('CE', 0)
    AL = jops.get('AL', 0)
    U  = jops.get('U',  1)
    recomputed_jc = float(((SQ * max(SC, 1)) + CE) * (AL * U))
    check('Jc_clt            (cognitive work density)', metrics.get('Jc_clt'), recomputed_jc)
else:
    print('SKIP     Jc_clt            (operands not present)')

# 3. W_RSQ — semantic coherence between INTENT and LOGIC
wops = metrics.get('W_RSQ_operands', {})
if wops:
    recomputed_wrsq = round(
        0.25 * wops.get('coherence_chain', 0) +
        0.25 * wops.get('evidence_grounding', 0) +
        0.20 * wops.get('judgment_resolution', 0) +
        0.30 * wops.get('NLI_coherence', 0), 4)
    check('W_RSQ             (semantic coherence INTENT->LOGIC)', round(metrics.get('W_RSQ', 0), 4), recomputed_wrsq)
else:
    print('SKIP     W_RSQ             (pre-RAI_v3 entry — use SEQ 154+)')

# 4. RAI — reasoning admissibility index
breakdown = metrics.get('rai_breakdown', {})
if breakdown:
    recomputed_rai = round(sum(breakdown.values()), 4)
    check('RAI               (reasoning admissibility index)', round(metrics.get('RAI', 0), 4), recomputed_rai)
else:
    print('SKIP     RAI               (breakdown not present)')

# 5. parent_hash — chain continuity
parent  = entry.get('parent_hash')
seq_num = entry.get('seq')
if seq_num and seq_num > 1:
    prior      = fetch(seq_num - 1)
    prior_hash = prior['event']['ENTRY'].get('entry_hash')
    check('parent_hash       (chain continuity)', parent, prior_hash)
else:
    print('SKIP     parent_hash       (genesis entry)')

print()
print('NOTE: entry_hash canonical serialization requires server-side')
print('specification. See Protocol page. Chain integrity is separately')
print('verified by chain_ok:true in the /ledger/verify endpoint.')
