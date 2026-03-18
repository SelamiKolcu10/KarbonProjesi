import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useTranslation } from "react-i18next";
import { createCurrencyFormatter, createNumberFormatter } from "@/lib/formatters";

type TsunamiChartProps = {
  projectionData: Record<string, number>;
};

type ChartRow = {
  year: string;
  tax: number;
};

function toChartData(projectionData: Record<string, number>): ChartRow[] {
  return Object.entries(projectionData)
    .map(([year, tax]) => ({
      year,
      tax: Number(tax),
    }))
    .filter((item) => Number.isFinite(item.tax))
    .sort((a, b) => Number(a.year) - Number(b.year));
}

export default function TsunamiChart({ projectionData }: TsunamiChartProps) {
  const { t, i18n } = useTranslation();
  const currencyFormatter = createCurrencyFormatter(i18n.language);
  const axisFormatter = createNumberFormatter(i18n.language);
  const chartData = toChartData(projectionData);
  const hasData = chartData.length > 0;

  return (
    <section className="rounded-xl border border-border/50 bg-card p-4 shadow-sm">
      <h3 className="mb-4 text-base font-semibold text-foreground">
        {t("dashboard.tsunamiChart.title")}
      </h3>

      {hasData ? (
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 8, right: 12, left: 8, bottom: 8 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.35 0.03 255 / 40%)" />
              <XAxis
                dataKey="year"
                tick={{ fontSize: 12, fill: "oklch(0.7 0.02 250)" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 12, fill: "oklch(0.7 0.02 250)" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(value: number) => `€${axisFormatter.format(value)}`}
              />
              <Tooltip
                formatter={(value) => currencyFormatter.format(Number(value) || 0)}
                contentStyle={{
                  backgroundColor: "oklch(0.18 0.03 255 / 95%)",
                  border: "1px solid oklch(0.35 0.03 255 / 60%)",
                  borderRadius: "0.75rem",
                  color: "#f8fafc",
                }}
                labelStyle={{ color: "#cbd5e1", fontWeight: 600 }}
              />
              <Bar dataKey="tax" fill="#ef4444" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="flex h-48 w-full items-center justify-center rounded-lg border border-dashed border-border/60 bg-background/30 px-4 text-center text-sm text-muted-foreground">
          {t("dashboard.tsunamiChart.empty")}
        </div>
      )}
    </section>
  );
}
