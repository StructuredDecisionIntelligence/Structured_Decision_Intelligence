# Structured Decision Intelligence (SDI)

**Diagnostic instruments and public contracts for inspecting a reasoning computer.**

This repository is not a codebase. The SDI kernel is not here. What is here
is everything needed to check the system's claims from the outside: scripts
that recompute the seals and scores on real committed reasoning acts, and
pointers to the live contract endpoints that define what a valid act is.
The machine itself lives at [sdi-protocol.org](https://www.sdi-protocol.org).
That site asks to be checked rather than believed. This repository is how.

> **NIST Submission:** The SDI specification was submitted as a public
> comment to the NIST AI Risk Management Framework Request for Information
> (Docket NIST-2025-0035, March 2026). Submission is participation in a
> public process, not endorsement by NIST.
>
> **USPTO Patent Application:** 19/425,875 (pending). Copyright TXu 2-498-043.

---

## Liveness, thirty seconds

Chromite (SDI-5AA8C82A2537) is SDI's public agent, commissioned to reason
about the protocol itself. Its chain is append-only, SHA-384 hash-chained,
and publicly readable. Pull the ten most recent sealed acts:

```
curl -s "https://api.sdi-protocol.org/ledger/recent/SDI-5AA8C82A2537?n=10" | python3 -m json.tool
```

The response is raw sealed records: entry and parent hashes, gate-computed
scores, cited evidence with capture times, and acts that examine and
resolve one another across the chain. Recent acts span multiple model
providers on one unbroken hash sequence. The response also states the
total acts on chain, so freshness is checkable from the payload itself.

Pull any single act by sequence number:

```
curl -s https://api.sdi-protocol.org/ledger/get/SDI-5AA8C82A2537/404 | python3 -m json.tool
```

Verify chain continuity end to end:

```
curl -s "https://api.sdi-protocol.org/ledger/verify/SDI-5AA8C82A2537?hashes_only=true" | python3 -m json.tool
```

`chain_ok: true` confirms hash continuity from genesis to the current tip.
No SDI software, account, or API key required. Standard curl and Python.

---

## The instruments

Each script recomputes something the system claims, from a pulled record's
own contents, and prints what it found. Each maps to a section of the
[verify page](https://www.sdi-protocol.org/verify), which walks the same
checks with current examples and publishes SHA-256 checksums for every
script here.

| Script | What it recomputes | What a match proves |
| --- | --- | --- |
| `extract_record.py` | Pulls the governed answer and core fields out of a raw entry | The record reads as reasoning, not just as data |
| `recompute_entry_hash.py` | The entry's SHA-384 seal from its canonical chain packet | The act's position and content cannot be altered without breaking the seal |
| `recompute_cognitive_hash.py` | The cognitive hash from the act's declared work operands | The recorded reasoning work is fingerprinted, not asserted |
| `jc_clt_live_compute.py` | The cognitive work density score from structural operands | The work floor follows arithmetically from what the act declares |
| `jc_per_joule_live_compute.py` | Work density per unit of compute | The efficiency figure derives from the record, not from marketing |
| `rai_live_compute.py` | The reasoning admissibility score from its published weights | The commit threshold was met by computation, not by assertion |
| `verify_sdi_entry.py` | All governance metrics on one entry, printing MATCH or MISMATCH per metric | The full governance stack for that act is self-consistent and independently verifiable |

### Test the instruments themselves

`example_record.json` is a real committed act (Chromite, seq 404), pulled
verbatim from the public chain and committed here so the instruments can
be verified before pointing them at anything live. Run any script against
it offline; the seals and scores inside it recompute like any other entry.
Its SHA-256 is stated in the commit that added it, and the same record is
always available live at the pull-any-entry URL above, so the committed
copy can itself be checked against the chain.

```
python3 extract_record.py < example_record.json
```

Run the full check on a live entry:

```
python3 verify_sdi_entry.py
```

Change the `SEQ` value at the top of the file to any entry number. Every
MATCH is a claim the system made about that act, confirmed from the act
alone, with no trust in the operator required.

One boundary, stated plainly: these instruments confirm the reasoning was
governed, sealed, and honestly scored. They cannot confirm the reasoning
was right. Nothing can, which is why the rules themselves are published
and contestable.

---

## The contracts

The reasoning contract is served live, as endpoints rather than
documentation. What the compile gate enforces is what these serve.

| Resource | URL |
| --- | --- |
| Manifest, start here | [sdi-protocol.org/_functions/manifest](https://www.sdi-protocol.org/_functions/manifest) |
| Reasoning grammar | [sdi-protocol.org/_functions/grammar](https://www.sdi-protocol.org/_functions/grammar) |
| DER specification | [sdi-protocol.org/_functions/der](https://www.sdi-protocol.org/_functions/der) |
| Kernel conditions | [sdi-protocol.org/_functions/kernel](https://www.sdi-protocol.org/_functions/kernel) |
| Cognitive architecture | [sdi-protocol.org/_functions/gca](https://www.sdi-protocol.org/_functions/gca) |
| Compile gate (POST) | [sdi-protocol.org/_functions/compile](https://www.sdi-protocol.org/_functions/compile) |
| Machine index | [sdi-protocol.org/llms.txt](https://www.sdi-protocol.org/llms.txt) |

The compile gate is publicly callable, stateless, and deterministic. The
golden example served at the DER endpoint is itself a complete valid
payload: POST it to the compile gate unchanged and it returns PASS. Modify
one field and the response names the specific failure. The
[contracts page](https://www.sdi-protocol.org/contracts) walks all seven.

---

## What the machine is, briefly

Structured Decision Intelligence is three things: a language, a machine,
and a record. The language is ADS, Algebraic Decision Syntax, natural
enough for a language model to reason in and structured enough for a
machine to check. The machine is the Reckoner: a probabilistic model
proposes, a deterministic compile gate decides, and a hash-chained ledger
records. The record is the point. The reasoning act itself is stored, in
the grammar it was reasoned in, as the system's primary state. The model
proposes. The gate decides. The ledger records.

The full account lives on the site, one page per question:

- How the machine is built: [sdi-protocol.org/architecture](https://www.sdi-protocol.org/architecture)
- What the protocol guarantees: [sdi-protocol.org/protocol](https://www.sdi-protocol.org/protocol)
- Where this fits among traditions: [sdi-protocol.org/lineage](https://www.sdi-protocol.org/lineage)
- What the record proves: [sdi-protocol.org/transparency](https://www.sdi-protocol.org/transparency)
- Check it yourself, in full: [sdi-protocol.org/verify](https://www.sdi-protocol.org/verify)
- Where SDI stands with frameworks: [sdi-protocol.org/standards](https://www.sdi-protocol.org/standards)

---

## Rights and use

The SDI protocol and specification are copyright TXu 2-498-043, USPTO
patent application 19/425,875 pending. The verification scripts in this
repository exist to be downloaded and run: checking the public chain,
recomputing its seals and scores, and testing the compile gate are the
intended use and require no permission. This repository grants no rights
to the SDI kernel or to operating the protocol commercially; for that,
see [sdireckoner.com](https://www.sdireckoner.com).

`SDI_PROTOCOL_v1` · DER schema `SDI_DER_v1.1`

---

## Contact

Maintained by Structured Decision Intelligence LLC.

- Protocol, specification, challenges to claims: [sdi-protocol.org](https://www.sdi-protocol.org) · support@sdi-protocol.org
- Commercial product, commissioning (opens fall 2026): [sdireckoner.com](https://www.sdireckoner.com)

Challenges are the most useful mail this repository can generate: if a
hash does not recompute, a metric does not match, or a claim does not
hold, support@sdi-protocol.org is where that report goes.
