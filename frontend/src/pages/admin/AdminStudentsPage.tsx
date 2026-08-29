import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { Card, CardContent, Input, PageHeader, LoadingState, Pagination, DataTable, type Column, Badge } from "@/components/ui";
import { Search } from "lucide-react";

interface Student {
  id: number;
  user_id: number;
  email: string;
  full_name: string;
  major: string | null;
  university_year: string | null;
  skills_count: number;
  recommendations_count: number;
}

export function AdminStudentsPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const params: Record<string, string> = { page: String(page), page_size: "20" };
  if (search) params.search = search;

  const { data, isLoading } = useQuery({
    queryKey: ["admin-students", params],
    queryFn: () => adminApi.getStudents(params),
  });

  const columns: Column<Student>[] = [
    { key: "id", header: "ID", className: "w-16" },
    { key: "full_name", header: "Name", render: (s) => <span className="font-medium">{s.full_name}</span> },
    { key: "email", header: "Email" },
    { key: "major", header: "Major", render: (s) => s.major || "—" },
    { key: "university_year", header: "Year", render: (s) => s.university_year || "—" },
    { key: "skills_count", header: "Skills", render: (s) => <Badge variant="secondary">{s.skills_count}</Badge> },
    { key: "recommendations_count", header: "Recs", render: (s) => <Badge variant="info">{s.recommendations_count}</Badge> },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Student Management" description="View student profiles and data" />

      <Card>
        <CardContent className="pt-6">
          <div className="max-w-md">
            <Input
              placeholder="Search by name or email..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              icon={<Search className="h-4 w-4" />}
            />
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <LoadingState message="Loading students..." fullScreen={false} />
      ) : (
        <>
          <DataTable
            columns={columns}
            data={data?.items ?? []}
            keyExtractor={(s) => s.id}
            emptyMessage="No students found."
          />
          <Pagination page={page} totalPages={data?.pages ?? 1} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}
