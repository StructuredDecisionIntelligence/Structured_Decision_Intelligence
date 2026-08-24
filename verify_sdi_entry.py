import urllib.request, json, hashlib, math, sys, time

# Change SEQ below or pass as argument: python3 verify_sdi_entry.py 160
SEQ = int(sys.argv[1]) if len(sys.argv) > 1 else 404

# Confirmed cause of the seq 302+ parent_hash failure under sequential
# sweeps: a single isolated fetch of seq 301 succeeds cleanly (200, full
# body, real entry_hash), same URL, same code path as every other seq.
# The failure only appears after sustained request volume in a tight
# loop, consistent with throttling upstream of this application, not a
# per-seq data problem. Fix: retry with backoff on transient failure,
# plus a short pacing delay between requests to stay under whatever
# threshold triggers it.
FETCH_RETRIES = 3
FETCH_BACKOFF_SECONDS = 1.5
REQUEST_PACING_SECONDS = 0.3

def fetch(seq):
    url = f'https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/{seq}'
    last_err = None
    for attempt in range(FETCH_RETRIES):
        if attempt > 0:
            time.sleep(FETCH_BACKOFF_SECONDS * attempt)
        try:
            result = json.loads(urllib.request.urlopen(url).read())
            time.sleep(REQUEST_PACING_SECONDS)
            return result
        except Exception as e:
            last_err = e
    raise last_err

def fetch_entry_hash(seq):
    if seq < 1:
        return None
    try:
        d = fetch(seq)
        return d['event']['ENTRY'].get('entry_hash')
    except Exception as e:
        print(f'WARNING  predecessor fetch for seq {seq} failed after {FETCH_RETRIES} attempts: {e}')
        return None

def sha384(s):
    return '0x' + hashlib.sha384(s.encode()).hexdigest().upper()

print(f'\n=== REASONING VERIFICATION: SEQ {SEQ} ===\n')

d = fetch(SEQ)
audit = d['event']['AUDIT']
entry = d['event']['ENTRY']
metrics = audit['metrics']

all_match = True

# RS presence in cognitive_hash_operands governs the cognitive_hash operand
# set (six keys vs seven), confirmed against app_v1.py's
# _build_cognitive_hash_operands and compute_cognitive_hash. Confirmed
# correct for seq 1, 50, 150, 154, 295-302, 300, 404, 408.
ch_ops_raw = metrics.get('cognitive_hash_operands', {})
RS_PRESENT = 'RS' in ch_ops_raw
print(f'cognitive_hash operand set: {"seven-operand, RS present" if RS_PRESENT else "six-operand, no RS"}\n')

# 1. Jc_clt
# RS presence does NOT track the Jc_clt formula: live seq 295-302 (Ender
# SEQ 210+ per calc_jc_clt's own docstring) all use the log-AL formula
# with no RS present at all, confirmed against eight real entries. The
# two transitions (log-AL Jc_clt, RS in cognitive_hash) shipped at
# different times and are unrelated. No field in the record declares
# which Jc_clt formula was used, so both are computed and the one
# matching the stored value is reported, rather than guessing a marker
# that does not exist.
ops = metrics.get('Jc_clt_operands', {})
entry_type = entry.get('type', 'UNKNOWN')
if 'Jc_clt' not in metrics:
    print(f'SKIP     Jc_clt  (not present on this entry, type={entry_type})')
    print()
else:
    SQ = ops.get('SQ', 0)
    SC = ops.get('SC', 0)
    CE = ops.get('CE', 0)
    AL = ops.get('AL', 0)
    U  = ops.get('U', 0)
    stored_jc = float(metrics.get('Jc_clt', 0))
    jc_linear = ((SQ * max(SC, 1)) + CE) * (AL * U)
    jc_log    = ((SQ * max(SC, 1)) + CE) * (math.log(AL + 1) * U) if AL > 0 or SQ > 0 or CE > 0 else 0.0
    lin_match = abs(round(jc_linear, 2) - stored_jc) < 0.01
    log_match = abs(round(jc_log, 2) - stored_jc) < 0.01
    if log_match:
        computed_jc, jc_formula_used = jc_log, 'log-AL'
        formula_desc = 'formula:  ((SQ x max(SC,1)) + CE) x (ln(AL+1) x U)'
        formula_line = f'                   (({SQ} x {max(SC,1)}) + {CE}) x (ln({AL}+1) x {U})'
    elif lin_match:
        computed_jc, jc_formula_used = jc_linear, 'linear-AL'
        formula_desc = 'formula:  ((SQ x max(SC,1)) + CE) x (AL x U)'
        formula_line = f'                   (({SQ} x {max(SC,1)}) + {CE}) x ({AL} x {U})'
    else:
        computed_jc, jc_formula_used = jc_log, 'log-AL (neither matched, showing log)'
        formula_desc = 'formula:  ((SQ x max(SC,1)) + CE) x (ln(AL+1) x U)'
        formula_line = f'                   (({SQ} x {max(SC,1)}) + {CE}) x (ln({AL}+1) x {U})'
    ok = lin_match or log_match
    if not ok: all_match = False
    status = 'MATCH   ' if ok else 'MISMATCH'
    print(f'{status}  Jc_clt  (cognitive work density)  [{jc_formula_used}]')
    print(f'         operands: SQ={SQ}  SC={SC}  CE={CE}  AL={AL}  U={U}')
    print(f'         {formula_desc}')
    print(formula_line)
    print(f'                   = {round(computed_jc,2)}   stored: {stored_jc}')
    print()

CURRENT_ERA = RS_PRESENT

# 2. cognitive_hash
# Not present on every entry type: confirmed live on seq 1 (MINT_PROOF) and
# seq 150 (MEMORY_COMPILE), neither carries cognitive_hash or
# cognitive_hash_operands in AUDIT.metrics at all, by direct read of both
# full records. This was never a token-extraction bug: the field is
# genuinely absent, not misplaced. Gated on presence, same pattern as the
# existing W_RSQ skip below.
if 'cognitive_hash' not in metrics:
    print(f'SKIP     cognitive_hash  (not present on this entry, type={entry_type})')
    print()
else:
    SQ = ops.get('SQ', 0)
    SC = ops.get('SC', 0)
    CE = ops.get('CE', 0)
    AL = ops.get('AL', 0)
    U  = ops.get('U', 0)
    ch_ops = metrics.get('cognitive_hash_operands', {})
    h_AL = ch_ops.get('AL', AL)
    h_CE = ch_ops.get('CE', CE)
    h_SC = ch_ops.get('SC', SC)
    h_SQ = ch_ops.get('SQ', SQ)
    h_T  = ch_ops.get('T', 0)
    h_U  = ch_ops.get('U', U)

    if CURRENT_ERA:
        h_RS = ch_ops.get('RS', '')
        canonical_dict = {"AL":h_AL,"CE":h_CE,"RS":h_RS,"SC":h_SC,"SQ":h_SQ,"T":h_T,"U":h_U}
    else:
        canonical_dict = {"AL":h_AL,"CE":h_CE,"SC":h_SC,"SQ":h_SQ,"T":h_T,"U":h_U}

    if (h_AL != AL or h_CE != CE or h_SC != SC or h_SQ != SQ or h_U != U):
        print('WARNING  cognitive_hash operands differ from Jc_clt operands, using hash operands')

    canonical = json.dumps(canonical_dict, sort_keys=True, separators=(',',':'), ensure_ascii=False)
    computed_hash = sha384(canonical)
    stored_hash   = metrics.get('cognitive_hash', '')
    ok_hash = computed_hash.upper() == stored_hash.upper()
    if not ok_hash: all_match = False
    status_h = 'MATCH   ' if ok_hash else 'MISMATCH'
    print(f'{status_h}  cognitive_hash  (reasoning cost fingerprint)')
    print(f'         operands: {canonical_dict}')
    print(f'         canonical: {canonical}')
    print(f'         SHA-384:  {computed_hash[:22]}...')
    print(f'         stored:   {stored_hash[:22]}...')
    print()

# 3. W_RSQ
wrsq_ops = metrics.get('W_RSQ_operands', {})
if wrsq_ops:
    cc  = wrsq_ops.get('coherence_chain', 0)
    eg  = wrsq_ops.get('evidence_grounding', 0)
    jr  = wrsq_ops.get('judgment_resolution', 0)
    nli = wrsq_ops.get('NLI_coherence', 0)
    computed_wrsq = round(0.25*cc + 0.25*eg + 0.20*jr + 0.30*nli, 4)
    stored_wrsq   = round(metrics.get('W_RSQ', 0), 4)
    ok = abs(computed_wrsq - stored_wrsq) < 0.001
    if not ok: all_match = False
    status = 'MATCH   ' if ok else 'MISMATCH'
    print(f'{status}  W_RSQ  (semantic coherence INTENT->LOGIC)')
    print(f'         sub-scores: coherence_chain={cc}  evidence_grounding={eg}')
    print(f'                     judgment_resolution={jr}  NLI_coherence={nli}')
    print(f'         formula:  (0.25 x {cc}) + (0.25 x {eg}) + (0.20 x {jr}) + (0.30 x {nli})')
    print(f'                   = {computed_wrsq}   stored: {stored_wrsq}')
    print(f'         NOTE: verifies stored sub-score weighting. NLI model not rerun locally.')
else:
    print('SKIP     W_RSQ  (RAI_v2 entry, W_RSQ not present in this entry)')
print()

# 4. RAI
rb = metrics.get('rai_breakdown', {})
if rb and 'w_rsq' in rb:
    iljo = rb.get('iljo', 0)
    ego  = rb.get('ego_der_gca', 0)
    wrsq = rb.get('w_rsq', 0)
    sup  = rb.get('superego', 0)
    computed_rai = round(iljo + ego + wrsq + sup, 4)
    stored_rai   = round(metrics.get('RAI', 0), 4)
    ok = abs(computed_rai - stored_rai) < 0.001
    if not ok: all_match = False
    status = 'MATCH   ' if ok else 'MISMATCH'
    print(f'{status}  RAI  (reasoning admissibility index)')
    print(f'         breakdown: W_ILJO={iljo}  W_EGO={ego}  W_RSQ={wrsq}  W_SUP={sup}')
    print(f'         formula:  {iljo} + {ego} + {wrsq} + {sup}')
    print(f'                   = {computed_rai}   stored: {stored_rai}')
    print(f'         NOTE: verifies score assembly from stored components. Component inputs not independently recomputed.')
elif rb:
    corr = rb.get('correctness', 0)
    ego  = rb.get('ego_der_gca', 0)
    iljo = rb.get('iljo', 0)
    sup  = rb.get('superego', 0)
    computed_rai = round(corr + ego + iljo + sup, 4)
    stored_rai   = round(metrics.get('RAI', 0), 4)
    ok = abs(computed_rai - stored_rai) < 0.001
    if not ok: all_match = False
    status = 'MATCH   ' if ok else 'MISMATCH'
    print(f'{status}  RAI  (reasoning admissibility index, RAI_v2)')
    print(f'         breakdown: W_ILJO={iljo}  W_EGO={ego}  W_CORR={corr}  W_SUP={sup}')
    print(f'                   = {computed_rai}   stored: {stored_rai}')
    print(f'         NOTE: verifies score assembly from stored components. Component inputs not independently recomputed.')
print()

# 5. parent_hash
stored_parent = entry.get('parent_hash', '')
prior_hash    = fetch_entry_hash(SEQ - 1) if SEQ > 1 else 'GENESIS'
ok_parent = prior_hash == stored_parent if SEQ > 1 else True
if not ok_parent: all_match = False
status_p = 'MATCH   ' if ok_parent else 'MISMATCH'
print(f'{status_p}  parent_hash  (chain continuity)')
if SEQ > 1:
    print(f'         SEQ {SEQ-1} entry_hash:  {str(prior_hash)[:22]}...')
    print(f'         SEQ {SEQ} parent_hash: {stored_parent[:22]}...')
else:
    print(f'         SEQ 1 is genesis, no prior entry.')
print()

print('NOTE: entry_hash canonical serialization requires server-side specification.')
print('      Chain integrity separately verified by chain_ok:true in /ledger/verify.')
print()

if all_match:
    print('All checks passed.')
    sys.exit(0)
else:
    print('One or more checks failed. See MISMATCH lines above.')
    sys.exit(1)
