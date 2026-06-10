import { useEffect, useMemo, useRef, useState } from "react";

import {
  getTicketById,
  processTicketWithAi,
  reprocessTicketWithAi,
  updateTicketStatus,
} from "@/api/tickets";
import { AutomationEventsCard } from "@/components/tickets/AutomationEventsCard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatDateTime, formatEnumLabel } from "@/lib/format";
import type {
  AgentRun,
  TicketCategory,
  TicketDetail,
  TicketPriority,
  TicketStatus,
} from "@/types/ticket";

type TicketDetailProps = {
  ticketId: string;
  onBack: () => void;
};

const statusOptions: TicketStatus[] = [
  "open",
  "in_progress",
  "waiting_customer",
  "resolved",
  "closed",
];

function getStatusBadgeVariant(status: TicketStatus) {
  if (status === "open") {
    return "secondary" as const;
  }

  if (status === "in_progress" || status === "waiting_customer") {
    return "default" as const;
  }

  if (status === "resolved" || status === "closed") {
    return "outline" as const;
  }

  return "secondary" as const;
}

function getPriorityBadgeVariant(priority: TicketPriority) {
  if (priority === "urgent" || priority === "high") {
    return "destructive" as const;
  }

  if (priority === "medium") {
    return "default" as const;
  }

  if (priority === "low") {
    return "secondary" as const;
  }

  return "outline" as const;
}

function getCategoryBadgeVariant(category: TicketCategory) {
  if (category === "unclassified") {
    return "outline" as const;
  }

  return "secondary" as const;
}

function getMissingInformationFromAgentRuns(agentRuns: AgentRun[]): string[] {
  const missingInfoAgentRun =
    agentRuns.find(
      (agentRun) => agentRun.agent_name === "Missing Information Agent"
    ) ??
    agentRuns.find((agentRun) =>
      Array.isArray(agentRun.output_json?.missing_information)
    );

  const missingInformation =
    missingInfoAgentRun?.output_json?.missing_information;

  if (!Array.isArray(missingInformation)) {
    return [];
  }

  return missingInformation.filter((item): item is string => {
    return typeof item === "string";
  });
}

function JsonPreview({
  title,
  value,
}: {
  title: string;
  value: Record<string, unknown> | null;
}) {
  if (!value) {
    return null;
  }

  return (
    <details className="mt-3">
      <summary className="cursor-pointer text-sm font-medium text-muted-foreground">
        {title}
      </summary>

      <pre className="mt-3 max-h-72 overflow-auto rounded-md bg-muted p-3 text-xs">
        {JSON.stringify(value, null, 2)}
      </pre>
    </details>
  );
}

export function TicketDetail({ ticketId, onBack }: TicketDetailProps) {
  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [isProcessingAi, setIsProcessingAi] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);
  const [shouldScrollToAiResult, setShouldScrollToAiResult] = useState(false);

  const aiResultRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadTicket() {
      try {
        setIsLoading(true);
        setLoadError(null);

        const loadedTicket = await getTicketById(ticketId);

        if (isMounted) {
          setTicket(loadedTicket);
        }
      } catch (error) {
        console.error(error);

        if (isMounted) {
          setLoadError(
            "Ticket could not be loaded. Please check that the backend is running."
          );
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadTicket();

    return () => {
      isMounted = false;
    };
  }, [ticketId]);

  const sortedAgentRuns = useMemo(() => {
    if (!ticket) {
      return [];
    }

    return [...ticket.agent_runs].sort((a, b) => {
      const createdAtDifference =
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime();

      if (createdAtDifference !== 0) {
        return createdAtDifference;
      }

      return a.execution_order - b.execution_order;
    });
  }, [ticket]);

  const latestGeneratedResponse = useMemo(() => {
    if (!ticket) {
      return undefined;
    }

    return [...ticket.generated_responses].sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )[0];
  }, [ticket]);

  const hasAiResult = useMemo(() => {
    if (!ticket) {
      return false;
    }

    return Boolean(
      ticket.internal_summary ||
      ticket.suggested_department ||
      ticket.category !== "unclassified" ||
      ticket.priority !== "unassigned" ||
      ticket.agent_runs.length > 0 ||
      ticket.generated_responses.length > 0
    );
  }, [ticket]);

  const missingInformation = useMemo(() => {
    if (!ticket) {
      return [];
    }

    return getMissingInformationFromAgentRuns(ticket.agent_runs);
  }, [ticket]);

  useEffect(() => {
    if (!shouldScrollToAiResult || !aiResultRef.current) {
      return;
    }

    aiResultRef.current.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });

    setShouldScrollToAiResult(false);
  }, [shouldScrollToAiResult, ticket]);

  async function handleStatusChange(nextStatus: TicketStatus) {
    if (!ticket) {
      return;
    }

    try {
      setIsUpdatingStatus(true);

      const updatedTicket = await updateTicketStatus(ticket.id, {
        status: nextStatus,
      });

      setTicket((currentTicket) => {
        if (!currentTicket) {
          return currentTicket;
        }

        return {
          ...currentTicket,
          ...updatedTicket,
        };
      });
    } catch (error) {
      console.error(error);
      setLoadError("Ticket status could not be updated. Please try again.");
    } finally {
      setIsUpdatingStatus(false);
    }
  }

  async function handleProcessWithAi() {
    if (!ticket) {
      return;
    }

    try {
      setAiError(null);
      setIsProcessingAi(true);

      const updatedTicket = hasAiResult
        ? await reprocessTicketWithAi(ticket.id)
        : await processTicketWithAi(ticket.id);

      setTicket(updatedTicket);
      setShouldScrollToAiResult(true);
    } catch (error) {
      console.error(error);

      setAiError(
        hasAiResult
          ? "Ticket could not be reprocessed with AI. Please try again."
          : "Ticket could not be processed with AI. Please try again."
      );
    } finally {
      setIsProcessingAi(false);
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading ticket...</CardTitle>
          <CardDescription>
            The selected support ticket is being loaded.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (loadError || !ticket) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Ticket unavailable</CardTitle>
          <CardDescription>{loadError ?? "Ticket not found."}</CardDescription>
        </CardHeader>

        <CardContent>
          <Button variant="outline" onClick={onBack}>
            Back to dashboard
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Button variant="outline" onClick={onBack}>
        Back to dashboard
      </Button>

      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="space-y-2">
              <CardTitle>{ticket.subject}</CardTitle>
              <CardDescription>
                Submitted by {ticket.requester_name} · {ticket.requester_email}
              </CardDescription>
            </div>

            <div className="flex flex-wrap gap-2">
              <Badge variant={getStatusBadgeVariant(ticket.status)}>
                {formatEnumLabel(ticket.status)}
              </Badge>

              <Badge variant={getPriorityBadgeVariant(ticket.priority)}>
                {formatEnumLabel(ticket.priority)}
              </Badge>

              <Badge variant={getCategoryBadgeVariant(ticket.category)}>
                {formatEnumLabel(ticket.category)}
              </Badge>

              <Badge variant="outline">{formatEnumLabel(ticket.source)}</Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="grid gap-4 text-sm md:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="text-muted-foreground">Created</p>
              <p className="font-medium">{formatDateTime(ticket.created_at)}</p>
            </div>

            <div>
              <p className="text-muted-foreground">Last updated</p>
              <p className="font-medium">{formatDateTime(ticket.updated_at)}</p>
            </div>

            <div>
              <p className="text-muted-foreground">Suggested department</p>
              <p className="font-medium">
                {ticket.suggested_department ?? "Not assigned yet"}
              </p>
            </div>

            <div>
              <p className="text-muted-foreground">Status</p>
              <select
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
                value={ticket.status}
                disabled={isUpdatingStatus}
                onChange={(event) =>
                  handleStatusChange(event.target.value as TicketStatus)
                }
              >
                {statusOptions.map((status) => (
                  <option key={status} value={status}>
                    {formatEnumLabel(status)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <p className="mb-2 text-sm font-medium">Description</p>
            <div className="whitespace-pre-wrap rounded-md border bg-muted/40 p-4 text-sm leading-6">
              {ticket.description}
            </div>
          </div>

          <div className="flex flex-col gap-3 border-t pt-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-medium">AI triage</p>
              <p className="text-sm text-muted-foreground">
                Run or re-run the multi-agent workflow to classify, prioritize,
                route, and draft a response.
              </p>
            </div>

            <Button onClick={handleProcessWithAi} disabled={isProcessingAi}>
              {isProcessingAi
                ? hasAiResult
                  ? "Reprocessing..."
                  : "Processing..."
                : hasAiResult
                  ? "Reprocess with AI"
                  : "Process with AI"}
            </Button>
          </div>

          {aiError ? (
            <div className="rounded-md border border-destructive bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {aiError}
            </div>
          ) : null}
        </CardContent>
      </Card>

      <section
        ref={aiResultRef}
        className="grid scroll-mt-6 gap-6 lg:grid-cols-2"
      >
        <Card>
          <CardHeader>
            <CardTitle>AI triage result</CardTitle>
            <CardDescription>
              Classification, routing, summary, and missing information detected
              by the agent workflow.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-5">
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-md border p-3">
                <p className="text-xs text-muted-foreground">Category</p>
                <p className="font-medium">{formatEnumLabel(ticket.category)}</p>
              </div>

              <div className="rounded-md border p-3">
                <p className="text-xs text-muted-foreground">Priority</p>
                <p className="font-medium">{formatEnumLabel(ticket.priority)}</p>
              </div>

              <div className="rounded-md border p-3">
                <p className="text-xs text-muted-foreground">Department</p>
                <p className="font-medium">
                  {ticket.suggested_department ?? "Not assigned"}
                </p>
              </div>
            </div>

            <div>
              <p className="mb-2 text-sm font-medium">Internal summary</p>
              <div className="min-h-24 rounded-md border bg-muted/40 p-4 text-sm leading-6">
                {ticket.internal_summary ??
                  "No AI summary available yet. Run AI processing to generate one."}
              </div>
            </div>

            <div>
              <p className="mb-2 text-sm font-medium">Missing information</p>

              {missingInformation.length > 0 ? (
                <ul className="list-disc space-y-1 rounded-md border bg-muted/40 p-4 pl-8 text-sm">
                  {missingInformation.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              ) : (
                <div className="rounded-md border bg-muted/40 p-4 text-sm text-muted-foreground">
                  No missing information detected yet.
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Generated response draft</CardTitle>
            <CardDescription>
              Suggested answer that a support agent can review before sending.
            </CardDescription>
          </CardHeader>

          <CardContent>
            {latestGeneratedResponse ? (
              <div className="space-y-3">
                <div className="whitespace-pre-wrap rounded-md border bg-muted/40 p-4 text-sm leading-6">
                  {latestGeneratedResponse.response_text}
                </div>

                <p className="text-xs text-muted-foreground">
                  Tone: {formatEnumLabel(latestGeneratedResponse.tone)} ·
                  Created: {formatDateTime(latestGeneratedResponse.created_at)}
                </p>
              </div>
            ) : (
              <p className="rounded-md border bg-muted/40 p-4 text-sm text-muted-foreground">
                No response draft generated yet.
              </p>
            )}
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Agent execution timeline</CardTitle>
          <CardDescription>
            Each row represents one agent in the multi-agent workflow.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {sortedAgentRuns.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No agent runs recorded yet.
            </p>
          ) : (
            sortedAgentRuns.map((agentRun) => (
              <div key={agentRun.id} className="rounded-lg border p-4">
                <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="font-medium">
                      {agentRun.execution_order}. {agentRun.agent_name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Created: {formatDateTime(agentRun.created_at)}
                    </p>
                  </div>

                  <Badge
                    variant={
                      agentRun.status === "completed"
                        ? "default"
                        : agentRun.status === "failed"
                          ? "destructive"
                          : "secondary"
                    }
                  >
                    {formatEnumLabel(agentRun.status)}
                  </Badge>
                </div>

                {agentRun.error_message ? (
                  <p className="mt-3 text-sm text-destructive">
                    {agentRun.error_message}
                  </p>
                ) : null}

                <JsonPreview title="View input JSON" value={agentRun.input_json} />
                <JsonPreview
                  title="View output JSON"
                  value={agentRun.output_json}
                />
              </div>
            ))
          )}
        </CardContent>
      </Card>

      <AutomationEventsCard automationEvents={ticket.automation_events} />

      <Card>
        <CardHeader>
          <CardTitle>Message history</CardTitle>
          <CardDescription>
            Original requester message and future conversation history.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {ticket.messages.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No messages recorded yet.
            </p>
          ) : (
            ticket.messages.map((message) => (
              <div key={message.id} className="rounded-lg border p-4">
                <div className="mb-2 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-medium">
                      {message.sender_name ??
                        formatEnumLabel(message.sender_type)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {message.sender_email ??
                        formatEnumLabel(message.sender_type)}
                    </p>
                  </div>

                  <p className="text-xs text-muted-foreground">
                    {formatDateTime(message.created_at)}
                  </p>
                </div>

                <p className="whitespace-pre-wrap text-sm leading-6">
                  {message.body}
                </p>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}