# rapp-brain/0 — second brains as verifiable dimensions

A **rapp-brain** is any directory of markdown knowledge pages plus one append-only
chain (`brain.jsonl`) of rapp/1 frames — one `brain.page` frame per page version:

```json
{ "kind": "brain.page", "stream_id": "brain:@owner/slug",
  "payload": { "slug": "wiki/some-page", "title": "…", "sha256": "<of the page bytes>",
               "tick": 106, "tick_frame": "<spine anchor hash>" } }
```

Properties this buys, for free:
- **Versioned knowledge**: editing a page mints a NEW frame — history is append-only;
  "what did this brain believe at tick N" is answerable forever.
- **Integrity**: every page is content-addressed; a tampered page fails its frame.
- **A shared clock**: pages are tick-anchored to the [DOGG spine]
  (https://github.com/kody-w/dogg), so any two brains' knowledge is time-joinable.
- **Assimilation**: because a brain is a dimension, brains pool exactly like any
  chain — over LAN, as a single-file git bundle, or by memorized chant — and the
  receiver's gate (re-verify frames + tick refs) bounces forgeries. Merge knowledge
  across people, devices, or companies without trusting the courier.
- **Privacy is orthogonal**: the chain lives BESIDE the pages, locally. A brain that
  never leaves a machine is still verifiable on it; sharing is a separate, deliberate
  act.

Identity: a brain carries a `rappid.json` (kind: `brain`, minted once per rapp/1 §6.2
— uuid-entropy tail, never a name-hash).

Reference implementation: [`brainify.py`](brainify.py) — point it at any directory of
markdown; incremental (unchanged pages skip), self-verifying (walks the whole chain
before claiming success), offline-capable (`--tick-head` a local spine mirror).

Frame envelope: [rapp/1](https://github.com/kody-w/rapp-1). Network + transports +
chants: [dogg/0](https://github.com/kody-w/dogg/blob/main/PROTOCOL.md).
