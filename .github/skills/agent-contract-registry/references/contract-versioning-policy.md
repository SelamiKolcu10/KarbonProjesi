# Contract Versioning Policy

## Amaç
Bu politika, Data Miner, Auditor ve Strategist ajanları arasındaki veri kontratlarının sürüm yönetimini, şema istikrarını ve geriye dönük uyumluluğu zorunlu kurallarla yönetir.

## Kapsam
- Ajanlar arası tüm JSON/Pydantic modelleri
- Pipeline mapper giriş/çıkış kontratları
- Orchestrator ve API katmanına taşınan agent çıktı kontratları

## Temel İlkeler
1. Tek kaynak doğruluk
- Kontratın kanonik tanımı Pydantic modelidir.
- JSON Schema çıktısı bu modelden türetilmelidir.

2. Açık sürümleme
- Her kontrat modeli model_version alanı taşımalıdır.
- model_version semver mantığıyla takip edilir: MAJOR.MINOR.PATCH.

3. Varsayılan backward compatibility
- Kırıcı değişiklikler istisnadır, varsayılan yol değildir.
- Tüketici ajanlar en az bir önceki minor sürümü okuyabilmelidir.

## Sürüm Artış Kuralları
### PATCH artışı
Aşağıdaki değişikliklerde PATCH artırılır:
- Açıklama/dokümantasyon güncellemesi
- Dahili validasyon mesajı iyileştirmesi (davranış kırmadan)
- JSON Schema metadata eklemeleri (ör. title, description)

### MINOR artışı
Aşağıdaki değişikliklerde MINOR artırılır:
- Yeni opsiyonel alan ekleme
- Yeni enum değeri ekleme (tüketici fallback davranışı mevcutsa)
- Geriye dönük uyumlu alias ekleme
- Varsayılan değeri olan yeni alt-nesne ekleme

### MAJOR artışı
Aşağıdaki değişikliklerde MAJOR artırılır:
- Alan silme
- Alan yeniden adlandırma (alias/deprecation olmadan)
- Tip daraltma (ör. float -> int)
- Optional alanı required yapma
- Mevcut alanın semantiğini değiştirme

## Required Field Politikası
1. Her required alan için:
- İş anlamı açıkça belirtilmelidir.
- Kabul edilen değer aralığı tanımlanmalıdır.
- Hata durumunda üretilecek validasyon mesajı net olmalıdır.

2. Required alan değişikliği:
- Optional -> Required geçişi MAJOR değişikliktir.
- Geçiş ancak iki aşamalı deprecation planı ile yapılır.

## Deprecation Politikası
1. Deprecation yaşam döngüsü
- Aşama 1: Yeni alan eklenir, eski alan desteklenir, uyarı üretilir.
- Aşama 2: Eski alan read-only/legacy olarak işaretlenir.
- Aşama 3: Planlanan MAJOR sürümde eski alan kaldırılır.

2. Deprecation bildirimi zorunludur
- Changelog kaydı
- Migration örneği
- Kaldırılma hedef sürümü

## Şema Drift Önleme Kuralları
1. Drift tanımı
- Üretici model ile tüketici model arasındaki alan uyumsuzluğu
- Mapper katmanının modelden farklı fiili payload üretmesi
- JSON Schema ile runtime validasyon davranışının ayrışması

2. Drift kontrolü
- Producer ve consumer için sözleşme snapshot testleri
- Mapper çıkışının target model ile doğrulanması
- Geçerli ve legacy örnek payload setleriyle regresyon testi

## Uyum Kontrol Geçitleri (Release Gates)
Bir kontrat değişikliği aşağıdaki geçitler sağlanmadan merge edilmez:
1. Model doğrulama geçidi
- Pydantic modeli üretici ve tüketicide çalışır.

2. Şema doğrulama geçidi
- JSON Schema güncel ve model ile tutarlıdır.

3. Uyumluluk geçidi
- En az bir önceki minor sürüm payload testleri geçer.

4. Regresyon geçidi
- Kritik metriklerde (emisyon/vergi) beklenmeyen sapma yoktur.

5. Dokümantasyon geçidi
- Sürüm notu ve migration adımları yayınlanmıştır.

## Önerilen Model Alanları
Her paylaşılan modelde önerilen minimum alan seti:
- model_version: str
- producer_agent: str
- produced_at: datetime
- payload_id: str
- trace_id: str

## Hata Kodları (Öneri)
- CONTRACT_VERSION_UNSUPPORTED
- CONTRACT_REQUIRED_FIELD_MISSING
- CONTRACT_TYPE_MISMATCH
- CONTRACT_ENUM_VALUE_UNKNOWN
- CONTRACT_DEPRECATED_FIELD_USED

## Uygulama Örnekleri
### Non-breaking örnek
- precursor_quality_score opsiyonel alanı eklendi
- model_version: 2.3.1 -> 2.4.0
- Legacy tüketici bu alanı yok sayarak çalışmaya devam eder

### Breaking örnek
- electricity_consumption_mwh alanı energy_consumption_mwh olarak değiştirildi
- model_version: 2.4.3 -> 3.0.0
- Geçiş için alias + deprecation planı + migration dokümanı gerekir

## Kabul Kriterleri
Bir kontrat değişikliği başarılı sayılmak için:
- Sürüm artışı doğru sınıfa göre yapılmış olmalı
- Required alan etkisi belgelenmiş olmalı
- Legacy payload testleri geçmiş olmalı
- Deprecation varsa kaldırma takvimi belirtilmiş olmalı
- Drift riski için mapper ve schema kontrolleri tamamlanmış olmalı
