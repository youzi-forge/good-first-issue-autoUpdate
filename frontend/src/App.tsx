import { useEffect, useState, useMemo } from "react";
import { IssueCard } from "./components/IssueCard";
import { FilterBar } from "./components/FilterBar";
import { Github, Loader2 } from "lucide-react";

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

interface Data {
    meta: {
        title: string;
        generated_at: string;
        total_issues: number;
        total_repos: number;
    };
    issues: Issue[];
}

function App() {
    const [data, setData] = useState<Data | null>(null);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [selectedLanguage, setSelectedLanguage] = useState<string | null>(null);
    const [minStars, setMinStars] = useState(0);

    useEffect(() => {
        fetch("data.json")
            .then((res) => res.json())
            .then((data) => {
                setData(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Failed to fetch data", err);
                setLoading(false);
            });
    }, []);

    const languages = useMemo(() => {
        if (!data) return [];
        const langs = new Set<string>();
        data.issues.forEach((issue) => {
            if (issue.language?.name) {
                langs.add(issue.language.name);
            }
        });
        return Array.from(langs).sort();
    }, [data]);

    const filteredIssues = useMemo(() => {
        if (!data) return [];
        return data.issues.filter((issue) => {
            const matchesSearch =
                search === "" ||
                issue.title.toLowerCase().includes(search.toLowerCase()) ||
                issue.repo.toLowerCase().includes(search.toLowerCase()) ||
                issue.labels.some((l) => l.toLowerCase().includes(search.toLowerCase()));

            const matchesLanguage =
                selectedLanguage === null || issue.language?.name === selectedLanguage;

            const matchesStars = issue.stars >= minStars;

            return matchesSearch && matchesLanguage && matchesStars;
        });
    }, [data, search, selectedLanguage, minStars]);

    if (loading) {
        return (
            <div className="flex h-screen w-full items-center justify-center bg-background">
                <Loader2 className="h-8 w-8 animate-spin text-accent" />
            </div>
        );
    }

    if (!data) {
        return (
            <div className="flex h-screen w-full items-center justify-center bg-background text-destructive">
                Failed to load data. Please check if data.json exists.
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background text-foreground selection:bg-accent/20">
            <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                <header className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
                            Good First Issues
                        </h1>
                        <p className="mt-2 text-muted-foreground">
                            Discover beginner-friendly issues in popular open-source projects.
                            <br className="hidden sm:block" />
                            Updated: {new Date(data.meta.generated_at).toLocaleString()}
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        <a
                            href="https://github.com/youzi-forge/good-first-issue-autoUpdate"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground"
                        >
                            <Github className="h-4 w-4" />
                            View on GitHub
                        </a>
                    </div>
                </header>

                <FilterBar
                    search={search}
                    setSearch={setSearch}
                    selectedLanguage={selectedLanguage}
                    setSelectedLanguage={setSelectedLanguage}
                    languages={languages}
                    minStars={minStars}
                    setMinStars={setMinStars}
                />

                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {filteredIssues.map((issue) => (
                        <IssueCard key={issue.url} issue={issue} />
                    ))}
                </div>

                {filteredIssues.length === 0 && (
                    <div className="mt-12 text-center text-muted-foreground">
                        No issues found matching your criteria.
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
