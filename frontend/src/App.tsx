import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  getBackendHealth,
  getDatabaseHealth,
  type DatabaseHealthResponse,
  type HealthResponse,
} from "@/api/client";

function App() {
  const [backendHealth, setBackendHealth] = useState<HealthResponse | null>(
    null
  );
  const [databaseHealth, setDatabaseHealth] =
    useState<DatabaseHealthResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function checkSystemHealth() {
    try {
      setIsLoading(true);
      setErrorMessage(null);

      const [backendResult, databaseResult] = await Promise.all([
        getBackendHealth(),
        getDatabaseHealth(),
      ]);

      setBackendHealth(backendResult);
      setDatabaseHealth(databaseResult);
    } catch (error) {
      console.error(error);
      setErrorMessage(
        "Frontend could not reach the backend. Check VITE_API_BASE_URL and make sure FastAPI is running."
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    checkSystemHealth();
  }, []);

  return (
    <main className="min-h-screen bg-background px-6 py-10">
      <div className="mx-auto flex max-w-5xl flex-col gap-8">
        <section className="space-y-4">
          <Badge variant="secondary">Phase 1</Badge>

          <div className="space-y-3">
            <h1 className="text-4xl font-bold tracking-tight">
              SupportDesk AI
            </h1>

            <p className="max-w-2xl text-muted-foreground">
              A full-stack AI-powered support ticket triage and workflow
              automation platform built with React, FastAPI, PostgreSQL, and
              n8n.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Badge>React</Badge>
            <Badge>TypeScript</Badge>
            <Badge>FastAPI</Badge>
            <Badge>PostgreSQL</Badge>
            <Badge>n8n</Badge>
            <Badge>AI Workflow</Badge>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Backend Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                FastAPI health endpoint connection check.
              </p>

              {backendHealth ? (
                <div className="rounded-lg border bg-card p-4 text-sm">
                  <p>
                    <span className="font-medium">Status:</span>{" "}
                    {backendHealth.status}
                  </p>
                  <p>
                    <span className="font-medium">App:</span>{" "}
                    {backendHealth.app}
                  </p>
                  <p>
                    <span className="font-medium">Environment:</span>{" "}
                    {backendHealth.environment}
                  </p>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No backend response yet.
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Database Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                PostgreSQL connection check through the backend.
              </p>

              {databaseHealth ? (
                <div className="rounded-lg border bg-card p-4 text-sm">
                  <p>
                    <span className="font-medium">Status:</span>{" "}
                    {databaseHealth.status}
                  </p>
                  <p>
                    <span className="font-medium">Database:</span>{" "}
                    {databaseHealth.database}
                  </p>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No database response yet.
                </p>
              )}
            </CardContent>
          </Card>
        </section>

        {errorMessage ? (
          <Card className="border-destructive">
            <CardContent className="pt-6 text-sm text-destructive">
              {errorMessage}
            </CardContent>
          </Card>
        ) : null}

        <div>
          <Button onClick={checkSystemHealth} disabled={isLoading}>
            {isLoading ? "Checking..." : "Recheck System Health"}
          </Button>
        </div>
      </div>
    </main>
  );
}

export default App;