import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "react-router-dom";
import { skillGapApi, skillsApi, recommendationsApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, Badge, PageHeader, LoadingState, EmptyState, ErrorState } from "@/components/ui";
import { Target, CheckCircle, XCircle, ArrowRight, TrendingUp, BarChart3 } from "lucide-react";

export function SkillGapPage() {
  const { careerName } = useParams<{ careerName: string }>();
  const decodedCareerName = careerName ? decodeURIComponent(careerName) : "";

  const { data: latestRecs, isLoading: recommendationsLoading } = useQuery({
    queryKey: ["latest-recommendation"],
    queryFn: () => recommendationsApi.getLatest(),
    enabled: !decodedCareerName,
  });

  const fallbackCareer = latestRecs?.recommendations?.[0]?.career ?? "";
  const effectiveCareerName = decodedCareerName || fallbackCareer;

  const { data: allCareers, isLoading: careersLoading } = useQuery({
    queryKey: ["careers"],
    queryFn: () => skillsApi.getCareers(),
  });

  const careerMatch = allCareers?.find(
    (c) => c.career_name.toLowerCase() === effectiveCareerName.toLowerCase()
  );

  const careerId = careerMatch?.career_id;

  const { data: skillGap, isLoading: gapLoading, error: gapError, refetch } = useQuery({
    queryKey: ["career-skill-gap", careerId],
    queryFn: () => skillGapApi.getCareerGap(careerId!),
    enabled: !!careerId,
  });

  const isLoading = careersLoading || gapLoading || (careerName ? false : recommendationsLoading);

  if (isLoading) {
    return <LoadingState message="Loading skill gap analysis..." />;
  }

  if (!careerMatch) {
    return (
      <div className="space-y-6 animate-fade-in">
        <PageHeader
          title="Skill Gap Analysis"
          description="Compare your skills against career requirements"
        />
        <EmptyState
          icon={<Target className="h-8 w-8" />}
          title="Career not found"
          description={`Could not find career "${effectiveCareerName}". Please go back to Career Explorer.`}
          action={
            <Link
              to="/careers"
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <ArrowRight className="h-4 w-4" />
              Back to Career Explorer
            </Link>
          }
        />
      </div>
    );
  }

  if (gapError) {
    return (
      <div className="space-y-6 animate-fade-in">
        <PageHeader
          title={`Skill Gap: ${decodedCareerName}`}
          description="Compare your skills against career requirements"
        />
        <ErrorState
          title="Failed to load skill gap"
          message={gapError instanceof Error ? gapError.message : "Unable to compute skill gap."}
          onRetry={refetch}
        />
      </div>
    );
  }

  if (!skillGap) {
    return (
      <div className="space-y-6 animate-fade-in">
        <PageHeader
          title={`Skill Gap: ${decodedCareerName}`}
          description="Compare your skills against career requirements"
        />
        <EmptyState
          icon={<Target className="h-8 w-8" />}
          title="No skill gap data"
          description="Unable to compute skill gap for this career."
        />
      </div>
    );
  }

  const { skill_gap, matched_skills, missing_skills } = skillGap;

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title={`Skill Gap: ${decodedCareerName}`}
        description="Compare your skills against career requirements"
        actions={
          <Link
            to="/careers"
            className="inline-flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent transition-colors"
          >
            <ArrowRight className="h-4 w-4" />
            Back to Careers
          </Link>
        }
      />

      {/* Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-100 p-2.5 text-blue-700">
                <Target className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{skill_gap.total_required}</p>
                <p className="text-xs text-muted-foreground">Total Required</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2.5 text-emerald-700">
                <CheckCircle className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{skill_gap.matched_count}</p>
                <p className="text-xs text-muted-foreground">Matched</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-red-100 p-2.5 text-red-700">
                <XCircle className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{skill_gap.missing_count}</p>
                <p className="text-xs text-muted-foreground">Missing</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-purple-100 p-2.5 text-purple-700">
                <BarChart3 className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{skill_gap.match_percentage}%</p>
                <p className="text-xs text-muted-foreground">Match Score</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Match Progress */}
      <Card className="overflow-hidden">
        <div className="bg-gradient-to-r from-emerald-500/10 to-primary/10 p-6">
          <div className="flex items-center justify-between mb-3">
            <span className="font-medium">Skill Match Progress</span>
            <span className="text-2xl font-bold text-primary">{skill_gap.match_percentage}%</span>
          </div>
          <div className="w-full bg-background/50 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-emerald-500 to-primary h-3 rounded-full transition-all duration-500"
              style={{ width: `${skill_gap.match_percentage}%` }}
            />
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Matched Skills */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-emerald-600" />
              Your Matching Skills ({matched_skills.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {matched_skills.length > 0 ? (
              <div className="space-y-2">
                {matched_skills.map((skill) => (
                  <div key={skill.id} className="flex items-center justify-between rounded-lg bg-emerald-50 px-3 py-2">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-emerald-600" />
                      <span className="text-sm font-medium">{skill.name}</span>
                    </div>
                    <Badge variant="outline" className="text-[10px] border-emerald-200 text-emerald-700">
                      {skill.category}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                No matching skills found. Add skills to your profile to improve your match.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Missing Skills */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-600" />
              Missing Skills ({missing_skills.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {missing_skills.length > 0 ? (
              <div className="space-y-2">
                {missing_skills.map((skill) => (
                  <div key={skill.skill_id} className="flex items-center justify-between rounded-lg bg-red-50 px-3 py-2">
                    <div className="flex items-center gap-2">
                      <XCircle className="h-4 w-4 text-red-600" />
                      <span className="text-sm font-medium">{skill.skill_name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={skill.priority === "High" ? "default" : "secondary"}
                        className={`text-[10px] ${
                          skill.priority === "High"
                            ? "bg-red-600"
                            : skill.priority === "Medium"
                            ? "bg-amber-500"
                            : ""
                        }`}
                      >
                        {skill.priority}
                      </Badge>
                      <span className="text-[10px] text-muted-foreground">
                        {skill.demand_count} jobs
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                You have all the required skills for this career!
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Learning Recommendations CTA */}
      {missing_skills.length > 0 && (
        <Card className="overflow-hidden">
          <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold">Ready to bridge your skill gap?</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  We found learning resources for {missing_skills.length} missing skill(s).
                </p>
              </div>
              <Link
                to="/learning-resources"
                className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                <TrendingUp className="h-4 w-4" />
                View Learning Resources
              </Link>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
