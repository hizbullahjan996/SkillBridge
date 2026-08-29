import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { Card, CardContent, Badge, PageHeader, LoadingState } from "@/components/ui";
import { Server, Database, Bot, Cpu } from "lucide-react";

export function AdminSystemPage() {
  const { data: health, isLoading } = useQuery({
    queryKey: ["admin-system-health"],
    queryFn: () => adminApi.getSystemHealth(),
    refetchInterval: 30000,
  });

  if (isLoading) {
    return <LoadingState message="Checking system health..." />;
  }

  if (!health) return null;

  const checks = [
    {
      name: "API Status",
      status: health.api_status,
      healthy: health.api_status === "healthy",
      icon: <Server className="h-5 w-5" />,
    },
    {
      name: "Database",
      status: health.database_status,
      healthy: health.database_status === "connected",
      icon: <Database className="h-5 w-5" />,
    },
    {
      name: "ML Model",
      status: health.ml_model_status,
      healthy: health.ml_model_status === "loaded",
      icon: <Cpu className="h-5 w-5" />,
    },
    {
      name: "LLM Provider",
      status: health.llm_provider_status,
      healthy: health.llm_provider_status?.startsWith("configured"),
      icon: <Bot className="h-5 w-5" />,
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="System Health" description="Real-time platform health monitoring" />

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {checks.map((check) => (
          <Card key={check.name}>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`rounded-lg p-2.5 ${check.healthy ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>
                    {check.icon}
                  </div>
                  <div>
                    <h3 className="font-medium text-sm">{check.name}</h3>
                    <p className="text-xs text-muted-foreground capitalize">{check.status}</p>
                  </div>
                </div>
                <Badge variant={check.healthy ? "success" : "warning"}>
                  {check.healthy ? "Healthy" : "Check"}
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
