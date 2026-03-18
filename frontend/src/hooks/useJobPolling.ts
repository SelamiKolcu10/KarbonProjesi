import { useEffect, useState } from "react";
import { JobService } from "@/lib/api/jobs";
import type { JobStatus } from "@/lib/api/types";

export function useJobPolling(jobId: string | null) {
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      return;
    }

    let isActive = true;

    const pollJobStatus = async () => {
      try {
        const job = await JobService.getJobStatus(jobId);

        if (!isActive) {
          return;
        }

        setStatus(job.status);

        if (job.status === "COMPLETED") {
          clearInterval(intervalId);
          setResult(job.result ?? null);
        }

        if (job.status === "FAILED" || job.status === "REJECTED_BY_GUARD") {
          clearInterval(intervalId);
          setError(job.error_message || "Job failed");
        }
      } catch (err: any) {
        if (!isActive) {
          return;
        }

        clearInterval(intervalId);
        setError(err?.message || "Failed to fetch job status");
      }
    };

    const intervalId = setInterval(pollJobStatus, 3000);

    void pollJobStatus();

    return () => {
      isActive = false;
      clearInterval(intervalId);
    };
  }, [jobId]);

  return { status, result, error };
}