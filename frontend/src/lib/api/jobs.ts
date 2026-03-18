import { apiClient } from "./client";
import { InputPayload, JobResponse, JobRecord } from "./types";

export const JobService = {
  async submitJob(payload: InputPayload): Promise<JobResponse> {
    const response = await apiClient.post<JobResponse>("/api/v1/jobs", payload);
    return response.data;
  },

  async getJobStatus(jobId: string): Promise<JobRecord> {
    const response = await apiClient.get<JobRecord>(`/api/v1/jobs/${jobId}`);
    return response.data;
  },
};
