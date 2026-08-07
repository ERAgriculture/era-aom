# Bran compound-model correction

Status: approved remediation design, 2026-08-07

`AOM_101104 Bran` is a feed-material component, not an anatomical plant part. Reclassify it from `aom:ingredientPart` / `aom:IngredientPartCategory` under `AOM_101019` to `aom:materialComponent` / `aom:FeedMaterialComponent` under `AOM_101085`.

`AOM_001614 Maize Bran` must retain one stable feed-material identity and publish independent semantic facets:

- `aom:sourceTaxon` → `http://purl.obolibrary.org/obo/NCBITaxon_4577` (`Zea mays`)
- `aom:materialComponent` → `AOM_101104` (`Bran`)
- `aom:productRole` → `AOM_101062` (`By-product role`)
- `aom:processingMethod` → `AOM_000838` (`Milling`)

Hierarchy remains navigation, not full compound semantics. Card must expose all four properties separately.

Definition target: maize-derived feed material consisting primarily of bran separated during milling; composition may include variable attached endosperm. Final wording must retain cited evidence and avoid treating bran as one botanical anatomical structure.
