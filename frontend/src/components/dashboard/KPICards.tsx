import { Euro, Factory, ShieldAlert } from "lucide-react";
import { useTranslation } from "react-i18next";
import { createCurrencyFormatter, createNumberFormatter } from "@/lib/formatters";

type KPICardsProps = {
  report: any;
};

function toNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const normalized = value.replace(/,/g, "").trim();
    const parsed = Number(normalized);
    return Number.isFinite(parsed) ? parsed : null;
  }

  return null;
}

function pickFirstNumber(...values: unknown[]): number | null {
  for (const value of values) {
    const parsed = toNumber(value);
    if (parsed !== null) {
      return parsed;
    }
  }

  return null;
}

export default function KPICards({ report }: KPICardsProps) {
  const { t, i18n } = useTranslation();
  const currencyFormatter = createCurrencyFormatter(i18n.language);
  const numberFormatter = createNumberFormatter(i18n.language, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
  const readinessScore = toNumber(report?.compliance_risk?.readiness_score);

  const projection2026 =
    report?.five_year_projection?.["2026"] ??
    report?.five_year_projection?.[2026];

  const estimatedTax = pickFirstNumber(
    projection2026?.baseline_liability,
    projection2026?.baseline_tax_liability,
    projection2026?.tax_liability,
    projection2026?.cbam_tax,
    projection2026?.estimated_tax,
    report?.audit_summary?.baseline_liability,
    report?.audit_summary?.baseline_tax_liability,
    report?.audit_summary?.tax_liability,
    report?.audit_summary?.cbam_tax,
    projection2026
  );

  const totalEmissions = pickFirstNumber(
    report?.audit_summary?.total_cbam_emissions,
    report?.audit_summary?.total_emissions,
    report?.audit_summary?.cbam_emissions_total,
    report?.audit_summary?.total_emissions_tco2e,
    report?.compliance_risk?.total_cbam_emissions,
    report?.compliance_risk?.total_emissions
  );

  const readinessColorClass =
    readinessScore === null
      ? "text-muted-foreground"
      : readinessScore < 70
      ? "text-red-600"
      : readinessScore > 80
        ? "text-green-600"
        : "text-amber-600";

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div className="rounded-xl border border-border/50 bg-card p-4 shadow-sm">
        <div className="mb-2 flex items-center gap-2 text-muted-foreground">
          <ShieldAlert className="h-4 w-4" />
          <span className="text-sm font-medium">{t("dashboard.kpiCards.readinessScore")}</span>
        </div>
        <p className={`text-2xl font-semibold ${readinessColorClass}`}>
          {readinessScore === null ? t("dashboard.kpiCards.notAvailable") : `${numberFormatter.format(readinessScore)}%`}
        </p>
      </div>

      <div className="rounded-xl border border-border/50 bg-card p-4 shadow-sm">
        <div className="mb-2 flex items-center gap-2 text-muted-foreground">
          <Euro className="h-4 w-4" />
          <span className="text-sm font-medium">{t("dashboard.kpiCards.estimatedTax2026")}</span>
        </div>
        <p className="text-2xl font-semibold text-foreground">
          {estimatedTax === null ? t("dashboard.kpiCards.notAvailable") : currencyFormatter.format(estimatedTax)}
        </p>
      </div>

      <div className="rounded-xl border border-border/50 bg-card p-4 shadow-sm">
        <div className="mb-2 flex items-center gap-2 text-muted-foreground">
          <Factory className="h-4 w-4" />
          <span className="text-sm font-medium">{t("dashboard.kpiCards.totalCbamEmissions")}</span>
        </div>
        <p className="text-2xl font-semibold text-foreground">
          {totalEmissions === null
            ? t("dashboard.kpiCards.notAvailable")
            : `${numberFormatter.format(totalEmissions)} ${t("dashboard.kpiCards.tco2e")}`}
        </p>
      </div>
    </div>
  );
}
