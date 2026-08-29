import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { profileApi, ProfileUpdate } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Select, PageHeader, LoadingState } from "@/components/ui";
import { User, ArrowLeft, Save, Loader2 } from "lucide-react";

const GENDERS = ["Male", "Female", "Other"];
const UNIVERSITY_YEARS = ["Freshman", "Sophomore", "Junior", "Senior"];
const MAJORS = [
  "Computer Science",
  "Software Engineering",
  "Data Science",
  "Artificial Intelligence",
  "Information Technology",
  "Cybersecurity",
  "Electrical Engineering",
  "Business Analytics",
];
const INTEREST_DOMAINS = [
  "Software Development",
  "Web Development",
  "Data & AI",
  "Cloud & Infrastructure",
  "Cybersecurity",
  "Systems & Networking",
  "Business & Analytics",
];

export function EditProfilePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => profileApi.getMyProfile(),
  });

  const mutation = useMutation({
    mutationFn: (data: ProfileUpdate) => profileApi.updateMyProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      queryClient.invalidateQueries({ queryKey: ["profile-completion"] });
      navigate("/profile");
    },
  });

  const [formData, setFormData] = useState<ProfileUpdate>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  const handleChange = (field: keyof ProfileUpdate, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value || undefined }));
  };

  if (isLoading) {
    return <LoadingState message="Loading profile..." />;
  }

  const sections = [
    {
      title: "Personal Information",
      icon: <User className="h-4 w-4" />,
      children: (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium mb-1.5">Full Name</label>
            <Input
              type="text"
              defaultValue={profile?.full_name}
              onChange={(e) => handleChange("full_name", e.target.value)}
              placeholder="Enter your full name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Age</label>
            <Input
              type="number"
              defaultValue={profile?.age ?? ""}
              onChange={(e) => handleChange("age", e.target.value ? parseInt(e.target.value) : 0)}
              min={15}
              max={50}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Gender</label>
            <Select
              defaultValue={profile?.gender ?? ""}
              onChange={(e) => handleChange("gender", e.target.value)}
              options={GENDERS.map((g) => ({ value: g, label: g }))}
              placeholder="Select gender"
            />
          </div>
        </div>
      ),
    },
    {
      title: "Academic Information",
      icon: null,
      children: (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">University Year</label>
            <Select
              defaultValue={profile?.university_year ?? ""}
              onChange={(e) => handleChange("university_year", e.target.value)}
              options={UNIVERSITY_YEARS.map((y) => ({ value: y, label: y }))}
              placeholder="Select year"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Major</label>
            <Select
              defaultValue={profile?.major ?? ""}
              onChange={(e) => handleChange("major", e.target.value)}
              options={MAJORS.map((m) => ({ value: m, label: m }))}
              placeholder="Select major"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">CGPA</label>
            <Input
              type="number"
              defaultValue={profile?.cgpa ?? ""}
              onChange={(e) => handleChange("cgpa", e.target.value ? parseFloat(e.target.value) : 0)}
              min={0}
              max={4}
              step={0.01}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Attendance %</label>
            <Input
              type="number"
              defaultValue={profile?.attendance_percentage ?? ""}
              onChange={(e) => handleChange("attendance_percentage", e.target.value ? parseFloat(e.target.value) : 0)}
              min={0}
              max={100}
            />
          </div>
        </div>
      ),
    },
    {
      title: "Experience",
      icon: null,
      children: (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Study Hours/Week</label>
            <Input
              type="number"
              defaultValue={profile?.study_hours_per_week ?? ""}
              onChange={(e) => handleChange("study_hours_per_week", e.target.value ? parseInt(e.target.value) : 0)}
              min={0}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Projects Completed</label>
            <Input
              type="number"
              defaultValue={profile?.projects_completed ?? ""}
              onChange={(e) => handleChange("projects_completed", e.target.value ? parseInt(e.target.value) : 0)}
              min={0}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Certifications</label>
            <Input
              type="number"
              defaultValue={profile?.certifications_count ?? ""}
              onChange={(e) => handleChange("certifications_count", e.target.value ? parseInt(e.target.value) : 0)}
              min={0}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Internships</label>
            <Input
              type="number"
              defaultValue={profile?.internships ?? ""}
              onChange={(e) => handleChange("internships", e.target.value ? parseInt(e.target.value) : 0)}
              min={0}
            />
          </div>
        </div>
      ),
    },
    {
      title: "Skills & Interests",
      icon: null,
      children: (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Interest Domain</label>
            <Select
              defaultValue={profile?.interest_domain ?? ""}
              onChange={(e) => handleChange("interest_domain", e.target.value)}
              options={INTEREST_DOMAINS.map((d) => ({ value: d, label: d }))}
              placeholder="Select domain"
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Communication (0-10)</label>
              <Input
                type="number"
                defaultValue={profile?.communication_skills ?? ""}
                onChange={(e) => handleChange("communication_skills", e.target.value ? parseInt(e.target.value) : 0)}
                min={0}
                max={10}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Teamwork (0-10)</label>
              <Input
                type="number"
                defaultValue={profile?.teamwork ?? ""}
                onChange={(e) => handleChange("teamwork", e.target.value ? parseInt(e.target.value) : 0)}
                min={0}
                max={10}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Problem Solving (0-10)</label>
              <Input
                type="number"
                defaultValue={profile?.problem_solving ?? ""}
                onChange={(e) => handleChange("problem_solving", e.target.value ? parseInt(e.target.value) : 0)}
                min={0}
                max={10}
              />
            </div>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <PageHeader
        title="Edit Profile"
        description="Update your academic and professional information"
        actions={
          <Button variant="ghost" size="sm" onClick={() => navigate("/profile")}>
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
        }
      />

      <form onSubmit={handleSubmit} className="space-y-6">
        {sections.map((section) => (
          <Card key={section.title}>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                {section.icon}
                {section.title}
              </CardTitle>
            </CardHeader>
            <CardContent>{section.children}</CardContent>
          </Card>
        ))}

        {mutation.isError && (
          <div className="p-4 bg-destructive/10 text-destructive rounded-lg text-sm">
            {mutation.error.message}
          </div>
        )}

        <div className="flex gap-3">
          <Button
            type="submit"
            disabled={mutation.isPending}
            className="flex-1"
          >
            {mutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                Save Changes
              </>
            )}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate("/profile")}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
