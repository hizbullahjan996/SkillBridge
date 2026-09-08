import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { recommendationsApi, skillsApi } from "@/lib/api";
import { Card, CardContent, Input, PageHeader, LoadingState, EmptyState, ErrorState } from "@/components/ui";
import { Briefcase, Search, GraduationCap, TrendingUp, Brain, Zap, Target } from "lucide-react";

export function CareersPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [expandedCareer, setExpandedCareer] = useState<number | null>(null);

  const { data: latestRec, isLoading: recLoading, error: recError, refetch: refetchRec } = useQuery({
    queryKey: ["latest-recommendation"],
    queryFn: () => recommendationsApi.getLatest(),
  });

  const { data: allCareers, isLoading: careersLoading } = useQuery({
    queryKey: ["careers"],
    queryFn: () => skillsApi.getCareers(),
  });

  const predictMutation = useMutation({
    mutationFn: () => recommendationsApi.predictCareers(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["latest-recommendation"] });
    },
  });

  const careerIdToData = new Map(
    (allCareers ?? []).map((c) => [c.career_id, c])
  );

  const predictions = latestRec?.recommendations ?? [];

  const enrichedPredictions = predictions.map((pred) => {
    const careerData = Array.from(careerIdToData.values()).find(
      (c) => c.career_name === pred.career
    );
    return { ...pred, careerData };
  });

  const filteredPredictions = enrichedPredictions.filter(
    (p) => !search || p.career.toLowerCase().includes(search.toLowerCase())
  );

  const isLoading = recLoading || careersLoading;

  if (isLoading) {
    return <LoadingState message="Loading career data..." />;
  }

  if (recError) {
    return (
      <div className="space-y-6 animate-fade-in">
        <PageHeader
          title="Career Explorer"
          description="Discover career paths matched to your skills and profile"
        />
        <ErrorState
          title="Failed to load career predictions"
          message={recError instanceof Error ? recError.message : "Unable to load career data."}
          onRetry={refetchRec}
        />
      </div>
    );
  }

  if (predictions.length === 0) {
    return (
      <div className="space-y-6 animate-fade-in">
        <PageHeader
          title="Career Explorer"
          description="Discover career paths matched to your skills and profile"
        />
        <EmptyState
          icon={<Brain className="h-8 w-8" />}
          title="No career predictions yet"
          description="Generate AI-powered career recommendations based on your profile and skills."
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
                  Get AI Recommendations
                </>
              )}
            </button>
          }
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Career Explorer"
        description={`Your AI-powered career recommendations (${predictions.length} matches)`}
        actions={
          <button
            onClick={() => predictMutation.mutate()}
            disabled={predictMutation.isPending}
            className="inline-flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent transition-colors disabled:opacity-50"
          >
            {predictMutation.isPending ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            ) : (
              <Zap className="h-4 w-4" />
            )}
            Refresh
          </button>
        }
      />

      <div className="relative max-w-md">
        <Input
          placeholder="Search careers..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          icon={<Search className="h-4 w-4" />}
        />
      </div>

      {filteredPredictions.length > 0 ? (
        <div className="space-y-4">
          {filteredPredictions.map((pred) => (
            <CareerCard
              key={pred.rank}
              rank={pred.rank}
              career={pred.career}
              probability={pred.probability}
              description={pred.careerData?.description}
              jobCount={pred.careerData?.job_count ?? 0}
              skillCount={pred.careerData?.skill_count ?? 0}
              isExpanded={expandedCareer === pred.rank}
              onToggle={() => setExpandedCareer(expandedCareer === pred.rank ? null : pred.rank)}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Search className="h-8 w-8" />}
          title="No careers match your search"
          description="Try a different search term."
        />
      )}
    </div>
  );
}

function CareerCard({
  rank,
  career,
  probability,
  description,
  jobCount,
  skillCount,
}: {
  rank: number;
  career: string;
  probability: number;
  description: string | null | undefined;
  jobCount: number;
  skillCount: number;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const matchColor =
    probability >= 0.4 ? "text-emerald-600" :
    probability >= 0.2 ? "text-blue-600" : "text-muted-foreground";

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-5">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-primary/10 p-2.5 text-primary">
            <Briefcase className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-sm">{career}</h3>
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary/10 text-[10px] font-bold text-primary">
                  #{rank}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-lg font-bold ${matchColor}`}>
                  {Math.round(probability * 100)}%
                </span>
                <span className="text-xs text-muted-foreground">match</span>
              </div>
            </div>

            {description && (
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{description}</p>
            )}

            <div className="flex flex-wrap gap-3 mt-3">
              <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                <TrendingUp className="h-3 w-3" />
                {jobCount} jobs
              </span>
              <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                <GraduationCap className="h-3 w-3" />
                {skillCount} skills required
              </span>
            </div>

            <div className="mt-3 flex items-center gap-3">
              <Link
                to={`/skill-gap/${encodeURIComponent(career)}`}
                className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
              >
                <Target className="h-3 w-3" />
                View Skill Gap
              </Link>
              <Link
                to="/jobs"
                className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
              >
                <Briefcase className="h-3 w-3" />
                View Matching Jobs
              </Link>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
