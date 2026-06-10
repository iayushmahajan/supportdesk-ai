import type { ReactNode } from "react";
import { Button } from "@/components/ui/button";

type AppView = "submit" | "dashboard" | "detail";

type AppShellProps = {
  children: ReactNode;
  currentView: AppView;
  onNavigateToSubmit: () => void;
  onNavigateToDashboard: () => void;
};

export function AppShell({
  children,
  currentView,
  onNavigateToSubmit,
  onNavigateToDashboard,
}: AppShellProps) {
  return (
    <main className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-5 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-medium text-primary">SupportDesk AI</p>
            <h1 className="text-2xl font-bold tracking-tight">
              Support ticket triage dashboard
            </h1>
            <p className="text-sm text-muted-foreground">
              AI-powered support ticket intake, triage, and workflow automation.
            </p>
          </div>

          <nav className="flex flex-wrap gap-2">
            <Button
              variant={currentView === "submit" ? "default" : "outline"}
              onClick={onNavigateToSubmit}
            >
              Submit Ticket
            </Button>

            <Button
              variant={
                currentView === "dashboard" || currentView === "detail"
                  ? "default"
                  : "outline"
              }
              onClick={onNavigateToDashboard}
            >
              Admin Dashboard
            </Button>
          </nav>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-8">{children}</div>
    </main>
  );
}