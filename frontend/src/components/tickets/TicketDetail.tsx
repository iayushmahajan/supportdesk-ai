import { useEffect, useMemo, useRef, useState } from "react";
import { AutomationEventsCard } from "@/components/tickets/AutomationEventsCard";
import { processTicketWithAi, updateTicketStatus } from "@/api/tickets";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { CategoryBadge } from "@/components/tickets/CategoryBadge";
import { PriorityBadge } from "@/components/tickets/PriorityBadge";
import { SourceBadge } from "@/components/tickets/SourceBadge";
import { StatusBadge } from "@/components/tickets/StatusBadge";
import { formatDateTime, formatEnumLabel } from "@/lib/format";
import type {
  AgentRun,
  TicketDetail as TicketDetailType,
  TicketStatus,
} from "@/types/ticket";

type TicketDetailProps = {
  ticket: TicketDetailType;
  onBack: () => void;
  onStatusUpdated: () => void;
};

const statusOptions: TicketStatus[] = [
  "open",
  "in_progress",
  "waiting_customer",
  "resolved",
  "closed",
];

function getMissingInformationFromAgentRuns(agentRuns: AgentRun[]): string[] {
  const missingInfoAgentRun =
    agentRuns.find(
      (agentRun) => agentRun.agent_name === "Missing Information Agent"
    ) ??
    agentRuns.find((agentRun) =>
      Array.isArray(agentRun.output_json?.missing_information)
    );

  const missingInformation = missingInfoAgentRun?.output_json?.missing_information;

  if (!Array.isArray(missingInformation)) {
    return [];
  }

  return missingInformation.filter((item): item is string => {
    return typeof item === "string";
  });
}

export function TicketDetail({
  ticket,
  onBack,
  onStatusUpdated,
}: TicketDetailProps) {
  const aiResultRef = useRef<HTMLDivElement | null>(null);

  const [selectedStatus, setSelectedStatus] = useState<TicketStatus>(
    ticket.status
  );
  const [isUpdating, setIsUpdating] = useState(false);
  const [isProcessingAi, setIsProcessingAi] = useState(false);
  const [shouldScrollToAiResult, setShouldScrollToAiResult] = useState(false);
  const [updateError, setUpdateError] = useState<string | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

  const sortedAgentRuns = useMemo(() => {
    return [...ticket.agent_runs].sort(
      (a, b) => a.execution_order - b.execution_order
    );
  }, [ticket.agent_runs]);


  const latestGeneratedResponse = useMemo(() => {
    return [...ticket.generated_responses].sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )[0];
  }, [ticket.generated_responses]);

  const missingInformation = getMissingInformationFromAgentRuns(ticket.agent_runs);

  const hasAiResult = Boolean(
    ticket.internal_summary ||
      ticket.suggested_department ||
      ticket.category !== "unclassified" ||
      ticket.priority !== "unassigned" ||
      ticket.agent_runs.length > 0 ||
      ticket.generated_responses.length > 0
  );

  useEffect(() => {
    setSelectedStatus(ticket.status);
  }, [ticket.status]);

  useEffect(() => {
    if (!shouldScrollToAiResult || !hasAiResult) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      aiResultRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });

      setShouldScrollToAiResult(false);
    }, 150);

    return () => window.clearTimeout(timeoutId);
  }, [shouldScrollToAiResult, hasAiResult, ticket.updated_at]);

  async function handleStatusUpdate() {
    try {
      setIsUpdating(true);
      setUpdateError(null);

      await updateTicketStatus(ticket.id, {
        status: selectedStatus,
      });

      onStatusUpdated();
    } catch (error) {
      console.error(error);
      setUpdateError("Status could not be updated.");
    } finally {
      setIsUpdating(false);
    }
  }

  async function handleAiProcessing() {
    if (hasAiResult) {
      return;
    }

    try {
      setIsProcessingAi(true);
      setAiError(null);

      await processTicketWithAi(ticket.id);

      setShouldScrollToAiResult(true);
      onStatusUpdated();
    } catch (error) {
      console.error(error);
      setAiError("AI processing failed. Check backend logs and LLM settings.");
    } finally {
      setIsProcessingAi(false);
    }
  }

  return (
    <div className="space-y-6">
      <Button variant="outline" onClick={onBack}>
        Back to dashboard
      </Button>

      <Card>
        <CardHeader className="space-y-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <CardTitle className="text-2xl">{ticket.subject}</CardTitle>
              <CardDescription>
                Created by {ticket.requester_name} on{" "}
                {formatDateTime(ticket.created_at)}
              </CardDescription>
            </div>

            <div className="flex flex-wrap gap-2">
              <StatusBadge status={ticket.status} />
              <PriorityBadge priority={ticket.priority} />
              <CategoryBadge category={ticket.category} />
              <SourceBadge source={ticket.source} />
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <section className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border bg-muted/40 p-4">
              <p className="text-sm font-medium">Requester</p>
              <p className="mt-1">{ticket.requester_name}</p>
              <p className="text-sm text-muted-foreground">
                {ticket.requester_email}
              </p>
            </div>

            <div className="rounded-lg border bg-muted/40 p-4">
              <p className="text-sm font-medium">Suggested department</p>
              <p className="mt-1">
                {ticket.suggested_department ?? "Not assigned yet"}
              </p>
              <p className="text-sm text-muted-foreground">
                Generated by AI processing.
              </p>
            </div>
          </section>

          <section className="space-y-2">
            <h3 className="font-semibold">Description</h3>
            <p className="whitespace-pre-wrap rounded-lg border bg-card p-4 text-sm leading-6">
              {ticket.description}
            </p>
          </section>

          <section className="space-y-3">
            <h3 className="font-semibold">AI processing</h3>

            {aiError ? (
              <div className="rounded-md border border-destructive bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {aiError}
              </div>
            ) : null}

            <div className="rounded-lg border bg-muted/40 p-4">
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="font-medium">
                    {hasAiResult
                      ? "AI triage already completed"
                      : "Run ticket triage workflow"}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {hasAiResult
                      ? "This ticket already has AI-generated triage results. A controlled re-run option can be added later."
                      : "Classifies category, detects priority, suggests routing, extracts missing information, and drafts a response."}
                  </p>
                </div>

                <Button
                  onClick={handleAiProcessing}
                  disabled={isProcessingAi || hasAiResult}
                >
                  {isProcessingAi
                    ? "Processing..."
                    : hasAiResult
                      ? "AI Processed"
                      : "Process with AI"}
                </Button>
              </div>
            </div>
          </section>

          <section className="space-y-3">
            <h3 className="font-semibold">Update status</h3>

            {updateError ? (
              <div className="rounded-md border border-destructive bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {updateError}
              </div>
            ) : null}

            <div className="flex flex-col gap-3 md:flex-row md:items-center">
              <select
                value={selectedStatus}
                onChange={(event) =>
                  setSelectedStatus(event.target.value as TicketStatus)
                }
                className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {statusOptions.map((status) => (
                  <option key={status} value={status}>
                    {formatEnumLabel(status)}
                  </option>
                ))}
              </select>

              <Button
                onClick={handleStatusUpdate}
                disabled={isUpdating || selectedStatus === ticket.status}
              >
                {isUpdating ? "Updating..." : "Update Status"}
              </Button>
            </div>
          </section>
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
              Structured result stored in the ticket and agent execution log.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4 text-sm">
            <div className="rounded-lg border bg-muted/40 p-4">
              <p className="font-medium">Internal summary</p>
              <p className="mt-2 whitespace-pre-wrap leading-6 text-muted-foreground">
                {ticket.internal_summary ?? "Not generated yet."}
              </p>
            </div>

            <div className="rounded-lg border bg-muted/40 p-4">
              <p className="font-medium">Missing information</p>

              {missingInformation.length > 0 ? (
                <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
                  {missingInformation.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p className="mt-2 text-muted-foreground">
                  No missing information detected yet.
                </p>
              )}
            </div>

            <div className="rounded-lg border bg-muted/40 p-4">
              <p className="font-medium">Latest generated response draft</p>
              <p className="mt-2 whitespace-pre-wrap leading-6 text-muted-foreground">
                {latestGeneratedResponse?.response_text ??
                  "No response draft generated yet."}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Agent execution timeline</CardTitle>
            <CardDescription>
              Each AI workflow step is stored as a separate agent run.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            {sortedAgentRuns.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No AI execution logs yet.
              </p>
            ) : (
              sortedAgentRuns.map((agentRun) => (
                <div key={agentRun.id} className="relative rounded-lg border p-4">
                  <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                    <div className="flex items-start gap-3">
                      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border bg-muted text-xs font-semibold">
                        {agentRun.execution_order}
                      </div>

                      <div>
                        <p className="font-medium">{agentRun.agent_name}</p>
                        <p className="text-sm text-muted-foreground">
                          {agentRun.output_json &&
                          typeof agentRun.output_json.reasoning === "string"
                            ? agentRun.output_json.reasoning
                            : "Agent completed its workflow step."}
                        </p>
                      </div>
                    </div>

                    <span className="rounded-full border px-3 py-1 text-xs font-medium">
                      {formatEnumLabel(agentRun.status)}
                    </span>
                  </div>

                  <div className="mt-3 grid gap-2 text-sm text-muted-foreground md:grid-cols-2">
                    <p>
                      Started:{" "}
                      {agentRun.started_at
                        ? formatDateTime(agentRun.started_at)
                        : "Not started"}
                    </p>
                    <p>
                      Completed:{" "}
                      {agentRun.completed_at
                        ? formatDateTime(agentRun.completed_at)
                        : "Not completed"}
                    </p>
                  </div>

                  {agentRun.output_json ? (
                    <details className="mt-3">
                      <summary className="cursor-pointer text-sm font-medium text-muted-foreground">
                        View agent output
                      </summary>

                      <pre className="mt-3 max-h-56 overflow-auto rounded-md bg-muted p-3 text-xs">
                        {JSON.stringify(agentRun.output_json, null, 2)}
                      </pre>
                    </details>
                  ) : null}

                  {agentRun.error_message ? (
                    <p className="mt-3 text-sm text-destructive">
                      {agentRun.error_message}
                    </p>
                  ) : null}
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </section>
   
      <AutomationEventsCard automationEvents={ticket.automation_events} />

      <Card>
        <CardHeader>
          <CardTitle>Message history</CardTitle>
          <CardDescription>
            Initial requester message is stored when the ticket is created.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {ticket.messages.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No messages available.
            </p>
          ) : (
            ticket.messages.map((message) => (
              <div key={message.id} className="rounded-lg border p-4">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <p className="text-sm font-medium">
                    {formatEnumLabel(message.sender_type)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formatDateTime(message.created_at)}
                  </p>
                </div>

                <p className="text-sm text-muted-foreground">
                  {message.sender_name ?? "Unknown sender"}
                </p>

                <p className="mt-3 whitespace-pre-wrap text-sm leading-6">
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