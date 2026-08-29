import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { StatCard, PageHeader, LoadingState } from "@/components/ui";
import { Bot, MessageSquare, Users, BarChart3 } from "lucide-react";

export function AdminAIPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ["admin-ai-analytics"],
    queryFn: () => adminApi.getAIAnalytics(),
  });

  if (isLoading) {
    return <LoadingState message="Loading AI analytics..." />;
  }

  if (!analytics) return null;

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="AI Assistant Analytics" description="Monitor AI chatbot usage and engagement" />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Conversations"
          value={analytics.total_conversations}
          icon={<Bot className="h-5 w-5" />}
        />
        <StatCard
          title="Total Messages"
          value={analytics.total_messages}
          icon={<MessageSquare className="h-5 w-5" />}
        />
        <StatCard
          title="Active Users"
          value={analytics.active_users}
          icon={<Users className="h-5 w-5" />}
        />
        <StatCard
          title="Avg Messages/Conversation"
          value={analytics.avg_messages_per_conversation.toFixed(1)}
          icon={<BarChart3 className="h-5 w-5" />}
        />
      </div>
    </div>
  );
}
