import { motion } from "framer-motion";
import { Upload, FileText, Table, File, Shield, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useState, useRef, useCallback, useEffect } from "react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useTranslation } from "react-i18next";
import { apiClient } from "@/lib/api/client";
import { JobService } from "@/lib/api/jobs";
import { InputPayload, JobRecord } from "@/lib/api/types";
import { useJobPolling } from "@/hooks/useJobPolling";
import { createNumberFormatter } from "@/lib/formatters";
import KPICards from "@/components/dashboard/KPICards";
import TsunamiChart from "@/components/dashboard/TsunamiChart";
import RecommendationCards from "@/components/dashboard/RecommendationCards";
import AuditTrail from "@/components/dashboard/AuditTrail";

type ApiQualityError = {
  code: string;
  message: string;
};

type UiQualityIssue = {
  code: string;
  title: string;
  detail: string;
  action: string;
};

const mapQualityErrorToUi = (
  item: ApiQualityError,
  t: (key: string, options?: Record<string, unknown>) => string
): UiQualityIssue => {
  const fallback = {
    title: t("upload.qualityErrors.fallback.title"),
    detail: item.message || t("upload.qualityErrors.fallback.detail"),
    action: t("upload.qualityErrors.fallback.action"),
  };

  const mappings: Record<string, Omit<UiQualityIssue, "code">> = {
    DQ_ZERO_PRODUCTION_ENERGY_CONFLICT: {
      title: t("upload.qualityErrors.DQ_ZERO_PRODUCTION_ENERGY_CONFLICT.title"),
      detail: t("upload.qualityErrors.DQ_ZERO_PRODUCTION_ENERGY_CONFLICT.detail"),
      action: t("upload.qualityErrors.DQ_ZERO_PRODUCTION_ENERGY_CONFLICT.action"),
    },
    DQ_EXTREME_ENERGY_INTENSITY: {
      title: t("upload.qualityErrors.DQ_EXTREME_ENERGY_INTENSITY.title"),
      detail: t("upload.qualityErrors.DQ_EXTREME_ENERGY_INTENSITY.detail"),
      action: t("upload.qualityErrors.DQ_EXTREME_ENERGY_INTENSITY.action"),
    },
    DQ_MISSING_CORE_ENERGY_DATA: {
      title: t("upload.qualityErrors.DQ_MISSING_CORE_ENERGY_DATA.title"),
      detail: t("upload.qualityErrors.DQ_MISSING_CORE_ENERGY_DATA.detail"),
      action: t("upload.qualityErrors.DQ_MISSING_CORE_ENERGY_DATA.action"),
    },
    DQ_INVALID_ALLOCATION_RATE: {
      title: t("upload.qualityErrors.DQ_INVALID_ALLOCATION_RATE.title"),
      detail: t("upload.qualityErrors.DQ_INVALID_ALLOCATION_RATE.detail"),
      action: t("upload.qualityErrors.DQ_INVALID_ALLOCATION_RATE.action"),
    },
    DQ_VALIDATION_PIPELINE_ERROR: {
      title: t("upload.qualityErrors.DQ_VALIDATION_PIPELINE_ERROR.title"),
      detail: t("upload.qualityErrors.DQ_VALIDATION_PIPELINE_ERROR.detail"),
      action: t("upload.qualityErrors.DQ_VALIDATION_PIPELINE_ERROR.action"),
    },
  };

  const selected = mappings[item.code] || fallback;
  return {
    code: item.code,
    ...selected,
  };
};

const parseNumericValue = (value: unknown): number | null => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const parsed = Number(value.replace(/,/g, "").trim());
    return Number.isFinite(parsed) ? parsed : null;
  }

  return null;
};

type RiskLevel = "low" | "medium" | "high" | "unknown";

const normalizeSignal = (value: unknown): string => {
  if (typeof value !== "string") {
    return "";
  }

  return value.toLowerCase().replace(/[-\s]/g, "_").trim();
};

const getRiskLevelFromReadiness = (score: number | null): RiskLevel => {
  if (score === null) {
    return "unknown";
  }

  if (score < 70) {
    return "high";
  }

  if (score > 80) {
    return "low";
  }

  return "medium";
};

const getRiskLevelFromComplianceSignal = (signal: string): RiskLevel => {
  if (!signal) {
    return "unknown";
  }

  if (
    signal.includes("non_compliant") ||
    signal.includes("rejected") ||
    signal.includes("critical") ||
    signal.includes("high")
  ) {
    return "high";
  }

  if (
    signal.includes("warning") ||
    signal.includes("attention") ||
    signal.includes("medium") ||
    signal.includes("moderate")
  ) {
    return "medium";
  }

  if (
    signal.includes("compliant") ||
    signal.includes("normal") ||
    signal.includes("low") ||
    signal.includes("pass")
  ) {
    return "low";
  }

  return "unknown";
};

const mergeRiskLevels = (a: RiskLevel, b: RiskLevel): RiskLevel => {
  const weight: Record<RiskLevel, number> = {
    unknown: 0,
    low: 1,
    medium: 2,
    high: 3,
  };

  return weight[a] >= weight[b] ? a : b;
};

const getRiskMeta = (score: number | null, complianceSignal: string): { className: string; level: RiskLevel } => {
  const readinessRisk = getRiskLevelFromReadiness(score);
  const complianceRisk = getRiskLevelFromComplianceSignal(complianceSignal);
  const finalRisk = mergeRiskLevels(readinessRisk, complianceRisk);

  if (finalRisk === "high") {
    return {
      className: "bg-red-500/15 text-red-300 border-red-500/30",
      level: finalRisk,
    };
  }

  if (finalRisk === "medium") {
    return {
      className: "bg-amber-500/15 text-amber-300 border-amber-500/30",
      level: finalRisk,
    };
  }

  if (finalRisk === "low") {
    return {
      className: "bg-green-500/15 text-green-300 border-green-500/30",
      level: finalRisk,
    };
  }

  return {
    className: "bg-muted text-muted-foreground border-border",
    level: finalRisk,
  };
};

const formatSignalFallback = (signal: string): string =>
  signal
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

export default function UploadPage() {
  const { t, i18n } = useTranslation();
  const compactNumberFormatter = createNumberFormatter(i18n.language, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  });
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [jsonPreview, setJsonPreview] = useState<object | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [qualityIssues, setQualityIssues] = useState<UiQualityIssue[]>([]);
  const [fileDeleted, setFileDeleted] = useState(false);
  const [extractionInfo, setExtractionInfo] = useState<{
    confidence?: number;
    columnLanguage?: string;
    extractionMode?: string;
  }>({});
  const [orchestratorInfo, setOrchestratorInfo] = useState<{
    jobId?: string;
    status?: JobRecord["status"];
    error?: string;
  }>({});
  const [cbamAllocationRate, setCbamAllocationRate] = useState<string>("0.99");
  const [jobId, setJobId] = useState<string | null>(null);
  const [analysisMessage, setAnalysisMessage] = useState<string>("");
  const [uploadProgress, setUploadProgress] = useState(0);
  const progressInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  const { status, result, error } = useJobPolling(jobId);

  const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50 MB

  const clearProgress = useCallback(() => {
    if (progressInterval.current) {
      clearInterval(progressInterval.current);
      progressInterval.current = null;
    }
  }, []);

  const startProgress = useCallback(() => {
    clearProgress();
    setUploadProgress(0);
    let current = 0;
    progressInterval.current = setInterval(() => {
      current += Math.random() * 8 + 2;
      if (current >= 90) {
        current = 90;
        clearInterval(progressInterval.current!);
        progressInterval.current = null;
      }
      setUploadProgress(Math.min(Math.round(current), 90));
    }, 200);
  }, [clearProgress]);

  useEffect(() => {
    return () => { clearProgress(); };
  }, [clearProgress]);

  useEffect(() => {
    if (!jobId) {
      return;
    }

    if (status) {
      setOrchestratorInfo((prev) => ({
        ...prev,
        status,
      }));
    }

    if (status === "PENDING" || status === "RUNNING") {
      setAnalysisMessage("Analysis in progress... Please wait.");
    }

    if (error || status === "FAILED" || status === "REJECTED_BY_GUARD") {
      const resolvedError = error || t("upload.orchestrator.failed");
      setUploadStatus("error");
      setErrorMessage(resolvedError);
      setAnalysisMessage("");
      setOrchestratorInfo((prev) => ({
        ...prev,
        error: resolvedError,
      }));
    }

    if (status === "COMPLETED" && result) {
      setUploadStatus("success");
      setAnalysisMessage("");
    }
  }, [jobId, status, result, error, t]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = async (file: File) => {
    // Client-side file size validation
    if (file.size > MAX_FILE_SIZE) {
      toast.error(t("upload.fileSizeExceeded"), {
        description: t("upload.selectedFileSize", {
          size: (file.size / 1024 / 1024).toFixed(1),
        }),
      });
      return;
    }

    setUploadedFile(file);
    setIsProcessing(true);
    setUploadStatus("uploading");
    setErrorMessage("");
    setQualityIssues([]);
    setJsonPreview(null);
    setFileDeleted(false);
    setExtractionInfo({});
    setOrchestratorInfo({});
    setJobId(null);
    setAnalysisMessage("");
    startProgress();

    try {
      const formData = new FormData();
      formData.append("file", file);

      let data: any;
      try {
        const response = await apiClient.post("/api/upload", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        data = response.data;
      } catch (err: any) {
        const status = err?.response?.status;
        const raw = err?.response?.data;
        const detail = raw?.detail || raw || { detail: t("upload.unknownError") };

        // Structured DataQuality validation response from backend
        if (status === 422) {
          const qualityErrorsRaw = Array.isArray(detail?.errors) ? detail.errors : [];
          const mappedIssues = qualityErrorsRaw.map((item: ApiQualityError) => mapQualityErrorToUi(item, t));

          setUploadStatus("error");
          setErrorMessage(t("upload.qualityErrors.bannerMessage"));
          setQualityIssues(mappedIssues);
          setJsonPreview(null);
          toast.error(t("upload.qualityErrors.toastTitle"), {
            description: t("upload.qualityErrors.toastDescription", {
              count: mappedIssues.length,
            }),
          });
          return;
        }

        throw new Error(detail?.detail || err?.message || t("upload.unknownError"));
      }

      clearProgress();
      setUploadProgress(100);
      setUploadStatus("success");
      setQualityIssues([]);
      setFileDeleted(data.file_deleted || false);

      // Çıkarılan veriyi JSON önizleme olarak göster
      if (data.structured_data) {
        setJsonPreview(data.structured_data);
      } else if (data.extraction) {
        setJsonPreview(data.extraction);
      } else {
        setJsonPreview(data);
      }

      // Ek bilgiler
      setExtractionInfo({
        confidence: data.extraction?.confidence,
        columnLanguage: data.extraction?.column_language,
        extractionMode: data.extraction_mode,
      });

      if (data.structured_payload) {
        setOrchestratorInfo({ status: "PENDING" });
        setAnalysisMessage("Analysis in progress...");

        const normalizedRate = Math.min(0.99, Number(cbamAllocationRate));
        const formData: InputPayload = {
          ...(data.structured_payload as InputPayload),
          cbam_allocation_rate: Number.isFinite(normalizedRate) ? normalizedRate : 0.99,
        };

        try {
          const job = await JobService.submitJob(formData);
          setJobId(job.job_id);
          setOrchestratorInfo({
            jobId: job.job_id,
            status: job.status,
            error: undefined,
          });

          if (job.status === "REJECTED_BY_GUARD") {
            setUploadStatus("error");
            setErrorMessage(job.message || t("upload.orchestrator.failed"));
            setAnalysisMessage("");
            toast.error(t("upload.orchestrator.rejected"));
            return;
          }
        } catch (err: any) {
          setUploadStatus("error");
          setJsonPreview(null);
          setAnalysisMessage("");

          if (err?.response?.status === 422) {
            const friendlyMessage = "Data quality validation failed. Please check your inputs and try again.";
            setErrorMessage(friendlyMessage);
            toast.error(friendlyMessage);
            return;
          }

          throw new Error(err?.message || t("upload.orchestrator.submitError"));
        }
      }
    } catch (err: any) {
      clearProgress();
      setUploadProgress(0);
      setUploadStatus("error");
      setAnalysisMessage("");
      setErrorMessage(err.message || t("upload.errorMessage"));
      setJsonPreview(null);
    } finally {
      setIsProcessing(false);
    }
  };

  if (status === "COMPLETED" && result) {
    const readinessScore = parseNumericValue(result?.compliance_risk?.readiness_score);
    const complianceSignalRaw =
      result?.compliance_risk?.compliance_status ??
      result?.compliance_risk?.risk_level ??
      result?.audit_summary?.compliance_status ??
      result?.audit_summary?.risk_level ??
      result?.status ??
      "";
    const complianceSignal = normalizeSignal(complianceSignalRaw);
    const riskMeta = getRiskMeta(readinessScore, complianceSignal);
    const riskLabel = t(`upload.result.risk.${riskMeta.level}`, {
      defaultValue: t("upload.result.risk.unknown"),
    });
    const complianceSignalLabel = complianceSignal
      ? t(`upload.result.signal.${complianceSignal}`, {
          defaultValue: formatSignalFallback(complianceSignal),
        })
      : null;

    return (
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h2 className="text-2xl font-bold text-foreground">{t("upload.title")}</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {t("upload.subtitle")}
          </p>
        </motion.div>

        <Card className="glass-card border-border">
          <CardContent className="p-6 space-y-4">
            <div className="flex flex-col gap-6">
              <div className="rounded-lg border border-green-500/30 bg-green-500/10 p-4 text-green-300">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-semibold">{t("upload.result.analysisComplete")}</p>
                  <Badge variant="outline" className={riskMeta.className}>
                    {riskLabel}
                  </Badge>
                </div>
              </div>

              <div className="rounded-xl border border-primary/30 bg-primary/10 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-primary mb-2">
                  {t("upload.result.aiConsultantSummary")}
                </p>
                <p className="text-sm leading-relaxed text-foreground/90">
                  {result?.ai_consultant_summary || t("upload.result.aiConsultantSummaryEmpty")}
                </p>
                <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                  {readinessScore !== null && (
                    <span className="rounded-md border border-border/60 bg-background/50 px-2 py-1">
                      {t("upload.result.readiness")} {compactNumberFormatter.format(readinessScore)}%
                    </span>
                  )}
                  {!!complianceSignalLabel && (
                    <span className="rounded-md border border-border/60 bg-background/50 px-2 py-1">
                      {t("upload.result.earlyWarningSignal")} {complianceSignalLabel}
                    </span>
                  )}
                  {jobId && (
                    <span className="rounded-md border border-border/60 bg-background/50 px-2 py-1">
                      {t("upload.orchestrator.jobId")}: {jobId}
                    </span>
                  )}
                </div>
              </div>

              <KPICards report={result} />

              <TsunamiChart projectionData={result?.five_year_projection || {}} />

              <section className="space-y-3">
                <h2 className="text-lg font-semibold text-foreground">Strategic Action Plan</h2>
                <RecommendationCards recommendations={result?.top_recommendations} />
              </section>

              <hr className="border-border/60" />

              <AuditTrail auditReport={result?.audit_trail_report} />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2 className="text-2xl font-bold text-foreground">{t("upload.title")}</h2>
        <p className="text-sm text-muted-foreground mt-1">
          {t("upload.subtitle")}
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="lg:col-span-2"
        >
          <Card className="glass-card border-border">
            <CardContent className="p-6">
              <div className="mb-4">
                <label htmlFor="cbam-allocation-rate" className="block text-xs font-medium text-foreground mb-2">
                  CBAM Allocation Rate
                </label>
                <input
                  id="cbam-allocation-rate"
                  type="number"
                  min={0}
                  max={0.99}
                  step={0.01}
                  value={cbamAllocationRate}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === "") {
                      setCbamAllocationRate("");
                      return;
                    }
                    const parsed = Number(value);
                    if (!Number.isFinite(parsed)) {
                      return;
                    }
                    setCbamAllocationRate(String(Math.min(0.99, Math.max(0, parsed))));
                  }}
                  disabled={isProcessing}
                  className="w-full rounded-md border border-border bg-background/70 px-3 py-2 text-sm text-foreground outline-none transition-colors focus:border-primary"
                />
                <p className="text-xs text-muted-foreground mt-1">Maximum allowed value: 0.99</p>
              </div>

              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={cn(
                  "border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 cursor-pointer",
                  isDragging
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50 hover:bg-accent/30"
                )}
              >
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  accept=".pdf,.xlsx,.xls,.csv"
                  onChange={handleFileInput}
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent flex items-center justify-center">
                    <Upload className="w-8 h-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    {t("upload.dragDrop")}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {t("upload.orSelect")} <span className="text-primary underline">{t("upload.selectFromComputer")}</span>
                  </p>
                  <div className="flex items-center justify-center gap-2">
                    <Badge variant="outline" className="text-xs">.PDF</Badge>
                    <Badge variant="outline" className="text-xs">.XLSX</Badge>
                    <Badge variant="outline" className="text-xs">.XLS</Badge>
                    <Badge variant="outline" className="text-xs">.CSV</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-4">{t("upload.maxFileSize")}</p>
                </label>
              </div>

              {uploadedFile && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    "mt-4 p-4 rounded-lg border",
                    uploadStatus === "success" && "bg-green-500/5 border-green-500/20",
                    uploadStatus === "uploading" && "bg-primary/5 border-primary/20",
                    uploadStatus === "error" && "bg-red-500/5 border-red-500/20",
                    uploadStatus === "idle" && "bg-primary/5 border-primary/20"
                  )}
                >
                  <div className="flex items-center gap-3">
                    {isProcessing ? (
                      <Loader2 className="w-8 h-8 text-primary animate-spin" />
                    ) : uploadStatus === "success" ? (
                      <CheckCircle className="w-8 h-8 text-green-500" />
                    ) : uploadStatus === "error" ? (
                      <AlertCircle className="w-8 h-8 text-red-500" />
                    ) : (
                      <FileText className="w-8 h-8 text-primary" />
                    )}
                    <div className="flex-1">
                      <p className="font-medium text-foreground">{uploadedFile.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                        {uploadStatus === "success" && ` — ✅ ${t("upload.successMessage")}`}
                        {uploadStatus === "error" && ` — ❌ ${errorMessage}`}
                      </p>
                      {uploadStatus === "uploading" && (
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                            <span>{t("upload.processing")}</span>
                            <span>%{uploadProgress}</span>
                          </div>
                          <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary rounded-full transition-all duration-300 ease-out"
                              style={{ width: `${uploadProgress}%` }}
                            />
                          </div>
                        </div>
                      )}
                      {(status === "PENDING" || status === "RUNNING") && (
                        <div className="mt-3 flex items-center gap-2 rounded-md border border-primary/30 bg-primary/10 p-2">
                          <Loader2 className="w-4 h-4 text-primary animate-spin" />
                          <p className="text-xs text-primary font-medium">Analysis in progress... Please wait.</p>
                        </div>
                      )}
                      {(error || status === "FAILED") && (
                        <div className="mt-3 rounded-md border border-red-500/30 bg-red-500/10 p-2">
                          <p className="text-xs text-red-300">{error || errorMessage || t("upload.orchestrator.failed")}</p>
                        </div>
                      )}
                      {orchestratorInfo.status && (
                        <p className="text-xs text-muted-foreground mt-2">
                          {t("upload.orchestrator.label")} {t(`upload.orchestrator.status.${orchestratorInfo.status}`)}
                          {orchestratorInfo.jobId ? ` (${t("upload.orchestrator.jobId")}: ${orchestratorInfo.jobId})` : ""}
                        </p>
                      )}
                      {analysisMessage && (
                        <p className="text-xs text-primary mt-1">{analysisMessage}</p>
                      )}
                      {orchestratorInfo.error && (
                        <p className="text-xs text-red-400 mt-1">{orchestratorInfo.error}</p>
                      )}
                    </div>
                    {fileDeleted && (
                      <Badge variant="outline" className="text-xs text-green-500 border-green-500/30">
                        <Shield className="w-3 h-3 mr-1" /> {t("upload.fileDeleted")}
                      </Badge>
                    )}
                  </div>

                  {uploadStatus === "error" && qualityIssues.length > 0 && (
                    <div className="mt-4 space-y-2">
                      {qualityIssues.map((issue) => (
                        <div key={`${issue.code}-${issue.title}`} className="rounded-md border border-red-500/30 bg-red-500/5 p-3">
                          <p className="text-xs font-semibold text-red-400">{issue.title}</p>
                          <p className="text-xs text-foreground/80 mt-1">{issue.detail}</p>
                          <p className="text-xs text-muted-foreground mt-1">{t("upload.qualityErrors.whatToDoLabel")} {issue.action}</p>
                          <p className="text-[10px] text-muted-foreground/80 mt-1">{t("upload.qualityErrors.codeLabel")} {issue.code}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* JSON Preview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <Card className="glass-card border-border h-full">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Table className="w-4 h-4" />
                {t("upload.jsonPreview")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {jsonPreview ? (
                <pre className="text-xs text-foreground/80 bg-background/50 p-3 rounded-lg overflow-auto max-h-64">
                  {JSON.stringify(jsonPreview, null, 2)}
                </pre>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <File className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">{t("upload.afterUploadLine1")}</p>
                  <p className="text-sm">{t("upload.afterUploadLine2")}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Info Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <div className="flex items-start gap-3 p-4 rounded-lg bg-card border border-border">
          <FileText className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground">
              {t("upload.pdfConfidence")}
            </p>
            {extractionInfo.confidence !== undefined && (
              <p className="text-xs text-primary mt-1 font-medium">
                {t("upload.confidenceLabel")}: %{Math.round(extractionInfo.confidence * 100)}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-start gap-3 p-4 rounded-lg bg-card border border-border">
          <Table className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground">
              {t("upload.excelColumns")}
            </p>
            {extractionInfo.columnLanguage && extractionInfo.columnLanguage !== "unknown" && (
              <p className="text-xs text-green-500 mt-1 font-medium">
                {t("upload.detectedLanguageLabel")}: {extractionInfo.columnLanguage}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-start gap-3 p-4 rounded-lg bg-card border border-border">
          <Shield className="w-5 h-5 text-orange-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground">
              {t("upload.documentsDeleted")}
            </p>
            {fileDeleted && (
              <p className="text-xs text-orange-500 mt-1 font-medium">
                ✅ {t("upload.fileDeletedSecurely")}
              </p>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
