# Structured Decision Intelligence (SDI)

**An open protocol for auditable, deterministic AI reasoning.**

SDI defines how AI systems structure, validate, and commit decisions. It provides a formal schema for AI-generated reasoning artifacts, a deterministic compile gate that enforces governance rules before any output is rendered, and an append-only ledger that preserves every committed reasoning turn as a verifiable chain of institutional memory.

The protocol is model-agnostic and provider-agnostic. Any AI system capable of structured output can be governed under SDI.

---

## S-ISA / Reasoning Contract

These resources expose the live contract behind Structured Decision Intelligence. They define the structure, validation rules, governance constants, and runtime boundaries that separate AI generation from committed system state.

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

## What the protocol defines

**Decision Execution Record (DER)**
A structured JSON schema that every governed reasoning turn must produce. The DER captures intent, logic decomposition, signal scoring, governance anchors, judgment, and outcome in a single verifiable artifact. It is the unit of committed reasoning in the SDI protocol.

**Compile Gate**
A deterministic validator that checks every DER before it can be committed. The gate enforces required schema sections, governance anchor presence, signal scoring rules, and boundedness constraints. A DER either compiles PASS or fails with explicit, enumerated errors. No partial credit.

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
When a question cannot be answered with sufficient grounded signal, the protocol produces a STOP DER — a structurally valid refusal artifact that compiles PASS and commits to the ledger as a governed non-answer. STOP is correct protocol behavior, not a failure state.

**Institutional Memory Ledger**
An append-only, hash-chained ledger that records every committed DER. Each entry includes a parent hash, entry hash, and CAS-ordered sequence number. The chain is independently verifiable. No reasoning turn is rendered to a user until it has been committed.

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

---

## Protocol Version

`SDI_PROTOCOL_v1` · DER schema `SDI_DER_v1.1`

---

## Implementation

The reference implementation — including the compile gate, ledger backend, shell orchestration layer, and GlassBox transparency demo — is maintained separately. The GlassBox demo runs three governed reasoning turns across a live AI provider, committing each turn to a hash-chained ledger in real time, with full reasoning visibility at every stage of the governance path.

Demo: [demo.sdi-protocol.org](https://demo.sdi-protocol.org)

---

## Protocol Governance

SDI is maintained by Structured Decision Intelligence LLC.

**Protocol Architect:** Donald J. Johnson
[linkedin.com/in/donald-j-johnson-structured-decision-intelligence](https://www.linkedin.com/in/donald-j-johnson-structured-decision-intelligence/)
donjohnson.sdi@gmail.com

---

## License

SDI Commons License. Permission is granted to interpret, implement, or extend this protocol provided that the governance constants — `SOVEREIGNTY`, `PRIMUM`, `BOUNDEDNESS`, `STOP_ON_UNCERTAINTY` — remain structurally enforced in any derivative implementation.
