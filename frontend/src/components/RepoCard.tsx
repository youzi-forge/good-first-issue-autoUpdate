import { Star, ExternalLink, Calendar, GitPullRequest } from "lucide-react";

interface Issue {
    title: string;
    number: number;
    url: string;
    createdAt: string;
    updatedAt: string;
    labels: string[];
}

interface Repository {
    name: string;
    url: string;
    stars: number;
    language?: {
        name: string;
        color: string;
    };
    issues: Issue[];
}

interface RepoCardProps {
    repo: Repository;
}

export function RepoCard({ repo }: RepoCardProps) {
    return (
        <div className="rounded-xl border border-border bg-card shadow-sm transition-all hover:shadow-md">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-border/50 p-4 sm:px-6">
                <div className="flex items-center gap-3">
                    <a
                        href={repo.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-lg font-semibold text-accent hover:underline"
                    >
                        {repo.name}
                    </a>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                        {repo.language && (
                            <span className="flex items-center gap-1.5">
                                <span
                                    className="h-2.5 w-2.5 rounded-full"
                                    style={{ backgroundColor: repo.language.color }}
                                />
                                {repo.language.name}
                            </span>
                        )}
                        <span className="flex items-center gap-1">
                            <Star className="h-3.5 w-3.5" />
                            {repo.stars.toLocaleString()}
                        </span>
                    </div>
                </div>
            </div>

            <div className="divide-y divide-border/50">
                {repo.issues.map((issue) => {
                    const date = new Date(issue.updatedAt);
                    const formattedDate = new Intl.DateTimeFormat("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                    }).format(date);

                    return (
                        <div key={issue.url} className="p-4 transition-colors hover:bg-muted/30 sm:px-6">
                            <div className="mb-2 flex items-start justify-between gap-4">
                                <a
                                    href={issue.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="font-medium text-foreground hover:text-accent transition-colors leading-snug"
                                >
                                    {issue.title}
                                </a>
                                <span className="shrink-0 text-xs text-muted-foreground font-mono">
                                    #{issue.number}
                                </span>
                            </div>

                            <div className="flex flex-wrap items-center gap-y-2 gap-x-4">
                                <div className="flex flex-wrap gap-2">
                                    {issue.labels.map((label) => (
                                        <span
                                            key={label}
                                            className="inline-flex items-center rounded-md border border-transparent bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground"
                                        >
                                            {label}
                                        </span>
                                    ))}
                                </div>
                                <div className="flex items-center gap-1 text-xs text-muted-foreground ml-auto">
                                    <Calendar className="h-3 w-3" />
                                    {formattedDate}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
