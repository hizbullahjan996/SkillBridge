import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { Card, CardContent, Input, Select, Badge, PageHeader, LoadingState, Pagination, DataTable, type Column } from "@/components/ui";
import { Search } from "lucide-react";

interface Resource {
  id: number;
  title: string;
  provider: string;
  resource_type: string;
  difficulty: string | null;
  is_free: boolean;
  skills: Array<{ id: number; name: string }>;
}

export function AdminResourcesPage() {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [page, setPage] = useState(1);

  const params: Record<string, string> = { page: String(page), page_size: "20" };
  if (search) params.search = search;
  if (typeFilter) params.resource_type = typeFilter;

  const { data, isLoading } = useQuery({
    queryKey: ["admin-resources", params],
    queryFn: () => adminApi.getResources(params),
  });

  const columns: Column<Resource>[] = [
    { key: "id", header: "ID", className: "w-16" },
    { key: "title", header: "Title", render: (r) => <span className="font-medium">{r.title}</span> },
    { key: "provider", header: "Provider" },
    { key: "resource_type", header: "Type", render: (r) => <Badge variant="secondary" className="capitalize">{r.resource_type}</Badge> },
    { key: "difficulty", header: "Difficulty", render: (r) => r.difficulty ? <Badge variant="outline" className="capitalize">{r.difficulty}</Badge> : "—" },
    { key: "is_free", header: "Free", render: (r) => r.is_free ? <Badge variant="success">Yes</Badge> : <Badge variant="secondary">No</Badge> },
    {
      key: "skills",
      header: "Skills",
      render: (r) => (
        <span className="text-xs text-muted-foreground">
          {r.skills?.map((s) => s.name).join(", ") || "—"}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Resource Management" description="Manage learning resources catalog" />

      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <Input
                placeholder="Search resources..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                icon={<Search className="h-4 w-4" />}
              />
            </div>
            <Select
              value={typeFilter}
              onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
              options={[
                { value: "course", label: "Course" },
                { value: "documentation", label: "Documentation" },
                { value: "tutorial", label: "Tutorial" },
                { value: "book", label: "Book" },
              ]}
              placeholder="All Types"
            />
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <LoadingState message="Loading resources..." fullScreen={false} />
      ) : (
        <>
          <DataTable
            columns={columns}
            data={data?.items ?? []}
            keyExtractor={(r) => r.id}
            emptyMessage="No resources found."
          />
          <Pagination page={page} totalPages={data?.pages ?? 1} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}
