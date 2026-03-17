// Mock data simulating Agent 1, 2, 3 JSON outputs

export const mockKpiData = {
  totalEmission: 124_850, // tCO₂e
  totalEmissionChange: +8.3, // % change from previous period
  cbamTax: 187_275, // EUR
  cbamTaxChange: +12.1,
  emissionIntensity: 1.42, // tCO₂/ton steel
  emissionIntensityChange: -3.2,
  complianceChange: +5.0,
  complianceStatus: "non_compliant" as "compliant" | "non_compliant" | "warning",
  lastAuditDate: "2025-03-10T08:30:00Z",
  lastDocument: "Fabrika_2025_Q1_Raporu.pdf",
  riskScore: 72,
};

export const mockEmissionBreakdown = {
  scope1: 58_420,
  scope2: 31_680,
  process: 34_750,
  sources: [
    { name: "Doğalgaz", value: 42_300, color: "#F59E0B" },
    { name: "Kömür", value: 28_100, color: "#6B7280" },
    { name: "Elektrik", value: 31_680, color: "#3B82F6" },
    { name: "Proses", value: 14_200, color: "#8B5CF6" },
    { name: "Hammadde", value: 8_570, color: "#EC4899" },
  ],
};

export const mockMonthlyTrend = [
  { ay: "Oca", emisyon: 18_200, hedef: 16_000 },
  { ay: "Şub", emisyon: 17_500, hedef: 16_000 },
  { ay: "Mar", emisyon: 19_800, hedef: 16_000 },
  { ay: "Nis", emisyon: 20_100, hedef: 16_000 },
  { ay: "May", emisyon: 18_900, hedef: 16_000 },
  { ay: "Haz", emisyon: 21_450, hedef: 16_000 },
  { ay: "Tem", emisyon: 22_300, hedef: 16_000 },
  { ay: "Ağu", emisyon: 20_800, hedef: 16_000 },
  { ay: "Eyl", emisyon: 19_600, hedef: 16_000 },
  { ay: "Eki", emisyon: 21_200, hedef: 16_000 },
  { ay: "Kas", emisyon: 20_500, hedef: 16_000 },
  { ay: "Ara", emisyon: 23_100, hedef: 16_000 },
];

export const mockEmissionDetails = [
  { id: 1, kaynak: "Doğalgaz Yakımı", miktar: 4_230_000, birim: "m³", kgCO2: 42_300_000, tCO2e: 42_300, anomali: false },
  { id: 2, kaynak: "Kömür Tüketimi", miktar: 12_800, birim: "ton", kgCO2: 28_160_000, tCO2e: 28_100, anomali: true, anomaliMesaj: "Önceki dönemden %34 yüksek" },
  { id: 3, kaynak: "Satın Alınan Elektrik", miktar: 45_600, birim: "MWh", kgCO2: 31_680_000, tCO2e: 31_680, anomali: false },
  { id: 4, kaynak: "Çelik Üretim Prosesi", miktar: 87_900, birim: "ton", kgCO2: 14_200_000, tCO2e: 14_200, anomali: false },
  { id: 5, kaynak: "Hammadde Taşıma", miktar: 320_000, birim: "km", kgCO2: 8_570_000, tCO2e: 8_570, anomali: true, anomaliMesaj: "Tedarikçi değişimi kaynaklı sapma" },
];

export const mockAuditTrail = [
  { timestamp: "2025-03-10T09:15:00Z", islem: "PDF yüklendi", kullanici: "Ahmet Yılmaz", detay: "Fabrika_2025_Q1_Raporu.pdf — 2.4 MB" },
  { timestamp: "2025-03-10T09:16:30Z", islem: "Ajan 1 çalıştı", kullanici: "Sistem", detay: "Veri çıkarımı tamamlandı — güven skoru: %87" },
  { timestamp: "2025-03-10T09:18:45Z", islem: "Ajan 2 çalıştı", kullanici: "Sistem", detay: "Emisyon hesaplama ve CBAM vergisi tamamlandı" },
  { timestamp: "2025-03-10T09:21:00Z", islem: "Ajan 3 çalıştı", kullanici: "Sistem", detay: "Strateji raporu oluşturuldu — 5 öneri" },
  { timestamp: "2025-03-10T09:22:10Z", islem: "Rapor oluşturuldu", kullanici: "Sistem", detay: "PDF raporu hazır — 18 sayfa" },
];

export const mockMaliEtki = {
  cbamFazFaktoru: 2.5, // 2026 %
  brutVergi: 187_275,
  efektifVergi: 156_400,
  celikBasinaMaliyet: 2.13, // EUR/ton
  uretimMiktari: 87_900, // ton çelik
};

export const mockCbamTimeline = [
  { yil: 2026, faz: 2.5, aktif: true },
  { yil: 2027, faz: 10 },
  { yil: 2028, faz: 22.5 },
  { yil: 2029, faz: 35 },
  { yil: 2030, faz: 47.5 },
  { yil: 2031, faz: 60 },
  { yil: 2032, faz: 72.5 },
  { yil: 2033, faz: 85 },
  { yil: 2034, faz: 100 },
];

export const mockScenarios = [
  {
    id: 1,
    baslik: "Elektriği Yenilenebilir Enerjiye Geçir",
    aciklama: "Rüzgar ve güneş enerjisi ile elektrik tedariki",
    tasarrufEmisyon: 31_680,
    maliKazanc: 48_200,
    zorluk: "orta" as const,
    oncelik: "yüksek" as const,
    sure: "12 ay",
    secili: false,
  },
  {
    id: 2,
    baslik: "Kömür Tüketimini Azalt",
    aciklama: "Doğalgaz ile hibrit yakma sistemi kurulumu",
    tasarrufEmisyon: 18_200,
    maliKazanc: 27_800,
    zorluk: "yüksek" as const,
    oncelik: "yüksek" as const,
    sure: "18 ay",
    secili: false,
  },
  {
    id: 3,
    baslik: "Isı Geri Kazanım Sistemi",
    aciklama: "Atık ısıyı prosese geri döndür",
    tasarrufEmisyon: 8_400,
    maliKazanc: 12_600,
    zorluk: "düşük" as const,
    oncelik: "orta" as const,
    sure: "6 ay",
    secili: false,
  },
  {
    id: 4,
    baslik: "Tedarik Zinciri Optimizasyonu",
    aciklama: "Yerel hammadde tedarikçilerine geçiş",
    tasarrufEmisyon: 6_200,
    maliKazanc: 9_400,
    zorluk: "orta" as const,
    oncelik: "orta" as const,
    sure: "9 ay",
    secili: false,
  },
  {
    id: 5,
    baslik: "Karbon Yakalama Pilot Projesi",
    aciklama: "Baca gazı karbondioksit yakalama sistemleri",
    tasarrufEmisyon: 22_000,
    maliKazanc: 33_500,
    zorluk: "yüksek" as const,
    oncelik: "düşük" as const,
    sure: "36 ay",
    secili: false,
  },
];

export const mockAiOzet = `**Kritik Durum Tespiti**
Fabrika, 2025 Q1 döneminde toplam 124.850 tCO₂e emisyon üretmiş olup CBAM eşik değerlerinin %8,3 üzerindedir.

**En Yüksek Risk Kaynakları**
Kömür tüketiminde önceki döneme göre %34'lük anormal artış tespit edilmiştir. Bu artışın yeni tedarikçi sözleşmesinden kaynaklandığı değerlendirilmektedir.

**Acil Öneri**
Yenilenebilir elektrik geçişi tek başına CBAM yükümlülüğünüzü %25 oranında azaltabilir. 2026 başlangıç tarihinden önce bu adımın atılması kritik önem taşımaktadır.

**Mali Projeksiyon**
Mevcut emisyon seviyesinde 2026 CBAM yükümlülüğünüz €187.275'dir. Önerilen senaryoların tamamı uygulandığında bu rakam €61.200'e düşebilir.`;

export const mockGeçmisRaporlar = [
  { id: 1, tarih: "2025-03-10T08:30:00Z", tesis: "İzmir Çelik Fabrikası A.Ş.", uyumluluk: "non_compliant", emisyon: 124_850, cbamVergi: 187_275, guvenSkoru: 87 },
  { id: 2, tarih: "2024-12-15T10:00:00Z", tesis: "İzmir Çelik Fabrikası A.Ş.", uyumluluk: "warning", emisyon: 115_200, cbamVergi: 172_800, guvenSkoru: 91 },
  { id: 3, tarih: "2024-09-20T09:15:00Z", tesis: "İzmir Çelik Fabrikası A.Ş.", uyumluluk: "compliant", emisyon: 98_400, cbamVergi: 147_600, guvenSkoru: 95 },
  { id: 4, tarih: "2024-06-05T11:30:00Z", tesis: "Ankara Demir Sanayi Ltd.", uyumluluk: "warning", emisyon: 78_900, cbamVergi: 118_350, guvenSkoru: 83 },
  { id: 5, tarih: "2024-03-18T08:45:00Z", tesis: "Bursa Metal İşleme A.Ş.", uyumluluk: "compliant", emisyon: 54_200, cbamVergi: 81_300, guvenSkoru: 96 },
];

export const mockNotifications = [
  { id: 1, tip: "critical", mesaj: "Emisyon eşiği aşıldı — kömür tüketimi kritik seviyede", zaman: "2 saat önce", okundu: false },
  { id: 2, tip: "warning", mesaj: "Veri güven skoru düşük — Hammadde taşıma verisi doğrulanmalı", zaman: "5 saat önce", okundu: false },
  { id: 3, tip: "info", mesaj: "CBAM 2026 uygulama takvimi güncellemesi yayınlandı", zaman: "1 gün önce", okundu: true },
  { id: 4, tip: "info", mesaj: "Q1 2025 raporu başarıyla oluşturuldu", zaman: "2 gün önce", okundu: true },
];

// Projection data
export const mockProjectionData = {
  bazYil: 2025,
  bazEmisyon: 124_850,
  hedefAzaltma: 40, // %
  onlemBaslangicYili: 2027,
  karbonFiyati: 85, // EUR/tCO2
  
  yillikProjeksiyon: [
    { yil: 2026, cbamFaz: 2.5, bazEmisyon: 124_818, optimizeEmisyon: 124_818, azaltim: 0, bazVergi: 265_238, optimizeVergi: 265_238, tasarruf: 0, kumulatifTasarruf: 0 },
    { yil: 2027, cbamFaz: 10, bazEmisyon: 127_314, optimizeEmisyon: 120_949, azaltim: 5.0, bazVergi: 1_082_172, optimizeVergi: 1_028_063, tasarruf: 54_109, kumulatifTasarruf: 54_109 },
    { yil: 2028, cbamFaz: 22.5, bazEmisyon: 129_861, optimizeEmisyon: 117_199, azaltim: 9.8, bazVergi: 2_483_585, optimizeVergi: 2_241_436, tasarruf: 242_150, kumulatifTasarruf: 296_258 },
    { yil: 2029, cbamFaz: 35, bazEmisyon: 132_458, optimizeEmisyon: 113_566, azaltim: 14.3, bazVergi: 3_940_621, optimizeVergi: 3_378_590, tasarruf: 562_031, kumulatifTasarruf: 858_289 },
    { yil: 2030, cbamFaz: 47.5, bazEmisyon: 135_107, optimizeEmisyon: 110_046, azaltim: 18.5, bazVergi: 5_454_946, optimizeVergi: 4_443_807, tasarruf: 1_011_858, kumulatifTasarruf: 1_870_148 },
    { yil: 2031, cbamFaz: 60, bazEmisyon: 137_809, optimizeEmisyon: 106_634, azaltim: 22.6, bazVergi: 7_028_267, optimizeVergi: 5_438_339, tasarruf: 1_589_928, kumulatifTasarruf: 3_460_076 },
    { yil: 2032, cbamFaz: 72.5, bazEmisyon: 140_565, optimizeEmisyon: 103_328, azaltim: 26.5, bazVergi: 8_662_339, optimizeVergi: 6_367_615, tasarruf: 2_294_724, kumulatifTasarruf: 5_754_799 },
    { yil: 2033, cbamFaz: 85, bazEmisyon: 143_377, optimizeEmisyon: 100_125, azaltim: 30.2, bazVergi: 10_358_963, optimizeVergi: 7_234_059, tasarruf: 3_124_913, kumulatifTasarruf: 8_879_712 },
    { yil: 2034, cbamFaz: 100, bazEmisyon: 146_244, optimizeEmisyon: 97_021, azaltim: 33.7, bazVergi: 12_430_755, optimizeVergi: 8_246_817, tasarruf: 4_183_938, kumulatifTasarruf: 13_063_650 },
  ],
  
  toplamlar: {
    bazVergiToplam: 51_706_886,
    optimizeVergiToplam: 38_643_234,
    toplamTasarruf: 13_063_652,
    emisyonAzaltmaYuzdesi: 22,
    basabasYili: 2031,
  }
};
