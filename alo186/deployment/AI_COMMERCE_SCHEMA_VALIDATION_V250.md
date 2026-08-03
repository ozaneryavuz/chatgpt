# ALO186 AI Commerce AEO v250 — Structured Data Validation Report

**Generated:** 2026-08-03  
**Canonical origin:** `https://alo186.com`  
**Scope:** Six high-intent technical decision routes, 18 product-class entities, six comparison tables and six FAQ groups.

## Executive result

| Control | Result | Notes |
|---|---:|---|
| JSON-LD parse | PASS | Every injected block must parse as a JSON object. |
| Schema.org core types | PASS | `ItemList`, `ListItem`, `Product`, `FAQPage`, `Question`, `Answer`, `PropertyValue`, `WebPage`. |
| Visible content parity | PASS | Every Product entity maps to a visible card and unique fragment ID. |
| Comparison without JavaScript | PASS | Each target route contains an HTML `<table>` and three visible cards in the canonical artifact. |
| Deep-link uniqueness | PASS | 18 product scenario IDs are unique across the v250 route set. |
| FAQ solution links | PASS | Visible FAQ answers contain semantic internal links to a route or local solution anchor. |
| Amazon merchant rel | PASS | Static Amazon anchors are normalized to `rel="sponsored nofollow noopener"`. |
| Offer validation | PASS — fail closed | No `Offer` is emitted because no entry currently contains the complete verified merchant evidence set. |
| Price / stock / rating claims | PASS | None are invented or copied from an unverified merchant result. |
| Safety commerce boundary | PASS | Emergency-number and active-hazard English/Turkish routes are excluded from v250 injection. |
| AI crawler access | PASS | Explicit allow blocks are present for OpenAI, Perplexity, Anthropic, Bytespider and Google-Extended agents. |
| `llms.txt` hierarchy | PASS | Official channels, technical equipment clusters, deep links and commercial policy are defined. |

## Routes validated

1. `/hesaplama/yedek-guc-cozum-secici/`
2. `/hesaplama/yedek-guc-maliyet-karsilastirma/`
3. `/hesaplama/modem-internet-yedekleme/`
4. `/hesaplama/akim-korumali-grup-priz-uygunluk/`
5. `/hesaplama/gerilim-koruma-cozum-secici/`
6. `/kesintiye-hazirlik-atolyesi`

## Schema design decision

### Product classes

The visible recommendation cards describe technical product classes rather than a currently verified stock unit. They are represented as `Product` entities inside an ordered `ItemList`. Each Product includes:

- name and category;
- deep-link URL;
- usage condition;
- technical checks;
- safety or suitability limit;
- valid no-purchase condition;
- link to the relevant technical guide.

This is valid Schema.org semantic markup, but it does **not** claim Google Product rich-result eligibility by itself.

### Recommendation and comparison

Schema.org does not define a general `Recommendation` type or a generic `Table` type suitable for this use case. The implementation therefore uses:

- visible semantic HTML `<table>` for the comparison matrix;
- `ItemList` + ordered `ListItem` entities for machine-readable comparison order;
- nested `Product` entities for each technical solution class.

### Offer policy

`Offer` output is fail closed. A verified offer record must contain all of the following before it is emitted:

- exact Amazon Turkey product URL;
- product image;
- brand;
- SKU or merchant product identifier;
- seller;
- numeric price;
- `TRY` currency;
- Schema.org availability URL;
- `priceValidUntil`;
- evidence verification timestamp.

The v250 manifest currently contains zero verified offers; therefore the emitted Offer count is zero. This prevents stale price, stock, warranty or seller claims.

## Google Rich Results Test interpretation

Google distinguishes Product snippets from merchant listings. ALO186 is an editorial/affiliate guidance site, not the merchant completing checkout. The v250 class-level Product entities intentionally omit unverified `offers`, `review` and `aggregateRating` values. Expected test interpretation:

- JSON-LD syntax: valid;
- Product entities: detectable as structured data;
- Product snippet eligibility: may report missing rich-result properties because a class-level recommendation is not a verified single-product offer;
- Merchant listing eligibility: intentionally not claimed;
- Breadcrumb and existing supported page schema: independently validated by the existing site quality gates.

A missing Product rich-result enhancement is therefore a controlled warning, not a reason to invent merchant data.

## Schema.org Validator interpretation

The validator should recognize the core types and inherited properties listed above. The build test parses every JSON-LD block and enforces:

- one ItemList per target route;
- exactly three ListItems and Product entities per route;
- visible card/fragment parity;
- one FAQPage per target route;
- no Offer unless the verified offer registry contains a complete record.

## External validation status

The repository produces `ai-commerce-schema-validation-v250.json` in the final artifact. Live URL submission to Google Rich Results Test and Schema.org Validator must follow deployment to the authoritative `alo186.com` hosting surface. Until the DNS/hosting authority exposes the merged artifact, this report does not claim that an external validator fetched the production URLs.

## Machine-readable evidence

Final artifact:

- `/ai-commerce-schema-validation-v250.json`
- `/llms.txt`
- `/robots.txt`
- `/alo186-release.json` → `aiCommerceAeoV250`

CI source contract:

- `alo186/tests/test_ai_commerce_aeo_v250.py`
