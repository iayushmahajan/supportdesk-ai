import { useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { AdminDashboardPage } from "@/pages/AdminDashboardPage";
import { TicketDetailPage } from "@/pages/TicketDetailPage";
import { TicketSubmissionPage } from "@/pages/TicketSubmissionPage";
import type { Ticket, TicketDetail } from "@/types/ticket";

type AppView = "submit" | "dashboard" | "detail";

function App() {
  const [currentView, setCurrentView] = useState<AppView>("dashboard");
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null);
  const [dashboardRefreshKey, setDashboardRefreshKey] = useState(0);

  function handleTicketCreated(ticket: Ticket | TicketDetail) {
    setSelectedTicketId(ticket.id);
    setDashboardRefreshKey((current) => current + 1);
    setCurrentView("detail");
  }

  function handleSelectTicket(ticketId: string) {
    setSelectedTicketId(ticketId);
    setCurrentView("detail");
  }

  function handleNavigateToSubmit() {
    setCurrentView("submit");
  }

  function handleNavigateToDashboard() {
    setSelectedTicketId(null);
    setDashboardRefreshKey((current) => current + 1);
    setCurrentView("dashboard");
  }

  return (
    <AppShell
      currentView={currentView}
      onNavigateToSubmit={handleNavigateToSubmit}
      onNavigateToDashboard={handleNavigateToDashboard}
    >
      {currentView === "submit" ? (
        <TicketSubmissionPage onTicketCreated={handleTicketCreated} />
      ) : null}

      {currentView === "dashboard" ? (
        <AdminDashboardPage
          refreshKey={dashboardRefreshKey}
          onSelectTicket={handleSelectTicket}
        />
      ) : null}

      {currentView === "detail" && selectedTicketId ? (
        <TicketDetailPage
          ticketId={selectedTicketId}
          onBack={handleNavigateToDashboard}
        />
      ) : null}
    </AppShell>
  );
}

export default App;