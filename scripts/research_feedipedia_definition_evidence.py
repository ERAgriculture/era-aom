#!/usr/bin/env python3
"""Research Feedipedia mappings without treating page co-reference as identity."""
import argparse
import csv
import json
import re
import ssl
import unicodedata
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "review/livestock-v8/definition_gap_queue.csv"
OUT = ROOT / "review/livestock-v9/feedipedia_definition_evidence.csv"


def clean_html(value):
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()


def normalized(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"\([^)]*\)", " ", value.casefold())
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def fetch(url):
    try:
        request = Request(url, headers={
            "User-Agent": "ERA-AOM vocabulary research/1.0 (+https://github.com/ERAgriculture/era-aom)"
        })
        with urlopen(request, timeout=30, context=ssl.create_default_context()) as response:
            body = response.read().decode("utf-8", "replace")
            final_url, status = response.geturl(), response.status
        title = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
        heading = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.I | re.S)
        folded = clean_html(body).casefold()
        return {
            "url": url, "final_url": final_url, "http_status": status,
            "page_title": clean_html(title.group(1)) if title else "",
            "page_heading": clean_html(heading.group(1)) if heading else "",
            "warning_detected": "do not quote" in folded or "under construction" in folded,
            "retrieval_error": "",
        }
    except Exception as error:  # evidence ledger must retain failed retrievals
        return {
            "url": url, "final_url": "", "http_status": 0, "page_title": "",
            "page_heading": "", "warning_detected": False,
            "retrieval_error": f"{type(error).__name__}: {error}",
        }


def relation(label, heading):
    concept, page = normalized(label), normalized(heading)
    if concept == page:
        return "lexically_exact"
    if concept and concept in page:
        return "feedipedia_scope_narrower"
    if page and page in concept:
        return "feedipedia_scope_broader"
    return "different_label_or_scope"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, help="JSON page cache; omit to retrieve live pages")
    parser.add_argument("--retrieved-on", default=date.today().isoformat())
    args = parser.parse_args()

    with QUEUE.open(encoding="utf-8", newline="") as handle:
        queue = [row for row in csv.DictReader(handle)
                 if row["recommended_route"] == "research_feedipedia"]
    for row in queue:
        row["feedipedia_url"] = next(
            value for value in row["public_mapping_targets"].split(";")
            if "feedipedia.org/" in value
        )
    url_counts = Counter(row["feedipedia_url"] for row in queue)
    urls = sorted(url_counts)

    if args.cache:
        pages = {row["url"]: row for row in json.loads(args.cache.read_text())}
    else:
        pages = {}
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(fetch, url): url for url in urls}
            for future in as_completed(futures):
                page = future.result()
                pages[page["url"]] = page

    rows = []
    for item in queue:
        page = pages[item["feedipedia_url"]]
        shared = url_counts[item["feedipedia_url"]]
        lexical = relation(item["preferred_label"], page["page_heading"])
        if page["http_status"] != 200:
            page_kind, disposition = "unavailable", "hold_retrieval_failed"
            rationale = "Source page could not be retrieved; no semantic claim approved."
        elif "/content/feeds?" in item["feedipedia_url"]:
            page_kind, disposition = "category_list", "hold_category_not_concept"
            rationale = "Feed listing is discovery evidence, not evidence for one material identity."
        elif page["warning_detected"]:
            page_kind, disposition = "warned_page", "hold_source_warning"
            rationale = "Source carries an under-construction or do-not-quote warning."
        elif shared > 1:
            page_kind, disposition = "shared_feed_page", "hold_shared_page_scope_review"
            rationale = "One Feedipedia page maps to multiple AOM concepts; co-reference does not establish synonymy."
        elif lexical == "lexically_exact":
            page_kind, disposition = "feed_page", "candidate_manual_definition_review"
            rationale = "Labels align, but source/component/process assertions still require governed review."
        else:
            page_kind, disposition = "feed_page", "hold_scope_and_facet_review"
            rationale = "Page wording or scope differs; review source identity, component, process, form, and product type separately."
        rows.append({
            "concept_id": item["concept_id"], "preferred_label": item["preferred_label"],
            "feedipedia_url": item["feedipedia_url"], "retrieved_on": args.retrieved_on,
            "http_status": page["http_status"], "final_url": page["final_url"],
            "page_title": page["page_title"], "page_heading": page["page_heading"],
            "page_kind": page_kind, "shared_mapping_count": shared,
            "warning_detected": str(bool(page["warning_detected"])).lower(),
            "lexical_relation": lexical, "evidence_disposition": disposition,
            "retrieval_error": page.get("retrieval_error", ""), "rationale": rationale,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Recorded {len(rows)} concept mappings across {len(urls)} Feedipedia pages")


if __name__ == "__main__":
    main()
