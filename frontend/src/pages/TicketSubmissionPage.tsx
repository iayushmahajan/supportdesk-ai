import { TicketSubmissionForm } from "@/components/tickets/TicketSubmissionForm";
import type { Ticket } from "@/types/ticket";

type TicketSubmissionPageProps = {
    onTicketCreated: (ticket: Ticket) => void;
};

export function TicketSubmissionPage({
    onTicketCreated,
}: TicketSubmissionPageProps) {
    return (
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <TicketSubmissionForm onTicketCreated={onTicketCreated} />

            <div className="rounded-lg border bg-card p-6">
                <h2 className="text-lg font-semibold">Example requests</h2>

                <div className="mt-4 space-y-3 text-sm text-muted-foreground">
                    <p>“I cannot log in.”</p>
                    <p>“My invoice amount is wrong.”</p>
                    <p>“Please update my address.”</p>
                    <p>“The dashboard is not loading.”</p>
                    <p>“I attached documents and need this processed.”</p>
                </div>

                <div className="mt-6 rounded-md bg-muted p-4 text-sm">
                    In Phase 4, these tickets will be processed by the AI service layer to
                    detect category, priority, missing information, routing, summary, and
                    response draft.
                </div>
            </div>
        </div>
    );
}