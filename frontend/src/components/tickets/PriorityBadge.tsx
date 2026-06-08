import { Badge } from "@/components/ui/badge";
import { formatEnumLabel } from "@/lib/format";
import type { TicketPriority } from "@/types/ticket";

type PriorityBadgeProps = {
    priority: TicketPriority;
};

export function PriorityBadge({ priority }: PriorityBadgeProps) {
    const variant =
        priority === "urgent" || priority === "high"
            ? "destructive"
            : priority === "unassigned"
                ? "outline"
                : "secondary";

    return <Badge variant={variant}>{formatEnumLabel(priority)}</Badge>;
}