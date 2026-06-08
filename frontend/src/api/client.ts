import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

if (!apiBaseUrl) {
  throw new Error("Missing VITE_API_BASE_URL environment variable");
}

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

export type HealthResponse = {
  status: string;
  app: string;
  environment: string;
};

export type DatabaseHealthResponse = {
  status: string;
  database: string;
};

export async function getBackendHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>("/health");
  return response.data;
}

export async function getDatabaseHealth(): Promise<DatabaseHealthResponse> {
  const response = await apiClient.get<DatabaseHealthResponse>("/health/db");
  return response.data;
}
