import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CategoryBadge } from "@/components/tickets/CategoryBadge";
import { PriorityBadge } from "@/components/tickets/PriorityBadge";
import { SourceBadge } from "@/components/tickets/SourceBadge";
import { StatusBadge } from "@/components/tickets/StatusBadge";
import { formatDateTime } from "@/lib/format";
import type { Ticket } from "@/types/ticket";

type TicketListProps = {
    tickets: Ticket[];
    onSelectTicket: (ticketId: string) => void;
};

export function TicketList({ tickets, onSelectTicket }: TicketListProps) {
    if (tickets.length === 0) {
        return (
            <Card>
                <CardContent className="py-10 text-center text-sm text-muted-foreground">
                    No tickets found. Create your first support request from the submit
                    page.
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="overflow-hidden rounded-lg border bg-card">
            <div className="hidden grid-cols-[1.6fr_1.2fr_0.9fr_0.9fr_0.9fr_1fr_0.7fr_0.6fr] gap-4 border-b bg-muted/50 px-6 py-3 text-sm font-medium text-muted-foreground md:grid">
                <div>Subject</div>
                <div>Requester</div>
                <div className="text-center">Category</div>
                <div className="text-center">Priority</div>
                <div className="text-center">Status</div>
                <div>Created</div>
                <div className="text-center">Source</div>
                <div className="text-right">Action</div>
            </div>

            <div className="divide-y">
                {tickets.map((ticket) => (
                    <div
                        key={ticket.id}
                        className="grid gap-3 px-6 py-5 md:grid-cols-[1.6fr_1.2fr_0.9fr_0.9fr_0.9fr_1fr_0.7fr_0.6fr] md:items-center md:gap-4"
                    >
                        <div className="min-w-0 space-y-1">
                            <p className="truncate font-medium">{ticket.subject}</p>

                            <div className="flex flex-wrap gap-2 md:hidden">
                                <StatusBadge status={ticket.status} />
                                <PriorityBadge priority={ticket.priority} />
                                <CategoryBadge category={ticket.category} />
                                <SourceBadge source={ticket.source} />
                            </div>

                            <p className="line-clamp-2 text-sm text-muted-foreground md:hidden">
                                {ticket.description}
                            </p>
                        </div>

                        <div className="min-w-0 text-sm">
                            <p className="truncate font-medium">{ticket.requester_name}</p>
                            <p className="truncate text-muted-foreground">
                                {ticket.requester_email}
                            </p>
                        </div>

                        <div className="hidden justify-center md:flex">
                            <CategoryBadge category={ticket.category} />
                        </div>

                        <div className="hidden justify-center md:flex">
                            <PriorityBadge priority={ticket.priority} />
                        </div>

                        <div className="hidden justify-center md:flex">
                            <StatusBadge status={ticket.status} />
                        </div>

                        <div className="text-sm text-muted-foreground">
                            {formatDateTime(ticket.created_at)}
                        </div>

                        <div className="hidden justify-center md:flex">
                            <SourceBadge source={ticket.source} />
                        </div>

                        <div className="flex justify-start md:justify-end">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => onSelectTicket(ticket.id)}
                            >
                                View
                            </Button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}