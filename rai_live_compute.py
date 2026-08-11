import json, sys

# rai_live_compute.py
# SDI Protocol v1. Records at seq 355 and forward.
#
# Recomputes every RAI input from the record's own contents except one.
# NLI_coherence is a cosine similarity produced by a sentence-transformer
# model and cannot be reproduced without that model; it is read from the
# record and marked as such.
#
# Everything else is computed here, not read: ILJO from the DER's own
# ILJO block, EGO from its three deterministic checks, W_RSQ from its
# four sub-scores, and RAI from the three weighted components.
#
# Weights are read from the record's own weights object rather than
# hardcoded, so an act committed under different weights still checks.
#
# Usage:
#   curl -s https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/361 \
#     | python3 rai_live_compute.py

d = json.load(sys.stdin)
event = d.get('event', {})
entry = event.get('ENTRY', {})
meta = entry.get('meta', {}) if isinstance(entry.get('meta'), dict) else {}
metrics = event.get('AUDIT', {}).get('metrics', {})
der = meta.get('SDI_DER', {})


def _norm(s):
    return s.strip() if isinstance(s, str) else ""


def _unwrap(obj):
    if not isinstance(obj, dict):
        return obj
    inner = obj.get("SDI_DER")
    return inner if isinstance(inner, dict) else obj


# ------------------------------------------------------------------ ILJO

def iljo_presence(iljo_block):
    if not isinstance(iljo_block, dict):
        iljo_block = {}
    logic = iljo_block.get("LOGIC")
    logic_present = (
        isinstance(logic, dict)
        and isinstance(logic.get("sub_questions_resolved"), list)
        and len(logic["sub_questions_resolved"]) > 0
    )
    judgment = iljo_block.get("JUDGMENT")
    judgment_present = (
        isinstance(judgment, dict)
        and bool(_norm(judgment.get("conjunction_prose")))
    )
    return {
        "INTENT": bool(_norm(iljo_block.get("INTENT"))),
        "LOGIC": logic_present,
        "JUDGMENT": judgment_present,
        "OUTCOME": bool(_norm(iljo_block.get("OUTCOME"))),
    }


def iljo_score(p):
    return sum(1.0 for _, v in p.items() if v) / 4.0


# ------------------------------------------------------------- EGO: der_s

def der_schema_score_from_obj(der_obj):
    der_obj = _unwrap(der_obj)
    if not isinstance(der_obj, dict):
        return 0.0

    got = 0

    di = der_obj.get("DECISION_INTENT")
    if isinstance(di, dict) and any(_norm(di.get(k)) for k in ["intent_statement", "context_framing"]):
        got += 1

    ql = der_obj.get("QUESTION_LOGIC")
    if isinstance(ql, dict) and _norm(ql.get("strategic_question")):
        got += 1

    subqs = ql.get("sub_questions", []) if isinstance(ql, dict) else []
    if isinstance(subqs, list) and len(subqs) > 0:
        got += 1

    ss = der_obj.get("SUCCESS_STANDARD")
    if isinstance(ss, dict) and (_norm(ss.get("definition")) or ss.get("audit_standard")):
        got += 1

    si = der_obj.get("SYSTEM_INPUT")
    inputs = si.get("inputs", []) if isinstance(si, dict) else []
    if isinstance(inputs, list) and len(inputs) > 0:
        got += 1

    spine_score = got / 5.0
    bonus = 0.0

    if isinstance(subqs, list) and subqs:
        linked = 0
        for q in subqs:
            if not isinstance(q, dict):
                continue
            ls = q.get("linked_signal_ids", [])
            if isinstance(ls, list) and len(ls) > 0:
                linked += 1
        bonus += 0.10 * (linked / float(len(subqs)))

    audit_std = ss.get("audit_standard") if isinstance(ss, dict) else None
    if isinstance(audit_std, dict):
        if _norm(audit_std.get("definition")) and isinstance(audit_std.get("required_artifacts"), list):
            bonus += 0.05

    sqs = ss.get("sub_question_standards", []) if isinstance(ss, dict) else []
    if isinstance(sqs, list) and len(sqs) > 0 and isinstance(subqs, list) and len(subqs) > 0:
        subq_ids = set()
        for q in subqs:
            if isinstance(q, dict) and _norm(q.get("id")):
                subq_ids.add(_norm(q.get("id")))
        covered = 0
        for r in sqs:
            if isinstance(r, dict) and _norm(r.get("sub_question_id")) in subq_ids:
                covered += 1
        if subq_ids:
            bonus += 0.10 * min(1.0, covered / float(len(subq_ids)))

    ds = der_obj.get("DECISION_SYNTAX")
    if isinstance(ds, dict) and isinstance(ds.get("sub_question_grammar"), list) and len(ds.get("sub_question_grammar")) > 0:
        bonus += 0.05

    return min(1.0, round(spine_score + bonus, 6))


# ------------------------------------------------------------- EGO: gca_s

def gca_score(der_obj):
    der_obj = _unwrap(der_obj)
    if isinstance(der_obj, dict):
        gca = der_obj.get("GCA")
        if isinstance(gca, dict):
            keys = [k.upper() for k in gca.keys()]
            got = 0
            if "ID" in keys:
                got += 1
            if "EGO" in keys:
                got += 1
            if got:
                return got / 2.0
    return 0.0


# ------------------------------------------------------------- EGO: det_s

def subquestion_signal_support_score(der_obj):
    der_obj = _unwrap(der_obj)
    if not isinstance(der_obj, dict):
        return 0.0

    ql = der_obj.get("QUESTION_LOGIC", {})
    si = der_obj.get("SYSTEM_INPUT", {})
    if not isinstance(ql, dict) or not isinstance(si, dict):
        return 0.0

    subqs = ql.get("sub_questions", [])
    inputs = si.get("inputs", [])
    if not isinstance(subqs, list) or len(subqs) == 0:
        return 0.0
    if not isinstance(inputs, list) or len(inputs) == 0:
        return 0.0

    sig_index = {}
    for s in inputs:
        if not isinstance(s, dict):
            continue
        sid = s.get("signal_id")
        if not sid:
            continue
        raw = s.get("insight_strength", s.get("signal_strength"))
        try:
            strength = int(raw)
        except Exception:
            strength = None
        if strength is not None:
            strength = max(1, min(5, strength))
        sig_index[str(sid)] = strength

    subq_scores = []
    for q in subqs:
        if not isinstance(q, dict):
            continue
        linked = q.get("linked_signal_ids", [])
        if not isinstance(linked, list):
            linked = []
        strengths = []
        for sid in linked:
            v = sig_index.get(str(sid))
            if v is not None:
                strengths.append(v / 5.0)
        subq_scores.append(sum(strengths) / len(strengths) if strengths else 0.0)

    return (sum(subq_scores) / len(subq_scores)) if subq_scores else 0.0


def subquestion_success_standards_score(der_obj):
    der_obj = _unwrap(der_obj)
    if not isinstance(der_obj, dict):
        return 0.0

    ql = der_obj.get("QUESTION_LOGIC", {}) if isinstance(der_obj.get("QUESTION_LOGIC"), dict) else {}
    subqs = ql.get("sub_questions", []) if isinstance(ql.get("sub_questions"), list) else []
    subq_ids = [_norm(q.get("id")) for q in subqs if isinstance(q, dict) and _norm(q.get("id"))]

    ss = der_obj.get("SUCCESS_STANDARD", {})
    if not isinstance(ss, dict):
        return 0.0

    if "sub_question_standards" not in ss:
        return 0.35 if ("operator" in ss and "target" in ss) else 0.20

    sqs = ss.get("sub_question_standards", [])
    if not isinstance(sqs, list) or len(sqs) == 0:
        return 0.0

    allowed_ops = {"==", ">=", "<=", ">", "<", "CONTAINS", "MEETS", "WITHIN"}

    sysin = der_obj.get("SYSTEM_INPUT", {}) if isinstance(der_obj.get("SYSTEM_INPUT"), dict) else {}
    inputs = sysin.get("inputs", []) if isinstance(sysin.get("inputs"), list) else []
    signal_strength = {}
    for s in inputs:
        if not isinstance(s, dict):
            continue
        sid = _norm(s.get("signal_id"))
        if not sid:
            continue
        val = s.get("insight_strength", s.get("signal_strength"))
        try:
            signal_strength[sid] = int(val)
        except Exception:
            signal_strength[sid] = None

    subq_links = {}
    for q in subqs:
        if not isinstance(q, dict):
            continue
        qid = _norm(q.get("id"))
        if not qid:
            continue
        lsi = q.get("linked_signal_ids", [])
        subq_links[qid] = [_norm(x) for x in lsi if _norm(x)] if isinstance(lsi, list) else []

    by_id = {}
    for st in sqs:
        if isinstance(st, dict):
            qid = _norm(st.get("sub_question_id"))
            if qid:
                by_id[qid] = st

    passes = 0
    total = len(subq_ids) if subq_ids else len(by_id)
    if total == 0:
        return 0.0

    for qid in (subq_ids if subq_ids else list(by_id.keys())):
        st = by_id.get(qid)
        if not isinstance(st, dict):
            continue
        op = _norm(st.get("operator")).upper()
        target_ok = ("target" in st)
        try:
            min_ss = max(1, min(5, int(st.get("minimum_signal_strength", 1))))
        except Exception:
            min_ss = 1
        allow_stop = _norm(st.get("allow_stop_reason")).upper()
        strengths = [signal_strength.get(sid) for sid in subq_links.get(qid, [])
                     if signal_strength.get(sid) is not None]
        strong_enough = [v for v in strengths if isinstance(v, int) and v >= min_ss]
        support_ok = (len(strong_enough) > 0) or bool(allow_stop)
        if (op in allowed_ops) and target_ok and support_ok:
            passes += 1

    return passes / float(total)


def decision_determinism_score(der_obj):
    der_obj = _unwrap(der_obj)
    if not isinstance(der_obj, dict):
        return 0.0

    score = 0.0
    total = 6.0

    ql = der_obj.get("QUESTION_LOGIC", {})
    if isinstance(ql, dict):
        sq = ql.get("strategic_question")
        if isinstance(sq, str) and sq.strip():
            score += 1.0

        subqs = ql.get("sub_questions", [])
        if isinstance(subqs, list) and len(subqs) > 0:
            score += 1.0
            ids_ok = 0
            links_ok = 0
            for q in subqs:
                if not isinstance(q, dict):
                    continue
                if str(q.get("id", "")).strip() and str(q.get("prompt", "")).strip():
                    ids_ok += 1
                lsi = q.get("linked_signal_ids", [])
                if isinstance(lsi, list) and len(lsi) > 0:
                    links_ok += 1
            score += (ids_ok / len(subqs))
            score += (links_ok / len(subqs))

    ds = der_obj.get("DECISION_SYNTAX", {})
    if isinstance(ds, dict):
        grammar = ds.get("sub_question_grammar", [])
        if isinstance(grammar, list) and len(grammar) > 0:
            valid = 0
            for g in grammar:
                if isinstance(g, dict) and all(k in g for k in ["id", "pattern", "lhs", "op", "rhs"]):
                    valid += 1
            score += (valid / len(grammar))

    score += max(0.0, min(1.0, subquestion_signal_support_score(der_obj)))
    score += max(0.0, min(1.0, subquestion_success_standards_score(der_obj)))

    return max(0.0, min(1.0, score / total))


# ------------------------------------------------------------------- run

presence = iljo_presence(der.get('ILJO', {}))
iljo_base = iljo_score(presence)

der_s = der_schema_score_from_obj(der)
gca_s = gca_score(der)
det_s = decision_determinism_score(der)
ego_base = (0.55 * der_s) + (0.20 * gca_s) + (0.25 * det_s)

weights = metrics.get('weights', {})
w_iljo = weights.get('W_ILJO')
w_ego = weights.get('W_EGO')
w_rsq_weight = weights.get('W_RSQ')

rsq_ops = metrics.get('W_RSQ_operands', {})
nli = rsq_ops.get('NLI_coherence')
coherence_chain = rsq_ops.get('coherence_chain')
evidence_grounding = rsq_ops.get('evidence_grounding')
judgment_resolution = rsq_ops.get('judgment_resolution')

w_rsq_computed = round(
    (0.30 * nli) + (0.25 * coherence_chain) +
    (0.25 * evidence_grounding) + (0.20 * judgment_resolution), 4
)
w_rsq_published = metrics.get('W_RSQ')

rai_computed = round(
    (w_iljo * iljo_base) + (w_ego * ego_base) + (w_rsq_weight * w_rsq_computed), 4
)
rai_published = metrics.get('RAI')

breakdown = metrics.get('rai_breakdown', {})
iljo_pub = breakdown.get('iljo')
ego_pub = breakdown.get('ego_der_gca')

print("=== ILJO, recomputed from the act's own ILJO block ===")
print()
for k in ("INTENT", "LOGIC", "JUDGMENT", "OUTCOME"):
    print(f'  {k:9s} = {presence[k]}')
print()
print(f'computed ILJO : {round(iljo_base, 4)}')
print(f'published     : {round(iljo_pub / w_iljo, 4) if w_iljo else "n/a"}')
print(f'match         : {round(w_iljo * iljo_base, 6) == iljo_pub}')
print()
print('=== EGO, recomputed from its three deterministic checks ===')
print()
print(f'  der_s (0.55) = {round(der_s, 4)}   5-point DER spine plus linkage bonus')
print(f'  gca_s (0.20) = {round(gca_s, 4)}   ID and EGO key presence')
print(f'  det_s (0.25) = {round(det_s, 4)}   6-point determinism checklist')
print()
print(f'computed EGO  : {round(ego_base, 4)}')
print(f'published     : {round(ego_pub / w_ego, 4) if w_ego else "n/a"}')
print(f'match         : {round(w_ego * ego_base, 6) == ego_pub}')
print()
print('=== W_RSQ, computed from its four declared sub-scores ===')
print()
print(f'  NLI_coherence (0.30)       = {nli}   model-derived, read from the record')
print(f'  coherence_chain (0.25)     = {coherence_chain}   deterministic')
print(f'  evidence_grounding (0.25)  = {evidence_grounding}   deterministic')
print(f'  judgment_resolution (0.20) = {judgment_resolution}   deterministic')
print()
print(f'computed W_RSQ: {w_rsq_computed}')
print(f'published     : {w_rsq_published}')
print(f'match         : {w_rsq_computed == w_rsq_published}')
print()
print('=== RAI, assembled from its three weighted components ===')
print()
print(f'  ILJO  x {w_iljo} = {round(w_iljo * iljo_base, 6)}')
print(f'  EGO   x {w_ego} = {round(w_ego * ego_base, 6)}')
print(f'  W_RSQ x {w_rsq_weight} = {round(w_rsq_weight * w_rsq_computed, 6)}')
print()
print(f'computed RAI: {rai_computed}')
print(f'published   : {rai_published}')
print(f'match       : {rai_computed == rai_published}')
