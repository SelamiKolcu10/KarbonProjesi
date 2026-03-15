# Çoklu Ajan (Multi-Agent) Karbon Denetim Sistemi - Rol ve Yetki Dağılımı

Bu proje, fabrika karbon emisyon verilerini analiz etmek, vergi hesaplamalarını yapmak ve sürdürülebilirlik stratejileri geliştirmek üzere tasarlanmış otonom bir ajan ağıdır.

## 🤖 Ajan Profilleri ve Görevleri

### 1. Veri Madencisi (Data Miner)
*   **Görevi:** Ham fabrika verilerini (enerji tüketimi, üretim hacmi, atık oranları) toplamak, temizlemek ve işlenebilir formata getirmek.
*   **Girdi:** Ham veri setleri, sensör logları veya veritabanı yığınları (PDF, CSV).
*   **Çıktı:** Yapılandırılmış, normalize edilmiş ve doğrulanmış (JSON formatında) temiz veri.
*   **Rolü:** Sistemin dış dünyadan beslendiği ana giriş kapısıdır. Karmaşık ve dağınık veriyi anlamlı hale getirir.

### 2. Denetçi (Auditor)
*   **Görevi:** Temizlenmiş verileri kullanarak mevcut yasal düzenlemelere (ör. CBAM) göre karbon ayak izini ve tahmini karbon vergisini hesaplamak.
*   **Girdi:** Veri Madencisi'nden gelen temiz ve yapılandırılmış veri.
*   **Çıktı:** Karbon emisyon değerleri, vergi raporları, sektörel limit aşım uyarıları ve sayısal denetim metrikleri.
*   **Rolü:** Sistemin yasal ve matematiksel aklıdır. Verilerin düzenlemelere uygunluğunu denetler ve maliyet analizini gerçekleştirir.

### 3. Stratejist (Strategist)
*   **Görevi:** Denetçi'nin raporlarını analiz ederek karbon salınımını ve maliyetleri düşürecek optimizasyon önerileri (üretim bandı düzenlemeleri, enerji verimliliği planları) sunmak.
*   **Girdi:** Denetçi'den gelen maliyet ve emisyon raporları.
*   **Çıktı:** Aksiyon alınabilir eylem planları, senaryo analizleri ve tahminleme (predictive) raporları.
*   **Rolü:** Sistemin danışmanlık katmanıdır. Salt veriyi yorumlayarak stratejik iş zekası üretir.

### 4. Web Arayüz Yöneticisi (Frontend/UI Agent) - *[GELİŞTİRME AŞAMASINDA]*
*   **Görevi:** Arka planda çalışan diğer ajanların ürettiği analitik verileri, raporları ve stratejileri son kullanıcıya (fabrika yöneticisi, denetim uzmanı) görsel ve interaktif bir web arayüzünde sunmak.
*   **Girdi:** Denetçi ve Stratejist'ten gelen sonuç verileri.
*   **Çıktı:** Kullanıcı dostu paneller, grafikler, dinamik tablolar ve anlık bildirimler.
*   **Sınırlandırma:** Bu ajan veri manipülasyonu yapamaz. Sadece okuma, görselleştirme ve kullanıcı etkileşimini yönetme yetkisine sahiptir. Akıl ve işlem mantığı tamamen arka plan ajanlarındadır.

---

## 🔄 Ajanlar Arası İlişkiler ve İş Akışı (Genel Bakış)

Ajanlar, ardışık (pipeline) bir mimaride birbirini besleyecek şekilde çalışır:

1.  **Verinin Sisteme Girmesi:** Süreç **Veri Madencisi** ile başlar. Karmaşık loglar ve dokümanlar alınır, gereksiz bilgilerden arındırılır.
2.  **Hesaplama ve Denetim:** Temizlenen bu veriler **Denetçi** ajana iletilir. Denetçi, matematiksel modelleri çalıştırarak tesisin emisyon miktarını bulur ve olası vergi cezasını hesaplar.
3.  **Strateji Geliştirme:** Denetimden çıkan maliyetli tablo doğrudan **Stratejist** ajana aktarılır. Stratejist, "bu vergiyi veya salınımı nasıl düşürebiliriz?" sorusuna yanıt arayarak çözüm senaryoları (örnek: "X sürecini yenilenebilir enerjiye kaydır") üretir.
4.  **Kullanıcıya Sunum:** Tüm bu aşamalardan elde edilen temiz veri, mali döküm ve stratejik öneriler paketlenerek **Web Arayüz Yöneticisi**'ne gönderilir. Arayüz ajanı, çıkan bu değerli raporu yöneticinin ekranına grafikler ve paneller eşliğinde yansıtır.

Bu işbirliği sayesinde ham veriden yola çıkılıp, tamamen otonom bir şekilde son kullanıcıya stratejik kararlar aldırabilecek düzeyde rafine edilmiş bilgi sunulur.


---

## 📅 Ajan Sistemi Güncelleme Geçmişi (Özet)

*   **15 Mart 2026:** Tüm ajanların (Data Miner, Auditor, Strategist, UI Agent) görev tanımları, girdileri/çıktıları ve mimari içerisindeki ardışık veri akış rolleri yüksek seviyeli (high-level) bir yapıda yeniden düzenlendi.
