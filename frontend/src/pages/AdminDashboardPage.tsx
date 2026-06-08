import { useEffect, useMemo, useState } from "react";

import { getTickets } from "@/api/tickets";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { TicketList } from "@/components/tickets/TicketList";
import type { Ticket, TicketStatus } from "@/types/ticket";

type AdminDashboardPageProps = {
    refreshKey: number;
    onSelectTicket: (ticketId: string) => void;
};

const statusFilterOptions: Array<TicketStatus | "all"> = [
    "all",
    "open",
    "in_progress",
    "waiting_customer",
    "resolved",
    "closed",
];

export function AdminDashboardPage({
    refreshKey,
    onSelectTicket,
}: AdminDashboardPageProps) {
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [statusFilter, setStatusFilter] = useState<TicketStatus | "all">("all");
    const [isLoading, setIsLoading] = useState(false);
    const [loadError, setLoadError] = useState<string | null>(null);

    async function loadTickets() {
        try {
            setIsLoading(true);
            setLoadError(null);

            const result = await getTickets();
            setTickets(result);
        } catch (error) {
            console.error(error);
            setLoadError(
                "Tickets could not be loaded. Check that the backend is running."
            );
        } finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        loadTickets();
    }, [refreshKey]);

    const filteredTickets = useMemo(() => {
        if (statusFilter === "all") {
            return tickets;
        }

        return tickets.filter((ticket) => ticket.status === statusFilter);
    }, [tickets, statusFilter]);

    const openTickets = tickets.filter((ticket) => ticket.status === "open");
    const resolvedTickets = tickets.filter(
        (ticket) => ticket.status === "resolved" || ticket.status === "closed"
    );
    const aiReadyTickets = tickets.filter(
        (ticket) => ticket.category === "unclassified"
    );

    return (
        <div className="space-y-6">
            <section className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Total tickets</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-3xl font-bold">{tickets.length}</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Open</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-3xl font-bold">{openTickets.length}</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Resolved/closed</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-3xl font-bold">{resolvedTickets.length}</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Needs AI triage</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-3xl font-bold">{aiReadyTickets.length}</p>
                    </CardContent>
                </Card>
            </section>

            <section className="space-y-4">
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    <div>
                        <h2 className="text-xl font-semibold">Ticket queue</h2>
                        <p className="text-sm text-muted-foreground">
                            View submitted support tickets and update their status.
                        </p>
                    </div>

                    <div className="flex gap-2">
                        <select
                            value={statusFilter}
                            onChange={(event) =>
                                setStatusFilter(event.target.value as TicketStatus | "all")
                            }
                            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                        >
                            {statusFilterOptions.map((status) => (
                                <option key={status} value={status}>
                                    {status === "all"
                                        ? "All statuses"
                                        : status
                                            .split("_")
                                            .map(
                                                (part) => part.charAt(0).toUpperCase() + part.slice(1)
                                            )
                                            .join(" ")}
                                </option>
                            ))}
                        </select>

                        <Button variant="outline" onClick={loadTickets} disabled={isLoading}>
                            {isLoading ? "Loading..." : "Refresh"}
                        </Button>
                    </div>
                </div>

                {loadError ? (
                    <div className="rounded-md border border-destructive bg-destructive/10 px-4 py-3 text-sm text-destructive">
                        {loadError}
                    </div>
                ) : null}

                {isLoading && tickets.length === 0 ? (
                    <Card>
                        <CardContent className="py-10 text-center text-sm text-muted-foreground">
                            Loading tickets...
                        </CardContent>
                    </Card>
                ) : (
                    <TicketList
                        tickets={filteredTickets}
                        onSelectTicket={onSelectTicket}
                    />
                )}
            </section>
        </div>
    );
}