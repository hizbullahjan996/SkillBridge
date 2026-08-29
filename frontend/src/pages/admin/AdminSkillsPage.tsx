import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { Card, CardContent, Input, PageHeader, LoadingState, Pagination, Badge, DataTable, type Column } from "@/components/ui";
import { Search } from "lucide-react";

interface SkillRow {
  skill_id: number;
  skill_name: string;
  category: string;
  student_count: number;
  job_count: number;
}

export function AdminSkillsPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const params: Record<string, string> = { page: String(page), page_size: "20" };
  if (search) params.search = search;

  const { data, isLoading } = useQuery({
    queryKey: ["admin-skills", params],
    queryFn: () => adminApi.getSkills(params),
  });

  const columns: Column<SkillRow>[] = [
    { key: "skill_id", header: "ID", className: "w-16" },
    { key: "skill_name", header: "Skill", render: (s) => <span className="font-medium">{s.skill_name}</span> },
    { key: "category", header: "Category", render: (s) => <Badge variant="secondary" className="capitalize">{s.category}</Badge> },
    { key: "student_count", header: "Students", render: (s) => <Badge variant="info">{s.student_count}</Badge> },
    { key: "job_count", header: "Jobs", render: (s) => <Badge variant="success">{s.job_count}</Badge> },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Skills Management" description="Browse and manage the skills catalog" />

      <Card>
        <CardContent className="pt-6">
          <div className="max-w-md">
            <Input
              placeholder="Search skills..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              icon={<Search className="h-4 w-4" />}
            />
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <LoadingState message="Loading skills..." fullScreen={false} />
      ) : (
        <>
          <DataTable
            columns={columns}
            data={data?.items ?? []}
            keyExtractor={(s) => s.skill_id}
            emptyMessage="No skills found."
          />
          <Pagination page={page} totalPages={data?.pages ?? 1} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}
