import { Star, GitPullRequest, Calendar, ExternalLink } from "lucide-react";
import { cn } from "../lib/utils";

interface Issue {
    repo: string;
    repo_url: string;
    stars: number;
    language?: {
        name: string;
        color: string;
    };
    title: string;
    number: number;
    url: string;
    createdAt: string;
    updatedAt: string;
    state: string;
    labels: string[];
}

interface IssueCardProps {
    issue: Issue;
}

export function IssueCard({ issue }: IssueCardProps) {
    const date = new Date(issue.updatedAt);
    const formattedDate = new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
    }).format(date);

    return (
        <div className="group relative flex flex-col justify-between rounded-xl border border-border bg-card p-5 shadow-sm transition-all hover:shadow-md hover:border-accent/50">
            <div className="mb-4">
                <div className="flex items-center justify-between gap-2 mb-2">
                    <a
                        href={issue.repo_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1.5"
                    >
                        {issue.repo}
                    </a>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        {issue.language && (
                            <span className="flex items-center gap-1">
                                <span
                                    className="h-2 w-2 rounded-full"
                                    style={{ backgroundColor: issue.language.color }}
                                />
                                {issue.language.name}
                            </span>
                        )}
                        <span className="flex items-center gap-1">
                            <Star className="h-3 w-3" />
                            {issue.stars.toLocaleString()}
                        </span>
                    </div>
                </div>

                <a
                    href={issue.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block"
                >
                    <h3 className="font-semibold text-lg leading-tight group-hover:text-accent-foreground transition-colors mb-2">
                        {issue.title}
                    </h3>
                </a>

                <div className="flex flex-wrap gap-2 mt-3">
                    {issue.labels.map((label) => (
                        <span
                            key={label}
                            className="inline-flex items-center rounded-full border border-transparent bg-secondary px-2.5 py-0.5 text-xs font-semibold text-secondary-foreground transition-colors hover:bg-secondary/80"
                        >
                            {label}
                        </span>
                    ))}
                </div>
            </div>

            <div className="flex items-center justify-between text-xs text-muted-foreground mt-auto pt-4 border-t border-border/50">
                <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formattedDate}
                    </span>
                    <span className="flex items-center gap-1">
                        #{issue.number}
                    </span>
                </div>
                <a
                    href={issue.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-accent-foreground flex items-center gap-1 font-medium"
                >
                    View Issue <ExternalLink className="h-3 w-3" />
                </a>
            </div>
        </div>
    );
}
