import { cn } from "@/lib/utils";

interface SkillChipProps {
  name: string;
  proficiency?: number;
  category?: string;
  onRemove?: () => void;
  onClick?: () => void;
  className?: string;
  selected?: boolean;
}

function SkillChip({ name, proficiency, category, onRemove, onClick, className, selected }: SkillChipProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition-colors",
        selected
          ? "bg-primary/10 border-primary/30 text-primary"
          : "bg-card border-border hover:bg-accent",
        onClick && "cursor-pointer",
        className
      )}
      onClick={onClick}
    >
      <span className="font-medium">{name}</span>
      {proficiency !== undefined && (
        <span className="text-xs text-muted-foreground">Lvl {proficiency}</span>
      )}
      {category && (
        <span className="text-xs text-muted-foreground hidden sm:inline">&middot; {category}</span>
      )}
      {onRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="ml-0.5 rounded-full p-0.5 hover:bg-destructive/10 hover:text-destructive"
        >
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}

export { SkillChip };
