import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

const searchItems = [
  {
    title: "Dashboard",
    description: "Resume overview and career intelligence",
    path: "/dashboard",
    keywords: ["home", "overview", "resume", "career"],
  },
  {
    title: "Resume Analysis",
    description: "Detailed analysis of your resume",
    path: "/resume-analysis",
    keywords: ["resume", "analysis", "skills", "experience", "education"],
  },
  {
    title: "ATS Intelligence",
    description: "ATS score, keywords and screening readiness",
    path: "/ats-intelligence",
    keywords: ["ats", "score", "keywords", "screening", "applicant"],
  },
  {
    title: "Job Matching",
    description: "Match your resume against a job description",
    path: "/job-matching",
    keywords: ["jobs", "matching", "job", "description", "compatibility"],
  },
  {
    title: "Settings",
    description: "Manage ResumeIQ preferences and stored data",
    path: "/settings",
    keywords: ["settings", "preferences", "data", "storage"],
  },
];

function GlobalSearch({ onClose }) {
  const [query, setQuery] = useState("");
  const inputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const results = useMemo(() => {
    const normalized = query.trim().toLowerCase();

    if (!normalized) {
      return searchItems;
    }

    return searchItems.filter((item) => {
      const searchableText = [
        item.title,
        item.description,
        ...item.keywords,
      ]
        .join(" ")
        .toLowerCase();

      return searchableText.includes(normalized);
    });
  }, [query]);

  const handleNavigate = (path) => {
    navigate(path);
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center bg-black/70 px-4 pt-[12vh] backdrop-blur-sm"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="w-full max-w-2xl overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0b1020] shadow-2xl shadow-black/50">
        <div className="flex items-center gap-3 border-b border-white/[0.06] px-5">
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="shrink-0 text-slate-500"
          >
            <circle cx="11" cy="11" r="6.5" />
            <path d="m16 16 4.5 4.5" />
          </svg>

          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Escape") {
                onClose();
              }

              if (event.key === "Enter" && results.length > 0) {
                handleNavigate(results[0].path);
              }
            }}
            placeholder="Search ResumeIQ..."
            aria-label="Search ResumeIQ"
            className="h-16 min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
          />

          <kbd className="rounded-md border border-white/[0.08] bg-white/[0.03] px-2 py-1 text-[9px] text-slate-600">
            ESC
          </kbd>
        </div>

        <div className="max-h-[55vh] overflow-y-auto p-2">
          {results.length > 0 ? (
            results.map((item) => (
              <button
                key={item.path}
                type="button"
                onClick={() => handleNavigate(item.path)}
                className="flex w-full items-center gap-4 rounded-xl px-4 py-3 text-left transition hover:bg-white/[0.05]"
              >
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-500/[0.08] text-blue-400">
                  <span className="text-xs font-bold">
                    {item.title.charAt(0)}
                  </span>
                </div>

                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-slate-200">
                    {item.title}
                  </p>

                  <p className="mt-0.5 truncate text-xs text-slate-600">
                    {item.description}
                  </p>
                </div>

                <span className="text-xs text-slate-700">↵</span>
              </button>
            ))
          ) : (
            <div className="px-4 py-10 text-center">
              <p className="text-sm font-medium text-slate-400">
                No results found
              </p>

              <p className="mt-1 text-xs text-slate-600">
                Try searching for a ResumeIQ section.
              </p>
            </div>
          )}
        </div>

        <div className="border-t border-white/[0.06] px-5 py-3">
          <p className="text-[10px] text-slate-600">
            Search pages and features across ResumeIQ
          </p>
        </div>
      </div>
    </div>
  );
}

export default GlobalSearch;