import { Badge } from "@/components/ui/badge";
import { formatEnumLabel } from "@/lib/format";
import type { TicketSource } from "@/types/ticket";

type SourceBadgeProps = {
    source: TicketSource;
};

export function SourceBadge({ source }: SourceBadgeProps) {
    return <Badge variant="outline">{formatEnumLabel(source)}</Badge>;
}