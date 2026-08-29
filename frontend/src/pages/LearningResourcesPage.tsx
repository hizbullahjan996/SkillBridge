import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { learningResourcesApi, LearningResource } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Select, Badge, PageHeader, LoadingState, EmptyState, Pagination } from "@/components/ui";
import { Search, BookOpen, ExternalLink, CheckCircle2, PlayCircle, Clock, Sparkles } from "lucide-react";

export function LearningResourcesPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState("");
  const [selectedDifficulty, setSelectedDifficulty] = useState("");
  const [selectedFree, setSelectedFree] = useState("");
  const [page, setPage] = useState(1);

  const params: Record<string, string> = { page: String(page), page_size: "12" };
  if (search) params.search = search;
  if (selectedType) params.resource_type = selectedType;
  if (selectedDifficulty) params.difficulty = selectedDifficulty;
  if (selectedFree) params.is_free = selectedFree;

  const { data, isLoading } = useQuery({
    queryKey: ["learning-resources", params],
    queryFn: () => learningResourcesApi.getResources(params),
  });

  const { data: recommended } = useQuery({
    queryKey: ["recommended-resources"],
    queryFn: () => learningResourcesApi.getRecommended(),
  });

  const { data: progressData } = useQuery({
    queryKey: ["learning-progress"],
    queryFn: () => learningResourcesApi.getProgress(),
  });

  const progressMap = new Map(
    progressData?.records?.map((r) => [r.resource_id, r.status]) ?? []
  );

  const startMutation = useMutation({
    mutationFn: (resourceId: number) => learningResourcesApi.startResource(resourceId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["learning-progress"] }),
  });

  const updateMutation = useMutation({
    mutationFn: ({ resourceId, status }: { resourceId: number; status: string }) =>
      learningResourcesApi.updateProgress(resourceId, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["learning-progress"] }),
  });

  const getProgressButton = (resource: LearningResource) => {
    const status = progressMap.get(resource.id);
    if (status === "completed") {
      return (
        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-600">
          <CheckCircle2 className="h-3.5 w-3.5" />
          Completed
        </span>
      );
    }
    if (status === "in_progress") {
      return (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => updateMutation.mutate({ resourceId: resource.id, status: "completed" })}
          className="text-amber-600 hover:text-amber-700 hover:bg-amber-50"
        >
          <Clock className="h-3.5 w-3.5" />
          Mark Complete
        </Button>
      );
    }
    return (
      <Button
        variant="ghost"
        size="sm"
        onClick={() => startMutation.mutate(resource.id)}
        disabled={startMutation.isPending}
        className="text-primary hover:text-primary hover:bg-primary/10"
      >
        <PlayCircle className="h-3.5 w-3.5" />
        Start
      </Button>
    );
  };

  if (isLoading) {
    return <LoadingState message="Loading resources..." />;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Learning Resources"
        description="Discover courses, tutorials, and materials to build your skills"
      />

      {/* Recommended Section */}
      {recommended && recommended.resources.length > 0 && (
        <Card className="overflow-hidden border-primary/20">
          <div className="bg-gradient-to-r from-primary/5 to-transparent">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                Recommended for You
                {recommended.career_name && (
                  <Badge variant="info" className="ml-2">{recommended.career_name}</Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {recommended.resources.slice(0, 3).map((rec) => (
                  <ResourceCard
                    key={rec.resource.id}
                    resource={rec.resource}
                    progressButton={getProgressButton(rec.resource)}
                    highlight={rec.matched_skill}
                    priority={rec.skill_priority}
                  />
                ))}
              </div>
            </CardContent>
          </div>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <Input
                placeholder="Search resources..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                icon={<Search className="h-4 w-4" />}
              />
            </div>
            <Select
              value={selectedType}
              onChange={(e) => { setSelectedType(e.target.value); setPage(1); }}
              options={[
                { value: "course", label: "Course" },
                { value: "documentation", label: "Documentation" },
                { value: "tutorial", label: "Tutorial" },
                { value: "video", label: "Video" },
                { value: "book", label: "Book" },
              ]}
              placeholder="All Types"
            />
            <Select
              value={selectedDifficulty}
              onChange={(e) => { setSelectedDifficulty(e.target.value); setPage(1); }}
              options={[
                { value: "beginner", label: "Beginner" },
                { value: "intermediate", label: "Intermediate" },
                { value: "advanced", label: "Advanced" },
              ]}
              placeholder="All Levels"
            />
            <Select
              value={selectedFree}
              onChange={(e) => { setSelectedFree(e.target.value); setPage(1); }}
              options={[
                { value: "true", label: "Free Only" },
                { value: "false", label: "Paid" },
              ]}
              placeholder="All"
            />
          </div>
        </CardContent>
      </Card>

      {/* Resources Grid */}
      {data?.items && data.items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.items.map((resource) => (
            <ResourceCard
              key={resource.id}
              resource={resource}
              progressButton={getProgressButton(resource)}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<BookOpen className="h-8 w-8" />}
          title="No resources found"
          description="Try adjusting your filters or search terms."
        />
      )}

      <Pagination page={page} totalPages={data?.pages ?? 1} onPageChange={setPage} />
    </div>
  );
}

function ResourceCard({
  resource,
  progressButton,
  highlight,
  priority,
}: {
  resource: LearningResource;
  progressButton: React.ReactNode;
  highlight?: string;
  priority?: string;
}) {
  const typeColors: Record<string, string> = {
    course: "bg-blue-100 text-blue-700",
    documentation: "bg-purple-100 text-purple-700",
    tutorial: "bg-emerald-100 text-emerald-700",
    video: "bg-amber-100 text-amber-700",
    book: "bg-rose-100 text-rose-700",
  };

  return (
    <Card className="flex flex-col h-full">
      <CardContent className="flex-1 p-5 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-sm leading-tight line-clamp-2">{resource.title}</h3>
          {priority && (
            <Badge
              variant={
                priority === "High" ? "destructive" :
                priority === "Medium" ? "warning" : "secondary"
              }
              className="flex-shrink-0"
            >
              {priority}
            </Badge>
          )}
        </div>
        <p className="text-xs text-muted-foreground">{resource.provider}</p>
        {resource.description && (
          <p className="text-xs text-muted-foreground line-clamp-2">{resource.description}</p>
        )}
        <div className="flex flex-wrap gap-1.5">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${typeColors[resource.resource_type] ?? "bg-gray-100 text-gray-700"}`}>
            {resource.resource_type}
          </span>
          {resource.difficulty && (
            <Badge variant="secondary">{resource.difficulty}</Badge>
          )}
          {resource.is_free && (
            <Badge variant="success">Free</Badge>
          )}
          {highlight && (
            <Badge variant="info">{highlight}</Badge>
          )}
        </div>
        {resource.skills && resource.skills.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {resource.skills.slice(0, 3).map((skill) => (
              <span key={skill.id} className="text-xs text-muted-foreground">
                {skill.name}
              </span>
            ))}
            {resource.skills.length > 3 && (
              <span className="text-xs text-muted-foreground">+{resource.skills.length - 3}</span>
            )}
          </div>
        )}
      </CardContent>
      <div className="flex items-center justify-between p-4 pt-0 border-t mt-auto">
        {progressButton}
        {resource.url ? (
          <a
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            Open
            <ExternalLink className="h-3 w-3" />
          </a>
        ) : (
          <span className="text-xs text-muted-foreground">No URL</span>
        )}
      </div>
    </Card>
  );
}
