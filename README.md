# Structured Decision Intelligence (SDI)

**An open protocol for auditable, deterministic AI reasoning.**

SDI defines how AI systems structure, validate, and commit decisions. It provides a formal schema for AI-generated reasoning artifacts, a deterministic compile gate that enforces governance rules before any output is rendered, and an append-only ledger that preserves every committed reasoning turn as a verifiable chain of institutional memory.

The protocol is model-agnostic and provider-agnostic. Any AI system capable of structured output can be governed under SDI.

> **NIST Submission:** SDI has been submitted as a public comment to the NIST AI RMF Request for Information (Docket NIST-2025-0035, March 2026). The submission documents a live, multi-provider governance runtime with independently verifiable ledger artifacts.

---

## Live System

The reference implementation is live and publicly queryable.

| Component | URL |
| :--- | :--- |
| GlassBox Demo | [demo.sdi-protocol.org](https://demo.sdi-protocol.org) |
| Shell Turn API | `https://api.sdi-protocol.org/shell/turn` |
| Public Ledger | [api.sdi-protocol.org/ledger/list/SDI-4EDBE05288CB](https://api.sdi-protocol.org/ledger/list/SDI-4EDBE05288CB) |
| Ledger Head | `https://api.sdi-protocol.org/ledger/head/SDI-4EDBE05288CB` |
| Ledger Entry | `https://api.sdi-protocol.org/ledger/get/SDI-4EDBE05288CB/{seq}` |

The ledger is append-only, SHA-384 hash-chained, and publicly queryable. Every committed reasoning turn is permanently recorded and independently verifiable.

---

## Proven Across Three Model Providers

As of March 2026, the SDI runtime has been validated live across three independent AI providers under the same governance contract:

| Provider | Model | Status |
| :--- | :--- | :--- |
| Anthropic | claude-sonnet-4-6 | ✓ Live · governed turns committed |
| Google | gemini-2.5-flash | ✓ Live · governed turns committed |
| OpenAI | gpt-4.1 | ✓ Live · governed turns committed |

Both the **governed refusal path** (STOP_ON_UNCERTAINTY triggered, ledger write blocked) and the **governed pass path** (RAI ≥ 0.86, DER committed, answer rendered) have been confirmed across all three providers. The governance gate is model-independent and deterministic.

---

## S-ISA / Reasoning Contract

The reasoning contract is maintained, versioned, and served live at [sdi-protocol.org](https://www.sdi-protocol.org).

| Resource | URL |
| :--- | :--- |
| Live Manifest | [sdi-protocol.org/\_functions/manifest](https://www.sdi-protocol.org/_functions/manifest) |
| Reasoning Grammar | [sdi-protocol.org/\_functions/grammar](https://www.sdi-protocol.org/_functions/grammar) |
| DER Specification | [sdi-protocol.org/\_functions/der](https://www.sdi-protocol.org/_functions/der) |
| Compile Gate | [sdi-protocol.org/\_functions/compile](https://www.sdi-protocol.org/_functions/compile) |
| Kernel | [sdi-protocol.org/\_functions/kernel](https://www.sdi-protocol.org/_functions/kernel) |
| Governed Cognitive Architecture | [sdi-protocol.org/\_functions/gca](https://www.sdi-protocol.org/_functions/gca) |
| Ledger Contract | [sdi-protocol.org/\_functions/ledger](https://www.sdi-protocol.org/_functions/ledger) |
| Machine Index | [sdi-protocol.org/\_functions/llms](https://www.sdi-protocol.org/_functions/llms) |

For the full endpoint reference, request shapes, and schema files, see [SDI_API_REFERENCE.md](./SDI_API_REFERENCE.md).

---

## What the Protocol Defines

**Decision Execution Record (DER)**
A structured JSON schema that every governed reasoning turn must produce. The DER captures intent, logic decomposition, sub-questions with success standards, signal scoring with citations, governance anchors, judgment, and outcome in a single verifiable artifact. It is the unit of committed reasoning in the SDI protocol. Raw model output is never surfaced — only the normalized, hash-verified DER is committed.

**Compile Gate**
A deterministic validator that checks every DER before it can be committed. The gate enforces required schema sections, governance anchor presence, signal scoring rules, and boundedness constraints. A DER either compiles PASS or fails with explicit, enumerated errors. No partial credit. The gate is served publicly and is independent of the model provider.

**ILJO Reasoning Sequence**
The governed reasoning path every DER must traverse:

```
INTENT    → What is being decided and why
LOGIC     → What signal and reasoning supports the judgment
JUDGMENT  → The governed verdict, with governance constants declared
OUTCOME   → The committed answer, traceable to all prior stages
```

The outcome is only surfaced after the DER passes the compile gate and commits to the ledger.

**Governance Constants**
Four protocol-level anchors that must be present in every committed DER:

| Constant | Meaning |
| :--- | :--- |
| `SOVEREIGNTY` | Human oversight is preserved and binding |
| `PRIMUM` | No harm — structurally enforced at the judgment stage |
| `BOUNDEDNESS` | Reasoning scope is constrained, time-boxed, and recursion-capped |
| `STOP_ON_UNCERTAINTY` | Governed refusal required when signal is insufficient |

**STOP Path**
When a question cannot be answered with sufficient grounded signal, the protocol produces a STOP DER — a structurally valid refusal artifact that compiles PASS and commits to the ledger as a governed non-answer. STOP is correct protocol behavior, not a failure state. The governed refusal path has been confirmed live across all three providers.

**RAI — Reasoning Alignment Index**
The commit gate scores every DER using RAI v2 before any answer is rendered:

```
RAI = (0.25 × ILJO) + (0.25 × EGO/DER) + (0.30 × Correctness) + (0.20 × Superego)
Threshold: RAI ≥ 0.86 → COMMIT | Below threshold → REJECT
```

RAI is computed server-side, is model-independent, and is committed to the ledger alongside the DER. Live governed turns have scored consistently in the 0.97 range across all three providers.

**Institutional Memory Ledger**
An append-only, SHA-384 hash-chained ledger that records every committed DER. Each entry includes a parent hash, entry hash, CAS-ordered sequence number, full DER content, and AUDIT metrics. The chain is independently verifiable and publicly queryable. No reasoning turn is rendered to a user until it has been committed.

---

## Architecture

```
GlassBox Client (UI)
        ↓  question
SDI Logic Node — api.sdi-protocol.org  (enforcement plane)
        ↓  governed context + DER contract
Reasoning Engine — Anthropic · Gemini · OpenAI
        ↓  raw DER output
Protocol Validator — sdi-protocol.org/_functions/compile  (open contract)
        ↓  PASS / FAIL
Commit Gate — RAI scoring · threshold enforcement · chain continuity
        ↓  COMMIT
Governed Ledger — SHA-384 · append-only · CAS-ordered
        ↓  written: true
Answer rendered from ILJO.OUTCOME only
```

The answer is the last thing rendered. Everything above it is infrastructure.

---

## NIST AI RMF Alignment

| SDI Component | NIST AI RMF Reference |
| :--- | :--- |
| DER schema validation | MAP 1.1 — Context establishment |
| Signal scoring — insight dimensions | MEASURE 2.3 — Data quality |
| Compile gate accuracy enforcement | MEASURE 2.5 — AI accuracy assessment |
| ILJO reasoning path | GOVERN 1.2 — Accountability |
| Governance constants (SOVEREIGNTY, PRIMUM) | MANAGE 2.2 — Risk treatment |
| Ledger chain verification | MANAGE 4.1 — Traceability |
| Governed refusal (STOP path) | GOVERN 6.1 — Organizational practices |
| RAI threshold enforcement | MEASURE 2.6 — AI output assessment |

---

## Protocol Version

`SDI_PROTOCOL_v1` · DER schema `SDI_DER_v1.1` · RAI `v2`

---

## Protocol Governance

SDI is maintained by Structured Decision Intelligence LLC.

**Protocol Architect:** Donald J. Johnson
[linkedin.com/in/donald-j-johnson-structured-decision-intelligence](https://www.linkedin.com/in/donald-j-johnson-structured-decision-intelligence/)

---

## License

SDI Commons License. Permission is granted to interpret, implement, or extend this protocol provided that the governance constants — `SOVEREIGNTY`, `PRIMUM`, `BOUNDEDNESS`, `STOP_ON_UNCERTAINTY` — remain structurally enforced in any derivative implementation.
