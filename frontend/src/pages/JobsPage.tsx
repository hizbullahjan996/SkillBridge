import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, Badge, PageHeader, LoadingState, EmptyState } from "@/components/ui";
import { Briefcase, MapPin, Building2, TrendingUp } from "lucide-react";

export function JobsPage() {

  const { data: analytics, isLoading } = useQuery({
    queryKey: ["admin-job-analytics"],
    queryFn: () => adminApi.getJobAnalytics(),
  });

  if (isLoading) {
    return <LoadingState message="Loading job data..." />;
  }

  if (!analytics) {
    return (
      <EmptyState
        icon={<Briefcase className="h-8 w-8" />}
        title="No job data available"
        description="Job analytics will appear here once data is collected."
      />
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Job Board"
        description="Explore job market trends and opportunities"
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-100 p-2.5 text-blue-700">
                <Briefcase className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{analytics.total_jobs.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">Total Jobs</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2.5 text-emerald-700">
                <MapPin className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{analytics.top_cities.length}</p>
                <p className="text-xs text-muted-foreground">Cities</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-purple-100 p-2.5 text-purple-700">
                <Building2 className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{analytics.top_sectors.length}</p>
                <p className="text-xs text-muted-foreground">Sectors</p>
              </div>
            </div>
          </CardContent>
        </Card>
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
