import { TicketDetail } from "@/components/tickets/TicketDetail";

type TicketDetailPageProps = {
    ticketId: string;
    onBack: () => void;
};

export function TicketDetailPage({ ticketId, onBack }: TicketDetailPageProps) {
    return <TicketDetail ticketId={ticketId} onBack={onBack} />;
}