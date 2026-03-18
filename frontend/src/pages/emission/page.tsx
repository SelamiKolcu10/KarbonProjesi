import { motion } from "framer-motion";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  LineChart,
  Line,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import {
  AlertTriangle,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  Euro,
  TrendingUp,
  Clock,
  CheckCircle2,
  Cpu,
  BarChart3,
} from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  mockEmissionBreakdown,
  mockMonthlyTrend,
  mockEmissionDetails,
  mockAuditTrail,
  mockMaliEtki,
  mockCbamTimeline,
} from "@/lib/mock-data";

// ─── Formatters ────────────────────────────────────────────────────────────────
const fmt = (n: number) => new Intl.NumberFormat("tr-TR").format(n);
const fmtEur = (n: number) =>
  new Intl.NumberFormat("tr-TR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);
const fmtDate = (iso: string) =>
  new Intl.DateTimeFormat("tr-TR", { dateStyle: "short", timeStyle: "short" }).format(new Date(iso));

// ─── Custom Tooltip ─────────────────────────────────────────────────────────────
function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-card border border-border rounded-lg p-3 shadow-xl text-xs">
      {label && <p className="text-muted-foreground mb-2 font-medium">{label}</p>}
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ background: p.color }} />
          <span className="text-muted-foreground">{p.name}:</span>
          <span className="text-foreground font-semibold tabular-nums">
            {fmt(p.value)} tCO₂e
          </span>
        </div>
      ))}
    </div>
  );
}

// ─── Scope Pie Chart ────────────────────────────────────────────────────────────
function ScopePieChart() {
  const { t } = useTranslation();
  const [active, setActive] = useState<number | null>(null);
  const SCOPE_DATA = [
    { name: t("emission.scope1"), value: mockEmissionBreakdown.scope1, color: "#F59E0B" },
    { name: t("emission.scope2"), value: mockEmissionBreakdown.scope2, color: "#3B82F6" },
    { name: t("emission.processEmissions"),  value: mockEmissionBreakdown.process, color: "#8B5CF6" },
  ];
  const TOTAL = SCOPE_DATA.reduce((s, d) => s + d.value, 0);
  return (
    <Card className="glass-card border-border">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold text-foreground">{t("emission.scopeDistribution")}</CardTitle>
        <p className="text-xs text-muted-foreground">{t("emission.scopeSubtitle")} — tCO₂e</p>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <ResponsiveContainer width={180} height={180}>
            <PieChart>
              <Pie
                data={SCOPE_DATA}
                cx="50%"
                cy="50%"
                innerRadius={52}
                outerRadius={80}
                paddingAngle={3}
                dataKey="value"
                onMouseEnter={(_, idx) => setActive(idx)}
                onMouseLeave={() => setActive(null)}
              >
                {SCOPE_DATA.map((entry, i) => (
                  <Cell
                    key={entry.name}
                    fill={entry.color}
                    opacity={active === null || active === i ? 1 : 0.4}
                    stroke="transparent"
                  />
                ))}
              </Pie>
              <Tooltip
                content={({ active: a, payload: p }) =>
                  a && p?.[0] ? (
                    <div className="bg-card border border-border rounded-lg p-2 shadow-xl text-xs">
                      <p className="text-foreground font-semibold">{p[0].name}</p>
                      <p className="text-muted-foreground">{fmt(p[0].value as number)} tCO₂e</p>
                      <p className="text-muted-foreground">{(((p[0].value as number) / TOTAL) * 100).toFixed(1)}%</p>
                    </div>
                  ) : null
                }
              />
            </PieChart>
          </ResponsiveContainer>
          {/* Legend */}
          <div className="flex-1 space-y-2.5">
            {SCOPE_DATA.map((d, i) => (
              <div
                key={d.name}
                className={cn("flex items-center justify-between p-2 rounded-lg transition-all cursor-default",
                  active === i ? "bg-accent" : "hover:bg-accent/50"
                )}
                onMouseEnter={() => setActive(i)}
                onMouseLeave={() => setActive(null)}
              >
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ background: d.color }} />
                  <span className="text-xs text-muted-foreground">{d.name}</span>
                </div>
                <div className="text-right">
                  <p className="text-xs font-semibold text-foreground tabular-nums">{fmt(d.value)}</p>
                  <p className="text-[10px] text-muted-foreground">{((d.value / TOTAL) * 100).toFixed(1)}%</p>
                </div>
              </div>
            ))}
            <div className="flex items-center justify-between pt-1 border-t border-border px-2">
              <span className="text-xs text-muted-foreground font-medium">{t("common.total")}</span>
              <span className="text-xs font-bold text-foreground tabular-nums">{fmt(TOTAL)} tCO₂e</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Source Bar Chart ───────────────────────────────────────────────────────────
function SourceBarChart() {
  const { t } = useTranslation();
  return (
    <Card className="glass-card border-border">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold text-foreground">{t("emission.emissionSources")}</CardTitle>
        <p className="text-xs text-muted-foreground">{t("emission.sourceBreakdown")} — tCO₂e</p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={mockEmissionBreakdown.sources} barSize={28} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.22 0.03 255)" vertical={false} />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 10, fill: "oklch(0.55 0.02 240)" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "oklch(0.55 0.02 240)" }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "oklch(0.22 0.03 255 / 50%)" }} />
            <Bar dataKey="value" name="tCO₂e" radius={[4, 4, 0, 0]}>
              {mockEmissionBreakdown.sources.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

// ─── Monthly Trend ──────────────────────────────────────────────────────────────
function TrendChart() {
  const { t } = useTranslation();
  return (
    <Card className="glass-card border-border">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-sm font-semibold text-foreground">{t("emission.monthlyTrend")}</CardTitle>
            <p className="text-xs text-muted-foreground">{t("emission.monthlyTrendSubtitle")}</p>
          </div>
          <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
            <span className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-primary inline-block rounded" /> {t("emission.actual")}</span>
            <span className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-destructive inline-block rounded border-dashed" /> {t("emission.target")}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={mockMonthlyTrend} margin={{ top: 4, right: 8, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.22 0.03 255)" vertical={false} />
            <XAxis
              dataKey="ay"
              tick={{ fontSize: 10, fill: "oklch(0.55 0.02 240)" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "oklch(0.55 0.02 240)" }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: "oklch(0.35 0.03 255)", strokeWidth: 1 }} />
            <ReferenceLine y={16000} stroke="#EF4444" strokeDasharray="5 3" strokeWidth={1.5} />
            <Line
              type="monotone"
              dataKey="emisyon"
              name={t("emission.actualEmission")}
              stroke="oklch(0.75 0.18 145)"
              strokeWidth={2.5}
              dot={{ fill: "oklch(0.75 0.18 145)", r: 3, strokeWidth: 0 }}
              activeDot={{ r: 5, strokeWidth: 0 }}
            />
            <Line
              type="monotone"
              dataKey="hedef"
              name={t("emission.target")}
              stroke="#EF4444"
              strokeWidth={1.5}
              strokeDasharray="5 3"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

// ─── Emission Details Table ─────────────────────────────────────────────────────
function EmissionTable() {
  const { t } = useTranslation();
  return (
    <Card className="glass-card border-border">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-sm font-semibold text-foreground">{t("emission.detailedBreakdown")}</CardTitle>
            <p className="text-xs text-muted-foreground">{t("emission.detailedBreakdownSubtitle")}</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 text-[10px] text-yellow-400">
              <span className="w-2 h-2 bg-yellow-500/40 rounded border border-yellow-500/50 inline-block" />
              {t("emission.anomaly")}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-left text-muted-foreground font-medium px-4 py-2.5">{t("emission.emissionSource")}</th>
                <th className="text-right text-muted-foreground font-medium px-4 py-2.5">{t("emission.quantity")}</th>
                <th className="text-left text-muted-foreground font-medium px-4 py-2.5">{t("emission.unit")}</th>
                <th className="text-right text-muted-foreground font-medium px-4 py-2.5">{t("emission.kgCO2")}</th>
                <th className="text-right text-muted-foreground font-medium px-4 py-2.5">tCO₂e</th>
                <th className="text-center text-muted-foreground font-medium px-4 py-2.5">{t("emission.status")}</th>
              </tr>
            </thead>
            <tbody>
              {mockEmissionDetails.map((row) => (
                <tr
                  key={row.id}
                  className={cn(
                    "border-b border-border/50 last:border-0 transition-colors",
                    row.anomali
                      ? "bg-yellow-500/5 hover:bg-yellow-500/10"
                      : "hover:bg-accent/30"
                  )}
                >
                  <td className="px-4 py-3 font-medium text-foreground">
                    <div className="flex items-center gap-2">
                      {row.anomali && <AlertTriangle className="w-3.5 h-3.5 text-yellow-400 flex-shrink-0" />}
                      {row.kaynak}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums text-foreground">
                    {new Intl.NumberFormat("tr-TR").format(row.miktar)}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground font-mono">{row.birim}</td>
                  <td className="px-4 py-3 text-right tabular-nums text-muted-foreground">
                    {new Intl.NumberFormat("tr-TR").format(row.kgCO2)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums font-semibold text-foreground">
                    {fmt(row.tCO2e)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {row.anomali ? (
                      <div className="group relative inline-block">
                        <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30 text-[10px] cursor-help">
                          {t("emission.anomaly")}
                        </Badge>
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 bg-card border border-yellow-500/30 rounded-lg p-2 text-[10px] text-foreground shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 text-left">
                          <p className="font-semibold text-yellow-400 mb-1">{t("emission.anomalyDetectedTitle")}</p>
                          <p className="text-muted-foreground">{row.anomaliMesaj}</p>
                        </div>
                      </div>
                    ) : (
                      <Badge className="bg-green-500/15 text-green-400 border-green-500/25 text-[10px]">
                        {t("common.normal")}
                      </Badge>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="bg-muted/20 border-t border-border">
                <td className="px-4 py-3 font-semibold text-foreground" colSpan={4}>{t("common.total")}</td>
                <td className="px-4 py-3 text-right tabular-nums font-bold text-foreground text-sm">
                  {fmt(mockEmissionDetails.reduce((s, r) => s + r.tCO2e, 0))}
                </td>
                <td className="px-4 py-3" />
              </tr>
            </tfoot>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── CBAM Financial Impact ──────────────────────────────────────────────────────
function MaliEtkiCard() {
  const { t } = useTranslation();
  return (
    <Card className="glass-card border-border">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
          <Euro className="w-4 h-4 text-primary" />
          {t("emission.financialImpact")}
        </CardTitle>
        <p className="text-xs text-muted-foreground">{t("emission.financialImpactSubtitle")}</p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 mb-5">
          {[
            { label: t("emission.cbamPhaseFactor"), value: `%${mockMaliEtki.cbamFazFaktoru}`, sub: t("emission.startRate2026"), color: "text-yellow-400" },
            { label: t("emission.grossTaxLiability"), value: fmtEur(mockMaliEtki.brutVergi), sub: t("emission.calculatedTotal"), color: "text-red-400" },
            { label: t("emission.effectiveTax"), value: fmtEur(mockMaliEtki.efektifVergi), sub: t("emission.afterCredits"), color: "text-orange-400" },
            { label: t("emission.costPerTonSteel"), value: `€${mockMaliEtki.celikBasinaMaliyet.toFixed(2)}/ton`, sub: t("emission.tonProduction", { value: fmt(mockMaliEtki.uretimMiktari) }), color: "text-foreground" },
          ].map((item) => (
            <div key={item.label} className="p-3 rounded-lg bg-muted/30 border border-border/50">
              <p className="text-[10px] text-muted-foreground mb-1">{item.label}</p>
              <p className={cn("text-base font-bold tabular-nums", item.color)}>{item.value}</p>
              <p className="text-[10px] text-muted-foreground mt-0.5">{item.sub}</p>
            </div>
          ))}
        </div>

        {/* CBAM Phase-in Timeline */}
        <div>
          <p className="text-xs font-semibold text-foreground mb-3 flex items-center gap-2">
            <TrendingUp className="w-3.5 h-3.5 text-primary" />
            {t("emission.cbamTimeline")}
          </p>
          <div className="relative">
            <div className="absolute top-3.5 left-0 right-0 h-0.5 bg-border" />
            <div className="flex items-start justify-between relative">
              {mockCbamTimeline.map((item) => (
                <div key={item.yil} className="flex flex-col items-center gap-1.5 relative">
                  <div className={cn(
                    "w-3 h-3 rounded-full border-2 z-10 transition-transform",
                    item.aktif
                      ? "bg-primary border-primary scale-125 shadow-[0_0_8px_oklch(0.75_0.18_145/0.6)]"
                      : item.faz >= 50
                      ? "bg-red-500/60 border-red-500"
                      : "bg-muted border-border"
                  )} />
                  <p className={cn("text-[9px] font-bold tabular-nums mt-1", item.aktif ? "text-primary" : "text-muted-foreground")}>
                    %{item.faz}
                  </p>
                  <p className={cn("text-[9px] tabular-nums", item.aktif ? "text-foreground font-medium" : "text-muted-foreground/60")}>
                    {item.yil}
                  </p>
                  {item.aktif && (
                    <Badge className="bg-primary/20 text-primary border-primary/30 text-[8px] px-1 py-0 absolute -bottom-5 whitespace-nowrap">
                      {t("emission.current")}
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Audit Trail ────────────────────────────────────────────────────────────────
function AuditTrail() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  return (
    <Card className="glass-card border-border">
      <CardHeader className="pb-2">
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex items-center justify-between w-full text-left"
        >
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold text-foreground">{t("emission.auditTrail")}</CardTitle>
            <Badge variant="secondary" className="text-[10px]">{t("emission.recordCount", { count: mockAuditTrail.length })}</Badge>
          </div>
          {open ? <ChevronDown className="w-4 h-4 text-muted-foreground" /> : <ChevronRight className="w-4 h-4 text-muted-foreground" />}
        </button>
      </CardHeader>
      {open && (
        <CardContent className="pt-0">
          <div className="space-y-0">
            {mockAuditTrail.map((item, i) => (
              <div key={i} className="flex gap-3 relative pb-4 last:pb-0">
                {i < mockAuditTrail.length - 1 && (
                  <div className="absolute left-3.5 top-7 bottom-0 w-px bg-border" />
                )}
                <div className="w-7 h-7 rounded-full bg-muted border border-border flex items-center justify-center flex-shrink-0 z-10">
                  {item.kullanici === "Sistem" ? (
                    <Cpu className="w-3 h-3 text-primary" />
                  ) : (
                    <CheckCircle2 className="w-3 h-3 text-green-400" />
                  )}
                </div>
                <div className="flex-1 min-w-0 pt-0.5">
                  <div className="flex items-baseline gap-2 flex-wrap">
                    <span className="text-xs font-semibold text-foreground">{item.islem}</span>
                    <span className="text-[10px] text-muted-foreground">{fmtDate(item.timestamp)}</span>
                    <Badge variant="secondary" className="text-[9px] px-1.5">{item.kullanici}</Badge>
                  </div>
                  <p className="text-[11px] text-muted-foreground mt-0.5">{item.detay}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      )}
    </Card>
  );
}

// ─── Page ───────────────────────────────────────────────────────────────────────
export default function EmissionPage() {
  const { t } = useTranslation();
  const anomalyCount = mockEmissionDetails.filter((r) => r.anomali).length;

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
          <h2 className="text-xl font-bold text-foreground">{t("emission.title")}</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {t("emission.headerSummary")}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {anomalyCount > 0 && (
            <Badge className="bg-yellow-500/15 text-yellow-400 border-yellow-500/30 gap-1.5 px-3 py-1.5">
              <AlertCircle className="w-3.5 h-3.5" />
              {t("emission.anomalyCountDetected", { count: anomalyCount })}
            </Badge>
          )}
          <Badge className="bg-muted text-muted-foreground border-border gap-1.5 px-3 py-1.5">
            <BarChart3 className="w-3.5 h-3.5" />
            {t("emission.totalValueLabel")}
          </Badge>
        </div>
      </motion.div>

      {/* Row 1: Pie + Bar charts */}
      <div className="grid grid-cols-2 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.05 }}>
          <ScopePieChart />
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.1 }}>
          <SourceBarChart />
        </motion.div>
      </div>

      {/* Row 2: Trend chart */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.15 }}>
        <TrendChart />
      </motion.div>

      {/* Row 3: Table */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.2 }}>
        <EmissionTable />
      </motion.div>

      {/* Row 4: Mali Etki + Audit */}
      <div className="grid grid-cols-2 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.25 }}>
          <MaliEtkiCard />
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.3 }}>
          <AuditTrail />
        </motion.div>
      </div>
    </div>
  );
}
