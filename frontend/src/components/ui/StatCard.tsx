import { cn } from "@/lib/utils";
import { Card } from "./Card";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  description?: string;
  trend?: { value: number; label: string };
  className?: string;
}

function StatCard({ title, value, icon, description, trend, className }: StatCardProps) {
  return (
    <Card className={cn("p-5", className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold tracking-tight">{value}</p>
        </div>
        <div className="rounded-lg bg-primary/10 p-2.5 text-primary">
          {icon}
        </div>
      </div>
      {(description || trend) && (
        <div className="mt-3">
          {trend && (
            <span
              className={cn(
                "text-xs font-medium",
                trend.value >= 0 ? "text-emerald-600" : "text-red-600"
              )}
            >
              {trend.value >= 0 ? "+" : ""}{trend.value}%
            </span>
          )}
          {description && (
            <span className="text-xs text-muted-foreground ml-1">{description}</span>
          )}
        </div>
      )}
    </Card>
  );
}

export { StatCard };
