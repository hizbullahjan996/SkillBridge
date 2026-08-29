import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, StatCard, PageHeader, LoadingState, Badge } from "@/components/ui";
import { Building2, MapPin, TrendingUp } from "lucide-react";

export function AdminJobsPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ["admin-job-analytics"],
    queryFn: () => adminApi.getJobAnalytics(),
  });

  if (isLoading) {
    return <LoadingState message="Loading job analytics..." />;
  }

  if (!analytics) return null;

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Job Analytics" description="Job market data and trends" />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          title="Total Jobs"
          value={analytics.total_jobs.toLocaleString()}
          icon={<Building2 className="h-5 w-5" />}
        />
        <StatCard
          title="Top Cities"
          value={analytics.top_cities.length}
          icon={<MapPin className="h-5 w-5" />}
        />
        <StatCard
          title="Top Skills"
          value={analytics.top_skills.length}
          icon={<TrendingUp className="h-5 w-5" />}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <MapPin className="h-4 w-4 text-primary" />
              Top Cities
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {analytics.top_cities.slice(0, 8).map((city) => (
                <div key={city.name} className="flex items-center justify-between">
                  <span className="text-sm">{city.name}</span>
                  <Badge variant="secondary">{city.count.toLocaleString()}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Building2 className="h-4 w-4 text-primary" />
              Top Sectors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {analytics.top_sectors.slice(0, 8).map((sector) => (
                <div key={sector.name} className="flex items-center justify-between">
                  <span className="text-sm">{sector.name}</span>
                  <Badge variant="secondary">{sector.count.toLocaleString()}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              Top Skills
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {analytics.top_skills.slice(0, 8).map((skill) => (
                <div key={skill.name} className="flex items-center justify-between">
                  <span className="text-sm">{skill.name}</span>
                  <Badge variant="secondary">{skill.count.toLocaleString()}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
