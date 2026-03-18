import { Award, Euro, TrendingUp, Zap, AlertCircle } from "lucide-react";
import { useTranslation } from "react-i18next";
import { createCurrencyFormatter, createNumberFormatter } from "@/lib/formatters";

type Recommendation = {
  strategy_name: string;
  difficulty?: string;
  action_plan?: string;
  annual_savings_eur?: number | string | null;
  capex_eur?: number | string | null;
  roi_payback_years?: number | string | null;
  potential_subsidies?: string[];
};

type RecommendationCardsProps = {
  recommendations?: Recommendation[];
};

function toNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const normalized = value.replace(/,/g, "").trim();
    if (!normalized) {
      return null;
    }

    const parsed = Number(normalized);
    return Number.isFinite(parsed) ? parsed : null;
  }

  return null;
}

function getDifficultyBadgeClass(difficulty?: string): string {
  const level = difficulty?.toLowerCase();

  if (level === "low") {
    return "bg-emerald-100 text-emerald-700 border-emerald-200";
  }

  if (level === "high") {
    return "bg-red-100 text-red-700 border-red-200";
  }

  return "bg-amber-100 text-amber-700 border-amber-200";
}

export default function RecommendationCards({ recommendations }: RecommendationCardsProps) {
  const { i18n } = useTranslation();
  const currencyFormatter = createCurrencyFormatter(i18n.language, "EUR", {
    maximumFractionDigits: 0,
  });
  const numberFormatter = createNumberFormatter(i18n.language, {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });

  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  return (
    <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      {recommendations.map((recommendation, index) => {
        const annualSavings = toNumber(recommendation.annual_savings_eur);
        const capex = toNumber(recommendation.capex_eur);
        const roiPayback = toNumber(recommendation.roi_payback_years);
        const subsidies = recommendation.potential_subsidies ?? [];

        return (
          <article
            key={`${recommendation.strategy_name}-${index}`}
            className="rounded-xl border border-border/50 bg-card p-5 shadow-sm"
          >
            <header className="mb-4 flex items-start justify-between gap-3">
              <div className="flex items-start gap-2">
                <TrendingUp className="mt-0.5 h-4 w-4 text-primary" />
                <h3 className="text-base font-semibold leading-tight text-foreground sm:text-lg">
                  {recommendation.strategy_name}
                </h3>
              </div>

              <span
                className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${getDifficultyBadgeClass(
                  recommendation.difficulty
                )}`}
              >
                <AlertCircle className="mr-1 h-3 w-3" />
                {recommendation.difficulty ?? "Medium"}
              </span>
            </header>

            <p className="mb-4 text-sm leading-6 text-muted-foreground">{recommendation.action_plan ?? "-"}</p>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded-lg border border-border/50 bg-background/40 p-3">
                <div className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Euro className="h-3.5 w-3.5" />
                  <span>Annual Savings</span>
                </div>
                <p className="text-sm font-semibold text-foreground">
                  {annualSavings === null ? "N/A" : currencyFormatter.format(annualSavings)}
                </p>
              </div>

              <div className="rounded-lg border border-border/50 bg-background/40 p-3">
                <div className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Zap className="h-3.5 w-3.5" />
                  <span>CAPEX</span>
                </div>
                <p className="text-sm font-semibold text-foreground">
                  {capex === null ? "N/A" : currencyFormatter.format(capex)}
                </p>
              </div>

              <div className="rounded-lg border border-border/50 bg-background/40 p-3">
                <div className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground">
                  <TrendingUp className="h-3.5 w-3.5" />
                  <span>ROI (Payback)</span>
                </div>
                <p className="text-sm font-semibold text-foreground">
                  {roiPayback === null ? "N/A" : `${numberFormatter.format(roiPayback)} Years`}
                </p>
              </div>
            </div>

            {subsidies.length > 0 && (
              <div className="mt-4 rounded-lg border border-emerald-200/60 bg-emerald-50/80 p-3">
                <div className="mb-2 flex items-center gap-1.5 text-xs font-medium text-emerald-700">
                  <Award className="h-3.5 w-3.5" />
                  <span>Potential Subsidies & Grants</span>
                </div>

                <ul className="space-y-1.5">
                  {subsidies.map((subsidy, subsidyIndex) => (
                    <li key={`${subsidy}-${subsidyIndex}`} className="flex items-start gap-2 text-sm text-emerald-800">
                      <Award className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                      <span>{subsidy}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </article>
        );
      })}
    </section>
  );
}
