import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, StatCard, PageHeader, LoadingState, Badge } from "@/components/ui";
import { BarChart3, BookOpen, CheckCircle2, TrendingUp } from "lucide-react";

export function AdminLearningPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ["admin-learning-analytics"],
    queryFn: () => adminApi.getLearningAnalytics(),
  });

  if (isLoading) {
    return <LoadingState message="Loading learning analytics..." />;
  }

  if (!analytics) return null;

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Learning Analytics" description="Track platform learning progress and engagement" />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Resources"
          value={analytics.total_resources}
          icon={<BookOpen className="h-5 w-5" />}
        />
        <StatCard
          title="Progress Records"
          value={analytics.total_progress_records}
          icon={<BarChart3 className="h-5 w-5" />}
        />
        <StatCard
          title="Started"
          value={analytics.started}
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <StatCard
          title="Completion Rate"
          value={`${analytics.completion_rate}%`}
          icon={<CheckCircle2 className="h-5 w-5" />}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Most Popular Resources</CardTitle>
          </CardHeader>
          <CardContent>
            {analytics.most_popular_resources.length > 0 ? (
              <div className="space-y-2">
                {analytics.most_popular_resources.map((r) => (
                  <div key={r.title} className="flex items-center justify-between">
                    <span className="text-sm truncate pr-2">{r.title}</span>
                    <Badge variant="secondary">{r.count}</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">No data yet</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Most Studied Skills</CardTitle>
          </CardHeader>
          <CardContent>
            {analytics.most_studied_skills.length > 0 ? (
              <div className="space-y-2">
                {analytics.most_studied_skills.map((s) => (
                  <div key={s.name} className="flex items-center justify-between">
                    <span className="text-sm">{s.name}</span>
                    <Badge variant="secondary">{s.count}</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">No data yet</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
