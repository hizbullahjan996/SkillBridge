import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { Card, CardContent, Input, Select, Badge, PageHeader, LoadingState, Pagination, DataTable, type Column } from "@/components/ui";
import { Search } from "lucide-react";

interface User {
  id: number;
  email: string;
  role: string;
  is_active: boolean;
  has_profile: boolean;
  created_at: string;
}

export function AdminUsersPage() {
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

  const params: Record<string, string> = { page: String(page), page_size: "20" };
  if (search) params.search = search;
  if (roleFilter) params.role = roleFilter;
  if (statusFilter) params.status = statusFilter;

  const { data, isLoading } = useQuery({
    queryKey: ["admin-users", params],
    queryFn: () => adminApi.getUsers(params),
  });

  const columns: Column<User>[] = [
    { key: "id", header: "ID", className: "w-16" },
    { key: "email", header: "Email" },
    {
      key: "role",
      header: "Role",
      render: (user) => (
        <Badge variant={user.role === "admin" ? "default" : "info"}>
          {user.role}
        </Badge>
      ),
    },
    {
      key: "is_active",
      header: "Status",
      render: (user) => (
        <Badge variant={user.is_active ? "success" : "destructive"}>
          {user.is_active ? "Active" : "Inactive"}
        </Badge>
      ),
    },
    {
      key: "has_profile",
      header: "Profile",
      render: (user) => (
        <span className={user.has_profile ? "text-emerald-600" : "text-muted-foreground"}>
          {user.has_profile ? "Complete" : "None"}
        </span>
      ),
    },
    {
      key: "created_at",
      header: "Joined",
      render: (user) => new Date(user.created_at).toLocaleDateString(),
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="User Management"
        description="View and manage platform users"
      />

      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <Input
                placeholder="Search by email..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                icon={<Search className="h-4 w-4" />}
              />
            </div>
            <Select
              value={roleFilter}
              onChange={(e) => { setRoleFilter(e.target.value); setPage(1); }}
              options={[
                { value: "student", label: "Student" },
                { value: "admin", label: "Admin" },
              ]}
              placeholder="All Roles"
            />
            <Select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              options={[
                { value: "active", label: "Active" },
                { value: "inactive", label: "Inactive" },
              ]}
              placeholder="All Status"
            />
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <LoadingState message="Loading users..." fullScreen={false} />
      ) : (
        <>
          <DataTable
            columns={columns}
            data={data?.items ?? []}
            keyExtractor={(user) => user.id}
            emptyMessage="No users found."
          />
          <Pagination page={page} totalPages={data?.pages ?? 1} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}
