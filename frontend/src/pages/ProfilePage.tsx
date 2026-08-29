import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { profileApi, skillsApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, StatCard, SkillChip, PageHeader, LoadingState, EmptyState } from "@/components/ui";
import { User, Award, Target, ArrowRight, Sparkles, BarChart3 } from "lucide-react";

export function ProfilePage() {
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => profileApi.getMyProfile(),
  });

  const { data: completion } = useQuery({
    queryKey: ["profile-completion"],
    queryFn: () => profileApi.getProfileCompletion(),
  });

  const { data: skills } = useQuery({
    queryKey: ["my-skills"],
    queryFn: () => skillsApi.getMySkills(),
  });

  if (profileLoading) {
    return <LoadingState message="Loading your profile..." />;
  }

  if (!profile) {
    return (
      <EmptyState
        icon={<User className="h-8 w-8" />}
        title="Profile Not Found"
        description="Complete your profile to get personalized career recommendations and skill analysis."
        action={
          <Link
            to="/profile/edit"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Complete Profile
            <ArrowRight className="h-4 w-4" />
          </Link>
        }
      />
    );
  }

  const profileSections = [
    {
      title: "Personal Information",
      items: [
        { label: "Full Name", value: profile.full_name },
        { label: "Age", value: profile.age || "Not set" },
        { label: "Gender", value: profile.gender || "Not set" },
      ],
    },
    {
      title: "Academic Information",
      items: [
        { label: "University Year", value: profile.university_year || "Not set" },
        { label: "Major", value: profile.major || "Not set" },
        { label: "CGPA", value: profile.cgpa || "Not set" },
        { label: "Attendance", value: profile.attendance_percentage ? `${profile.attendance_percentage}%` : "Not set" },
      ],
    },
    {
      title: "Experience",
      items: [
        { label: "Study Hours/Week", value: profile.study_hours_per_week || "Not set" },
        { label: "Projects Completed", value: profile.projects_completed || "Not set" },
        { label: "Certifications", value: profile.certifications_count || "Not set" },
        { label: "Internships", value: profile.internships || "Not set" },
      ],
    },
    {
      title: "Skills & Interests",
      items: [
        { label: "Interest Domain", value: profile.interest_domain || "Not set" },
        { label: "Communication", value: profile.communication_skills ? `${profile.communication_skills}/10` : "Not set" },
        { label: "Teamwork", value: profile.teamwork ? `${profile.teamwork}/10` : "Not set" },
        { label: "Problem Solving", value: profile.problem_solving ? `${profile.problem_solving}/10` : "Not set" },
      ],
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="My Profile"
        description="Your academic and professional profile"
        actions={
          <Link
            to="/profile/edit"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            <User className="h-4 w-4" />
            Edit Profile
          </Link>
        }
      />

      {/* Profile Completion */}
      {completion && (
        <Card className="overflow-hidden">
          <div className="bg-gradient-to-r from-primary/10 to-primary/5 p-6">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Target className="h-5 w-5 text-primary" />
                <span className="font-medium">Profile Completion</span>
              </div>
              <span className="text-2xl font-bold text-primary">{completion.percentage}%</span>
            </div>
            <div className="w-full bg-background/50 rounded-full h-2.5">
              <div
                className="bg-primary h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${completion.percentage}%` }}
              />
            </div>
            {completion.missing_fields.length > 0 && (
              <p className="mt-2 text-sm text-muted-foreground">
                Missing: {completion.missing_fields.join(", ")}
              </p>
            )}
          </div>
        </Card>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Skills Added"
          value={skills?.length ?? 0}
          icon={<BarChart3 className="h-5 w-5" />}
        />
        <StatCard
          title="Profile Completion"
          value={`${completion?.percentage ?? 0}%`}
          icon={<Target className="h-5 w-5" />}
        />
        <StatCard
          title="Projects"
          value={profile.projects_completed ?? 0}
          icon={<Award className="h-5 w-5" />}
        />
        <StatCard
          title="Interest Domain"
          value={profile.interest_domain || "Not set"}
          icon={<Sparkles className="h-5 w-5" />}
        />
      </div>

      {/* Profile Sections */}
      <div className="grid gap-6 md:grid-cols-2">
        {profileSections.map((section) => (
          <Card key={section.title}>
            <CardHeader>
              <CardTitle className="text-base">{section.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="space-y-3">
                {section.items.map((item) => (
                  <div key={item.label} className="flex items-center justify-between">
                    <dt className="text-sm text-muted-foreground">{item.label}</dt>
                    <dd className="text-sm font-medium">{item.value}</dd>
                  </div>
                ))}
              </dl>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Skills */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Technical Skills</CardTitle>
          <Link
            to="/skills"
            className="text-sm text-primary hover:underline flex items-center gap-1"
          >
            Manage Skills
            <ArrowRight className="h-3 w-3" />
          </Link>
        </CardHeader>
        <CardContent>
          {skills && skills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {skills.map((ss) => (
                <SkillChip
                  key={ss.id}
                  name={ss.skill?.name ?? "Unknown"}
                  proficiency={ss.proficiency}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-6">
              <p className="text-sm text-muted-foreground mb-3">
                No skills added yet.
              </p>
              <Link
                to="/skills"
                className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
              >
                Add your first skill
                <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
