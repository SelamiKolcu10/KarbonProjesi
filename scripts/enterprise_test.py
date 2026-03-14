import sys
import json

try:
    from src.agents.auditor import InputPayload, ProcessInputs, PrecursorInput
    from src.agents.strategist.chief_consultant import ChiefConsultantAgent
    print("✅ Kurumsal Modüller Başarıyla Yüklendi.")
except ImportError as e:
    print(f"❌ HATA: İçe aktarma sorunu. Lütfen klasör yapısını kontrol et.\nDetay: {e}")
    sys.exit(1)

def run_enterprise_simulation():
    print("\n" + "★"*70)
    print("🚀 CBAM ENTERPRISE AI - FULL SYSTEM INTEGRATION TEST")
    print("★"*70)

    # =====================================================================
    # ADIM 1: AJAN 1 (Data Fusion & Unit Normalization Simülasyonu)
    # Fabrikadan 1 PDF Fatura (Elektrik) ve 1 Excel (Üretim/Hammadde) geldi.
    # Ajan 1 bunları birleştirdi ve birimleri çevirdi (lbs -> ton).
    # =====================================================================
    print("\n[1/3] 🧬 Ajan #1: Data Fusion (Veri Birleştirme) devrede...")
    
    fused_data = {
        "facility_name": "GLOBAL ÇELİK A.Ş. (Enterprise Test)",
        "reporting_period": "2026-Q1",
        # Excel'den "11,023,113 lbs" geldi, Ajan 1 bunu 5000 Tona çevirdi!
        "production_quantity_tons": 5000.0, 
        "energy": {
            "electricity_mwh": 2500.0,   # PDF Faturadan geldi
            "natural_gas_m3": 100000.0   # Excel'den geldi
        },
        "process": {
            "electrode_ton": 12.5,
            "limestone_ton": 250.0
        },
        "precursors": [
            {"name": "pig-iron", "qty": 500.0, "factor": None}, # Kirli Tedarikçi (Default 2.30)
            {"name": "scrap-steel", "qty": 4000.0, "factor": 0.35} # Temiz Tedarikçi
        ]
    }
    print("   ✅ PDF ve Excel verileri tek bir JSON'da birleştirildi.")
    print("   🔄 Akıllı Çeviri: '11,023,113 lbs' üretim verisi '5000 Ton' olarak normalize edildi.")

    # =====================================================================
    # ADIM 2: AJAN 2 (Allocation & Dynamic Grid)
    # Fabrikanın sadece %85'i ihracata (CBAM'a) çalışıyor. %15 iç piyasa.
    # Şebeke verisi o ay rüzgarlı geçtiği için 0.43 değil, 0.38 (Canlı API).
    # =====================================================================
    print("\n[2/3] 🧮 Ajan #2: Gelişmiş Hesaplama (Allocation & Dynamic Grid) devrede...")
    
    payload = InputPayload(
        facility_name=fused_data["facility_name"],
        facility_id="TR-IST-ENT-001",
        reporting_period=fused_data["reporting_period"],
        production_quantity_tons=fused_data["production_quantity_tons"],
        electricity_consumption_mwh=fused_data["energy"]["electricity_mwh"],
        natural_gas_consumption_m3=fused_data["energy"]["natural_gas_m3"],
        coal_consumption_tons=0.0,
        process_inputs=ProcessInputs(
            electrode_consumption_ton=fused_data["process"]["electrode_ton"],
            limestone_consumption_ton=fused_data["process"]["limestone_ton"]
        ),
        precursors=[
            PrecursorInput(
                material_name=p["name"], 
                quantity_ton=p["qty"], 
                embedded_emissions_factor=p["factor"]
            ) for p in fused_data["precursors"]
        ],
        # YENİ LEVEL 99 ÖZELLİKLERİ:
        cbam_allocation_rate=0.85,  # Emisyonların sadece %85'i vergilendirilecek
        dynamic_grid_factor=0.38,   # API'den gelen canlı, daha temiz şebeke verisi
        data_source="enterprise_test"
    )
    print("   ✅ Paylaştırma Oranı (%85) ve Dinamik Şebeke (0.38) ayarlandı.")

    # =====================================================================
    # ADIM 3: AJAN 3 (Chief Consultant: Tsunami, Stress Test, Subsidies)
    # =====================================================================
    print("\n[3/3] 👔 Ajan #3: Baş Danışman (Chief Consultant) raporu hazırlıyor...")
    
    # Sistemin tüm beyinleri burada ateşleniyor
    consultant = ChiefConsultantAgent()
    report = consultant.generate_report(payload)

    # =====================================================================
    # YÖNETİCİ ÖZETİ (EXECUTIVE DASHBOARD) PRINT
    # =====================================================================
    print("\n" + "="*70)
    print(f"📊 {report.facility_name.upper()} - CBAM STRATEJİ RAPORU")
    print("="*70)

    # AI ÖZETİ
    print(f"\n🤖 AI DANIŞMAN NOTU:\n{report.ai_consultant_summary}\n")

    # 1. RİSK VE UYUM
    print(f"🚨 RİSK VE UYUM (COMPLIANCE GUARD)")
    print(f"   • Hazırlık Skoru: %{report.compliance_risk.readiness_score:.0f}")
    if report.compliance_risk.cost_of_dirty_supply_eur > 0:
        print(f"   • ⚠️ TEDARİKÇİ RİSKİ: Pik-Demir tedarikçiniz AB standartlarından kirli!")
        print(f"     Bu durum size fazladan €{report.compliance_risk.cost_of_dirty_supply_eur:,.2f} vergi cezası yaratıyor.")

    # 2. TSUNAMİ ETKİSİ (5 YIL)
    print(f"\n🌊 CBAM TSUNAMİ ETKİSİ (VERGİ PROJEKSİYONU)")
    for year, tax in report.five_year_projection.items():
        bar = "█" * int(tax / 20000) # Basit görselleştirme
        print(f"   • {year}: €{tax:>9,.2f} | {bar}")

    # 3. STRES TESTİ (MONTE CARLO)
    print(f"\n📈 PİYASA STRES TESTİ (Karbon Fiyatı Dalgalanması - 2030 bazlı)")
    print(f"   • En İyi Senaryo (-%20) : €{report.stress_test_scenarios['Best Case']:,.2f}")
    print(f"   • Beklenen Durum (Baz) : €{report.stress_test_scenarios['Base Case']:,.2f}")
    print(f"   • EN KÖTÜ SENARYO (+%30): €{report.stress_test_scenarios['Worst Case']:,.2f} ⚠️")

    # 4. YATIRIM STRATEJİSİ VE HİBELER
    print(f"\n💡 EN İYİ YATIRIM FIRSATI (STRATEGY SIMULATOR)")
    if report.top_recommendations:
        top_rec = report.top_recommendations[0]
        print(f"   ▶ {top_rec.strategy_name.upper()}")
        print(f"   • Yıllık Tasarruf: €{top_rec.annual_savings_eur:,.2f}")
        print(f"   • Tahmini Yatırım (CAPEX): €{top_rec.estimated_capex_eur:,.2f}")
        
        if top_rec.payback_period_years > 0:
            print(f"   • Amortisman (ROI): {top_rec.payback_period_years:.1f} Yıl")
        else:
            print(f"   • Amortisman (ROI): Hemen (0 Yıl)")
            
        if top_rec.potential_subsidies:
            print(f"   • 🎁 UYGUN HİBE/KREDİLER:")
            for sub in top_rec.potential_subsidies:
                print(f"      - {sub}")
    print("="*70)

if __name__ == "__main__":
    run_enterprise_simulation()
