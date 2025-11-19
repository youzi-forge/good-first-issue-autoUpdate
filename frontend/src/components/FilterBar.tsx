import { Search, X } from "lucide-react";

interface FilterBarProps {
    search: string;
    setSearch: (value: string) => void;
    selectedLanguage: string | null;
    setSelectedLanguage: (value: string | null) => void;
    languages: string[];
    minStars: number;
    setMinStars: (value: number) => void;
}

export function FilterBar({
    search,
    setSearch,
    selectedLanguage,
    setSelectedLanguage,
    languages,
    minStars,
    setMinStars,
}: FilterBarProps) {
    return (
        <div className="sticky top-4 z-10 mb-8 space-y-4 rounded-2xl border border-border/50 bg-background/80 p-4 backdrop-blur-xl shadow-sm transition-all hover:shadow-md hover:border-border">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search issues, repos, or labels..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="h-10 w-full rounded-xl border border-border bg-secondary/50 pl-10 pr-4 text-sm outline-none transition-all focus:border-accent focus:bg-background focus:ring-2 focus:ring-accent/20"
                    />
                    {search && (
                        <button
                            onClick={() => setSearch("")}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        >
                            <X className="h-3 w-3" />
                        </button>
                    )}
                </div>

                <div className="flex flex-wrap items-center gap-3">
                    <select
                        value={selectedLanguage || ""}
                        onChange={(e) => setSelectedLanguage(e.target.value || null)}
                        className="h-10 rounded-xl border border-border bg-secondary/50 px-3 text-sm outline-none transition-all focus:border-accent focus:bg-background focus:ring-2 focus:ring-accent/20"
                    >
                        <option value="">All Languages</option>
                        {languages.map((lang) => (
                            <option key={lang} value={lang}>
                                {lang}
                            </option>
                        ))}
                    </select>

                    <div className="flex items-center gap-2 rounded-xl border border-border bg-secondary/50 px-3 py-2">
                        <label htmlFor="min-stars" className="text-xs font-medium text-muted-foreground whitespace-nowrap">
                            Min Stars:
                        </label>
                        <input
                            id="min-stars"
                            type="number"
                            min="0"
                            step="100"
                            value={minStars}
                            onChange={(e) => setMinStars(Number(e.target.value))}
                            className="w-16 bg-transparent text-sm outline-none"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
