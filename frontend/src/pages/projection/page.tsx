import { useState, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import {
  ComposedChart,
  Area,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import type { TooltipProps } from "recharts";
import {
  TrendingDown,
  Euro,
  Leaf,
  Target,
  Sliders,
  Info,
  ChevronDown,
  ChevronUp,
  Zap,
  Factory,
  CalendarClock,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
} from "lucide-react";
import { cn } from "@/lib/utils.ts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { Slider } from "@/components/ui/slider.tsx";
import { Label } from "@/components/ui/label.tsx";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select.tsx";
import { mockKpiData, mockMaliEtki, mockCbamTimeline } from "@/lib/mock-data.ts";

// ─── Formatters ────────────────────────────────────────────────────────────────
const fmt = (n: number) => new Intl.NumberFormat("tr-TR").format(Math.round(n));
const fmtEur = (n: number) =>
  new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(n);

// ─── Constants ─────────────────────────────────────────────────────────────────
const BASE_EMISSION = mockKpiData.totalEmission;
const BASE_PRODUCTION = mockMaliEtki.uretimMiktari;
const BASE_INTENSITY = mockKpiData.emissionIntensity;

const CBAM_PHASE = mockCbamTimeline;
const CARBON_PRICE_SCENARIOS: Record<string, number> = {
  dusuk: 55,
  orta: 85,
  yuksek: 120,
  asgari: 40,
};

// ─── Projection Engine ──────────────────────────────────────────────────────────
interface ProjectionRow {
  yil: number;
  bazEmisyon: number;
  optimizeEmisyon: number;
  hedefEmisyon: number;
  cbamFaz: number;
  bazVergi: number;
  optimizeVergi: number;
  tasarruf: number;
  kumulatifTasarruf: number;
  uretim: number;
}

function buildProjection(params: {
  yillikAzaltma: number;
  uretimDegisim: number;
  karbonFiyat: number;
  onlemBaslangic: number;
  hedefYuzde: number;
}): ProjectionRow[] {
  const { yillikAzaltma, uretimDegisim, karbonFiyat, onlemBaslangic, hedefYuzde } = params;
  let kumulatif = 0;
  const rows: ProjectionRow[] = [];

  for (const { yil, faz } of CBAM_PHASE) {
    const yilOncesi = yil - 2026;
    const uretimFak = Math.pow(1 + uretimDegisim / 100, yilOncesi);
    const uretim = BASE_PRODUCTION * uretimFak;

    const bazEmisyon = BASE_INTENSITY * uretim;

    let optimizeEmisyon = bazEmisyon;
    if (yil >= onlemBaslangic) {
      const yilSonra = yil - onlemBaslangic;
      const azaltmaFak = Math.pow(1 - yillikAzaltma / 100, yilSonra + 1);
      optimizeEmisyon = bazEmisyon * azaltmaFak;
    }

    const hedefEmisyon = bazEmisyon * (1 - hedefYuzde / 100);

    const bazVergi = (bazEmisyon * karbonFiyat * faz) / 100;
    const optimizeVergi = (optimizeEmisyon * karbonFiyat * faz) / 100;
    const tasarruf = bazVergi - optimizeVergi;
    kumulatif += tasarruf;

    rows.push({
      yil,
      bazEmisyon: Math.round(bazEmisyon),
      optimizeEmisyon: Math.round(optimizeEmisyon),
      hedefEmisyon: Math.round(hedefEmisyon),
      cbamFaz: faz,
      bazVergi: Math.round(bazVergi),
      optimizeVergi: Math.round(optimizeVergi),
      tasarruf: Math.round(tasarruf),
      kumulatifTasarruf: Math.round(kumulatif),
      uretim: Math.round(uretim),
    });
  }
  return rows;
}

// ─── Custom Tooltip ─────────────────────────────────────────────────────────────
function EmissionTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-card/95 backdrop-blur border border-white/10 rounded-xl p-3 shadow-xl text-xs space-y-1.5 min-w-[220px]">
      <p className="font-bold text-sm text-foreground">{label}</p>
      {payload.map((entry) => (
        <div key={entry.dataKey} className="flex items-center justify-between gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-muted-foreground">{entry.name}</span>
          </span>
          <span className="font-semibold text-foreground">{fmt(entry.value as number)} tCO₂e</span>
        </div>
      ))}
    </div>
  );
}

function TaxTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-card/95 backdrop-blur border border-white/10 rounded-xl p-3 shadow-xl text-xs space-y-1.5 min-w-[220px]">
      <p className="font-bold text-sm text-foreground">{label}</p>
      {payload.map((entry) => (
        <div key={entry.dataKey} className="flex items-center justify-between gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-muted-foreground">{entry.name}</span>
          </span>
          <span className="font-semibold text-foreground">{fmtEur(entry.value as number)}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Slider Row ─────────────────────────────────────────────────────────────────
function SliderRow({
  label,
  value,
  min,
  max,
  step,
  unit,
  onChange,
  color,
  description,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit: string;
  onChange: (v: number) => void;
  color: string;
  description?: string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label className="text-sm font-medium text-foreground">{label}</Label>
        <span className={cn("text-sm font-bold tabular-nums px-2 py-0.5 rounded-md", color)}>
          {value > 0 && unit !== "yıl" ? "+" : ""}
          {value}
          {unit}
        </span>
      </div>
      {description && <p className="text-xs text-muted-foreground">{description}</p>}
      <Slider
        min={min}
        max={max}
        step={step}
        value={[value]}
        onValueChange={([v]) => onChange(v)}
        className="w-full"
      />
    </div>
  );
}

// ─── KPI Card ───────────────────────────────────────────────────────────────────
function KpiCard({
  icon: Icon,
  title,
  value,
  sub,
  color,
  delay,
}: {
  icon: React.ElementType;
  title: string;
  value: string;
  sub: string;
  color: string;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
    >
      <Card className="bg-card/60 backdrop-blur border-white/10 hover:border-white/20 transition-colors">
        <CardContent className="p-4 flex items-center gap-3">
          <div className={cn("p-2.5 rounded-xl", color)}>
            <Icon className="w-5 h-5 text-white" />
          </div>
          <div className="min-w-0">
            <p className="text-xs text-muted-foreground truncate">{title}</p>
            <p className="text-lg font-bold text-foreground leading-tight">{value}</p>
            <p className="text-xs text-muted-foreground">{sub}</p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// ─── Main Page ──────────────────────────────────────────────────────────────────
export default function ProjectionPage() {
  const { t } = useTranslation();
  const [yillikAzaltma, setYillikAzaltma] = useState(5);
  const [uretimDegisim, setUretimDegisim] = useState(2);
  const [karbonSenaryosu, setKarbonSenaryosu] = useState("orta");
  const [onlemBaslangic, setOnlemBaslangic] = useState(2027);
  const [hedefYuzde, setHedefYuzde] = useState(40);
  const [controlsOpen, setControlsOpen] = useState(true);
  const [activeChart, setActiveChart] = useState<"emisyon" | "vergi">("emisyon");

  const karbonFiyat = CARBON_PRICE_SCENARIOS[karbonSenaryosu];

  const data = useMemo(
    () =>
      buildProjection({
        yillikAzaltma,
        uretimDegisim,
        karbonFiyat,
        onlemBaslangic,
        hedefYuzde,
      }),
    [yillikAzaltma, uretimDegisim, karbonFiyat, onlemBaslangic, hedefYuzde]
  );

  const totalBazVergi = data.reduce((s, r) => s + r.bazVergi, 0);
  const totalOptVergi = data.reduce((s, r) => s + r.optimizeVergi, 0);
  const totalTasarruf = totalBazVergi - totalOptVergi;
  const finalRow = data[data.length - 1];
  const firstSavingYear = data.find((r) => r.tasarruf > 50_000)?.yil ?? null;
  const avgAzaltma =
    data.length > 0
      ? ((data[0].bazEmisyon - finalRow.optimizeEmisyon) / data[0].bazEmisyon) * 100
      : 0;

  const estimatedCapex = yillikAzaltma * BASE_EMISSION * 0.01 * 500;
  const breakEvenRow = data.find((r) => r.kumulatifTasarruf >= estimatedCapex);

  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
      >
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Target className="w-6 h-6 text-primary" />
            Emisyon Projeksiyon Aracı
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {t("projection.subtitle")}
          </p>
        </div>
        <Badge
          variant="outline"
          className="self-start sm:self-auto border-amber-500/40 text-amber-400 bg-amber-500/10 px-3 py-1"
        >
          <AlertCircle className="w-3.5 h-3.5 mr-1.5" />
          Baz Yıl: 2025 Q1 Verisi
        </Badge>
      </motion.div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <KpiCard
            icon={Euro}
            title={t("projection.totalTaxLiability")}
            value={fmtEur(totalBazVergi)}
            sub={t("projection.baseCumulative")}
            color="bg-red-500/80"
            delay={0.05}
          />
          <KpiCard
            icon={TrendingDown}
            title="Optimize Senaryo Vergisi"
            value={fmtEur(totalOptVergi)}
            sub={t("projection.baseCumulative")}
            color="bg-emerald-500/80"
            delay={0.1}
          />
          <KpiCard
            icon={Leaf}
            title={t("projection.totalSavings")}
            value={fmtEur(totalTasarruf)}
            sub={`Kümülatif ${fmt(avgAzaltma)}% ${t("projection.emissionReduction")}`}
            color="bg-primary/80"
            delay={0.15}
          />
          <KpiCard
            icon={CalendarClock}
            title={t("projection.investmentReturn")}
            value={breakEvenRow ? `${breakEvenRow.yil}` : "2034+"}
            sub={breakEvenRow ? t("projection.estimatedBreakeven") : t("projection.longTermInvestment")}
            color="bg-violet-500/80"
            delay={0.2}
          />
        </div>

      {/* Controls Panel */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
        <Card className="bg-card/60 backdrop-blur border-white/10">
          <CardHeader
            className="cursor-pointer select-none"
            onClick={() => setControlsOpen((o) => !o)}
          >
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <Sliders className="w-4 h-4 text-primary" />
                {t("projection.scenarioParameters")}
              </CardTitle>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground hidden sm:block">
                  Karbon Fiyatı: €{karbonFiyat}/tCO₂
                </span>
                {controlsOpen ? (
                  <ChevronUp className="w-4 h-4 text-muted-foreground" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                )}
              </div>
            </div>
          </CardHeader>
          {controlsOpen && (
            <CardContent className="pt-0">
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                <SliderRow
                  label={t("projection.annualReductionRate")}
                  value={yillikAzaltma}
                  min={0}
                  max={20}
                  step={0.5}
                  unit="%"
                  onChange={setYillikAzaltma}
                  color="bg-emerald-500/20 text-emerald-400"
                  description={t("projection.reductionDescription")}
                />
                <SliderRow
                  label={t("projection.productionVolumeChange")}
                  value={uretimDegisim}
                  min={-5}
                  max={10}
                  step={0.5}
                  unit="%"
                  onChange={setUretimDegisim}
                  color="bg-blue-500/20 text-blue-400"
                  description={t("projection.productionDescription")}
                />
                <SliderRow
                  label={t("projection.targetReduction")}
                  value={hedefYuzde}
                  min={10}
                  max={80}
                  step={5}
                  unit="%"
                  onChange={setHedefYuzde}
                  color="bg-violet-500/20 text-violet-400"
                  description={t("projection.targetDescription")}
                />

                {/* Carbon price scenario */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-foreground">
                    Karbon Fiyat Senaryosu
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    EU ETS referanslı tahmini karbon fiyatı (€/tCO₂)
                  </p>
                  <Select value={karbonSenaryosu} onValueChange={setKarbonSenaryosu}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="asgari">Asgari — €40/tCO₂ (düşük tahmin)</SelectItem>
                      <SelectItem value="dusuk">Düşük — €55/tCO₂</SelectItem>
                      <SelectItem value="orta">Orta — €85/tCO₂ (baz)</SelectItem>
                      <SelectItem value="yuksek">Yüksek — €120/tCO₂ (stres testi)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Measure start year */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-foreground">
                    {t("projection.measureStartYear")}
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    Azaltım önlemlerinin uygulamaya girdiği yıl
                  </p>
                  <Select
                    value={String(onlemBaslangic)}
                    onValueChange={(v) => setOnlemBaslangic(Number(v))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {[2026, 2027, 2028, 2029, 2030].map((y) => (
                        <SelectItem key={y} value={String(y)}>
                          {y}
                          {y === 2026 ? ` ${t("projection.startImmediately")}` : y === 2030 ? ` ${t("projection.late")}` : ""}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Info card */}
                <div className="flex items-start gap-2 bg-primary/10 border border-primary/20 rounded-xl p-3">
                  <Info className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p className="text-foreground font-medium">Hesaplama Metodolojisi</p>
                    <p>
                      Emisyon = Yoğunluk × Üretim × (1−azaltma)^yıl
                    </p>
                    <p>
                      CBAM Vergisi = Emisyon × Karbon Fiyatı × Faz Faktörü / 100
                    </p>
                    <p className="text-amber-400">
                      * Projeksiyon tahminidir, resmi CBAM hesabı değildir.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          )}
        </Card>
      </motion.div>

      {/* Chart Toggle */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setActiveChart("emisyon")}
          className={cn(
            "px-4 py-1.5 rounded-full text-sm font-medium transition-all",
            activeChart === "emisyon"
              ? "bg-primary text-primary-foreground shadow"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Leaf className="w-3.5 h-3.5 inline mr-1.5" />
          {t("projection.title")}
        </button>
        <button
          onClick={() => setActiveChart("vergi")}
          className={cn(
            "px-4 py-1.5 rounded-full text-sm font-medium transition-all",
            activeChart === "vergi"
              ? "bg-primary text-primary-foreground shadow"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Euro className="w-3.5 h-3.5 inline mr-1.5" />
          CBAM Vergi Projeksiyonu
        </button>
      </div>

      {/* Emission Chart */}
      {activeChart === "emisyon" && (
        <motion.div
          key="emisyon"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.35 }}
        >
          <Card className="bg-card/60 backdrop-blur border-white/10">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Leaf className="w-4 h-4 text-emerald-400" />
                Emisyon Projeksiyonu (tCO₂e)
                <Badge className="ml-auto bg-white/5 text-muted-foreground border-white/10 text-xs font-normal">
                  CBAM Faz Faktörü ile
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={360}>
                <ComposedChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="bazGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#EF4444" stopOpacity={0.25} />
                      <stop offset="100%" stopColor="#EF4444" stopOpacity={0.02} />
                    </linearGradient>
                    <linearGradient id="optGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#10B981" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#10B981" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    dataKey="yil"
                    tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}K`}
                    tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    width={50}
                  />
                  <Tooltip content={<EmissionTooltip />} />
                  <Legend
                    wrapperStyle={{ fontSize: 12, color: "hsl(var(--muted-foreground))" }}
                  />
                  <ReferenceLine
                    x={onlemBaslangic}
                    stroke="#F59E0B"
                    strokeDasharray="5 4"
                    label={{
                      value: `Önlem Başlangıcı`,
                      fill: "#F59E0B",
                      fontSize: 11,
                      position: "insideTopRight",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="bazEmisyon"
                    name="Baz Senaryo"
                    fill="url(#bazGrad)"
                    stroke="#EF4444"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Area
                    type="monotone"
                    dataKey="optimizeEmisyon"
                    name="Optimize Senaryo"
                    fill="url(#optGrad)"
                    stroke="#10B981"
                    strokeWidth={2.5}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="hedefEmisyon"
                    name="Hedef Emisyon"
                    stroke="#8B5CF6"
                    strokeWidth={2}
                    strokeDasharray="6 3"
                    dot={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Tax Chart */}
      {activeChart === "vergi" && (
        <motion.div
          key="vergi"
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.35 }}
        >
          <Card className="bg-card/60 backdrop-blur border-white/10">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Euro className="w-4 h-4 text-amber-400" />
                CBAM Vergi Projeksiyonu (€)
                <Badge className="ml-auto bg-amber-500/10 text-amber-400 border-amber-500/30 text-xs font-normal">
                  Karbon Fiyatı: €{karbonFiyat}/tCO₂
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={360}>
                <ComposedChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    dataKey="yil"
                    tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tickFormatter={(v: number) =>
                      v >= 1_000_000 ? `€${(v / 1_000_000).toFixed(1)}M` : `€${(v / 1000).toFixed(0)}K`
                    }
                    tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    width={65}
                  />
                  <Tooltip content={<TaxTooltip />} />
                  <Legend
                    wrapperStyle={{ fontSize: 12, color: "hsl(var(--muted-foreground))" }}
                  />
                  <ReferenceLine
                    x={onlemBaslangic}
                    stroke="#F59E0B"
                    strokeDasharray="5 4"
                    label={{
                      value: `Önlem Başlangıcı`,
                      fill: "#F59E0B",
                      fontSize: 11,
                      position: "insideTopRight",
                    }}
                  />
                  <Bar
                    dataKey="bazVergi"
                    name="Baz Senaryo Vergisi"
                    fill="#EF4444"
                    fillOpacity={0.7}
                    radius={[3, 3, 0, 0]}
                  />
                  <Bar
                    dataKey="optimizeVergi"
                    name="Optimize Senaryo Vergisi"
                    fill="#10B981"
                    fillOpacity={0.8}
                    radius={[3, 3, 0, 0]}
                  />
                  <Line
                    type="monotone"
                    dataKey="kumulatifTasarruf"
                    name={t("projection.cumulativeSavings")}
                    stroke="#8B5CF6"
                    strokeWidth={2.5}
                    dot={false}
                    yAxisId={0}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Year-by-Year Table */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <Card className="bg-card/60 backdrop-blur border-white/10">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Zap className="w-4 h-4 text-primary" />
              Yıllık Projeksiyon Tablosu
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    {[
                      t("projection.year"),
                      t("projection.cbamPhase"),
                      t("projection.baseEmission"),
                      t("projection.optimizedEmission"),
                      t("projection.reduction"),
                      t("projection.baseTax"),
                      t("projection.optimizedTax"),
                      t("projection.annualSavings"),
                      t("projection.cumulativeSavings"),
                    ].map((h) => (
                      <th
                        key={h}
                        className="text-xs text-muted-foreground font-medium text-left px-4 py-3"
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.map((row, i) => {
                    const azaltimPct =
                      row.bazEmisyon > 0
                        ? ((row.bazEmisyon - row.optimizeEmisyon) / row.bazEmisyon) * 100
                        : 0;
                    const isOnlemYil = row.yil === onlemBaslangic;
                    const isBreakEven = breakEvenRow?.yil === row.yil;

                    return (
                      <motion.tr
                        key={row.yil}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.02 * i }}
                        className={cn(
                          "border-b border-white/5 hover:bg-white/5 transition-colors",
                          isOnlemYil && "bg-amber-500/5",
                          isBreakEven && "bg-emerald-500/5"
                        )}
                      >
                        <td className="px-4 py-2.5 font-bold text-foreground">
                          {row.yil}
                          {isOnlemYil && (
                            <Badge className="ml-1.5 text-[10px] bg-amber-500/20 text-amber-400 border-amber-500/30">
                              Başlangıç
                            </Badge>
                          )}
                          {isBreakEven && (
                            <Badge className="ml-1.5 text-[10px] bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                              <CheckCircle2 className="w-2.5 h-2.5 mr-0.5" />
                              Başabaş
                            </Badge>
                          )}
                        </td>
                        <td className="px-4 py-2.5">
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 rounded-full bg-white/10 overflow-hidden">
                              <div
                                className="h-full bg-primary rounded-full"
                                style={{ width: `${row.cbamFaz}%` }}
                              />
                            </div>
                            <span className="text-muted-foreground text-xs">{row.cbamFaz}%</span>
                          </div>
                        </td>
                        <td className="px-4 py-2.5 text-red-400 font-mono text-xs">
                          {fmt(row.bazEmisyon)}
                        </td>
                        <td className="px-4 py-2.5 text-emerald-400 font-mono text-xs">
                          {fmt(row.optimizeEmisyon)}
                        </td>
                        <td className="px-4 py-2.5">
                          <span
                            className={cn(
                              "text-xs font-semibold",
                              azaltimPct > 0 ? "text-emerald-400" : "text-muted-foreground"
                            )}
                          >
                            {azaltimPct > 0 ? "-" : ""}
                            {azaltimPct.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-red-400 font-mono text-xs">
                          {fmtEur(row.bazVergi)}
                        </td>
                        <td className="px-4 py-2.5 text-emerald-400 font-mono text-xs">
                          {fmtEur(row.optimizeVergi)}
                        </td>
                        <td className="px-4 py-2.5 text-violet-400 font-mono text-xs font-semibold">
                          +{fmtEur(row.tasarruf)}
                        </td>
                        <td className="px-4 py-2.5 text-primary font-mono text-xs font-bold">
                          {fmtEur(row.kumulatifTasarruf)}
                        </td>
                      </motion.tr>
                    );
                  })}
                </tbody>
                <tfoot>
                  <tr className="border-t border-white/20 bg-white/5">
                    <td colSpan={5} className="px-4 py-3 text-xs font-bold text-foreground">
                      TOPLAM (2026–2034)
                    </td>
                    <td className="px-4 py-3 text-red-400 font-mono text-xs font-bold">
                      {fmtEur(totalBazVergi)}
                    </td>
                    <td className="px-4 py-3 text-emerald-400 font-mono text-xs font-bold">
                      {fmtEur(totalOptVergi)}
                    </td>
                    <td colSpan={2} className="px-4 py-3 text-primary font-mono text-xs font-bold">
                      {fmtEur(totalTasarruf)} tasarruf
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Action Card */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <Card className="bg-gradient-to-r from-primary/20 via-primary/10 to-transparent border-primary/30">
          <CardContent className="p-5 flex flex-col sm:flex-row items-start sm:items-center gap-4 justify-between">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-primary/20">
                <Factory className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground">
                  {firstSavingYear
                    ? `${firstSavingYear} yılında yıllık €50.000+ tasarruf başlıyor`
                    : t("projection.adjustParameters")}
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {breakEvenRow
                    ? `Tahmini yatırım geri dönüşü ${breakEvenRow.yil} yılında gerçekleşiyor (capex: ${fmtEur(estimatedCapex)})`
                    : t("projection.moveStartEarlier")}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Badge className="bg-primary/20 text-primary border-primary/30">
                <ArrowRight className="w-3 h-3 mr-1" />
                Strateji Sayfasına Git
              </Badge>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
