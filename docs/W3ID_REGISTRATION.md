# ERA-AOM w3id registration

Official w3id process requires new `era-aom/` directory containing `.htaccess`
and `README.md`, contact information, local testing, and pull request to
`perma-id/w3id.org`. ERA-AOM generator implements that contract without making
external changes.

Approved target names live in `config/publication-targets.json`. DNS does not
currently resolve, so generated files are review-ready, not submission-ready.

1. Generate and validate:

```sh
python scripts/build_w3id_proposal.py --config=config/publication-targets.json --output=/tmp/era-aom
python scripts/validate_w3id_proposal.py /tmp/era-aom
```

2. Test `.htaccess` in local w3id checkout using representative `Accept`
   headers. Confirm every 303 destination returns expected media type.
3. Confirm CGIAR DNS, browser, and release-asset URLs resolve.
4. Obtain explicit approval before forking/submitting external w3id PR.

Never commit production-host credentials. Target configuration may be committed
later only if it contains public URLs and approved maintainer information.
