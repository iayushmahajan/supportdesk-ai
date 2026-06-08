import { Badge } from "@/components/ui/badge";
import { formatEnumLabel } from "@/lib/format";
import type { TicketStatus } from "@/types/ticket";

type StatusBadgeProps = {
    status: TicketStatus;
};

export function StatusBadge({ status }: StatusBadgeProps) {
    const variant =
        status === "resolved" || status === "closed"
            ? "secondary"
            : status === "waiting_customer"
                ? "outline"
                : "default";

    return <Badge variant={variant}>{formatEnumLabel(status)}</Badge>;
}