export interface InputPayload {
  facility_name: string;
  reporting_period: string;
  production_quantity_tons: number;
  electricity_consumption_mwh: number;
  natural_gas_consumption_m3: number;
  cbam_allocation_rate: number;
  dynamic_grid_factor?: number;
}

export type JobStatus =
  | "PENDING"
  | "RUNNING"
  | "COMPLETED"
  | "FAILED"
  | "REJECTED_BY_GUARD";

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  message?: string;
}

export interface JobRecord {
  job_id: string;
  status: JobStatus;
  result?: any;
  error_message?: string;
}
