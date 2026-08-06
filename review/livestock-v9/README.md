# Feedipedia definition evidence review

This batch records source-page evidence for every active definition gap routed
to Feedipedia. It does not treat shared page mappings, lexical resemblance, or
taxon co-reference as concept identity.

`feedipedia_definition_evidence.csv` separates retrieval facts from governance
disposition. Eight lexical matches are candidates for manual definition review;
none is automatically approved. Each candidate must retain AOM source identity
and model component, process, physical form, product type, integrity, and
composition as separate assertions where applicable. Ingestion must consume
those structured fields rather than parse preferred labels.

Rebuild from live public pages with:

```sh
python scripts/research_feedipedia_definition_evidence.py
```

Feedipedia pages are evidence links. This repository stores only concise page
metadata, warning state, and review classification—not copied datasheet prose.
