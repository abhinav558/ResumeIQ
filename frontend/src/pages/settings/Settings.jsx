import { useNavigate } from "react-router-dom";
import { useResumeContext } from "../../context/ResumeContext";

function Icon({ name, size = 18 }) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "1.7",
    strokeLinecap: "round",
    strokeLinejoin: "round",
  };

  const icons = {
    library: (
      <svg {...common}>
        <path d="M5 4.5A1.5 1.5 0 0 1 6.5 3H19v16H6.5A1.5 1.5 0 0 0 5 20.5v-16Z" />
        <path d="M5 20.5A1.5 1.5 0 0 1 6.5 19H19" />
        <path d="M8.5 7h7" />
        <path d="M8.5 10.5h7" />
        <path d="M8.5 14h4.5" />
      </svg>
    ),

    trash: (
      <svg {...common}>
        <path d="M4 7h16" />
        <path d="M10 11v6" />
        <path d="M14 11v6" />
        <path d="M6 7l1 14h10l1-14" />
        <path d="M9 7V4h6v3" />
      </svg>
    ),

    shield: (
      <svg {...common}>
        <path d="M12 3 20 6v5c0 5-3.3 8.6-8 10-4.7-1.4-8-5-8-10V6l8-3Z" />
        <path d="m9 12 2 2 4-4" />
      </svg>
    ),

    file: (
      <svg {...common}>
        <path d="M6 3.5h8l4 4V20a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z" />
        <path d="M14 3.5V8h4" />
        <path d="M8 12h8" />
        <path d="M8 16h5" />
      </svg>
    ),

    arrow: (
      <svg {...common}>
        <path d="M5 12h14" />
        <path d="m13 6 6 6-6 6" />
      </svg>
    ),
  };

  return icons[name] || null;
}

function Settings() {
  const navigate = useNavigate();

  const {
    analysis,
    resumeText,
    clearAnalysis,
  } = useResumeContext();

  const hasStoredData = Boolean(
    analysis || resumeText
  );

  const handleClearData = () => {
    if (!hasStoredData) {
      return;
    }

    const confirmed = window.confirm(
      "Clear the resume analysis and resume text currently stored in this browser? Your saved resumes in Resume Library will not be deleted."
    );

    if (!confirmed) {
      return;
    }

    clearAnalysis();
    navigate("/dashboard");
  };

  return (
    <div className="px-5 py-7 sm:px-7 lg:px-9 lg:py-9">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-blue-400">
            Account
          </p>

          <h2 className="mt-2 text-2xl font-bold tracking-tight text-white">
            Settings
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-500">
            Manage your ResumeIQ workspace and
            understand how your resume data is
            stored.
          </p>
        </div>

        <div className="space-y-5">
          {/* Workspace */}
          <section className="rounded-2xl border border-white/[0.07] bg-white/[0.025]">
            <div className="border-b border-white/[0.06] px-5 py-4">
              <h3 className="text-sm font-semibold text-white">
                Workspace
              </h3>

              <p className="mt-1 text-xs text-slate-600">
                Information about your current
                ResumeIQ workspace.
              </p>
            </div>

            <div className="divide-y divide-white/[0.05]">
              <div className="flex items-center justify-between gap-6 px-5 py-4">
                <div>
                  <p className="text-xs font-medium text-slate-300">
                    Workspace
                  </p>

                  <p className="mt-1 text-[11px] text-slate-600">
                    Current ResumeIQ workspace
                  </p>
                </div>

                <span className="text-xs text-slate-500">
                  Resume workspace
                </span>
              </div>

              <div className="flex items-center justify-between gap-6 px-5 py-4">
                <div>
                  <p className="text-xs font-medium text-slate-300">
                    Current analysis
                  </p>

                  <p className="mt-1 text-[11px] text-slate-600">
                    Resume analysis currently
                    available in this browser
                  </p>
                </div>

                <span
                  className={`rounded-lg px-2.5 py-1 text-[10px] font-semibold ${
                    hasStoredData
                      ? "bg-emerald-500/[0.08] text-emerald-400"
                      : "bg-white/[0.04] text-slate-600"
                  }`}
                >
                  {hasStoredData
                    ? "Available"
                    : "No data"}
                </span>
              </div>
            </div>
          </section>

          {/* Resume Library */}
          <section className="rounded-2xl border border-white/[0.07] bg-white/[0.025]">
            <div className="border-b border-white/[0.06] px-5 py-4">
              <h3 className="text-sm font-semibold text-white">
                Resume Library
              </h3>

              <p className="mt-1 text-xs text-slate-600">
                Access resumes you have saved to
                your ResumeIQ account.
              </p>
            </div>

            <div className="px-5 py-5">
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-500/[0.08] text-blue-400">
                    <Icon
                      name="library"
                      size={17}
                    />
                  </div>

                  <div>
                    <p className="text-xs font-medium text-slate-300">
                      Saved resumes
                    </p>

                    <p className="mt-1 max-w-2xl text-[11px] leading-relaxed text-slate-600">
                      Your saved resumes are
                      stored in your ResumeIQ
                      account and can be reopened
                      from the Resume Library.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() =>
                    navigate("/resume-library")
                  }
                  className="mt-4 inline-flex h-9 items-center justify-center gap-2 rounded-lg border border-blue-400/10 bg-blue-500/[0.07] px-3 text-xs font-semibold text-blue-300 transition hover:border-blue-400/20 hover:bg-blue-500/[0.12] hover:text-blue-200"
                >
                  Open Resume Library

                  <Icon
                    name="arrow"
                    size={14}
                  />
                </button>
              </div>
            </div>
          </section>

          {/* Data & Privacy */}
          <section className="rounded-2xl border border-white/[0.07] bg-white/[0.025]">
            <div className="border-b border-white/[0.06] px-5 py-4">
              <h3 className="text-sm font-semibold text-white">
                Data & Privacy
              </h3>

              <p className="mt-1 text-xs text-slate-600">
                Understand and manage resume data
                currently stored by ResumeIQ.
              </p>
            </div>

            <div className="space-y-4 px-5 py-5">
              {/* Browser data */}
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/[0.035] text-slate-500">
                    <Icon
                      name="file"
                      size={16}
                    />
                  </div>

                  <div>
                    <p className="text-xs font-medium text-slate-300">
                      Current browser data
                    </p>

                    <p className="mt-1 max-w-2xl text-[11px] leading-relaxed text-slate-600">
                      ResumeIQ keeps the current
                      analysis and extracted resume
                      text in your browser so the
                      report remains available while
                      you move between application
                      pages.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  disabled={!hasStoredData}
                  onClick={handleClearData}
                  className="mt-4 inline-flex h-9 items-center justify-center gap-2 rounded-lg border border-red-500/20 bg-red-500/[0.06] px-3 text-xs font-medium text-red-400 transition hover:bg-red-500/[0.1] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <Icon
                    name="trash"
                    size={14}
                  />

                  Clear current browser data
                </button>

                <p className="mt-2 text-[10px] leading-5 text-slate-700">
                  This does not delete resumes saved
                  in your Resume Library.
                </p>
              </div>

              {/* Account storage */}
              <div className="rounded-xl border border-emerald-400/10 bg-emerald-500/[0.025] p-4">
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-500/[0.07] text-emerald-400">
                    <Icon
                      name="shield"
                      size={16}
                    />
                  </div>

                  <div>
                    <p className="text-xs font-medium text-slate-300">
                      Account-saved resumes
                    </p>

                    <p className="mt-1 max-w-2xl text-[11px] leading-relaxed text-slate-600">
                      Resumes explicitly saved by
                      ResumeIQ are associated with
                      your account and can be managed
                      from the Resume Library.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* About */}
          <section className="rounded-2xl border border-white/[0.07] bg-white/[0.025]">
            <div className="border-b border-white/[0.06] px-5 py-4">
              <h3 className="text-sm font-semibold text-white">
                About ResumeIQ
              </h3>
            </div>

            <div className="px-5 py-5">
              <p className="text-xs leading-relaxed text-slate-500">
                ResumeIQ provides resume
                intelligence, ATS analysis and
                job-matching insights from your
                resume.
              </p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

export default Settings;