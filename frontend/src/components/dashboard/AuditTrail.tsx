import { BookOpen, Scale } from "lucide-react";

type AuditTrailStep = {
  step_name: string;
  result_value: number | string;
  unit?: string;
  formula_applied?: string;
  regulation_reference?: string;
};

type AuditReport = {
  legal_disclaimer: string;
  steps: AuditTrailStep[];
};

type AuditTrailProps = {
  auditReport?: AuditReport;
};

export default function AuditTrail({ auditReport }: AuditTrailProps) {
  if (!auditReport) {
    return null;
  }

  return (
    <section className="rounded-xl border border-border/60 bg-muted/30 p-4 shadow-sm sm:p-5">
      <header className="mb-4 flex items-center gap-2 border-b border-border/50 pb-3">
        <Scale className="h-4 w-4 text-foreground" />
        <h2 className="text-base font-semibold text-foreground sm:text-lg">Legal & Calculation Audit Trail</h2>
      </header>

      <div className="space-y-3">
        {(auditReport.steps ?? []).map((step, index) => (
          <article key={`${step.step_name}-${index}`} className="rounded-lg border border-border/60 bg-card p-4">
            <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <h3 className="text-sm font-semibold text-foreground sm:text-base">{step.step_name}</h3>

              <div className="text-left sm:text-right">
                <p className="text-base font-semibold text-foreground sm:text-lg">
                  {step.result_value}
                  {step.unit ? ` ${step.unit}` : ""}
                </p>
              </div>
            </div>

            <div className="mb-3">
              <code className="inline-block max-w-full break-words font-mono bg-muted p-1 rounded text-sm text-foreground">
                {step.formula_applied ?? "-"}
              </code>
            </div>

            <div className="flex items-start gap-1.5 text-xs italic text-muted-foreground sm:text-sm">
              <BookOpen className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              <p>{step.regulation_reference ?? ""}</p>
            </div>
          </article>
        ))}
      </div>

      <footer className="mt-4 border-t border-border/50 pt-3">
        <p className="text-xs italic text-muted-foreground sm:text-sm">{auditReport.legal_disclaimer}</p>
      </footer>
    </section>
  );
}
