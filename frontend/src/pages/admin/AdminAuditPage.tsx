import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { Badge, PageHeader, LoadingState, Pagination, DataTable, type Column } from "@/components/ui";

interface AuditLog {
  id: number;
  admin_user_id: number;
  admin_email: string | null;
  action: string;
  resource_type: string | null;
  resource_id: number | null;
  metadata: Record<string, unknown> | null;
  timestamp: string;
}

export function AdminAuditPage() {
  const [page, setPage] = useState(1);

  const params: Record<string, string> = { page: String(page), page_size: "20" };

  const { data, isLoading } = useQuery({
    queryKey: ["admin-audit-logs", params],
    queryFn: () => adminApi.getAuditLogs(params),
  });

  const columns: Column<AuditLog>[] = [
    { key: "id", header: "ID", className: "w-16" },
    { key: "admin_email", header: "Admin", render: (l) => l.admin_email || "System" },
    {
      key: "action",
      header: "Action",
      render: (l) => <Badge variant="info">{l.action}</Badge>,
    },
    {
      key: "resource_type",
      header: "Resource",
      render: (l) => l.resource_type ? `${l.resource_type}#${l.resource_id}` : "—",
    },
    {
      key: "timestamp",
      header: "Time",
      render: (l) => new Date(l.timestamp).toLocaleString(),
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Audit Logs" description="Track admin actions and system events" />

      {isLoading ? (
        <LoadingState message="Loading audit logs..." fullScreen={false} />
      ) : (
        <>
          <DataTable
            columns={columns}
            data={data?.items ?? []}
            keyExtractor={(l) => l.id}
            emptyMessage="No audit logs yet."
          />
          <Pagination page={page} totalPages={data?.pages ?? 1} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}
