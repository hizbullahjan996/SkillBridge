import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { StatCard, LoadingState, ErrorState } from "@/components/ui";
import { Users, GraduationCap, Building2, Wrench, BookOpen, Briefcase, Bot, BarChart3 } from "lucide-react";

export function AdminDashboardPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: () => adminApi.getDashboard(),
  });

  if (isLoading) {
    return <LoadingState message="Loading dashboard..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Failed to load dashboard"
        message="You may not have admin access."
        onRetry={refetch}
      />
    );
  }

  const cards = [
    { title: "Total Users", value: data?.users ?? 0, icon: <Users className="h-5 w-5" /> },
    { title: "Total Students", value: data?.students ?? 0, icon: <GraduationCap className="h-5 w-5" /> },
    { title: "Total Jobs", value: data?.jobs ?? 0, icon: <Building2 className="h-5 w-5" /> },
    { title: "Total Skills", value: data?.skills ?? 0, icon: <Wrench className="h-5 w-5" /> },
    { title: "Learning Resources", value: data?.learning_resources ?? 0, icon: <BookOpen className="h-5 w-5" /> },
    { title: "Career Recommendations", value: data?.career_recommendations ?? 0, icon: <Briefcase className="h-5 w-5" /> },
    { title: "AI Conversations", value: data?.ai_conversations ?? 0, icon: <Bot className="h-5 w-5" /> },
    { title: "Learning Progress", value: data?.learning_progress_records ?? 0, icon: <BarChart3 className="h-5 w-5" /> },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold tracking-tight lg:text-3xl">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Platform overview and key metrics</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => (
          <StatCard
            key={card.title}
            title={card.title}
            value={card.value.toLocaleString()}
            icon={card.icon}
          />
        ))}
      </div>
    </div>
  );
}
