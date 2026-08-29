import { useState, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { assistantApi, AssistantMessage } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, Button, Textarea, PageHeader } from "@/components/ui";
import { Send, MessageSquare, Plus, Bot, User, HelpCircle } from "lucide-react";

const SUGGESTED_QUESTIONS = [
  "What skills should I learn first?",
  "Which career matches my profile?",
  "Why am I missing these skills?",
  "How can I prepare for my recommended jobs?",
];

export function AssistantPage() {
  const queryClient = useQueryClient();
  const [message, setMessage] = useState("");
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: conversations } = useQuery({
    queryKey: ["assistant-conversations"],
    queryFn: () => assistantApi.getConversations(),
  });

  const chatMutation = useMutation({
    mutationFn: ({ msg, convId }: { msg: string; convId?: number }) =>
      assistantApi.chat(msg, convId),
    onSuccess: (data) => {
      setConversationId(data.conversation_id);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "user",
          content: message,
          created_at: new Date().toISOString(),
        },
        {
          id: data.conversation_id,
          role: "assistant",
          content: data.answer,
          created_at: new Date().toISOString(),
        },
      ]);
      setMessage("");
      queryClient.invalidateQueries({ queryKey: ["assistant-conversations"] });
    },
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!message.trim() || chatMutation.isPending) return;
    chatMutation.mutate({ msg: message.trim(), convId: conversationId });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestion = (suggestion: string) => {
    setMessage(suggestion);
  };

  const handleClearConversation = () => {
    setConversationId(undefined);
    setMessages([]);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="AI Career Assistant"
        description="Get personalized career guidance powered by AI"
        actions={
          <Button variant="ghost" size="sm" onClick={handleClearConversation}>
            <Plus className="h-4 w-4" />
            New Conversation
          </Button>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Area */}
        <div className="lg:col-span-3">
          <Card className="flex flex-col h-[600px]">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
                  <div className="rounded-full bg-primary/10 p-4">
                    <Bot className="h-10 w-10 text-primary" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold mb-2">
                      How can I help with your career?
                    </h2>
                    <p className="text-sm text-muted-foreground max-w-md">
                      Ask me about your career recommendations, skill gaps,
                      learning roadmap, or anything career-related.
                    </p>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg">
                    {SUGGESTED_QUESTIONS.map((q) => (
                      <button
                        key={q}
                        onClick={() => handleSuggestion(q)}
                        className="flex items-center gap-2 p-3 text-left text-sm border rounded-lg hover:bg-accent transition-colors"
                      >
                        <HelpCircle className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`flex items-start gap-2 max-w-[85%] ${
                      msg.role === "user" ? "flex-row-reverse" : ""
                    }`}
                  >
                    <div
                      className={`flex-shrink-0 h-7 w-7 rounded-full flex items-center justify-center ${
                        msg.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {msg.role === "user" ? (
                        <User className="h-3.5 w-3.5" />
                      ) : (
                        <Bot className="h-3.5 w-3.5" />
                      )}
                    </div>
                    <div
                      className={`rounded-2xl px-4 py-2.5 text-sm ${
                        msg.role === "user"
                          ? "bg-primary text-primary-foreground rounded-tr-sm"
                          : "bg-muted rounded-tl-sm"
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    </div>
                  </div>
                </div>
              ))}

              {chatMutation.isPending && (
                <div className="flex justify-start">
                  <div className="flex items-start gap-2">
                    <div className="h-7 w-7 rounded-full bg-muted flex items-center justify-center">
                      <Bot className="h-3.5 w-3.5 text-muted-foreground" />
                    </div>
                    <div className="bg-muted rounded-2xl rounded-tl-sm px-4 py-3">
                      <div className="flex gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse-soft" />
                        <span className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse-soft" style={{ animationDelay: "0.2s" }} />
                        <span className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse-soft" style={{ animationDelay: "0.4s" }} />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {chatMutation.isError && (
                <div className="flex justify-start">
                  <div className="bg-destructive/10 text-destructive px-4 py-2.5 rounded-2xl rounded-tl-sm text-sm">
                    Sorry, something went wrong. Please try again.
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            <div className="border-t p-4">
              <div className="flex gap-2">
                <Textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about your career..."
                  rows={1}
                  className="min-h-[40px] resize-none"
                />
                <Button
                  onClick={handleSend}
                  disabled={!message.trim() || chatMutation.isPending}
                  size="icon"
                  className="flex-shrink-0"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Based on your SkillBridge data. Responses are for guidance only.
              </p>
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Conversations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1 max-h-[300px] overflow-y-auto">
                {conversations && conversations.length > 0 ? (
                  conversations.slice(0, 10).map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => {
                        setConversationId(conv.id);
                        assistantApi.getConversation(conv.id).then((data) => {
                          setMessages(data.messages);
                        });
                      }}
                      className={`w-full text-left p-2.5 rounded-lg text-sm transition-colors truncate ${
                        conversationId === conv.id
                          ? "bg-primary/10 text-primary"
                          : "hover:bg-accent text-muted-foreground"
                      }`}
                    >
                      {conv.title || "Untitled"}
                    </button>
                  ))
                ) : (
                  <p className="text-xs text-muted-foreground text-center py-4">
                    No conversations yet
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Data Sources</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-xs text-muted-foreground space-y-2">
                <li className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                  Your skill profile
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                  Career recommendations
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                  Skill gap analysis
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                  Learning roadmap
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
