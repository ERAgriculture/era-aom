#!/usr/bin/env python3
"""Deterministic release writers and pinned runtime contract."""

import json
import platform
from collections import defaultdict
from xml.sax.saxutils import escape, quoteattr

import pyarrow as pa
import pyarrow.parquet as pq
import rdflib
from rdflib import BNode, Literal, RDF, URIRef


RUNTIME_CONTRACT = {
    "python": "3.12",
    "rdflib": "7.6.0",
    "pyarrow": "24.0.0",
}


def validate_runtime_contract():
    observed = {
        "python": ".".join(platform.python_version_tuple()[:2]),
        "rdflib": rdflib.__version__,
        "pyarrow": pa.__version__,
    }
    if observed != RUNTIME_CONTRACT:
        raise RuntimeError(
            f"Release writer runtime mismatch: expected {RUNTIME_CONTRACT}, observed {observed}"
        )
    return observed


def term_key(term):
    if isinstance(term, URIRef):
        return ("uri", str(term))
    if isinstance(term, BNode):
        return ("blank", str(term))
    if isinstance(term, Literal):
        return (
            "literal",
            str(term),
            term.language or "",
            str(term.datatype or ""),
        )
    raise TypeError(f"Unsupported RDF term: {term!r}")


def identifier(term):
    if isinstance(term, URIRef):
        return str(term)
    if isinstance(term, BNode):
        return f"_:{term}"
    raise TypeError(f"RDF resource expected: {term!r}")


def require_ground_graph(graph):
    blank_nodes = {term for triple in graph for term in triple if isinstance(term, BNode)}
    if blank_nodes:
        raise ValueError(
            f"Release graph contains {len(blank_nodes)} blank nodes; assign stable identifiers first"
        )


def jsonld_value(term):
    if isinstance(term, (URIRef, BNode)):
        return {"@id": identifier(term)}
    if isinstance(term, Literal):
        value = {"@value": str(term)}
        if term.language:
            value["@language"] = term.language
        elif term.datatype:
            value["@type"] = str(term.datatype)
        return value
    raise TypeError(f"Unsupported JSON-LD term: {term!r}")


def write_jsonld(graph, path):
    require_ground_graph(graph)
    grouped = defaultdict(lambda: defaultdict(list))
    for subject, predicate, obj in graph:
        grouped[subject][predicate].append(obj)
    document = []
    for subject in sorted(grouped, key=term_key):
        node = {"@id": identifier(subject)}
        for predicate in sorted(grouped[subject], key=term_key):
            objects = sorted(set(grouped[subject][predicate]), key=term_key)
            if predicate == RDF.type and all(isinstance(obj, URIRef) for obj in objects):
                node["@type"] = [str(obj) for obj in objects]
            else:
                node[str(predicate)] = [jsonld_value(obj) for obj in objects]
        document.append(node)
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_rdfxml(graph, path):
    require_ground_graph(graph)
    qnames = {}
    namespaces = {"rdf": str(RDF)}
    for predicate in sorted(set(graph.predicates()), key=term_key):
        prefix, namespace, local = graph.namespace_manager.compute_qname(
            predicate, generate=False
        )
        if not prefix:
            raise ValueError(f"RDF/XML predicate lacks explicit prefix: {predicate}")
        qnames[predicate] = f"{prefix}:{local}"
        namespace_text = str(namespace)
        if prefix in namespaces and namespaces[prefix] != namespace_text:
            raise ValueError(f"RDF/XML prefix collision: {prefix}")
        namespaces[prefix] = namespace_text

    grouped = defaultdict(list)
    for subject, predicate, obj in graph:
        grouped[subject].append((predicate, obj))

    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<rdf:RDF"]
    for prefix, namespace in sorted(namespaces.items()):
        lines.append(f"   xmlns:{prefix}={quoteattr(namespace)}")
    lines[-1] += ">"
    for subject in sorted(grouped, key=term_key):
        lines.append(f"  <rdf:Description rdf:about={quoteattr(identifier(subject))}>")
        for predicate, obj in sorted(
            grouped[subject], key=lambda pair: (term_key(pair[0]), term_key(pair[1]))
        ):
            qname = qnames[predicate]
            if isinstance(obj, URIRef):
                lines.append(f"    <{qname} rdf:resource={quoteattr(str(obj))}/>")
                continue
            if isinstance(obj, Literal):
                attributes = ""
                if obj.language:
                    attributes = f" xml:lang={quoteattr(obj.language)}"
                elif obj.datatype:
                    attributes = f" rdf:datatype={quoteattr(str(obj.datatype))}"
                lines.append(
                    f"    <{qname}{attributes}>{escape(str(obj))}</{qname}>"
                )
                continue
            raise TypeError(f"Unsupported RDF/XML object: {obj!r}")
        lines.append("  </rdf:Description>")
    lines.append("</rdf:RDF>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_parquet(table, path):
    pq.write_table(
        table,
        path,
        version="2.6",
        data_page_version="1.0",
        compression="zstd",
        compression_level=3,
        use_dictionary=True,
        write_statistics=True,
        use_compliant_nested_type=True,
        store_schema=True,
    )
