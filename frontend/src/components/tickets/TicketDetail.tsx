import { useState } from "react";

import { updateTicketStatus } from "@/api/tickets";
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
import type { TicketDetail as TicketDetailType, TicketStatus } from "@/types/ticket";

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

export function TicketDetail({
    ticket,
    onBack,
    onStatusUpdated,
}: TicketDetailProps) {
    const [selectedStatus, setSelectedStatus] = useState<TicketStatus>(
        ticket.status
    );
    const [isUpdating, setIsUpdating] = useState(false);
    const [updateError, setUpdateError] = useState<string | null>(null);

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
                            <p className="text-sm font-medium">Routing</p>
                            <p className="mt-1">
                                {ticket.suggested_department ?? "Not assigned yet"}
                            </p>
                            <p className="text-sm text-muted-foreground">
                                AI routing will be added in Phase 4.
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

            <section className="grid gap-6 lg:grid-cols-2">
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

                <Card>
                    <CardHeader>
                        <CardTitle>AI and automation preview</CardTitle>
                        <CardDescription>
                            These sections are prepared for later phases.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4 text-sm">
                        <div className="rounded-lg border bg-muted/40 p-4">
                            <p className="font-medium">Internal summary</p>
                            <p className="mt-1 text-muted-foreground">
                                {ticket.internal_summary ?? "Not generated yet."}
                            </p>
                        </div>

                        <div className="rounded-lg border bg-muted/40 p-4">
                            <p className="font-medium">Agent runs</p>
                            <p className="mt-1 text-muted-foreground">
                                {ticket.agent_runs.length} agent run(s) stored.
                            </p>
                        </div>

                        <div className="rounded-lg border bg-muted/40 p-4">
                            <p className="font-medium">Generated responses</p>
                            <p className="mt-1 text-muted-foreground">
                                {ticket.generated_responses.length} response draft(s) stored.
                            </p>
                        </div>

                        <div className="rounded-lg border bg-muted/40 p-4">
                            <p className="font-medium">Automation events</p>
                            <p className="mt-1 text-muted-foreground">
                                {ticket.automation_events.length} automation event(s) stored.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </section>
        </div>
    );
}