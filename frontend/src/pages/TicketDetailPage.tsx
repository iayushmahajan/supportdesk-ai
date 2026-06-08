import { useEffect, useState } from "react";

import { getTicketById } from "@/api/tickets";
import { Card, CardContent } from "@/components/ui/card";
import { TicketDetail } from "@/components/tickets/TicketDetail";
import type { TicketDetail as TicketDetailType } from "@/types/ticket";

type TicketDetailPageProps = {
    ticketId: string;
    onBack: () => void;
};

export function TicketDetailPage({ ticketId, onBack }: TicketDetailPageProps) {
    const [ticket, setTicket] = useState<TicketDetailType | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [loadError, setLoadError] = useState<string | null>(null);

    async function loadTicket() {
        try {
            setIsLoading(true);
            setLoadError(null);

            const result = await getTicketById(ticketId);
            setTicket(result);
        } catch (error) {
            console.error(error);
            setLoadError("Ticket could not be loaded.");
        } finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        loadTicket();
    }, [ticketId]);

    if (isLoading && !ticket) {
        return (
            <Card>
                <CardContent className="py-10 text-center text-sm text-muted-foreground">
                    Loading ticket detail...
                </CardContent>
            </Card>
        );
    }

    if (loadError) {
        return (
            <Card className="border-destructive">
                <CardContent className="space-y-4 py-8">
                    <p className="text-sm text-destructive">{loadError}</p>
                    <button className="text-sm underline" onClick={onBack}>
                        Back to dashboard
                    </button>
                </CardContent>
            </Card>
        );
    }

    if (!ticket) {
        return (
            <Card>
                <CardContent className="py-10 text-center text-sm text-muted-foreground">
                    Ticket not found.
                </CardContent>
            </Card>
        );
    }

    return (
        <TicketDetail
            ticket={ticket}
            onBack={onBack}
            onStatusUpdated={loadTicket}
        />
    );
}