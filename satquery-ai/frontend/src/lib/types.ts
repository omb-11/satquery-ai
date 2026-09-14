export interface UploadedFile {
  file_id: string;
  filename: string;
  modality: string;
  has_crs: boolean;
  width: number;
  height: number;
  preview_url: string;
  validation: boolean;
}

export interface TraceStep {
  step_num: number;
  name: string;
  status: 'running' | 'success' | 'done' | 'error' | 'skipped';
  tool: string;
  output: string;
  elapsed_ms: number;
  timestamp: string;
}

export interface EvidenceItem {
  source: string;
  claim: string;
  region: number[];
  score: number;
  category: string;
}

export interface ConfidenceReport {
  score: number;
  level: 'High' | 'Medium' | 'Low';
  factors: string[];
  limitations: string[];
}

export interface AnalysisResult {
  run_id: string;
  task_type: string;
  answer: string;
  findings: any;
  evidence: EvidenceItem[];
  confidence: ConfidenceReport;
  models_used: string[];
  parameters: Record<string, any>;
  limitations: string | string[];
  tool_results?: Record<string, any>;
  input_metadata?: any[];
  trace: TraceStep[];
  processing_times: Record<string, number>;
}

export interface ModelInfo {
  name: string;
  version: string;
  status: 'Ready' | 'Fallback' | 'Not installed' | 'Error';
  task_types: string[];
  device: string;
  checkpoint: string;
  fallback: string;
}

export interface SystemInfo {
  cpu_count: number;
  ram_total_gb: number;
  device: string;
  cuda_available: boolean;
  gpu_name: string;
  disk_free_gb: number;
}
