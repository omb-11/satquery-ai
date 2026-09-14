import axios from 'axios';
import { AnalysisResult, ModelInfo, SystemInfo } from './types';

const api = axios.create({
  baseURL: '/api/v1',
});

export const uploadFiles = async (files: File[]) => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));
  
  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const analyzeImages = async (
  query: string, 
  fileIds: string[], 
  inputMode: string,
  parameters?: Record<string, any>
): Promise<AnalysisResult> => {
  const response = await api.post('/analyze', {
    query,
    file_ids: fileIds,
    input_mode: inputMode,
    parameters: parameters || {}
  });
  return response.data;
};

export const analyzeStream = async (
  query: string,
  fileIds: string[],
  inputMode: string,
  onStep: (step: any) => void,
  onComplete: (result: AnalysisResult) => void,
  onError: (error: any) => void,
  parameters?: Record<string, any>
) => {
  try {
    const response = await fetch('/api/v1/analyze/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        file_ids: fileIds,
        input_mode: inputMode,
        parameters: parameters || {}
      }),
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    if (!response.body) throw new Error('ReadableStream not supported.');
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6).trim();
          if (!dataStr || dataStr === '[DONE]') continue;
          try {
            const parsed = JSON.parse(dataStr);
            if (parsed.type === 'step') {
              onStep(parsed.data);
            } else if (parsed.type === 'complete' || parsed.type === 'result') {
              onComplete(parsed.result || parsed.data);
            } else if (parsed.type === 'error') {
              onError(new Error(parsed.message || 'Stream error'));
            }
          } catch (e) {
            console.error('Error parsing SSE event:', e, dataStr);
          }
        }
      }
    }
  } catch (error) {
    onError(error);
  }
};

export const getModels = async (): Promise<ModelInfo[]> => {
  const response = await api.get('/models');
  return response.data;
};

export const getSystemInfo = async (): Promise<SystemInfo> => {
  const response = await api.get('/system/info');
  return response.data;
};

export const getSystemStatus = async () => {
  const response = await api.get('/system/status');
  return response.data;
};

export const getRuns = async () => {
  const response = await api.get('/runs');
  return response.data;
};

export const getRun = async (id: string) => {
  const response = await api.get(`/runs/${id}`);
  return response.data;
};

export const getReport = async (id: string) => {
  const response = await api.get(`/reports/${id}/json`);
  return response.data;
};

export const getReportHtmlUrl = (id: string) => {
  return `/api/v1/reports/${id}`;
};

export const getGeminiSettings = async () => {
  const response = await api.get('/settings/gemini');
  return response.data;
};

export const updateGeminiSettings = async (apiKey: string, model: string) => {
  const response = await api.post('/settings/gemini', { api_key: apiKey, model });
  return response.data;
};

export const testGeminiConnection = async (apiKey?: string, model?: string) => {
  const response = await api.post('/settings/gemini/test', { api_key: apiKey, model });
  return response.data;
};

export const getPrecisionSettings = async () => {
  const response = await api.get('/settings/precision');
  return response.data;
};

export const updatePrecisionSettings = async (precisionMode: string) => {
  const response = await api.post('/settings/precision', { precision_mode: precisionMode });
  return response.data;
};

