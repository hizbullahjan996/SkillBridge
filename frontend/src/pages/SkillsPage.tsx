import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { skillsApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Select, SkillChip, PageHeader, LoadingState, EmptyState } from "@/components/ui";
import { Search, Plus, X, Filter } from "lucide-react";

export function SkillsPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");

  const { data: allSkills, isLoading: skillsLoading } = useQuery({
    queryKey: ["skills", selectedCategory, search],
    queryFn: () =>
      skillsApi.getSkills({
        ...(selectedCategory && { category: selectedCategory }),
        ...(search && { search }),
      }),
  });

  const { data: mySkills, isLoading: mySkillsLoading } = useQuery({
    queryKey: ["my-skills"],
    queryFn: () => skillsApi.getMySkills(),
  });

  const addMutation = useMutation({
    mutationFn: (skillId: number) =>
      skillsApi.addSkill({ skill_id: skillId, proficiency: 5 }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-skills"] });
    },
  });

  const removeMutation = useMutation({
    mutationFn: (skillId: number) => skillsApi.removeSkill(skillId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-skills"] });
    },
  });

  const mySkillIds = new Set(mySkills?.map((s) => s.skill_id) ?? []);

  if (skillsLoading || mySkillsLoading) {
    return <LoadingState message="Loading skills..." />;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Skills Management"
        description="Build your technical skill profile"
        actions={
          <Link
            to="/profile"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Back to Profile
          </Link>
        }
      />

      {/* My Skills */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Filter className="h-4 w-4 text-primary" />
            My Skills ({mySkills?.length ?? 0})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {mySkills && mySkills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {mySkills.map((ss) => (
                <SkillChip
                  key={ss.id}
                  name={ss.skill?.name ?? "Unknown"}
                  proficiency={ss.proficiency}
                  onRemove={() => removeMutation.mutate(ss.skill_id)}
                />
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground text-center py-4">
              No skills added yet. Browse and add skills below.
            </p>
          )}
        </CardContent>
      </Card>

      {/* Browse Skills */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Browse Skills</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <Input
                placeholder="Search skills..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                icon={<Search className="h-4 w-4" />}
              />
            </div>
            <Select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              options={[
                { value: "technical", label: "Technical" },
                { value: "soft", label: "Soft Skills" },
              ]}
              placeholder="All Categories"
            />
          </div>

          {allSkills && allSkills.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {allSkills.map((skill) => {
                const isSelected = mySkillIds.has(skill.id);
                return (
                  <div
                    key={skill.id}
                    className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                  >
                    <div className="min-w-0">
                      <div className="font-medium text-sm truncate">{skill.name}</div>
                      <div className="text-xs text-muted-foreground capitalize">{skill.category}</div>
                    </div>
                    {isSelected ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeMutation.mutate(skill.id)}
                        className="text-destructive hover:text-destructive hover:bg-destructive/10 flex-shrink-0"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    ) : (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => addMutation.mutate(skill.id)}
                        disabled={addMutation.isPending}
                        className="text-primary hover:text-primary hover:bg-primary/10 flex-shrink-0"
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState
              icon={<Search className="h-6 w-6" />}
              title="No skills found"
              description="Try adjusting your search or filters."
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
