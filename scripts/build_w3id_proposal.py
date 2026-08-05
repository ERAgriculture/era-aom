#!/usr/bin/env python3
"""Generate w3id.org registration files from approved publication targets."""

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


FORMATS = {
    "text/turtle": "aom-livestock.ttl",
    "application/ld+json": "aom-livestock.jsonld",
    "application/rdf+xml": "aom-livestock.rdf",
}


def https_url(value, field):
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{field} must be an absolute HTTPS URL")
    if parsed.netloc == "example.org" or parsed.netloc.endswith(".example.org"):
        raise ValueError(f"{field} still uses example.org")
    return value.rstrip("/")


def build(config, allow_unapproved=False):
    if not config.get("approved") and not allow_unapproved:
        raise ValueError("Publication targets require explicit approved=true")
    if config["namespace"] != "https://w3id.org/era-aom/":
        raise ValueError("Unexpected namespace")
    html = https_url(config["html_base"], "html_base")
    artifacts = https_url(config["artifact_base"], "artifact_base")
    github = config["maintainer_github"].strip()
    if not github:
        raise ValueError("maintainer_github required")

    lines = [
        "# ERA-AOM persistent namespace",
        f"# Maintainer: {config['maintainer_name']} (GitHub: {github})",
        "Options +FollowSymLinks",
        "Options -MultiViews",
        "RewriteEngine On",
        '<IfModule mod_headers.c>',
        '  Header always set Vary "Accept"',
        '</IfModule>',
        "",
    ]
    for accept, filename in FORMATS.items():
        pattern = accept.replace("+", r"\+")
        lines.extend([
            f"RewriteCond %{{HTTP_ACCEPT}} {pattern} [NC]",
            f"RewriteRule ^(?:livestock/.*)?$ {artifacts}/{filename} [R=303,L]",
            "",
        ])
    lines.extend([
        f"RewriteRule ^livestock/(.+)$ {html}/en/page/$1 [R=303,NE,L]",
        f"RewriteRule ^(?:livestock)?/?$ {html}/en/ [R=303,NE,L]",
        f"RewriteRule ^release/{config['release']}/?$ {artifacts}/manifest.json [R=303,NE,L]",
        f"RewriteRule ^ https://github.com/ERAgriculture/era-aom [R=303,NE,L]",
        "",
    ])
    readme = f"""# ERA-AOM

Persistent namespace for Agriculture Ontology for Meta-analysis (ERA-AOM),
owned by Alliance of Bioversity International and CIAT and published under
CC BY 4.0.

- Namespace: <https://w3id.org/era-aom/>
- Repository: <https://github.com/ERAgriculture/era-aom>
- Release: `{config['release']}`

## Contact

{config['maintainer_name']}
GitHub: <https://github.com/{github}>
"""
    return "\n".join(lines), readme


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--allow-unapproved", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    htaccess, readme = build(config, args.allow_unapproved)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / ".htaccess").write_text(htaccess)
    (output / "README.md").write_text(readme)
    print(f"Generated w3id proposal at {output}")


if __name__ == "__main__":
    main()
