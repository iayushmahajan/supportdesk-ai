import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDateTime, formatEnumLabel } from "@/lib/format";
import type { AutomationEvent } from "@/types/ticket";

type AutomationEventsCardProps = {
  automationEvents: AutomationEvent[];
};

export function AutomationEventsCard({
  automationEvents,
}: AutomationEventsCardProps) {
  const sortedEvents = [...automationEvents].sort(
    (a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Automation events</CardTitle>
        <CardDescription>
          n8n webhook calls, simulated notifications, and callback logs.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {sortedEvents.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No automation events recorded yet.
          </p>
        ) : (
          sortedEvents.map((event) => (
            <div key={event.id} className="rounded-lg border p-4">
              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="font-medium">{formatEnumLabel(event.event_type)}</p>
                  <p className="text-sm text-muted-foreground">
                    Provider: {event.provider}
                  </p>
                </div>

                <span className="rounded-full border px-3 py-1 text-xs font-medium">
                  {formatEnumLabel(event.status)}
                </span>
              </div>

              <div className="mt-3 grid gap-2 text-sm text-muted-foreground md:grid-cols-2">
                <p>Created: {formatDateTime(event.created_at)}</p>
                <p>
                  Completed:{" "}
                  {event.completed_at
                    ? formatDateTime(event.completed_at)
                    : "Not completed"}
                </p>
              </div>

              {event.response_json ? (
                <details className="mt-3">
                  <summary className="cursor-pointer text-sm font-medium text-muted-foreground">
                    View automation response
                  </summary>

                  <pre className="mt-3 max-h-56 overflow-auto rounded-md bg-muted p-3 text-xs">
                    {JSON.stringify(event.response_json, null, 2)}
                  </pre>
                </details>
              ) : null}

              {event.error_message ? (
                <p className="mt-3 text-sm text-destructive">
                  {event.error_message}
                </p>
              ) : null}
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}