import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  ReferenceLine,
} from "recharts";
import {
  BrainCircuit,
  Euro,
  Leaf,
  Zap,
  TrendingDown,
  Clock,
  ChevronDown,
  ChevronRight,
  CheckSquare,
  Square,
  AlertTriangle,
  Sparkles,
  Calculator,
  BarChart3,
} from "lucide-react";
import { cn } from "@/lib/utils.ts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { Button } from "@/components/ui/button.tsx";
import {
  mockKpiData,
  mockScenarios,
  mockAiOzet,
  mockCbamTimeline,
  mockMaliEtki,
} from "@/lib/mock-data.ts";

// ─── Formatters ────────────────────────────────────────────────────────────────
const fmt = (n: number) => new Intl.NumberFormat("tr-TR").format(Math.round(n));
const fmtEur = (n: number) =>
  new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(n);

// ─── Risk Gauge ─────────────────────────────────────────────────────────────────
function RiskGauge({ score }: { score: number }) {
  const clamp = Math.min(100, Math.max(0, score));
  const R = 70;
  const cx = 90;
  const cy = 85;

  const polarToXY = (angle: number, r: number) => ({
    x: cx + r * Math.cos(angle),
    y: cy - r * Math.sin(angle),
  });

  const arcPath = (inner: number, outer: number, start: number, end: number) => {
    const s1 = polarToXY(start, outer);
    const e1 = polarToXY(end, outer);
    const s2 = polarToXY(end, inner);
    const e2 = polarToXY(start, inner);
    return `M ${s1.x} ${s1.y} A ${outer} ${outer} 0 0 1 ${e1.x} ${e1.y} L ${s2.x} ${s2.y} A ${inner} ${inner} 0 1 0 ${e2.x} ${e2.y} Z`;
  };

  const segments = [
    { from: 0,  to: 33,  color: "#22C55E" },
    { from: 33, to: 66,  color: "#F59E0B" },
    { from: 66, to: 100, color: "#EF4444" },
  ];

  const scoreAngle = Math.PI - (clamp / 100) * Math.PI;
  const needle = polarToXY(scoreAngle, R - 8);

  const riskLabel = clamp >= 66 ? "YÜKSEK RİSK" : clamp >= 33 ? "ORTA RİSK" : "DÜŞÜK RİSK";
  const riskColor = clamp >= 66 ? "text-red-400" : clamp >= 33 ? "text-yellow-400" : "text-green-400";
  const badgeBg = clamp >= 66
    ? "bg-red-500/20 text-red-400 border-red-500/30"
    : clamp >= 33
    ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
    : "bg-green-500/20 text-green-400 border-green-500/30";

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 180 100" className="w-full max-w-[220px]">
        {segments.map((seg) => {
          const a1 = Math.PI - (seg.from / 100) * Math.PI;
          const a2 = Math.PI - (seg.to / 100) * Math.PI;
          return (
            <path
              key={seg.from}
              d={arcPath(50, R, a1, a2)}
              fill={seg.color}
              opacity={0.2}
            />
          );
        })}
        {clamp > 0 && (
          <path
            d={arcPath(50, R, Math.PI, scoreAngle)}
            fill={clamp >= 66 ? "#EF4444" : clamp >= 33 ? "#F59E0B" : "#22C55E"}
            opacity={0.75}
          />
        )}
        <circle cx={needle.x} cy={needle.y} r={4} fill="white" opacity={0.9} />
        <line x1={cx} y1={cy} x2={needle.x} y2={needle.y} stroke="white" strokeWidth={1.5} opacity={0.7} />
        <circle cx={cx} cy={cy} r={4} fill="white" opacity={0.9} />
        <text x={cx} y={cy - 14} textAnchor="middle" fill="white" fontSize={22} fontWeight="bold">
          {clamp}
        </text>
        <text x={cx} y={cy - 1} textAnchor="middle" fill="oklch(0.55 0.02 240)" fontSize={9}>
          / 100
        </text>
        <text x={14} y={95} fill="oklch(0.55 0.02 240)" fontSize={8}>Düşük</text>
        <text x={155} y={95} fill="oklch(0.55 0.02 240)" fontSize={8} textAnchor="end">Yüksek</text>
      </svg>
      <Badge className={cn("mt-1 text-xs px-3 py-1", badgeBg)}>
        {riskLabel}
      </Badge>
      <p className={cn("text-2xl font-bold mt-2 tabular-nums", riskColor)}>{clamp}</p>
      <p className="text-xs text-muted-foreground">CBAM Uyumluluk Risk Skoru</p>
    </div>
  );
}

// ─── Scenario Types ─────────────────────────────────────────────────────────────
type Difficulty = "düşük" | "orta" | "yüksek";
type Priority   = "düşük" | "orta" | "yüksek";

const difficultyConfig: Record<Difficulty, { label: string; class: string }> = {
  düşük:   { label: "Düşük",   class: "bg-green-500/15 text-green-400 border-green-500/25"  },
  orta:    { label: "Orta",    class: "bg-yellow-500/15 text-yellow-400 border-yellow-500/25" },
  yüksek:  { label: "Yüksek",  class: "bg-red-500/15 text-red-400 border-red-500/25"        },
};
const priorityConfig: Record<Priority, { label: string; class: string }> = {
  yüksek: { label: "Yüksek",  class: "bg-primary/15 text-primary border-primary/25"          },
  orta:   { label: "Orta",    class: "bg-blue-500/15 text-blue-400 border-blue-500/25"        },
  düşük:  { label: "Düşük",   class: "bg-muted text-muted-foreground border-border"           },
};

// ─── Simulation Panel ────────────────────────────────────────────────────────────
function SimulationPanel({
  selected,
  totalEmission,
  totalTax,
}: {
  selected: typeof mockScenarios;
  totalEmission: number;
  totalTax: number;
}) {
  const savedEmission = selected.reduce((s, sc) => s + sc.tasarrufEmisyon, 0);
  const savedMoney    = selected.reduce((s, sc) => s + sc.maliKazanc, 0);
  const newEmission   = Math.max(0, totalEmission - savedEmission);
  const newTax        = Math.max(0, totalTax - savedMoney);
  const reduction     = totalEmission > 0 ? ((savedEmission / totalEmission) * 100) : 0;

  const barData = [
    { name: "Mevcut", emisyon: totalEmission, fill: "#EF4444" },
    { name: "Senaryo Sonrası", emisyon: newEmission, fill: "#22C55E" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="glass-card border-primary/25 bg-primary/5">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Calculator className="w-4 h-4 text-primary" />
            <CardTitle className="text-sm font-semibold text-foreground">
              Anlık Simülasyon — {selected.length} senaryo seçildi
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-3 mb-4">
            {[
              { label: "Emisyon Tasarrufu", value: `${fmt(savedEmission)} tCO₂e`, color: "text-green-400", icon: <Leaf className="w-3.5 h-3.5" /> },
              { label: "Mali Kazanç", value: fmtEur(savedMoney), color: "text-green-400", icon: <Euro className="w-3.5 h-3.5" /> },
              { label: "Yeni Emisyon", value: `${fmt(newEmission)} tCO₂e`, color: "text-foreground", icon: <BarChart3 className="w-3.5 h-3.5" /> },
              { label: "Yeni Vergi", value: fmtEur(newTax), color: "text-foreground", icon: <Euro className="w-3.5 h-3.5" /> },
            ].map((item) => (
              <div key={item.label} className="p-3 rounded-lg bg-muted/30 border border-border/50 text-center">
                <div className={cn("flex items-center justify-center gap-1 mb-1", item.color)}>{item.icon}</div>
                <p className={cn("text-sm font-bold tabular-nums", item.color)}>{item.value}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">{item.label}</p>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-4">
            <ResponsiveContainer width="50%" height={90}>
              <BarChart data={barData} barSize={36} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.22 0.03 255)" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 9, fill: "oklch(0.55 0.02 240)" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 9, fill: "oklch(0.55 0.02 240)" }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  content={({ active, payload }) =>
                    active && payload?.[0] ? (
                      <div className="bg-card border border-border rounded-lg p-2 text-xs shadow-xl">
                        <p className="text-foreground font-semibold">{fmt(payload[0].value as number)} tCO₂e</p>
                      </div>
                    ) : null
                  }
                />
                <Bar dataKey="emisyon" radius={[4, 4, 0, 0]}>
                  {barData.map((d) => <Cell key={d.name} fill={d.fill} opacity={0.8} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-2">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-muted-foreground">Emisyon Azalması</span>
                  <span className="text-green-400 font-bold">{reduction.toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-muted/50 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-green-500 rounded-full"
                    initial={{ width: "0%" }}
                    animate={{ width: `${Math.min(100, reduction)}%` }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-muted-foreground">Vergi Tasarrufu</span>
                  <span className="text-green-400 font-bold">
                    {totalTax > 0 ? ((savedMoney / totalTax) * 100).toFixed(1) : 0}%
                  </span>
                </div>
                <div className="h-2 bg-muted/50 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-primary rounded-full"
                    initial={{ width: "0%" }}
                    animate={{ width: `${Math.min(100, totalTax > 0 ? (savedMoney / totalTax) * 100 : 0)}%` }}
                    transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
                  />
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// ─── Scenario Table ──────────────────────────────────────────────────────────────
function ScenarioTable() {
  const [scenarios, setScenarios] = useState(mockScenarios);

  const toggleScenario = (id: number) => {
    setScenarios((prev) => prev.map((s) => (s.id === id ? { ...s, secili: !s.secili } : s)));
  };

  const selected = useMemo(() => scenarios.filter((s) => s.secili), [scenarios]);

  return (
    <div className="space-y-4">
      <Card className="glass-card border-border">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Zap className="w-4 h-4 text-primary" />
                Optimizasyon Senaryoları
              </CardTitle>
              <p className="text-xs text-muted-foreground mt-0.5">
                Senaryoları seçin → anlık simülasyon hesaplanır
              </p>
            </div>
            {selected.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="text-xs text-muted-foreground h-7"
                onClick={() => setScenarios((prev) => prev.map((s) => ({ ...s, secili: false })))}
              >
                Temizle
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="w-10 px-4 py-2.5" />
                <th className="text-left text-muted-foreground font-medium px-4 py-2.5">Senaryo</th>
                <th className="text-right text-muted-foreground font-medium px-4 py-2.5">Tasarruf (tCO₂e)</th>
                <th className="text-right text-muted-foreground font-medium px-4 py-2.5">Mali Kazanç</th>
                <th className="text-center text-muted-foreground font-medium px-4 py-2.5">Süre</th>
                <th className="text-center text-muted-foreground font-medium px-4 py-2.5">Zorluk</th>
                <th className="text-center text-muted-foreground font-medium px-4 py-2.5">Öncelik</th>
              </tr>
            </thead>
            <tbody>
              {scenarios.map((sc) => (
                <tr
                  key={sc.id}
                  onClick={() => toggleScenario(sc.id)}
                  className={cn(
                    "border-b border-border/50 last:border-0 cursor-pointer transition-all duration-200",
                    sc.secili
                      ? "bg-primary/8 hover:bg-primary/12"
                      : "hover:bg-accent/40"
                  )}
                >
                  <td className="px-4 py-3 text-center">
                    {sc.secili ? (
                      <CheckSquare className="w-4 h-4 text-primary mx-auto" />
                    ) : (
                      <Square className="w-4 h-4 text-muted-foreground/50 mx-auto" />
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <p className={cn("font-medium", sc.secili ? "text-primary" : "text-foreground")}>
                      {sc.baslik}
                    </p>
                    <p className="text-[10px] text-muted-foreground mt-0.5">{sc.aciklama}</p>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-green-400 font-semibold tabular-nums">
                      −{fmt(sc.tasarrufEmisyon)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-green-400 font-semibold tabular-nums">
                      {fmtEur(sc.maliKazanc)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="flex items-center justify-center gap-1 text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      {sc.sure}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Badge className={cn("text-[10px] px-1.5", difficultyConfig[sc.zorluk as Difficulty].class)}>
                      {difficultyConfig[sc.zorluk as Difficulty].label}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Badge className={cn("text-[10px] px-1.5", priorityConfig[sc.oncelik as Priority].class)}>
                      {priorityConfig[sc.oncelik as Priority].label}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <AnimatePresence>
        {selected.length > 0 && (
          <SimulationPanel
            selected={selected}
            totalEmission={mockKpiData.totalEmission}
            totalTax={mockMaliEtki.brutVergi}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

// ─── CBAM Timeline Chart ─────────────────────────────────────────────────────────
function CbamTimelineChart() {
  const [hovered, setHovered] = useState<number | null>(null);

  const areaData = mockCbamTimeline.map((d) => ({
    yil: String(d.yil),
    faz: d.faz,
    aktif: d.aktif ?? false,
  }));

  return (
    <Card className="glass-card border-border">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
              <TrendingDown className="w-4 h-4 text-primary" />
              CBAM Phase-in Takvimi
            </CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">
              2026–2034 · %2,5'ten %100'e kademeli uygulama
            </p>
          </div>
          <Badge className="bg-primary/15 text-primary border-primary/25 text-[10px] px-2">
            Şu an: 2026 · %2,5
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={160}>
          <AreaChart data={areaData} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="cbamGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#EF4444" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#EF4444" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.22 0.03 255)" vertical={false} />
            <XAxis
              dataKey="yil"
              tick={{ fontSize: 10, fill: "oklch(0.55 0.02 240)" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "oklch(0.55 0.02 240)" }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => `%${v}`}
              domain={[0, 100]}
            />
            <Tooltip
              content={({ active, payload, label }) =>
                active && payload?.[0] ? (
                  <div className="bg-card border border-border rounded-lg p-2 shadow-xl text-xs">
                    <p className="text-muted-foreground">{label}</p>
                    <p className="text-foreground font-bold">CBAM Faz: %{payload[0].value}</p>
                    {label === "2026" && (
                      <p className="text-primary text-[10px] mt-0.5">← Şu anki dönem</p>
                    )}
                  </div>
                ) : null
              }
            />
            <ReferenceLine x="2026" stroke="oklch(0.75 0.18 145)" strokeWidth={2} strokeDasharray="4 2" />
            <Area
              type="monotone"
              dataKey="faz"
              stroke="#EF4444"
              strokeWidth={2.5}
              fill="url(#cbamGrad)"
              dot={(props: any) => {
                const { cx, cy, index } = props;
                const d = areaData[index];
                return (
                  <circle
                    key={index}
                    cx={cx}
                    cy={cy}
                    r={d.aktif ? 6 : hovered === index ? 5 : 3.5}
                    fill={d.aktif ? "oklch(0.75 0.18 145)" : "#EF4444"}
                    stroke={d.aktif ? "oklch(0.75 0.18 145 / 0.4)" : "transparent"}
                    strokeWidth={d.aktif ? 6 : 0}
                    style={{ cursor: "pointer", transition: "r 0.2s" }}
                    onMouseEnter={() => setHovered(index)}
                    onMouseLeave={() => setHovered(null)}
                  />
                );
              }}
            />
          </AreaChart>
        </ResponsiveContainer>

        <div className="grid grid-cols-9 gap-1 mt-4">
          {mockCbamTimeline.map((item) => (
            <div
              key={item.yil}
              className={cn(
                "rounded-lg p-2 text-center border transition-all",
                item.aktif
                  ? "bg-primary/15 border-primary/40 shadow-[0_0_12px_oklch(0.75_0.18_145/0.2)]"
                  : item.faz >= 50
                  ? "bg-red-500/8 border-red-500/20"
                  : "bg-muted/30 border-border/40"
              )}
            >
              <p className={cn("text-[11px] font-bold tabular-nums",
                item.aktif ? "text-primary" : item.faz >= 50 ? "text-red-400" : "text-muted-foreground"
              )}>
                %{item.faz}
              </p>
              <p className={cn("text-[9px] tabular-nums mt-0.5",
                item.aktif ? "text-foreground font-medium" : "text-muted-foreground/60"
              )}>
                {item.yil}
              </p>
            </div>
          ))}
        </div>

        <div className="flex items-start gap-2.5 mt-4 p-3 rounded-lg bg-yellow-500/8 border border-yellow-500/20">
          <AlertTriangle className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-semibold text-yellow-400">Aciliyet: CBAM 2026 başlıyor</p>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Şu an %2,5 oranında uygulanmakta. 2034'e kadar her yıl artacak olan bu oran,
              harekete geçmemeniz durumunda toplam yükümlülüğünüzü yaklaşık <span className="text-red-400 font-semibold">40 kat</span> artırabilir.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Page ───────────────────────────────────────────────────────────────────────
export default function StrategyPage() {
  const [aiOpen, setAiOpen] = useState(true);

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
          <h2 className="text-xl font-bold text-foreground">Strateji Raporu</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Ajan 3 çıktısı — optimizasyon önerileri ve interaktif simülasyon
          </p>
        </div>
        <Badge className="bg-red-500/15 text-red-400 border-red-500/25 text-xs px-3 py-1.5">
          Risk Skoru: {mockKpiData.riskScore}/100
        </Badge>
      </motion.div>

      {/* Row 1: Gauge + AI Summary */}
      <div className="grid grid-cols-5 gap-4">
        <motion.div
          className="col-span-2"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.05 }}
        >
          <Card className="glass-card border-border h-full flex flex-col items-center justify-center py-6">
            <p className="text-xs text-muted-foreground mb-4 font-medium uppercase tracking-wider">
              CBAM Uyumluluk Riski
            </p>
            <RiskGauge score={mockKpiData.riskScore} />
            <div className="grid grid-cols-3 gap-2 mt-6 w-full px-4">
              {[
                { label: "0–33", color: "bg-green-500/60", text: "Güvenli" },
                { label: "34–66", color: "bg-yellow-500/60", text: "Dikkat" },
                { label: "67–100", color: "bg-red-500/60", text: "Kritik" },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
                  <span className={cn("w-2 h-2 rounded-sm flex-shrink-0", item.color)} />
                  <span>{item.text}</span>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>

        <motion.div
          className="col-span-3"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card className="glass-card border-primary/20 bg-primary/5 h-full">
            <CardHeader className="pb-2">
              <button
                className="flex items-center justify-between w-full text-left"
                onClick={() => setAiOpen((o) => !o)}
              >
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-3.5 h-3.5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-sm font-semibold text-foreground">AI Danışman Özeti</CardTitle>
                    <p className="text-[10px] text-muted-foreground">Ajan 3 — yönetici özeti</p>
                  </div>
                </div>
                {aiOpen
                  ? <ChevronDown className="w-4 h-4 text-muted-foreground" />
                  : <ChevronRight className="w-4 h-4 text-muted-foreground" />}
              </button>
            </CardHeader>
            <AnimatePresence initial={false}>
              {aiOpen && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.25 }}
                  className="overflow-hidden"
                >
                  <CardContent className="pt-0 space-y-3">
                    {mockAiOzet.split("\n\n").map((para, i) => {
                      const lines = para.split("\n");
                      return (
                        <div key={i} className={cn("space-y-1", i > 0 && "pt-2 border-t border-primary/15")}>
                          {lines.map((line, j) => {
                            if (line.startsWith("**") && line.endsWith("**")) {
                              return (
                                <p key={j} className="text-xs font-bold text-primary">
                                  {line.replaceAll("**", "")}
                                </p>
                              );
                            }
                            return (
                              <p key={j} className="text-xs text-foreground/85 leading-relaxed">{line}</p>
                            );
                          })}
                        </div>
                      );
                    })}
                  </CardContent>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>
        </motion.div>
      </div>

      {/* Row 2: Scenario Table + Simulation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.15 }}
      >
        <ScenarioTable />
      </motion.div>

      {/* Row 3: CBAM Timeline */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <CbamTimelineChart />
      </motion.div>
    </div>
  );
}
