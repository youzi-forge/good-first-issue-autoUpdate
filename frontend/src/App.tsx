import { useEffect, useState, useMemo } from "react";
import { RepoCard } from "./components/RepoCard";
import { FilterBar } from "./components/FilterBar";
import { Github, Loader2, ChevronLeft, ChevronRight } from "lucide-react";

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

interface RawIssue {
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
    issues: RawIssue[];
}



function App() {
    const [data, setData] = useState<Data | null>(null);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [selectedLanguage, setSelectedLanguage] = useState<string | null>(null);
    const [minStars, setMinStars] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage, setItemsPerPage] = useState(10);

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

    // Reset page when filters change
    useEffect(() => {
        setCurrentPage(1);
    }, [search, selectedLanguage, minStars, itemsPerPage]);

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

    const groupedRepos = useMemo(() => {
        if (!data) return [];

        // First filter the raw issues
        const filteredRawIssues = data.issues.filter((issue) => {
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

        // Then group by repository
        const repoMap = new Map<string, Repository>();

        filteredRawIssues.forEach((issue) => {
            if (!repoMap.has(issue.repo)) {
                repoMap.set(issue.repo, {
                    name: issue.repo,
                    url: issue.repo_url,
                    stars: issue.stars,
                    language: issue.language,
                    issues: [],
                });
            }
            repoMap.get(issue.repo)!.issues.push({
                title: issue.title,
                number: issue.number,
                url: issue.url,
                createdAt: issue.createdAt,
                updatedAt: issue.updatedAt,
                labels: issue.labels,
            });
        });

        // Sort issues within each repo by updatedAt (descending)
        repoMap.forEach((repo) => {
            repo.issues.sort((a, b) => {
                return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
            });
        });

        // Convert to array and sort by stars (descending)
        return Array.from(repoMap.values()).sort((a, b) => b.stars - a.stars);
    }, [data, search, selectedLanguage, minStars]);

    const totalPages = Math.ceil(groupedRepos.length / itemsPerPage);
    const currentRepos = groupedRepos.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );

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
            <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
                <header className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
                            Good First Issues
                        </h1>
                        <p className="mt-2 text-muted-foreground">
                            Discover beginner-friendly issues in popular open-source projects.
                            <br />
                            <span className="text-sm opacity-80">
                                Showing issues from repositories with &gt;1000 stars, updated in the last 90 days.
                                <br />
                                Repositories sorted by stars. Issues within each repo sorted by last update (newest first).
                            </span>
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
                    itemsPerPage={itemsPerPage}
                    setItemsPerPage={setItemsPerPage}
                />

                <div className="space-y-6">
                    {currentRepos.map((repo) => (
                        <RepoCard key={repo.name} repo={repo} />
                    ))}
                </div>

                {groupedRepos.length === 0 && (
                    <div className="mt-12 text-center text-muted-foreground">
                        No issues found matching your criteria.
                    </div>
                )}

                {totalPages > 1 && (
                    <div className="mt-10 flex items-center justify-center gap-4">
                        <button
                            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="flex items-center gap-1 rounded-lg border border-border bg-card px-3 py-2 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-accent/10 hover:border-accent transition-colors"
                        >
                            <ChevronLeft className="h-4 w-4" />
                            Previous
                        </button>
                        <span className="text-sm text-muted-foreground">
                            Page {currentPage} of {totalPages}
                        </span>
                        <button
                            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                            className="flex items-center gap-1 rounded-lg border border-border bg-card px-3 py-2 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-accent/10 hover:border-accent transition-colors"
                        >
                            Next
                            <ChevronRight className="h-4 w-4" />
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
