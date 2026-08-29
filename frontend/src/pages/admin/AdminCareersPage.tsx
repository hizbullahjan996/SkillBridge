import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { PageHeader, LoadingState, Badge, EmptyState, DataTable, type Column } from "@/components/ui";
import { Briefcase } from "lucide-react";

interface Career {
  career_id: number;
  career_name: string;
  recommendation_count: number;
  job_count: number;
  skill_count: number;
}

export function AdminCareersPage() {
  const { data: careers, isLoading } = useQuery({
    queryKey: ["admin-careers"],
    queryFn: () => adminApi.getCareers(),
  });

  const columns: Column<Career>[] = [
    { key: "career_id", header: "ID", className: "w-16" },
    { key: "career_name", header: "Career", render: (c) => <span className="font-medium">{c.career_name}</span> },
    { key: "recommendation_count", header: "Recommendations", render: (c) => <Badge variant="info">{c.recommendation_count}</Badge> },
    { key: "job_count", header: "Jobs", render: (c) => <Badge variant="success">{c.job_count}</Badge> },
    { key: "skill_count", header: "Skills", render: (c) => <Badge variant="secondary">{c.skill_count}</Badge> },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Career Management" description="View career paths and their metrics" />

      {isLoading ? (
        <LoadingState message="Loading careers..." fullScreen={false} />
      ) : careers && careers.length > 0 ? (
        <DataTable
          columns={columns}
          data={careers}
          keyExtractor={(c) => c.career_id}
          emptyMessage="No careers found."
        />
      ) : (
        <EmptyState
          icon={<Briefcase className="h-8 w-8" />}
          title="No careers available"
          description="Career data will appear here once loaded."
        />
      )}
    </div>
  );
}
