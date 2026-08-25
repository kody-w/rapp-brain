#!/usr/bin/env python3
"""brainify — convert any second brain into a frame-based dimension, in place.

For every .md page under the brain's root: mint a brain.page frame (slug, title,
sha256, tick, tick_frame) onto <root>/brain.jsonl (stream brain:@<owner>/<slug>).
Incremental and append-only: unchanged pages are skipped; an edited page mints a NEW
frame — versioned knowledge. The chain lives BESIDE the pages; nothing is moved,
rewritten, or pushed. Local-only brains stay local — this adds the dimension layer,
not an exit path.

  python3 brainify.py <root> <stream-slug> [--include sub1,sub2]
"""
import sys, json, hashlib, pathlib, datetime, argparse

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rapp as R

def utc():
    n = datetime.datetime.now(datetime.timezone.utc)
    return n.strftime("%Y-%m-%dT%H:%M:%S.") + f"{n.microsecond // 1000:03d}Z"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root"); ap.add_argument("slug")
    ap.add_argument("--include", help="comma-separated subdirs to limit to")
    ap.add_argument("--tick-head", help="path to a local ticks/HEAD.json mirror (offline); default fetches the public spine")
    a = ap.parse_args()
    root = pathlib.Path(a.root).expanduser()
    stream = f"brain:@kody-w/{a.slug}"
    chainf = root / "brain.jsonl"
    tick = json.loads(pathlib.Path(a.tick_head).expanduser().read_text() if a.tick_head else __import__("urllib.request",fromlist=["r"]).urlopen("https://raw.githubusercontent.com/kody-w/dogg/main/ticks/HEAD.json",timeout=10).read().decode())
    chain = [json.loads(l) for l in chainf.read_text().splitlines()] if chainf.exists() else []
    head = chain[-1] if chain else None
    latest = {}          # slug -> last recorded sha
    for fr in chain:
        latest[fr["payload"]["slug"]] = fr["payload"]["sha256"]
    roots = [root / s.strip() for s in a.include.split(",")] if a.include else [root]
    minted = skipped = 0
    for base in roots:
        for p in sorted(base.rglob("*.md")):
            if any(seg.startswith(".") for seg in p.relative_to(root).parts):
                continue
            slug = str(p.relative_to(root))[:-3]
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            if latest.get(slug) == h:
                skipped += 1
                continue
            lines = p.read_text(errors="ignore").splitlines()
            title = next((l.lstrip("# ").strip() for l in lines if l.strip().startswith("#")),
                         slug)[:120]
            f = R.build_frame("brain.page", stream, (head["seq"] + 1) if head else 0, utc(),
                {"slug": slug, "title": title, "sha256": h,
                 "tick": tick["count"] - 1, "tick_frame": tick["head_frame"]},
                prev=(head["payload_hash"] if head else None))
            ok, step, why = R.verify_frame(f, head=head, stream_id_of_record=stream)
            if not ok:
                raise ValueError(f"{slug}: {step} {why}")
            with open(chainf, "a") as fh:
                fh.write(json.dumps(f) + "\n")
            head = f
            latest[slug] = h
            minted += 1
    # verify the full chain end-to-end before claiming success
    h2 = None
    total = 0
    for fr in [json.loads(l) for l in chainf.read_text().splitlines()]:
        ok, s, w = R.verify_frame(fr, head=h2, stream_id_of_record=stream)
        assert ok, (fr.get("seq"), s, w)
        h2 = fr; total += 1
    print(f"{a.slug}: minted {minted}, unchanged {skipped} — chain {total} frames verifies ✓ "
          f"@ tick {tick['count']-1} ({stream})")

if __name__ == "__main__":
    main()
