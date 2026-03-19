# PR Checklist - Agent Contract Registry

Bu kontrol listesi, ajanlar arası kontrat değişikliği içeren her PR için zorunludur.

## A. Değişiklik Sınıflandırması
- [ ] Değişiklik türü belirlendi: PATCH / MINOR / MAJOR
- [ ] Sürüm artışı değişiklik türü ile uyumlu
- [ ] Breaking etki varsa açıkça işaretlendi

## B. Model ve Şema Doğruluğu
- [ ] Pydantic model güncellemesi tamamlandı
- [ ] model_version alanı güncellendi
- [ ] Required alanlar net biçimde tanımlandı
- [ ] JSON Schema çıktısı model ile tutarlı
- [ ] Alan tipleri ve validasyon sınırları gözden geçirildi

## C. Backward Compatibility
- [ ] En az bir önceki minor sürüm payload desteği doğrulandı
- [ ] Field rename/silme varsa deprecation planı eklendi
- [ ] Alias veya adapter katmanı (gerekiyorsa) eklendi
- [ ] Legacy payload örnekleri ile test edildi

## D. Drift ve Mapper Kontrolü
- [ ] Producer model -> mapper -> consumer model zinciri doğrulandı
- [ ] Mapper çıktısı hedef Pydantic modelini hatasız geçiyor
- [ ] Runtime validasyon ile JSON Schema davranışı uyumlu

## E. Test Kapsamı
- [ ] Unit testler güncellendi
- [ ] Integration testler güncellendi
- [ ] Contract snapshot/regression testleri güncellendi
- [ ] Kritik finansal/emisyon metriklerinde beklenmeyen sapma yok

## F. Dokümantasyon ve Operasyon
- [ ] Changelog girdisi eklendi
- [ ] Migration adımları eklendi (breaking/deprecation durumunda)
- [ ] Kaldırılacak alanlar için hedef sürüm belirtildi
- [ ] API/Orchestrator response etkisi belgelenmiş

## G. Onay Kapıları
- [ ] En az bir reviewer kontrat uyumluluğunu onayladı
- [ ] Risk seviyesi değerlendirildi (Low/Medium/High)
- [ ] Geri dönüş planı (rollback/feature flag) tanımlandı

## PR Sonucu
- [ ] Bu PR kontrat güvenliği açısından merge edilmeye hazır

## Reviewer Notu (zorunlu)
- Etkilenen kontratlar:
- Uyumluluk seviyesi:
- Kalan riskler:
- Takip aksiyonu:
