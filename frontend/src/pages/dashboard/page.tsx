import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import {
  Wind,
  Euro,
  BarChart3,
  ShieldCheck,
  ShieldAlert,
  TrendingUp,
  TrendingDown,
  Clock,
  FileText,
  AlertTriangle,
  AlertCircle,
  Info,
  ChevronRight,
} from "lucide-react";
import { mockKpiData, mockNotifications, mockGeçmisRaporlar } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const formatNumber = (n: number) =>
  new Intl.NumberFormat("tr-TR").format(n);

const formatCurrency = (n: number) =>
  new Intl.NumberFormat("tr-TR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);

const formatDate = (iso: string) =>
  new Intl.DateTimeFormat("tr-TR", { dateStyle: "medium", timeStyle: "short" }).format(new Date(iso));

type KpiCardProps = {
  title: string;
  value: string;
  unit?: string;
  change?: number;
  status: "green" | "yellow" | "red";
  icon: React.ReactNode;
  delay?: number;
  t: (key: string, options?: Record<string, unknown>) => string;
};

function KpiCard({ title, value, unit, change, status, icon, delay = 0, t }: KpiCardProps) {
  const statusColors = {
    green: { border: "border-green-500/30", glow: "shadow-green-500/10", badge: "bg-green-500/15 text-green-400", dot: "bg-green-400" },
    yellow: { border: "border-yellow-500/30", glow: "shadow-yellow-500/10", badge: "bg-yellow-500/15 text-yellow-400", dot: "bg-yellow-400" },
    red: { border: "border-red-500/30", glow: "shadow-red-500/10", badge: "bg-red-500/15 text-red-400", dot: "bg-red-400" },
  };
  const c = statusColors[status];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
    >
      <Card className={cn("glass-card border shadow-lg relative overflow-hidden", c.border, c.glow)}>
        <div className={cn("absolute top-0 right-0 w-20 h-20 rounded-full blur-2xl opacity-20", 
          status === "green" ? "bg-green-400" : status === "yellow" ? "bg-yellow-400" : "bg-red-400"
        )} />
        <CardContent className="p-5">
          <div className="flex items-start justify-between mb-3">
            <div className={cn("w-9 h-9 rounded-lg flex items-center justify-center", c.badge)}>
              {icon}
            </div>
            <div className={cn("flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-full", c.badge)}>
              <span className={cn("w-1.5 h-1.5 rounded-full", c.dot)} />
              {status === "green" ? t("common.normal") : status === "yellow" ? t("common.attention") : t("common.critical")}
            </div>
          </div>
          <p className="text-xs text-muted-foreground mb-1">{title}</p>
          <div className="flex items-end gap-1.5">
            <span className="text-2xl font-bold text-foreground tabular-nums">{value}</span>
            {unit && <span className="text-sm text-muted-foreground mb-0.5">{unit}</span>}
          </div>
          {change !== undefined && (
            <div className="flex items-center gap-1 mt-2">
              {change > 0 ? (
                <TrendingUp className="w-3.5 h-3.5 text-destructive" />
              ) : (
                <TrendingDown className="w-3.5 h-3.5 text-green-400" />
              )}
              <span className={cn("text-xs font-medium", change > 0 ? "text-destructive" : "text-green-400")}>
                {t(change > 0 ? "dashboard.trendUp" : "dashboard.trendDown", { value: Math.abs(change) })}
              </span>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}

const notificationIcons = {
  critical: <AlertCircle className="w-3.5 h-3.5 text-destructive" />,
  warning: <AlertTriangle className="w-3.5 h-3.5 text-yellow-400" />,
  info: <Info className="w-3.5 h-3.5 text-blue-400" />,
};

const notificationBg = {
  critical: "border-destructive/20 bg-destructive/5",
  warning: "border-yellow-500/20 bg-yellow-500/5",
  info: "border-blue-500/20 bg-blue-500/5",
};

export default function Dashboard() {
  const { t } = useTranslation();
  const complianceStatus = mockKpiData.complianceStatus;

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="flex items-start justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold text-foreground">{t("dashboard.overview")}</h2>
          <div className="flex items-center gap-2 mt-1">
            <Clock className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">
              {t("dashboard.lastAudit")}: {formatDate(mockKpiData.lastAuditDate)} — <span className="text-foreground/70">{mockKpiData.lastDocument}</span>
            </span>
          </div>
        </div>
        <Link to="/belge-yukle">
          <Button className="gap-2 text-sm">
            <FileText className="w-4 h-4" />
            {t("dashboard.newDocument")}
          </Button>
        </Link>
      </motion.div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title={t("dashboard.totalEmission")}
          value={formatNumber(mockKpiData.totalEmission)}
          unit="tCO₂e"
          change={mockKpiData.totalEmissionChange}
          status="red"
          icon={<Wind className="w-4 h-4" />}
          delay={0}
          t={t}
        />
        <KpiCard
          title={t("dashboard.estimatedCbamTax")}
          value={formatCurrency(mockKpiData.cbamTax)}
          change={mockKpiData.cbamTaxChange}
          status="red"
          icon={<Euro className="w-4 h-4" />}
          delay={0.05}
          t={t}
        />
        <KpiCard
          title={t("dashboard.emissionIntensity")}
          value={mockKpiData.emissionIntensity.toFixed(2)}
          unit={t("dashboard.emissionIntensityUnit")}
          change={mockKpiData.emissionIntensityChange}
          status="yellow"
          icon={<BarChart3 className="w-4 h-4" />}
          delay={0.1}
          t={t}
        />
        <KpiCard
          title={t("dashboard.complianceStatus")}
          value={complianceStatus === "compliant" ? t("common.compliant") : complianceStatus === "warning" ? t("common.attention") : t("common.nonCompliant")}
          change={mockKpiData.complianceChange}
          status={complianceStatus === "compliant" ? "green" : complianceStatus === "warning" ? "yellow" : "red"}
          icon={complianceStatus === "compliant" ? <ShieldCheck className="w-4 h-4" /> : <ShieldAlert className="w-4 h-4" />}
          delay={0.15}
          t={t}
        />
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Risk Score */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <Card className="glass-card border-border h-full">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-foreground">{t("dashboard.riskScore")}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center">
                <div className="relative w-32 h-16 mb-3">
                  <svg viewBox="0 0 120 60" className="w-full h-full">
                    <path
                      d="M 10 55 A 50 50 0 0 1 110 55"
                      fill="none"
                      stroke="oklch(0.22 0.03 255)"
                      strokeWidth="8"
                      strokeLinecap="round"
                    />
                    <path
                      d="M 10 55 A 50 50 0 0 1 110 55"
                      fill="none"
                      stroke="#EF4444"
                      strokeWidth="8"
                      strokeLinecap="round"
                      strokeDasharray={`${(mockKpiData.riskScore / 100) * 157} 157`}
                    />
                    <text x="60" y="52" textAnchor="middle" className="text-xl" fill="#f1f5f9" fontSize="18" fontWeight="bold">
                      {mockKpiData.riskScore}
                    </text>
                  </svg>
                </div>
                <div className="flex items-center justify-between w-full text-xs text-muted-foreground px-2">
                  <span>{t("dashboard.riskLow")}</span>
                  <Badge className="bg-red-500/20 text-red-400 border-red-500/30 text-xs">{t("dashboard.highRisk")}</Badge>
                  <span>{t("dashboard.riskHigh")}</span>
                </div>
                <p className="text-xs text-muted-foreground text-center mt-2">{t("dashboard.riskDescription")}</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.25 }}
        >
          <Card className="glass-card border-border h-full">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-foreground">{t("dashboard.cbamFinancialSummary")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { label: t("dashboard.cbamPhaseFactor"), value: "%2,5", color: "text-yellow-400" },
                { label: t("dashboard.grossTaxLiability"), value: "€187.275", color: "text-red-400" },
                { label: t("dashboard.effectiveTax"), value: "€156.400", color: "text-orange-400" },
                { label: t("dashboard.costPerTonSteel"), value: "€2,13/ton", color: "text-foreground" },
                { label: t("dashboard.productionQuantity"), value: "87.900 ton", color: "text-foreground" },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between py-1.5 border-b border-border/50 last:border-0">
                  <span className="text-xs text-muted-foreground">{item.label}</span>
                  <span className={cn("text-xs font-semibold tabular-nums", item.color)}>{item.value}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>

        {/* Notifications */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
        >
          <Card className="glass-card border-border h-full">
            <CardHeader className="pb-3 flex-row items-center justify-between">
              <CardTitle className="text-sm font-semibold text-foreground">{t("dashboard.recentNotifications")}</CardTitle>
              <Link to="/bildirimler">
                <Button variant="ghost" size="sm" className="text-xs h-6 px-2 text-muted-foreground hover:text-foreground">
                  {t("dashboard.viewAll")} <ChevronRight className="w-3 h-3 ml-1" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent className="space-y-2">
              {mockNotifications.slice(0, 4).map((n) => (
                <div
                  key={n.id}
                  className={cn("flex items-start gap-2.5 p-2 rounded-lg border", notificationBg[n.tip as keyof typeof notificationBg])}
                >
                  <div className="mt-0.5 flex-shrink-0">
                    {notificationIcons[n.tip as keyof typeof notificationIcons]}
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs text-foreground/90 leading-tight line-clamp-2">{n.mesaj}</p>
                    <p className="text-[10px] text-muted-foreground mt-0.5">{n.zaman}</p>
                  </div>
                  {!n.okundu && <span className="w-1.5 h-1.5 bg-primary rounded-full mt-1 flex-shrink-0" />}
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Reports */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.35 }}
      >
        <Card className="glass-card border-border">
          <CardHeader className="pb-3 flex-row items-center justify-between">
            <CardTitle className="text-sm font-semibold text-foreground">{t("dashboard.recentAudits")}</CardTitle>
            <Link to="/raporlar">
              <Button variant="ghost" size="sm" className="text-xs h-6 px-2 text-muted-foreground hover:text-foreground">
                {t("dashboard.allReports")} <ChevronRight className="w-3 h-3 ml-1" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left text-muted-foreground font-medium pb-2">{t("dashboard.facility")}</th>
                    <th className="text-left text-muted-foreground font-medium pb-2">{t("dashboard.date")}</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">{t("dashboard.emission")}</th>
                    <th className="text-right text-muted-foreground font-medium pb-2">{t("dashboard.cbamTax")}</th>
                    <th className="text-center text-muted-foreground font-medium pb-2">{t("dashboard.compliance")}</th>
                  </tr>
                </thead>
                <tbody>
                  {mockGeçmisRaporlar.slice(0, 3).map((r) => (
                    <tr key={r.id} className="border-b border-border/50 last:border-0 hover:bg-accent/30 transition-colors">
                      <td className="py-2.5 text-foreground">{r.tesis}</td>
                      <td className="py-2.5 text-muted-foreground">{new Intl.DateTimeFormat("tr-TR", { dateStyle: "short" }).format(new Date(r.tarih))}</td>
                      <td className="py-2.5 text-right text-foreground tabular-nums">{formatNumber(r.emisyon)} {t("dashboard.emissionUnit")}</td>
                      <td className="py-2.5 text-right text-foreground tabular-nums">{formatCurrency(r.cbamVergi)}</td>
                      <td className="py-2.5 text-center">
                        <Badge className={cn("text-[10px] px-1.5",
                          r.uyumluluk === "compliant" ? "bg-green-500/20 text-green-400 border-green-500/30" :
                          r.uyumluluk === "warning" ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" :
                          "bg-red-500/20 text-red-400 border-red-500/30"
                        )}>
                          {r.uyumluluk === "compliant" ? t("common.compliant") : r.uyumluluk === "warning" ? t("common.attention") : t("common.nonCompliant")}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
