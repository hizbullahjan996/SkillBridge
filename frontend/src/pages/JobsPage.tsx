import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { jobRecommendationsApi, jobsApi, recommendationsApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, Badge, PageHeader, LoadingState, EmptyState, ErrorState } from "@/components/ui";
import { Briefcase, MapPin, Building2, TrendingUp, Zap, DollarSign, Star } from "lucide-react";

export function JobsPage() {
  const queryClient = useQueryClient();

  const { data: latestRec } = useQuery({
    queryKey: ["latest-recommendation"],
    queryFn: () => recommendationsApi.getLatest(),
  });

  const hasPredictions = latestRec && latestRec.recommendations.length > 0;

  const { data: jobData, isLoading, error, refetch } = useQuery({
    queryKey: ["job-recommendations"],
    queryFn: () => jobRecommendationsApi.getRecommended({ page_size: "20" }),
    enabled: hasPredictions,
  });

  const { data: analytics } = useQuery({
    queryKey: ["job-analytics"],
    queryFn: () => jobsApi.getAnalytics(),
  });

  const predictMutation = useMutation({
    mutationFn: () => recommendationsApi.predictCareers(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["latest-recommendation"] });
      queryClient.invalidateQueries({ queryKey: ["job-recommendations"] });
    },
  });

  if (!hasPredictions && !isLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <PageHeader
          title="Job Board"
          description="Explore job market trends and opportunities"
        />
        <EmptyState
          icon={<Briefcase className="h-8 w-8" />}
          title="No job recommendations yet"
          description="Generate career predictions first to get personalized job recommendations."
          action={
            <button
              onClick={() => predictMutation.mutate()}
              disabled={predictMutation.isPending}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {predictMutation.isPending ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                  Generating...
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4" />
                  Get Career Predictions
                </>
              )}
            </button>
          }
        />

        {/* Show market analytics anyway */}
        {analytics && (
          <>
            <h3 className="text-lg font-semibold">Market Overview</h3>
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
          </>
        )}
      </div>
    );
  }

  if (isLoading) {
    return <LoadingState message="Loading job recommendations..." />;
  }

  if (error) {
    return (
      <div className="space-y-6 animate-fade-in">
        <PageHeader
          title="Job Board"
          description="Explore job market trends and opportunities"
        />
        <ErrorState
          title="Failed to load job recommendations"
          message={error instanceof Error ? error.message : "Unable to load jobs."}
          onRetry={refetch}
        />
      </div>
    );
  }

  const jobs = jobData?.items ?? [];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Job Board"
        description={`${jobData?.total ?? 0} personalized job recommendations`}
      />

      {/* Summary Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-100 p-2.5 text-blue-700">
                <Briefcase className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{jobData?.total ?? 0}</p>
                <p className="text-xs text-muted-foreground">Matching Jobs</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2.5 text-emerald-700">
                <Star className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {jobs.filter((j) => j.in_top_career).length}
                </p>
                <p className="text-xs text-muted-foreground">Top Career Matches</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-purple-100 p-2.5 text-purple-700">
                <TrendingUp className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {jobs.length > 0 ? Math.round(jobs.reduce((sum, j) => sum + j.match_score, 0) / jobs.length) : 0}%
                </p>
                <p className="text-xs text-muted-foreground">Avg Match Score</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Job Listings */}
      {jobs.length > 0 ? (
        <div className="space-y-3">
          {jobs.map((job) => (
            <Card key={job.job_id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-sm">{job.job_title}</h3>
                      {job.in_top_career && (
                        <Badge variant="default" className="text-[10px] bg-emerald-600">
                          Top Match
                        </Badge>
                      )}
                    </div>
                    <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Building2 className="h-3 w-3" />
                        {job.company}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {job.city}
                      </span>
                      {job.sector && (
                        <Badge variant="outline" className="text-[10px]">{job.sector}</Badge>
                      )}
                      {job.job_type && (
                        <Badge variant="secondary" className="text-[10px]">{job.job_type}</Badge>
                      )}
                    </div>
                    {(job.salary_min || job.salary_max) && (
                      <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                        <DollarSign className="h-3 w-3" />
                        {job.salary_min && job.salary_max
                          ? `${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}`
                          : job.salary_average
                          ? `Avg: ${job.salary_average.toLocaleString()}`
                          : "Salary not specified"}
                      </div>
                    )}
                  </div>

                  <div className="text-right flex-shrink-0">
                    <div className="text-lg font-bold text-primary">
                      {Math.round(job.match_score)}%
                    </div>
                    <div className="text-[10px] text-muted-foreground">match</div>
                    <div className="mt-1 text-[10px] text-muted-foreground">
                      {job.matched_skills}/{job.total_required_skills} skills
                    </div>
                  </div>
                </div>

                {/* Score bars */}
                <div className="grid grid-cols-4 gap-2 mt-3">
                  <ScoreBar label="Career" score={job.career_score} />
                  <ScoreBar label="Skills" score={job.skill_match_percentage} />
                  <ScoreBar label="Education" score={job.education_score} />
                  <ScoreBar label="Experience" score={job.experience_score} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Briefcase className="h-8 w-8" />}
          title="No matching jobs found"
          description="Try adjusting your filters or update your profile for better matches."
        />
      )}

      {/* Market Analytics */}
      {analytics && (
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
      )}
    </div>
  );
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  const color =
    score >= 70 ? "bg-emerald-500" :
    score >= 40 ? "bg-blue-500" : "bg-gray-300";
  return (
    <div>
      <div className="flex items-center justify-between text-[10px] text-muted-foreground mb-1">
        <span>{label}</span>
        <span>{Math.round(score)}%</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-1.5">
        <div className={`${color} h-1.5 rounded-full`} style={{ width: `${Math.min(100, score)}%` }} />
      </div>
    </div>
  );
}
