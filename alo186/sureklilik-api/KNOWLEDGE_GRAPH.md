# ALO186 Knowledge Graph v1

ALO186 içindeki il/ilçe–EDAŞ, güvenlik kararı, resmî kanal, hesaplayıcı, ürün, tesis, varlık, kritik yük ve olay ilişkilerini **kaynak ve kanıt taşıyan** ortak bir veri modelinde birleştirir.

## Neden PostgreSQL tabanlı?

İlk sürüm mevcut yönetilen PostgreSQL üzerinde çalışır. Böylece:

- ayrı Neo4j lisansı, yedekleme ve operasyon yükü oluşmaz,
- tenant izolasyonu mevcut kuruluş modeliyle korunur,
- Alembic, PostgreSQL backup ve PITR Knowledge Graph tablolarını otomatik kapsar,
- veri hacmi ve sorgu biçimi gerçek kullanımda ölçülmeden ikinci graph veritabanı eklenmez,
- JSON-LD ve bounded graph traversal ihtiyacı karşılanır.

Neo4j/Apache AGE ancak çok derin traversal veya milyonlarca yoğun edge ile ölçülmüş ihtiyaç oluşursa ayrı read model olarak değerlendirilmelidir.

## Veri modeli

### `kg_entities`

Bir varlığı temsil eder:

- Province
- District
- DistributionCompany
- OfficialChannel
- Problem
- SafetyRoute
- EmergencyNumber
- Tool
- ContentPage
- ProductCategory
- Product
- Organization
- Location
- Asset
- CriticalLoad
- Incident
- IncidentTask
- Standard
- Regulation
- Source

Her entity:

- `canonical_key`
- `kind`
- `name`
- `description`
- `properties_json`
- `scope_key`
- `organization_id`
- `is_public`
- `status`

taşır.

### `kg_sources`

Assertion'ın dayandığı kaynağı tutar:

- resmî web sayfası,
- sürümlü veri seti,
- ALO186 editoryal katalogu,
- saha denetimi,
- teknik rapor,
- standart veya mevzuat.

Önemli alanlar:

- authority score
- URL
- lisans
- content hash
- son kontrol zamanı
- kaynak sağlık durumu

### `kg_assertions`

Graph edge veya literal iddiadır.

Entity ilişkisi:

```text
Marmaris --partOf--> Muğla
Marmaris --servedBy--> ADM Elektrik
Kablo yere düştü --routesTo--> 112
Ana jeneratör --locatedAt--> Ana Otel
```

Literal iddia:

```text
Ana jeneratör --ratedPowerKva--> {"value": 630, "unit": "kVA"}
Problem --hasRiskLevel--> "red"
```

Her assertion:

- source
- confidence
- valid_from / valid_to
- verified_at
- evidence_hash
- properties
- status
- public/private flag

taşır.

### `kg_verification_runs`

Bir kaynak, entity veya assertion için yapılan doğrulama çalışmasını kaydeder:

- verified
- unchanged
- changed
- unreachable
- invalid
- error

## Scope ve tenant izolasyonu

### Global public graph

```text
scope_key = global
is_public = true
organization_id = null
```

Public endpointlerden okunabilir. Tenant kullanıcıları da bu varlıkları okuyabilir fakat değiştiremez.

### Kuruluş private graph

```text
scope_key = org:<organization_uuid>
is_public = false
organization_id = <organization_uuid>
```

Yalnız bearer oturumu ve doğru `X-Organization-ID` ile okunur. Admin ve technician yazabilir; viewer yalnız okuyabilir.

Tenant assertion, kendi private entity'lerini veya global public entity'leri hedefleyebilir. Başka kuruluşun private entity/source/assertion verisine erişemez.

## Public API

```text
GET /api/v1/kg/public/search?q=Marmaris
GET /api/v1/kg/public/entities/district:... 
GET /api/v1/kg/public/entities/problem:fallen_conductor/jsonld
GET /api/v1/kg/public/path?from_key=...&to_key=...&max_depth=4
GET /api/v1/kg/public/health
```

Public API yalnız global ve `is_public=true` kayıtları döndürür.

## Tenant API

Bütün çağrılarda:

```http
Authorization: Bearer <token>
X-Organization-ID: <organization_uuid>
```

### Entity

```text
GET    /api/v1/kg/entities
POST   /api/v1/kg/entities
GET    /api/v1/kg/entities/{entity_id}
PATCH  /api/v1/kg/entities/{entity_id}
DELETE /api/v1/kg/entities/{entity_id}
GET    /api/v1/kg/entities/{entity_id}/neighbors
```

### Source ve assertion

```text
POST   /api/v1/kg/sources
POST   /api/v1/kg/assertions
PATCH  /api/v1/kg/assertions/{assertion_id}
DELETE /api/v1/kg/assertions/{assertion_id}
POST   /api/v1/kg/verifications
```

### Traversal ve sağlık

```text
GET /api/v1/kg/path
GET /api/v1/kg/health
```

Traversal en fazla 6 derinlik ve sınırlı edge kümesiyle çalışır; kontrolsüz graph sorgusu kabul etmez.

## JSON-LD ve AEO

Public entity endpointi JSON-LD üretir:

```json
{
  "@context": {
    "@vocab": "https://schema.alo186.com/v1/",
    "servedBy": {"@type": "@id"},
    "source": {"@id": "https://schema.org/citation", "@type": "@id"}
  },
  "@id": "https://www.alo186.com/kg/problem:fallen_conductor",
  "@type": "Problem",
  "name": "Kablo yere düştü",
  "routesTo": {
    "@id": "https://www.alo186.com/kg/route:112",
    "confidence": 1.0,
    "source": "https://github.com/ozaneryavuz/chatgpt/tree/main/alo186/karar-motoru"
  }
}
```

Bu çıktı:

- web sayfası structured data üretimi,
- answer engine retrieval,
- AI agent citation/provenance,
- içerik ve API arasında anlam bütünlüğü

için kullanılabilir.

## Seed ve senkronizasyon

Manuel:

```bash
cd alo186/sureklilik-api
python -m app.knowledge_seed sync-public --timeout 30
```

Strict kapsam kontrolü:

```bash
python -m app.knowledge_seed sync-public --timeout 30 --strict
```

Seed şu verileri idempotent biçimde oluşturur:

- 81 il
- 973 ilçe
- 21 elektrik dağıtım şirketi
- İstanbul ilçe bazlı BEDAŞ/AYEDAŞ ayrımı
- 25 problem ve güvenlik rotası
- ALO186 araçları
- 7 ürün kategorisi
- doğrulanmış ilk ürün kartları

TurkiyeAPI erişilemezse non-strict mod mevcut graph'ı silmez; kaynak durumunu `unreachable` olarak işaretler ve statik ALO186 kataloglarını senkronize etmeye devam eder.

Render üretiminde:

```text
ALO186_KG_SEED_PUBLIC=true
ALO186_KG_SEED_STRICT=false
ALO186_KG_SEED_TIMEOUT=30
```

ile migration sonrası ilk seed yapılır. Retention cron aynı zamanda günlük public graph sync çalıştırır.

## Graph health

Public veya tenant health endpointi şu göstergeleri üretir:

- entity sayısı
- assertion sayısı
- stale assertion
- orphan entity
- düşük güven
- süresi geçmiş assertion
- çakışan aktif literal claim
- sağlıksız kaynak
- başarısız verification run
- 0–100 health score

### Çakışma yönetimi

Aynı subject ve predicate için birden fazla farklı aktif literal değer bulunursa conflict sayılır.

Çözüm sırası:

1. Kaynakların authority score ve tarihini karşılaştırın.
2. Hatalı assertion'ı `disputed` yapın.
3. Yeni doğrulama run'ı ekleyin.
4. Geçerli assertion'ı `verified_at` ile yenileyin.
5. Eski assertion'ı `superseded` veya `retired` yapın.

Assertion geçmişi fiziksel olarak silinmez; audit ve teknik kanıt korunur.

## Monitoring

Knowledge Graph health endpointi Prometheus gauge'larını yeniler:

```text
alo186_kg_health_score
alo186_kg_entities
alo186_kg_assertions
alo186_kg_stale_assertions
alo186_kg_orphan_entities
alo186_kg_conflicting_claims
```

Grafana alarm eşikleri:

- public health score < 85
- public entity sayısı < 100
- stale assertion > 100
- conflict > 0

GitHub synthetic monitor `/api/v1/kg/public/health` endpointini çağırır; graph boşsa veya health score 70 altındaysa başarısız olur.

## Backup ve restore

Knowledge Graph tabloları aynı PostgreSQL içinde bulunduğu için mevcut:

- managed PostgreSQL PITR,
- günlük `pg_dump`,
- SHA-256 doğrulama,
- Restic + Cloudflare R2,
- izole restore tatbikatı

kapsamına otomatik girer.

Restore sonrasında:

```bash
python -m app.knowledge_seed sync-public --timeout 30
```

çalıştırılarak public katalog doğrulanır; tenant graph verisi seed tarafından değiştirilmez.

## Güvenlik sınırları

- Public API private tenant graph döndürmez.
- Tenant API global graph'ı değiştiremez.
- Viewer yazamaz.
- Her assertion source gerektirir.
- Assertion tam olarak bir entity object veya literal value taşır.
- Serbest Cypher/SPARQL/SQL endpointi yoktur.
- Traversal derinlik ve edge sayısıyla sınırlıdır.
- Public claim yayınlama yalnız seed/editoryal pipeline üzerinden yapılır.
- Ürün fiyatı ve stok graph içinde güncel veri gibi saklanmaz.

## Test

```bash
pytest -q tests/test_knowledge_graph.py tests/test_knowledge_seed.py
alembic upgrade head
alembic check
```

Test kapsamı:

- public/private ayrımı
- tenant izolasyonu
- rol yetkileri
- entity/source/assertion CRUD
- object/literal XOR
- source zorunluluğu
- idempotent upsert
- bounded path
- JSON-LD provenance
- health ve conflict
- verification lifecycle
- Prometheus metric
- 81/973/21/25 seed kapsamı
- remote fallback
- strict coverage failure

## Gelecek fazlar

- tesis ve varlık kayıtlarından otomatik tenant graph projection
- teknik rapor ve ölçüm provenance adapter'ları
- standart/mevzuat sürüm grafiği
- sigorta risk API'si
- graph tabanlı ürün/BOM önerisi
- hybrid RAG retrieval
- outcome-labelled failure mode graph
- gerekirse PostgreSQL read modelinden Apache AGE/Neo4j projeksiyonu
