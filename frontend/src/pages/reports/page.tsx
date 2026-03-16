import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import Papa from "papaparse";
import {
  FileText,
  Download,
  FileSpreadsheet,
  Search,
  Filter,
  Calendar,
  Building2,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Eye,
  TrendingDown,
  TrendingUp,
  BarChart3,
  Euro,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils.ts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Input } from "@/components/ui/input.tsx";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select.tsx";
import { mockGeçmisRaporlar, mockEmissionDetails, mockMaliEtki } from "@/lib/mock-data.ts";
import { toast } from "sonner";

// ─── Types ─────────────────────────────────────────────────────────────────────
type Compliance = "compliant" | "warning" | "non_compliant";

const complianceConfig: Record<Compliance, {
  label: string; badgeClass: string; icon: React.ReactNode; rowClass: string;
}> = {
  compliant: {
    label: "Uyumlu",
    badgeClass: "bg-green-500/15 text-green-400 border-green-500/25",
    icon: <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />,
    rowClass: "",
  },
  warning: {
    label: "Dikkat",
    badgeClass: "bg-yellow-500/15 text-yellow-400 border-yellow-500/25",
    icon: <AlertTriangle className="w-3.5 h-3.5 text-yellow-400" />,
    rowClass: "bg-yellow-500/3",
  },
  non_compliant: {
    label: "Uyumsuz",
    badgeClass: "bg-red-500/15 text-red-400 border-red-500/25",
    icon: <ShieldAlert className="w-3.5 h-3.5 text-red-400" />,
    rowClass: "bg-red-500/3",
  },
};

// ─── Formatters ────────────────────────────────────────────────────────────────
const fmt = (n: number) => new Intl.NumberFormat("tr-TR").format(n);
const fmtEur = (n: number) =>
  new Intl.NumberFormat("tr-TR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);
const fmtDate = (iso: string) =>
  new Intl.DateTimeFormat("tr-TR", { dateStyle: "medium" }).format(new Date(iso));
const fmtFull = (iso: string) =>
  new Intl.DateTimeFormat("tr-TR", { dateStyle: "long", timeStyle: "short" }).format(new Date(iso));

// ─── PDF Generator ──────────────────────────────────────────────────────────────
function generateReportPDF(report: (typeof mockGeçmisRaporlar)[0]) {
  const doc = new jsPDF();
  const pageW = doc.internal.pageSize.getWidth();

  doc.setFillColor(15, 23, 42);
  doc.rect(0, 0, pageW, 32, "F");

  doc.setTextColor(255, 255, 255);
  doc.setFontSize(16);
  doc.setFont("helvetica", "bold");
  doc.text("CBAM KARBON DENETIM RAPORU", pageW / 2, 14, { align: "center" });

  doc.setFontSize(9);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(148, 163, 184);
  doc.text("Karbon Sinir Duzenleme Mekanizmasi - Ajan 4 Ciktisi", pageW / 2, 22, { align: "center" });

  doc.setTextColor(30, 30, 30);
  doc.setFontSize(11);
  doc.setFont("helvetica", "bold");
  doc.text("Denetim Bilgileri", 14, 44);
  doc.setDrawColor(220, 220, 220);
  doc.line(14, 46, pageW - 14, 46);

  const meta = [
    ["Tesis Adi",          report.tesis],
    ["Denetim Tarihi",     fmtFull(report.tarih)],
    ["Periyot",            "2025 Q1 (Ocak - Mart 2025)"],
    ["Uyumluluk Durumu",   complianceConfig[report.uyumluluk as Compliance].label],
    ["Veri Guven Skoru",   `%${report.guvenSkoru}`],
  ];

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  meta.forEach(([k, v], i) => {
    const y = 54 + i * 7;
    doc.setTextColor(100, 100, 100);
    doc.text(k + ":", 14, y);
    doc.setTextColor(30, 30, 30);
    doc.text(v, 70, y);
  });

  const kpis = [
    { label: "Toplam Emisyon", value: `${fmt(report.emisyon)} tCO2e` },
    { label: "CBAM Vergisi (Tahmini)", value: fmtEur(report.cbamVergi) },
    { label: "Emisyon Yogunlugu", value: "1,42 tCO2/ton" },
    { label: "Uretim Miktari", value: "87.900 ton" },
  ];
  const boxW = (pageW - 28 - 9) / 4;
  kpis.forEach((kpi, i) => {
    const x = 14 + i * (boxW + 3);
    const y = 100;
    doc.setFillColor(245, 247, 250);
    doc.roundedRect(x, y, boxW, 18, 2, 2, "F");
    doc.setFontSize(7);
    doc.setTextColor(100, 100, 100);
    doc.text(kpi.label, x + boxW / 2, y + 6, { align: "center" });
    doc.setFontSize(10);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(30, 30, 30);
    doc.text(kpi.value, x + boxW / 2, y + 13, { align: "center" });
    doc.setFont("helvetica", "normal");
  });

  doc.setFontSize(11);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(30, 30, 30);
  doc.text("Detayli Emisyon Kirilimi", 14, 130);

  autoTable(doc, {
    startY: 134,
    head: [["Emisyon Kaynagi", "Miktar", "Birim", "tCO2e", "Durum"]],
    body: mockEmissionDetails.map((r) => [
      r.kaynak,
      new Intl.NumberFormat("tr-TR").format(r.miktar),
      r.birim,
      fmt(r.tCO2e),
      r.anomali ? "! Anomali" : "Normal",
    ]),
    foot: [["TOPLAM", "", "", fmt(mockEmissionDetails.reduce((s, r) => s + r.tCO2e, 0)), ""]],
    theme: "grid",
    headStyles: { fillColor: [15, 23, 42], textColor: 255, fontSize: 8, fontStyle: "bold" },
    bodyStyles: { fontSize: 8, textColor: [30, 30, 30] },
    footStyles: { fillColor: [240, 240, 240], fontStyle: "bold", fontSize: 8 },
    columnStyles: {
      0: { cellWidth: 60 },
      1: { halign: "right" },
      3: { halign: "right", fontStyle: "bold" },
      4: { halign: "center" },
    },
    alternateRowStyles: { fillColor: [248, 250, 252] },
    didDrawCell: (data) => {
      if (data.section === "body" && data.column.index === 4) {
        const val = mockEmissionDetails[data.row.index];
        if (val?.anomali) {
          doc.setTextColor(217, 119, 6);
        } else {
          doc.setTextColor(22, 163, 74);
        }
      }
    },
  });

  const afterTable = (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 10;

  doc.setFontSize(11);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(30, 30, 30);
  doc.text("Mali Etki - CBAM Yukumluluğu", 14, afterTable);

  autoTable(doc, {
    startY: afterTable + 4,
    head: [["Kalem", "Deger"]],
    body: [
      ["CBAM Faz Faktoru (2026)", `%${mockMaliEtki.cbamFazFaktoru}`],
      ["Brut Vergi Yukumluluğu", fmtEur(mockMaliEtki.brutVergi)],
      ["Efektif Vergi (Krediler haric)", fmtEur(mockMaliEtki.efektifVergi)],
      ["Celik Basina Maliyet", `€${mockMaliEtki.celikBasinaMaliyet.toFixed(2)}/ton`],
    ],
    theme: "striped",
    headStyles: { fillColor: [15, 23, 42], textColor: 255, fontSize: 8 },
    bodyStyles: { fontSize: 8 },
    alternateRowStyles: { fillColor: [248, 250, 252] },
    columnStyles: { 1: { halign: "right", fontStyle: "bold" } },
  });

  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(7);
    doc.setTextColor(150, 150, 150);
    doc.text(
      `CBAM Karbon Yonetim Sistemi - Ajan 4 Ciktisi - Sayfa ${i}/${pageCount}`,
      pageW / 2,
      doc.internal.pageSize.getHeight() - 8,
      { align: "center" }
    );
  }

  doc.save(`CBAM_Rapor_${report.tesis.replace(/\s+/g, "_")}_${fmtDate(report.tarih).replace(/\./g, "-")}.pdf`);
}

// ─── CSV Exporter ───────────────────────────────────────────────────────────────
function exportAllCSV(data: typeof mockGeçmisRaporlar) {
  const rows = data.map((r) => ({
    "Denetim Tarihi":     fmtDate(r.tarih),
    "Tesis Adi":          r.tesis,
    "Uyumluluk":          complianceConfig[r.uyumluluk as Compliance].label,
    "Toplam Emisyon (tCO2e)": r.emisyon,
    "CBAM Vergisi (EUR)": r.cbamVergi,
    "Guven Skoru (%)":    r.guvenSkoru,
  }));
  const csv = Papa.unparse(rows, { quotes: true, header: true, delimiter: ";" });
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `CBAM_Denetim_Arsivi_${new Date().toISOString().split("T")[0]}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// ─── Summary Stats ──────────────────────────────────────────────────────────────
function SummaryStats({ data }: { data: typeof mockGeçmisRaporlar }) {
  const total = data.length;
  const compliant = data.filter((r) => r.uyumluluk === "compliant").length;
  const avgEmission = total > 0 ? data.reduce((s, r) => s + r.emisyon, 0) / total : 0;
  const totalTax = data.reduce((s, r) => s + r.cbamVergi, 0);
  const trend = data.length > 1
    ? ((data[0].emisyon - data[data.length - 1].emisyon) / data[data.length - 1].emisyon) * 100
    : 0;

  return (
    <div className="grid grid-cols-4 gap-3">
      {[
        {
          label: "Toplam Denetim",
          value: String(total),
          sub: "kayıt",
          icon: <FileText className="w-4 h-4" />,
          color: "text-foreground",
          bg: "bg-muted/30 border-border/50",
        },
        {
          label: "Uyumluluk Oranı",
          value: total > 0 ? `%${Math.round((compliant / total) * 100)}` : "—",
          sub: `${compliant}/${total} uyumlu`,
          icon: <ShieldCheck className="w-4 h-4" />,
          color: compliant / total >= 0.7 ? "text-green-400" : "text-yellow-400",
          bg: compliant / total >= 0.7 ? "bg-green-500/5 border-green-500/20" : "bg-yellow-500/5 border-yellow-500/20",
        },
        {
          label: "Ort. Emisyon",
          value: `${fmt(Math.round(avgEmission))}`,
          sub: "tCO₂e / dönem",
          icon: trend > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />,
          color: trend > 0 ? "text-red-400" : "text-green-400",
          bg: "bg-muted/30 border-border/50",
        },
        {
          label: "Toplam CBAM Vergisi",
          value: fmtEur(totalTax),
          sub: "tüm dönemler",
          icon: <Euro className="w-4 h-4" />,
          color: "text-orange-400",
          bg: "bg-orange-500/5 border-orange-500/20",
        },
      ].map((stat) => (
        <Card key={stat.label} className={cn("glass-card border", stat.bg)}>
          <CardContent className="p-4">
            <div className={cn("flex items-center gap-1.5 mb-2", stat.color)}>
              {stat.icon}
              <span className="text-[10px] font-medium text-muted-foreground">{stat.label}</span>
            </div>
            <p className={cn("text-xl font-bold tabular-nums", stat.color)}>{stat.value}</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">{stat.sub}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// ─── Report Detail Row ──────────────────────────────────────────────────────────
function ReportRow({
  report,
  onPdf,
}: {
  report: (typeof mockGeçmisRaporlar)[0];
  onPdf: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const cfg = complianceConfig[report.uyumluluk as Compliance];

  return (
    <>
      <tr
        className={cn(
          "border-b border-border/50 last:border-0 transition-colors cursor-pointer",
          cfg.rowClass,
          expanded ? "bg-accent/40" : "hover:bg-accent/30"
        )}
        onClick={() => setExpanded((o) => !o)}
      >
        <td className="px-4 py-3">
          <div className="flex items-center gap-2">
            {expanded
              ? <ChevronDownIcon className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" />
              : <ChevronRightIcon className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" />}
            <span className="text-xs text-foreground font-medium">{fmtDate(report.tarih)}</span>
          </div>
        </td>
        <td className="px-4 py-3">
          <div className="flex items-center gap-2">
            <Building2 className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" />
            <span className="text-xs text-foreground">{report.tesis}</span>
          </div>
        </td>
        <td className="px-4 py-3 text-right">
          <span className="text-xs tabular-nums text-foreground">{fmt(report.emisyon)}</span>
          <span className="text-[10px] text-muted-foreground ml-1">tCO₂e</span>
        </td>
        <td className="px-4 py-3 text-right">
          <span className="text-xs tabular-nums text-foreground">{fmtEur(report.cbamVergi)}</span>
        </td>
        <td className="px-4 py-3 text-center">
          <div className="flex items-center justify-center gap-1.5">
            <Badge className={cn("text-[10px] px-1.5 gap-1", cfg.badgeClass)}>
              {cfg.icon}
              {cfg.label}
            </Badge>
          </div>
        </td>
        <td className="px-4 py-3 text-center">
          <div className="flex items-center justify-center">
            <div className={cn(
              "text-[10px] font-semibold px-2 py-0.5 rounded-full",
              report.guvenSkoru >= 90 ? "bg-green-500/15 text-green-400" :
              report.guvenSkoru >= 80 ? "bg-yellow-500/15 text-yellow-400" :
              "bg-red-500/15 text-red-400"
            )}>
              %{report.guvenSkoru}
            </div>
          </div>
        </td>
        <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
          <div className="flex items-center justify-end gap-1.5">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0 text-muted-foreground hover:text-foreground"
              onClick={() => setExpanded((o) => !o)}
            >
              <Eye className="w-3.5 h-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 px-2 gap-1 text-muted-foreground hover:text-foreground text-[10px]"
              onClick={onPdf}
            >
              <Download className="w-3 h-3" />
              PDF
            </Button>
          </div>
        </td>
      </tr>

      {expanded && (
        <tr className="border-b border-border/50">
          <td colSpan={7} className="px-4 pb-3 pt-0">
            <motion.div
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className="bg-muted/20 rounded-xl border border-border/40 p-4 grid grid-cols-3 gap-4"
            >
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2 font-medium">Emisyon Kırılımı</p>
                <div className="space-y-1.5">
                  {[
                    { label: "Scope 1 (Doğrudan)", value: "58.420", color: "bg-yellow-500" },
                    { label: "Scope 2 (Elektrik)",  value: "31.680", color: "bg-blue-500"   },
                    { label: "Proses",               value: "34.750", color: "bg-purple-500" },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between text-[11px]">
                      <div className="flex items-center gap-1.5">
                        <span className={cn("w-2 h-2 rounded-sm", item.color)} />
                        <span className="text-muted-foreground">{item.label}</span>
                      </div>
                      <span className="text-foreground font-medium tabular-nums">{item.value} tCO₂e</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2 font-medium">Mali Özet</p>
                <div className="space-y-1.5">
                  {[
                    { label: "CBAM Faz Faktörü", value: "%2,5" },
                    { label: "Brüt Vergi",        value: fmtEur(report.cbamVergi) },
                    { label: "Efektif Vergi",      value: fmtEur(Math.round(report.cbamVergi * 0.835)) },
                    { label: "€/ton Çelik",        value: "€2,13" },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between text-[11px]">
                      <span className="text-muted-foreground">{item.label}</span>
                      <span className="text-foreground font-medium tabular-nums">{item.value}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2 font-medium">Tespit Edilen Anomaliler</p>
                <div className="space-y-1.5">
                  {report.uyumluluk !== "compliant" ? (
                    <>
                      <div className="flex items-start gap-1.5 text-[11px]">
                        <AlertTriangle className="w-3 h-3 text-yellow-400 flex-shrink-0 mt-0.5" />
                        <span className="text-muted-foreground">Kömür tüketiminde önceki dönemden %34 artış</span>
                      </div>
                      <div className="flex items-start gap-1.5 text-[11px]">
                        <AlertTriangle className="w-3 h-3 text-yellow-400 flex-shrink-0 mt-0.5" />
                        <span className="text-muted-foreground">Hammadde taşıma — tedarikçi değişimi</span>
                      </div>
                    </>
                  ) : (
                    <div className="flex items-center gap-1.5 text-[11px]">
                      <CheckCircle2 className="w-3 h-3 text-green-400" />
                      <span className="text-muted-foreground">Anomali tespit edilmedi</span>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </td>
        </tr>
      )}
    </>
  );
}

function ChevronDownIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path d="m6 9 6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function ChevronRightIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path d="m9 6 6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ─── Page ───────────────────────────────────────────────────────────────────────
export default function ReportsPage() {
  const [search, setSearch] = useState("");
  const [filterCompliance, setFilterCompliance] = useState<string>("all");
  const [filterTesis, setFilterTesis] = useState<string>("all");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const uniqueTesisler = useMemo(
    () => Array.from(new Set(mockGeçmisRaporlar.map((r) => r.tesis))),
    []
  );

  const filtered = useMemo(() => {
    return mockGeçmisRaporlar.filter((r) => {
      if (search && !r.tesis.toLowerCase().includes(search.toLowerCase())) return false;
      if (filterCompliance !== "all" && r.uyumluluk !== filterCompliance) return false;
      if (filterTesis !== "all" && r.tesis !== filterTesis) return false;
      if (dateFrom && new Date(r.tarih) < new Date(dateFrom)) return false;
      if (dateTo && new Date(r.tarih) > new Date(dateTo + "T23:59:59")) return false;
      return true;
    });
  }, [search, filterCompliance, filterTesis, dateFrom, dateTo]);

  const hasFilters = search || filterCompliance !== "all" || filterTesis !== "all" || dateFrom || dateTo;

  const clearFilters = () => {
    setSearch("");
    setFilterCompliance("all");
    setFilterTesis("all");
    setDateFrom("");
    setDateTo("");
  };

  const handlePdf = (report: (typeof mockGeçmisRaporlar)[0]) => {
    toast.promise(
      new Promise<void>((resolve) => {
        setTimeout(() => {
          generateReportPDF(report);
          resolve();
        }, 600);
      }),
      {
        loading: "PDF hazırlanıyor...",
        success: "PDF başarıyla indirildi",
        error: "PDF oluşturma hatası",
      }
    );
  };

  const handleCsvExport = () => {
    exportAllCSV(filtered);
    toast.success(`${filtered.length} kayıt Excel'e aktarıldı`);
  };

  return (
    <div className="space-y-5">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="flex items-start justify-between"
      >
        <div>
          <h2 className="text-xl font-bold text-foreground">Geçmiş Raporlar</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Denetim arşivi — {mockGeçmisRaporlar.length} kayıt
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            className="gap-2 text-xs h-9"
            onClick={handleCsvExport}
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            Excel'e Aktar ({filtered.length})
          </Button>
          <Button
            className="gap-2 text-xs h-9"
            onClick={() => {
              toast.promise(
                new Promise<void>((res) => setTimeout(() => { filtered.forEach((r) => generateReportPDF(r)); res(); }, 400)),
                { loading: "Tüm PDF'ler hazırlanıyor...", success: "İndirme başladı", error: "Hata" }
              );
            }}
          >
            <Download className="w-3.5 h-3.5" />
            Tümünü İndir
          </Button>
        </div>
      </motion.div>

      {/* Summary stats */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35, delay: 0.05 }}>
        <SummaryStats data={filtered} />
      </motion.div>

      {/* Filters */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35, delay: 0.1 }}>
        <Card className="glass-card border-border">
          <CardHeader className="pb-3 pt-4">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Filter className="w-3.5 h-3.5 text-muted-foreground" />
              Filtreler
              {hasFilters && (
                <button onClick={clearFilters} className="flex items-center gap-1 text-[10px] text-muted-foreground hover:text-foreground transition-colors ml-2 font-normal">
                  <X className="w-3 h-3" />
                  Temizle
                </button>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-5 gap-3">
              <div className="col-span-2 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                <Input
                  placeholder="Tesis adı ara..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9 h-9 text-xs"
                />
              </div>

              <Select value={filterCompliance} onValueChange={setFilterCompliance}>
                <SelectTrigger className="h-9 text-xs">
                  <SelectValue placeholder="Uyumluluk" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tüm Durumlar</SelectItem>
                  <SelectItem value="compliant">Uyumlu</SelectItem>
                  <SelectItem value="warning">Dikkat</SelectItem>
                  <SelectItem value="non_compliant">Uyumsuz</SelectItem>
                </SelectContent>
              </Select>

              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
                <Input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="pl-9 h-9 text-xs"
                  placeholder="Başlangıç tarihi"
                />
              </div>

              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
                <Input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="pl-9 h-9 text-xs"
                  placeholder="Bitiş tarihi"
                />
              </div>
            </div>

            {hasFilters && (
              <div className="flex items-center gap-2 mt-3 flex-wrap">
                <span className="text-[10px] text-muted-foreground">Aktif filtreler:</span>
                {search && (
                  <Badge variant="secondary" className="text-[10px] gap-1 px-2">
                    Arama: "{search}"
                    <button onClick={() => setSearch("")}><X className="w-2.5 h-2.5" /></button>
                  </Badge>
                )}
                {filterCompliance !== "all" && (
                  <Badge variant="secondary" className="text-[10px] gap-1 px-2">
                    {complianceConfig[filterCompliance as Compliance]?.label}
                    <button onClick={() => setFilterCompliance("all")}><X className="w-2.5 h-2.5" /></button>
                  </Badge>
                )}
                {dateFrom && (
                  <Badge variant="secondary" className="text-[10px] gap-1 px-2">
                    Başlangıç: {fmtDate(dateFrom)}
                    <button onClick={() => setDateFrom("")}><X className="w-2.5 h-2.5" /></button>
                  </Badge>
                )}
                {dateTo && (
                  <Badge variant="secondary" className="text-[10px] gap-1 px-2">
                    Bitiş: {fmtDate(dateTo)}
                    <button onClick={() => setDateTo("")}><X className="w-2.5 h-2.5" /></button>
                  </Badge>
                )}
                <span className="text-[10px] text-muted-foreground ml-auto">
                  {filtered.length} / {mockGeçmisRaporlar.length} kayıt gösteriliyor
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Table */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35, delay: 0.15 }}>
        <Card className="glass-card border-border">
          <CardContent className="p-0">
            {filtered.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 gap-3">
                <div className="w-12 h-12 rounded-xl bg-muted/50 border border-border/40 flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-muted-foreground/50" />
                </div>
                <p className="text-sm text-muted-foreground">Filtre kriterlerine uyan kayıt bulunamadı</p>
                <Button variant="ghost" size="sm" onClick={clearFilters} className="text-xs">
                  Filtreleri temizle
                </Button>
              </div>
            ) : (
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border bg-muted/30">
                    <th className="text-left text-muted-foreground font-medium px-4 py-3">Tarih</th>
                    <th className="text-left text-muted-foreground font-medium px-4 py-3">Tesis</th>
                    <th className="text-right text-muted-foreground font-medium px-4 py-3">Emisyon</th>
                    <th className="text-right text-muted-foreground font-medium px-4 py-3">CBAM Vergisi</th>
                    <th className="text-center text-muted-foreground font-medium px-4 py-3">Uyumluluk</th>
                    <th className="text-center text-muted-foreground font-medium px-4 py-3">Güven</th>
                    <th className="text-right text-muted-foreground font-medium px-4 py-3">İşlemler</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((report) => (
                    <ReportRow
                      key={report.id}
                      report={report}
                      onPdf={() => handlePdf(report)}
                    />
                  ))}
                </tbody>
              </table>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
