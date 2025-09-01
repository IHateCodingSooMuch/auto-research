#!/usr/bin/env python3
out_dir = ROOT / "research" / str(date.year) / slug
sources_dir = out_dir / "sources"
out_dir.mkdir(parents=True, exist_ok=True)
sources_dir.mkdir(parents=True, exist_ok=True)


rprint(f"[bold green]Researching:[/bold green] {topic}")


plan = make_plan(topic, depth, model, temperature)
with open(out_dir / "plan.json", "w", encoding="utf-8") as f:
json.dump(plan, f, ensure_ascii=False, indent=2)


# Search
seen_urls = set()
fetched: List[Tuple[str, str, str]] = [] # (url, text, raw)
shingles_cache = []


for sq in plan.get("subquestions", []):
for q in sq.get("queries", [])[:3]:
results = ddg_search(q, max_results=max_per_query, region=region)
for r in results:
url = r["url"]
if any(url.startswith(x) for x in ("https://twitter.com/", "https://x.com/")):
continue # skip volatile social links by default
if url in seen_urls: continue
text, raw = fetch(url, timeout_s)
if len((text or "").strip()) < min_chars:
continue
sh = shingle_3grams(text)
is_dup = any(jaccard(sh, prev) >= dedupe_j for prev in shingles_cache)
if is_dup:
continue
shingles_cache.append(sh)
seen_urls.add(url)
fetched.append((url, text, raw))
if len(fetched) >= max_sources:
break
if len(fetched) >= max_sources:
break
if len(fetched) >= max_sources:
break


# Notes per source
per_source_notes: List[Tuple[int, str, str]] = [] # (index, url, notes)
for i, (url, text, raw) in enumerate(fetched, start=1):
# save raw text snapshot
snap_path = sources_dir / f"{i:02d}.txt"
with open(snap_path, "w", encoding="utf-8") as f:
f.write(text)
notes = summarize_block(text, url, model, temperature)
per_source_notes.append((i, url, notes))


# Write notes.md
notes_md = ["# Source Notes\n"]
for i, (idx, url, notes) in enumerate(per_source_notes, start=1):
notes_md.append(f"## [{i}] {url}\n\n{notes}\n")
(out_dir / "notes.md").write_text("\n".join(notes_md), encoding="utf-8")


# Synthesis draft
meta = {
"title": topic,
"slug": slug,
"created": now_iso(),
"source_count": len(per_source_notes),
"tags": plan.get("tags", []),
}
draft = front_matter(meta) + synthesize(topic, per_source_notes, plan, model, temperature)
(out_dir / "draft.md").write_text(draft, encoding="utf-8")


# Metadata
metadata = {
"topic": topic,
"slug": slug,
"created": now_iso(),
"plan": plan,
"params": {"max_sources": max_sources, "max_per_query": max_per_query, "depth": depth, "region": region},
"sources": [u for (u,_,_) in fetched],
}
(out_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


# Pretty table
tbl = Table(title="Sources")
tbl.add_column("#", justify="right", style="cyan")
tbl.add_column("URL", style="magenta")
for i, (u,_,_) in enumerate(fetched, start=1):
tbl.add_row(str(i), u)
rprint(tbl)
rprint(f"Saved to: {out_dir}")


if __name__ == "__main__":
APP()
