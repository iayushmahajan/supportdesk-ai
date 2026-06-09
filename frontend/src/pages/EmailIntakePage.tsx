import { EmailIntakeForm } from "@/components/tickets/EmailIntakeForm";
import type { TicketDetail } from "@/types/ticket";

type EmailIntakePageProps = {
  onTicketCreated: (ticket: TicketDetail) => void;
};

export function EmailIntakePage({ onTicketCreated }: EmailIntakePageProps) {
  return (
    <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <EmailIntakeForm onTicketCreated={onTicketCreated} />

      <div className="rounded-lg border bg-card p-6">
        <h2 className="text-lg font-semibold">What this demonstrates</h2>

        <div className="mt-4 space-y-3 text-sm text-muted-foreground">
          <p>
            This simulates an incoming support email and converts it into a
            normal ticket.
          </p>
          <p>
            The ticket uses <span className="font-medium">source=email</span>{" "}
            and can then use the same AI triage and automation workflow.
          </p>
          <p>
            In a production version, this could be connected to Gmail, Outlook,
            IMAP, or an n8n email trigger.
          </p>
        </div>

        <div className="mt-6 rounded-md bg-muted p-4 text-sm">
          Recommended test: create an email ticket, open the ticket detail, then
          run AI processing.
        </div>
      </div>
    </div>
  );
}