import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { Card, CardContent, Input, Badge, PageHeader, LoadingState, EmptyState } from "@/components/ui";
import { Briefcase, Search, GraduationCap, TrendingUp } from "lucide-react";

export function CareersPage() {
  const [search, setSearch] = useState("");

  const { data: careers, isLoading } = useQuery({
    queryKey: ["admin-careers"],
    queryFn: () => adminApi.getCareers(),
  });

  if (isLoading) {
    return <LoadingState message="Loading careers..." />;
  }

  const filteredCareers = careers?.filter(
    (c) => !search || c.career_name.toLowerCase().includes(search.toLowerCase())
  ) ?? [];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Career Explorer"
        description="Discover career paths matched to your skills and profile"
      />

      <div className="relative max-w-md">
        <Input
          placeholder="Search careers..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          icon={<Search className="h-4 w-4" />}
        />
      </div>

      {filteredCareers.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCareers.map((career) => (
            <Card key={career.career_id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-5">
                <div className="flex items-start gap-3">
                  <div className="rounded-lg bg-primary/10 p-2.5 text-primary">
                    <Briefcase className="h-5 w-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-sm">{career.career_name}</h3>
                    <div className="flex flex-wrap gap-2 mt-3">
                      <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                        <GraduationCap className="h-3 w-3" />
                        {career.recommendation_count} recommendations
                      </span>
                      <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                        <TrendingUp className="h-3 w-3" />
                        {career.job_count} jobs
                      </span>
                    </div>
                    <div className="mt-2">
                      <Badge variant="secondary">{career.skill_count} skills</Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Briefcase className="h-8 w-8" />}
          title="No careers found"
          description={search ? "Try a different search term." : "No career data available yet."}
        />
      )}
    </div>
  );
}
