import { Badge } from "@/components/ui/badge";
import { formatEnumLabel } from "@/lib/format";
import type { TicketCategory } from "@/types/ticket";

type CategoryBadgeProps = {
    category: TicketCategory;
};

export function CategoryBadge({ category }: CategoryBadgeProps) {
    return (
        <Badge variant={category === "unclassified" ? "outline" : "secondary"}>
            {formatEnumLabel(category)}
        </Badge>
    );
}