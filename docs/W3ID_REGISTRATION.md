# ERA-AOM w3id registration

Official w3id process requires new `era-aom/` directory containing `.htaccess`
and `README.md`, contact information, local testing, and pull request to
`perma-id/w3id.org`. ERA-AOM generator implements that contract without making
external changes.

1. Copy `config/publication-targets.example.json` outside version control.
2. Replace example destinations, name maintainers, and set `approved=true` only
   after publisher approval and live destination checks.
3. Generate and validate:

```sh
python scripts/build_w3id_proposal.py --config=/path/to/targets.json --output=/tmp/era-aom
python scripts/validate_w3id_proposal.py /tmp/era-aom
```

4. Test `.htaccess` in local w3id checkout using representative `Accept`
   headers. Confirm every 303 destination returns expected media type.
5. Obtain explicit approval before forking/submitting external w3id PR.

Never commit production-host credentials. Target configuration may be committed
later only if it contains public URLs and approved maintainer information.
