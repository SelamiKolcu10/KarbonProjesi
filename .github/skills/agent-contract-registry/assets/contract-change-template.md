# Contract Change Template

## 1) Değişiklik Özeti
- Değişiklik adı:
- İlgili ajan sınırı (Producer -> Consumer):
- Etkilenen model(ler):
- Mevcut sürüm:
- Önerilen yeni sürüm:
- Değişiklik sınıfı: PATCH / MINOR / MAJOR

## 2) Problem ve Gerekçe
- Hangi iş ihtiyacı bu değişikliği tetikledi?
- Değişiklik yapılmazsa oluşacak risk nedir?

## 3) Şema Farkı (Schema Diff)
### Eklenen alanlar
- alan_adı:
  - tip:
  - required mi:
  - default:
  - açıklama:

### Güncellenen alanlar
- alan_adı:
  - eski tip/kurallar:
  - yeni tip/kurallar:
  - kırıcı etki var mı:

### Kaldırılan/yeniden adlandırılan alanlar
- alan_adı:
  - yerine gelen alan:
  - deprecation başlangıç sürümü:
  - kaldırma hedef sürümü:

## 4) Required Fields Etki Analizi
- Yeni required alan var mı?
- Optional -> Required dönüşümü var mı?
- Tüketici tarafında zorunlu kod değişikliği gerekiyor mu?

## 5) Backward Compatibility Planı
- Desteklenecek legacy sürümler:
- Alias/adaptör stratejisi:
- Deprecation uyarı mesajları:
- Tam geçiş tarihi:

## 6) Test Planı
### Unit testler
- Üretici model validasyon testleri
- Tüketici model validasyon testleri

### Integration testler
- Producer -> Mapper -> Consumer tam akış testi
- Legacy payload kabul testi

### Regression testler
- Kritik metrik doğrulaması (emisyon, mali yükümlülük)
- Beklenen tolerans:

## 7) Operasyonel Etki
- API response değişikliği var mı?
- Orchestrator job çıktısı etkileniyor mu?
- Frontend/raporlama etkisi var mı?

## 8) Risk Değerlendirmesi
- Risk seviyesi: Low / Medium / High
- Ana riskler:
- Azaltım aksiyonları:
- Geri dönüş planı:

## 9) Onay Kriterleri
- [ ] Sürüm artışı kurala uygun
- [ ] JSON Schema güncel
- [ ] Required alanlar doğrulandı
- [ ] Legacy uyumluluk testleri geçti
- [ ] Changelog ve migration notları eklendi

## 10) Örnek Payloadlar
### Yeni sürüm örneği
{
  "model_version": "X.Y.Z",
  "...": "..."
}

### Legacy sürüm örneği
{
  "model_version": "A.B.C",
  "...": "..."
}
