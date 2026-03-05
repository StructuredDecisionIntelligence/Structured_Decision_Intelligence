# Structured Decision Intelligence (SDI)

**An open protocol for auditable, deterministic AI reasoning.**

SDI is a governance framework that structures how AI systems reason, record, and commit decisions. It defines a formal schema for AI-generated reasoning artifacts, a deterministic compile gate that validates them, and an append-only ledger that preserves them as an auditable chain of institutional memory.

The protocol is designed to operate across AI providers — any model that can produce structured output can be governed under SDI.

---

## What the protocol defines

**Decision Execution Record (DER)**
A structured JSON schema that every governed reasoning turn must produce. The DER captures intent, logic decomposition, signal scoring, governance anchors, judgment, and outcome in a single verifiable artifact. It is provider-agnostic and model-agnostic.

**Compile Gate**
A deterministic validator that checks every DER before it can be committed. The gate enforces required schema sections, governance anchor presence, signal scoring rules, and boundedness constraints. A DER either compiles PASS or fails with explicit errors — no partial credit.

**ILJO Reasoning Sequence**
The governed reasoning path every DER must traverse: Intent → Logic → Judgment → Outcome. Each stage is a named, auditable field. The outcome is only rendered after all prior stages are structurally present and validated.

**Governance Constants**
Protocol-level anchors that must be present in every committed DER:
- `SOVEREIGNTY` — human oversight is preserved and binding
- `PRIMUM` — no harm principle, structurally enforced
- `BOUNDEDNESS` — reasoning scope is constrained and time-boxed
- `STOP_ON_UNCERTAINTY` — governed refusal when signal is insufficient

**STOP Path**
When a question cannot be answered with sufficient grounded signal, the protocol produces a STOP DER — a structurally valid refusal artifact that compiles PASS and commits to the ledger as a governed non-answer. This is correct protocol behavior, not a failure.

**Institutional Memory Ledger**
An append-only, hash-chained ledger that records every committed DER. Each entry includes a parent hash, entry hash, and CAS-ordered sequence number. The chain is independently verifiable. No reasoning turn is rendered to a user until it has been committed.

---

## Protocol version

`SDI_PROTOCOL_v1` · DER schema `SDI_DER_v1.1`

---

## Repository contents

| File | Description |
| :--- | :--- |
| `SDI_Core_Syntax_Kernel` | Core grammar rules for DER structure and ILJO sequence |
| `SDI_Protocol_Manifest_v1.0.0` | Protocol identity, governance constants, anchor definitions |
| `immutable_decision_ledger_format.json` | Ledger entry schema and chain-of-custody format |
| `foresight_simulation_parameters.json` | Bounded prediction constraints |
| `sdi_syntax_patterns` | Formal syntax patterns for governed reasoning |

---

## Implementation

The reference implementation — including the compile gate, ledger backend, shell orchestration layer, and GlassBox demo — is maintained separately. The demo is available at [demo.sdi-protocol.org](https://demo.sdi-protocol.org) and runs three governed reasoning turns across a live AI provider, committing each turn to a hash-chained ledger in real time.

---

## NIST AI RMF alignment

SDI maps to the NIST AI Risk Management Framework across its core functions:

| SDI Component | NIST AI RMF Reference |
| :--- | :--- |
| DER schema validation | MAP 1.1 — Context establishment |
| Signal scoring (insight dimensions) | MEASURE 2.3 — Data quality |
| Compile gate accuracy check | MEASURE 2.5 — AI accuracy assessment |
| ILJO reasoning path | GOVERN 1.2 — Accountability |
| Governance anchors (SOVEREIGNTY, PRIMUM) | MANAGE 2.2 — Risk treatment |
| Ledger chain verification | MANAGE 4.1 — Traceability |

---

## Protocol governance

The SDI protocol is maintained by Structured Decision Intelligence LLC.

**Author:** Don Johnson, Protocol Architect
**Contact:** donjohnson.sdi@gmail.com
**Protocol signal:** `SDI_PROTOCOL_v1 // ILJO // GOVERNED`

---

## License

SDI Commons License. Permission is granted to interpret, implement, or extend this protocol provided that the governance constants — `SOVEREIGNTY`, `PRIMUM`, `BOUNDEDNESS`, `STOP_ON_UNCERTAINTY` — remain structurally enforced in any derivative implementation.
