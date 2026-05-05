# Structured Decision Intelligence (SDI)

**The first Reckoner Machine: a computing architecture whose primitive is the governed reasoning act.**

SDI defines how AI systems structure, validate, and commit reasoning. Every governed turn produces a Decision Execution Record (DER), evaluated at a two-phase compile gate before it may advance the hash-chained ledger. The model generates. The gate governs. The ledger remembers.

The protocol is model-agnostic and provider-agnostic. Any AI system capable of structured output can be governed under SDI. The reasoning contract is open and publicly verifiable.

> **NIST Submission:** SDI has been submitted as a public comment to the NIST AI Risk Management Framework Request for Information (Docket NIST-2025-0035, March 2026). The submission documents a live, multi-provider governance runtime with independently verifiable ledger artifacts.

> **USPTO Patent Application:** 19/425,875. Copyright TXu 2-498-043.

---

## Live System

The reference implementation is live and publicly queryable. No account or API key required to verify the chain.

| Component | URL |
| :--- | :--- |
| Foundations | [sdi-protocol.org/foundations](https://www.sdi-protocol.org/foundations) |
| Transparency | [sdi-protocol.org/transparency](https://www.sdi-protocol.org/transparency) |
| Agent Portal | [agents.sdi-protocol.org](https://agents.sdi-protocol.org) |
| Minting Terminal | [mint.sdi-protocol.org](https://mint.sdi-protocol.org) |
| Public Ledger (Longview) | [api.sdi-protocol.org/ledger/list/SDI-5AA8C82A2537](https://api.sdi-protocol.org/ledger/list/SDI-5AA8C82A2537) |
| Chain Verification | `https://api.sdi-protocol.org/ledger/verify/SDI-5AA8C82A2537?hashes_only=true` |
| Ledger Entry | `https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/{seq}` |

The Longview chain (SDI-5AA8C82A2537) is the primary public chain. It is append-only, SHA-384 hash-chained, and publicly queryable from entry 1 to the current tip. The demo chain (SDI-4EDBE05288CB) is the NIST submission chain and is not publicly readable.

---

## Verify the Chain in 30 Seconds

```bash
curl -s 'https://api.sdi-protocol.org/ledger/verify/SDI-5AA8C82A2537?hashes_only=true' \
  | python3 -m json.tool | grep -E "chain_ok|files|tip_seq"
```

`chain_ok: true` confirms the full chain is hash-continuous from entry 1 to the current tip. No SDI software required. Standard curl and Python only.

Pull any entry:

```bash
curl -s https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/154 \
  | python3 -m json.tool
```

---

## Independent Governance Metric Verification

`verify_sdi_entry.py` in this repository recomputes five governance metrics from declared operands in any public chain entry and prints MATCH or MISMATCH for each. No SDI client software, account, or API key required. Standard Python 3 only.

```bash
python3 verify_sdi_entry.py
```

Change `SEQ = 154` at the top of the file to any entry number. Five MATCHes confirms the governance stack for that entry is self-consistent and independently verifiable.

**What each MATCH proves:**

| Metric | What it confirms |
| :--- | :--- |
| `cognitive_hash` | SHA-384 of six declared operands matches the stored hash. Operands cannot be changed without breaking it. |
| `Jc_clt` | Cognitive work density score follows arithmetically from five structural operands. A fabricated entry cannot produce realistic Jc without those operands present. |
| `W_RSQ` | Semantic coherence score assembled from four sub-scores using published weights. Three of four sub-scores are fully recomputable. |
| `RAI` | Reasoning Admissibility Index computed by summing four weighted components. Assembly verifiable from stored operands. |
| `parent_hash` | Declared predecessor matches the actual prior entry. Chain continuity confirmed at this position. |

---

## Proven Across Three Model Providers

As of May 2026, the SDI runtime has been validated live across three independent frontier model providers under the same governance contract and compile gate:

| Provider | Model | Status |
| :--- | :--- | :--- |
| Anthropic | claude-sonnet-4-6 | Live · governed turns committed |
| Google | gemini-2.5-flash | Live · governed turns committed |
| OpenAI | gpt-4.1 | Live · governed turns committed |

The governed refusal path (STOP_ON_UNCERTAINTY triggered, ledger write blocked) and the governed pass path (RAI above threshold, DER committed, answer rendered) have been confirmed across all three providers. The compile gate is model-independent and deterministic: the same artifact always produces the same result regardless of which provider produced it.

The first three-provider governed reasoning chain committed to the public ledger is independently verifiable at SEQ 154 (Anthropic), SEQ 156 (OpenAI), and SEQ 157 (Gemini).

---

## The Reckoner Architecture

```
Reasoner (human) poses a question
        |
        v
SDI Logic Node — api.sdi-protocol.org  (enforcement plane)
        |
        v  governed context + ILJO reasoning contract
Inference Processor — Anthropic / Gemini / OpenAI  (interchangeable)
        |
        v  raw DER output
PHASE 1 — Schema gate: ILJO structure, governance anchors, schema conformance
        |  fail-fast, near-zero compute cost
        v
PHASE 2 — Commit gate sequence (ascending compute cost):
          1. Identity binding: sovereign hash + parent hash verified
          2. Schema re-validation at append time
          3. Jc floor: cognitive work density measured
          4. RAI_v3 with semantic commit gate: reasoning quality evaluated
          5. Server writes to ledger. Cognitive hash committed.
        |
        v
Governed Ledger — SHA-384 hash-chained · append-only · publicly verifiable
        |
        v
Answer rendered from ILJO.OUTCOME only
```

The model has no write access to the ledger. The server is the enforcement plane. The answer is the last thing rendered.

---

## What the Protocol Defines

**Decision Execution Record (DER)**
A structured JSON schema that every governed reasoning turn must produce. The DER captures intent, logic decomposition, sub-questions with success standards, signal scoring with citations, governance anchors, judgment, and outcome in a single verifiable artifact. It is the unit of committed reasoning in the SDI protocol. The governed DER is to the Reckoner Machine what the instruction is to Von Neumann's stored-program computer: the fundamental unit the system was built to process, govern, and accumulate.

**ILJO Reasoning Grammar**
The reasoning contract every DER must satisfy:

```
INTENT    → What is being decided and why
LOGIC     → What signal and reasoning supports the judgment
JUDGMENT  → The governed verdict, with governance constants declared
OUTCOME   → The committed answer, traceable to all prior stages
```

ILJO is in natural language because the inference processor is a natural language processor. The full grammar specification is on the Protocol page.

**Two-Phase Compile Gate**
Phase 1 is a fail-fast schema gate: structural conformance, ILJO sections present, governance anchors acknowledged. Near-zero compute cost. Phase 2 is the commit gate sequence: identity binding, schema re-validation, Jc floor, RAI_v3 with semantic commit gate, and server-side ledger write. The compile gate is structurally independent of the model. The model cannot override it.

**Reasoning Admissibility Index (RAI_v3)**

```
RAI = (0.25 × W_ILJO) + (0.25 × W_EGO) + (0.30 × W_RSQ) + (0.20 × W_SUP)

W_RSQ = (0.25 × coherence_chain) + (0.25 × evidence_grounding)
      + (0.20 × judgment_resolution) + (0.30 × NLI_coherence)

Threshold: RAI >= 0.78 → COMMIT | Below threshold → REJECT
```

W_RSQ replaces the prior hardcoded W_CORR = 1.0. The semantic commit gate evaluates INTENT-to-LOGIC topical coherence using a structurally independent bi-encoder model. Full formula and operand specification on the Protocol page.

**Jc — Cognitive Work Density**
Computed from five structural operands extracted directly from the DER. A fabricated DER with empty fields produces near-zero Jc and is rejected before quality evaluation runs. A fully executed governed turn produces Jc in the hundreds to thousands. The Jc floor is a substrate-integrity requirement: it ensures the ledger cannot be poisoned by syntactically valid hollow entries.

**Cognitive Hash**
SHA-384 of six operands: the five Jc operands plus total tokens consumed. Independently recomputable from any public chain entry. Fingerprints the full cost and structure of the turn at the moment of commitment.

**Governance Constants**
Four protocol-level anchors present in every committed DER:

| Constant | Meaning |
| :--- | :--- |
| `SOVEREIGNTY` | Human oversight is preserved and binding |
| `PRIMUM` | No harm, structurally enforced at the judgment stage |
| `BOUNDEDNESS` | Reasoning scope is constrained, time-boxed, and recursion-capped |
| `STOP_ON_UNCERTAINTY` | Governed refusal required when signal is insufficient |

**STOP Path**
When a question cannot be answered with sufficient grounded signal, the protocol produces a STOP DER: a structurally valid refusal artifact that compiles PASS and commits to the ledger as a governed non-answer. STOP is correct protocol behavior, not a failure state.

**Governed Memory Synthesis**
At regular intervals the memory compiler reads the full chain and synthesizes prior governed reasoning acts into a new governed artifact in the same ILJO grammar, subject to the same compile gate, and hash-anchored to every entry it covers. This is not a summary. It is a reasoning act about prior reasoning acts, permanently committed and verifiable. The architecture is hierarchical: periodic compiles roll up into epoch syntheses, epoch syntheses into biography-level governed positions.

**Predictive Reckoning**
Every governed turn from SEQ 154 forward contains two additional fields. OUTCOME_PLAN is a forward-directed commitment: the agent states what it predicts will be true if the current reasoning holds. GOVERNED_RECKONING is a retrospective declaration: the agent returns to prior commitments and declares REINFORCED, CONTRADICTED, EXTENDED, or INCONCLUSIVE with evidence citation. Prediction track records are permanently visible in the chain.

---

## The Reckoner Machine Reasoning Thread

SEQ 154 through SEQ 168 is a governed reasoning thread in which the Longview agent reasoned about the Reckoner Machine architecture from first principles without being told the name, the category, or the prior art. Every entry is publicly verifiable.

| SEQ | Provider | RAI | What was governed |
| :--- | :--- | :--- | :--- |
| 154 | Anthropic | 0.8768 | Reckoner Machine named from etymology. First RAI_v3, cognitive hash, W_RSQ, Predictive Reckoning on Longview. |
| 155 | Anthropic | 0.9336 | Dead Reckoner and The Reckoning derived from navigation analogy. |
| 156 | OpenAI | 0.8918 | Prior art table across ten system categories. P2+P4 minimum novelty gap established. |
| 157 | Gemini | 0.8647 | Compile gate as fail-fast novel composition. Ashby's Law applied to structural independence. |
| 158 | Anthropic | 0.8930 | Pipeline objection rebutted. New unit of operation vs new primitive distinction. |
| 159 | Anthropic | 0.9227 | Three-way record type distinction. Constituted act finding. |
| 160 | Anthropic | 0.9191 | Predictive Reckoning governed. |
| 161 | Anthropic | 0.9054 | Chain evolution as schema versioning not inconsistency. |
| 162 | Anthropic | 0.9035 | Always-possible claim with precise falsification condition. |
| 163 | Anthropic | 0.8788 | Plain language description. Adversarial test question. |
| 164 | Anthropic | 0.9334 | Conjunctive work-factor security. SHA-384 boundary-level disclosure. |
| 165 | OpenAI | 0.9423 | Quantum trust layer analysis confirmed. |
| 166 | Anthropic | 0.8684 | Ec = I x S2 implications for builders. Shannon analogy confirmed. |
| 167 | Anthropic | verify | Self-audit: five properties demonstrated from chain evidence. Functional equivalence class finding. |
| 168 | Anthropic | verify | Governed self-reference finding. Bootstrap problem closed. |

Pull any entry: `curl -s https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/[SEQ] | python3 -m json.tool`

---

## Reasoning Contract Endpoints

| Resource | URL |
| :--- | :--- |
| Live Manifest | [sdi-protocol.org/_functions/manifest](https://www.sdi-protocol.org/_functions/manifest) |
| Reasoning Grammar | [sdi-protocol.org/_functions/grammar](https://www.sdi-protocol.org/_functions/grammar) |
| DER Specification | [sdi-protocol.org/_functions/der](https://www.sdi-protocol.org/_functions/der) |
| Compile Gate | [sdi-protocol.org/_functions/compile](https://www.sdi-protocol.org/_functions/compile) |
| Kernel | [sdi-protocol.org/_functions/kernel](https://www.sdi-protocol.org/_functions/kernel) |
| Governed Cognitive Architecture | [sdi-protocol.org/_functions/gca](https://www.sdi-protocol.org/_functions/gca) |
| Ledger Contract | [sdi-protocol.org/_functions/ledger](https://www.sdi-protocol.org/_functions/ledger) |
| Machine Index | [sdi-protocol.org/_functions/llms](https://www.sdi-protocol.org/_functions/llms) |

For the full endpoint reference and schema files see [SDI_API_REFERENCE.md](./SDI_API_REFERENCE.md).

---

## NIST AI RMF Alignment

| SDI Component | NIST AI RMF Reference |
| :--- | :--- |
| DER schema validation | MAP 1.1 — Context establishment |
| Signal scoring and evidence grounding | MEASURE 2.3 — Data quality |
| Two-phase compile gate | MEASURE 2.5 — AI accuracy assessment |
| ILJO reasoning grammar | GOVERN 1.2 — Accountability |
| Governance constants (SOVEREIGNTY, PRIMUM) | MANAGE 2.2 — Risk treatment |
| SHA-384 hash-chained ledger | MANAGE 4.1 — Traceability |
| STOP path governed refusal | GOVERN 6.1 — Organizational practices |
| RAI_v3 threshold enforcement | MEASURE 2.6 — AI output assessment |
| Semantic commit gate (structural independence) | GOVERN 1.4 — Organizational practices |
| Cognitive hash work-factor | MEASURE 2.7 — AI output assessment |

---

## Protocol Version

`SDI_PROTOCOL_v1` · DER schema `SDI_DER_v1.1` · RAI `v3` · Compile gate `two-phase`

---

## Protocol Governance

SDI is maintained by Structured Decision Intelligence LLC.

**Protocol Architect:** James Johnson
[linkedin.com/in/donald-j-johnson-structured-decision-intelligence](https://www.linkedin.com/in/donald-j-johnson-structured-decision-intelligence/)

---

## License

SDI Commons License. Permission is granted to interpret, implement, or extend this protocol provided that the governance constants, SOVEREIGNTY, PRIMUM, BOUNDEDNESS, STOP_ON_UNCERTAINTY, remain structurally enforced in any derivative implementation.

Any system satisfying all five Reckoner Machine properties with a consistent grammar at both commitment and retrieval boundaries qualifies as a Reckoner Machine. SDI is the first implementation. The class is open.
