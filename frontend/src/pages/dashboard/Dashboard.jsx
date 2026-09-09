import { useMemo } from "react";
import { useNavigate } from "react-router-dom";

import ResumeUploader from "../../components/dashboard/ResumeUploader";
import { useResumeContext } from "../../context/ResumeContext";

function Dashboard() {
  const navigate = useNavigate();
  const { setAnalysis, analysis } = useResumeContext();

  const hasAnalysis = Boolean(analysis);

  /* ============================================================
     SAFE DATA NORMALIZATION
  ============================================================ */

  const intelligenceScore = Number(
    analysis?.resume_intelligence_score || 0
  );

  const atsScore = Number(
    analysis?.ats_analysis?.ats_score || 0
  );

  const skillsScore = Number(
    analysis?.skills_analysis?.skill_score || 0
  );

  const projectScore = Number(
    analysis?.project_analysis?.score || 0
  );

  const skillCount =
    Number(analysis?.skills_analysis?.total_skills) || 0;

  const projectCount =
    Number(analysis?.project_analysis?.project_count) || 0;

  const matchedKeywords =
    analysis?.ats_analysis?.keyword_analysis?.matched?.length ||
    analysis?.ats_analysis?.matched_keywords?.length ||
    0;

  const missingKeywords =
    analysis?.ats_analysis?.keyword_analysis?.missing?.length ||
    analysis?.ats_analysis?.missing_keywords?.length ||
    0;

  const recommendations = Array.isArray(
    analysis?.recommendations
  )
    ? analysis.recommendations
    : [];

  const strengths = Array.isArray(
    analysis?.ats_analysis?.strengths
  )
    ? analysis.ats_analysis.strengths
    : [];

  const keywordCoverage =
    matchedKeywords + missingKeywords > 0
      ? (matchedKeywords /
          (matchedKeywords + missingKeywords)) *
        100
      : 0;

  /* ============================================================
     RESUME STATUS
  ============================================================ */

  const resumeStatus = useMemo(() => {
    if (!hasAnalysis) {
      return {
        label: "Not analyzed",
        description:
          "Upload your resume to unlock your intelligence report.",
        tone: "neutral",
      };
    }

    if (intelligenceScore >= 85) {
      return {
        label: "Excellent",
        description:
          "Your resume is performing strongly across key areas.",
        tone: "success",
      };
    }

    if (intelligenceScore >= 70) {
      return {
        label: "Good",
        description:
          "Your resume has a solid foundation with room to improve.",
        tone: "blue",
      };
    }

    if (intelligenceScore >= 55) {
      return {
        label: "Needs improvement",
        description:
          "Several areas are limiting your resume's performance.",
        tone: "warning",
      };
    }

    return {
      label: "Needs attention",
      description:
        "Your resume needs meaningful improvements before applying.",
      tone: "danger",
    };
  }, [hasAnalysis, intelligenceScore]);

  const statusClasses = {
    success:
      "border-emerald-400/10 bg-emerald-400/[0.06] text-emerald-400",
    blue:
      "border-blue-400/10 bg-blue-400/[0.06] text-blue-400",
    warning:
      "border-amber-400/10 bg-amber-400/[0.06] text-amber-400",
    danger:
      "border-red-400/10 bg-red-400/[0.06] text-red-400",
    neutral:
      "border-white/[0.08] bg-white/[0.025] text-slate-500",
  };

  /* ============================================================
     ANALYSIS COMPLETE
  ============================================================ */

  const handleAnalysisComplete = (result) => {
    if (!result) return;

    setAnalysis(result);
    navigate("/resume-analysis");
  };

  return (
    <div className="relative min-h-[calc(100vh-76px)] overflow-hidden bg-[#050810] text-white">
      {/* ==========================================================
          AMBIENT BACKGROUND
      ========================================================== */}

      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 overflow-hidden"
      >
        <div className="absolute -right-40 -top-40 h-[520px] w-[520px] rounded-full bg-blue-600/[0.055] blur-[150px]" />

        <div className="absolute left-1/3 top-1/2 h-[420px] w-[420px] rounded-full bg-indigo-600/[0.035] blur-[150px]" />

        <div className="absolute -bottom-40 -left-40 h-[500px] w-[500px] rounded-full bg-cyan-600/[0.025] blur-[150px]" />
      </div>

      <main className="relative mx-auto max-w-[1480px] px-5 py-7 sm:px-8 sm:py-9 xl:px-10">

        {/* ========================================================
            PAGE HEADER
        ======================================================== */}

        <section className="mb-8">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <div className="mb-3 flex items-center gap-2">
                <span
                  aria-hidden="true"
                  className="h-1.5 w-1.5 rounded-full bg-blue-400 shadow-[0_0_12px_rgba(96,165,250,0.8)]"
                />

                <span className="text-[10px] font-bold uppercase tracking-[0.22em] text-blue-400">
                  Career intelligence
                </span>
              </div>

              <h1 className="max-w-3xl text-3xl font-bold tracking-[-0.03em] text-white sm:text-4xl lg:text-[42px]">
                Your resume,
                <span className="text-slate-500">
                  {" "}
                  engineered for opportunity.
                </span>
              </h1>

              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
                Analyze your resume, understand how recruiters and
                ATS systems see it, and turn weaknesses into
                measurable improvements.
              </p>
            </div>

            {hasAnalysis && (
              <button
                type="button"
                onClick={() => navigate("/resume-analysis")}
                className="group inline-flex shrink-0 items-center justify-center gap-3 rounded-xl border border-white/[0.08] bg-white/[0.025] px-5 py-3 text-xs font-semibold text-slate-300 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-blue-500/25 hover:bg-blue-500/[0.06] hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              >
                Open latest analysis

                <span
                  aria-hidden="true"
                  className="transition-transform duration-200 group-hover:translate-x-1"
                >
                  →
                </span>
              </button>
            )}
          </div>
        </section>

        {/* ========================================================
            HERO INTELLIGENCE PANEL
        ======================================================== */}

        {hasAnalysis ? (
          <section className="mb-6 overflow-hidden rounded-[28px] border border-white/[0.07] bg-[#090e1a] shadow-2xl shadow-black/20">
            <div className="grid lg:grid-cols-[1.2fr_0.8fr]">

              {/* SCORE */}
              <div className="relative overflow-hidden p-7 sm:p-9">
                <div
                  aria-hidden="true"
                  className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-blue-600/[0.08] blur-[90px]"
                />

                <div className="relative">
                  <div className="flex items-start justify-between gap-5">
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-600">
                        Resume intelligence
                      </p>

                      <h2 className="mt-2 text-lg font-semibold text-slate-200">
                        Overall performance
                      </h2>
                    </div>

                    <span
                      className={`rounded-full border px-3 py-1.5 text-[9px] font-bold uppercase tracking-wider ${statusClasses[resumeStatus.tone]}`}
                    >
                      {resumeStatus.label}
                    </span>
                  </div>

                  <div className="mt-8 flex flex-col gap-8 sm:flex-row sm:items-center">
                    <ScoreRing score={intelligenceScore} />

                    <div className="max-w-md">
                      <p className="text-sm leading-6 text-slate-400">
                        {resumeStatus.description}
                      </p>

                      <div className="mt-5 flex flex-wrap gap-2">
                        <InsightPill
                          label={`${skillCount} skills detected`}
                        />

                        <InsightPill
                          label={`${matchedKeywords} ATS keywords matched`}
                        />

                        <InsightPill
                          label={`${projectCount} projects analyzed`}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* BREAKDOWN */}
              <div className="border-t border-white/[0.06] bg-white/[0.012] p-7 sm:p-9 lg:border-l lg:border-t-0">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-600">
                      Performance signals
                    </p>

                    <h3 className="mt-2 text-sm font-semibold text-slate-200">
                      What is driving your score
                    </h3>
                  </div>

                  <span className="whitespace-nowrap text-[10px] text-slate-700">
                    Latest analysis
                  </span>
                </div>

                <div className="mt-7 space-y-5">
                  <MetricBar
                    label="ATS readiness"
                    value={atsScore}
                    suffix="%"
                  />

                  <MetricBar
                    label="Skills strength"
                    value={skillsScore}
                    suffix="%"
                  />

                  <MetricBar
                    label="Project quality"
                    value={projectScore}
                    suffix="%"
                  />

                  <MetricBar
                    label="Keyword coverage"
                    value={keywordCoverage}
                    suffix="%"
                  />
                </div>
              </div>
            </div>
          </section>
        ) : (
          /* ======================================================
             EMPTY HERO
          ====================================================== */

          <section className="mb-6 overflow-hidden rounded-[28px] border border-blue-500/[0.12] bg-gradient-to-br from-blue-500/[0.07] via-[#090e1a] to-[#090e1a] shadow-2xl shadow-black/20">
            <div className="relative p-7 sm:p-10">
              <div
                aria-hidden="true"
                className="pointer-events-none absolute -right-24 -top-24 h-80 w-80 rounded-full bg-blue-500/[0.08] blur-[100px]"
              />

              <div className="relative max-w-3xl">
                <span className="inline-flex rounded-full border border-blue-400/10 bg-blue-400/[0.06] px-3 py-1.5 text-[9px] font-bold uppercase tracking-[0.16em] text-blue-400">
                  Start your intelligence report
                </span>

                <h2 className="mt-5 text-2xl font-bold tracking-tight text-white sm:text-3xl">
                  See exactly how your resume performs.
                </h2>

                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
                  ResumeIQ evaluates your resume across ATS
                  compatibility, skills, projects, experience,
                  education, certifications, keywords and more.
                </p>

                <div className="mt-6 grid gap-3 sm:grid-cols-3">
                  <MiniCapability
                    number="01"
                    title="Analyze"
                    text="Structure & content"
                  />

                  <MiniCapability
                    number="02"
                    title="Measure"
                    text="ATS & intelligence"
                  />

                  <MiniCapability
                    number="03"
                    title="Improve"
                    text="Actionable insights"
                  />
                </div>
              </div>
            </div>
          </section>
        )}

        {/* ========================================================
            UPLOAD WORKSPACE
        ======================================================== */}

        <section className="mb-6">
          <ResumeUploader
            onAnalysisComplete={handleAnalysisComplete}
          />
        </section>

        {/* ========================================================
            QUICK INTELLIGENCE
        ======================================================== */}

        {hasAnalysis && (
          <section className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              label="ATS score"
              value={atsScore.toFixed(0)}
              unit="/100"
              description="Applicant tracking readiness"
              icon="◎"
              accent="blue"
            />

            <StatCard
              label="Skills"
              value={skillCount}
              description="Relevant skills detected"
              icon="✦"
              accent="emerald"
            />

            <StatCard
              label="Projects"
              value={projectCount}
              description="Projects evaluated"
              icon="◇"
              accent="indigo"
            />

            <StatCard
              label="Keywords"
              value={matchedKeywords}
              description={`${missingKeywords} opportunities identified`}
              icon="⌁"
              accent="amber"
            />
          </section>
        )}

        {/* ========================================================
            INSIGHTS
        ======================================================== */}

        {hasAnalysis && (
          <section className="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">

            {/* RECOMMENDATIONS */}
            <div className="rounded-[26px] border border-white/[0.07] bg-[#090e1a] p-6 shadow-xl shadow-black/10 sm:p-7">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-blue-400">
                    Recommended next steps
                  </p>

                  <h2 className="mt-2 text-lg font-semibold text-white">
                    Highest-impact improvements
                  </h2>
                </div>

                <button
                  type="button"
                  onClick={() => navigate("/resume-analysis")}
                  className="rounded-md px-1 text-[10px] font-semibold text-slate-500 transition hover:text-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                >
                  View all →
                </button>
              </div>

              <div className="mt-6 space-y-3">
                {recommendations.length > 0 ? (
                  recommendations
                    .slice(0, 4)
                    .map((recommendation, index) => (
                      <Recommendation
                        key={`${recommendation}-${index}`}
                        number={index + 1}
                        text={recommendation}
                      />
                    ))
                ) : (
                  <EmptyInsight text="No recommendations available." />
                )}
              </div>
            </div>

            {/* STRENGTHS */}
            <div className="rounded-[26px] border border-white/[0.07] bg-[#090e1a] p-6 shadow-xl shadow-black/10 sm:p-7">
              <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-emerald-400">
                Resume strengths
              </p>

              <h2 className="mt-2 text-lg font-semibold text-white">
                What you're doing well
              </h2>

              <div className="mt-6 space-y-3">
                {strengths.length > 0 ? (
                  strengths
                    .slice(0, 4)
                    .map((strength, index) => (
                      <div
                        key={`${strength}-${index}`}
                        className="flex gap-3 rounded-xl border border-white/[0.05] bg-white/[0.015] p-3.5 transition-colors hover:border-emerald-400/10"
                      >
                        <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-400/10 text-[9px] font-bold text-emerald-400">
                          ✓
                        </span>

                        <p className="text-xs leading-5 text-slate-400">
                          {strength}
                        </p>
                      </div>
                    ))
                ) : (
                  <EmptyInsight text="Your detailed strengths will appear here." />
                )}
              </div>
            </div>
          </section>
        )}

        {/* ========================================================
            EMPTY STATE CAPABILITIES
        ======================================================== */}

        {!hasAnalysis && (
          <section className="grid gap-4 md:grid-cols-3">
            <CapabilityCard
              index="01"
              title="Resume Analysis"
              description="Understand structure, readability, sections, content quality and overall resume intelligence."
            />

            <CapabilityCard
              index="02"
              title="ATS Intelligence"
              description="Discover keyword coverage, missing terms and the signals that affect automated screening."
            />

            <CapabilityCard
              index="03"
              title="Job Matching"
              description="Compare your resume against real job descriptions and identify the strongest opportunities."
            />
          </section>
        )}
      </main>
    </div>
  );
}

/* ================================================================
   SCORE RING
================================================================ */

function ScoreRing({ score }) {
  const radius = 48;
  const circumference = 2 * Math.PI * radius;

  const safeScore = Math.min(
    100,
    Math.max(0, Number(score) || 0)
  );

  const offset =
    circumference -
    (safeScore / 100) * circumference;

  return (
    <div
      className="relative h-32 w-32 shrink-0"
      aria-label={`Resume intelligence score: ${safeScore.toFixed(0)} out of 100`}
    >
      <svg
        className="h-full w-full -rotate-90"
        viewBox="0 0 120 120"
        aria-hidden="true"
      >
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          className="text-white/[0.05]"
        />

        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="text-blue-500 transition-all duration-1000"
        />
      </svg>

      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold tracking-tight text-white">
          {safeScore.toFixed(0)}
        </span>

        <span className="text-[8px] font-bold uppercase tracking-[0.16em] text-slate-600">
          score
        </span>
      </div>
    </div>
  );
}

/* ================================================================
   METRIC BAR
================================================================ */

function MetricBar({ label, value, suffix }) {
  const safeValue = Math.min(
    100,
    Math.max(0, Number(value) || 0)
  );

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400">
          {label}
        </span>

        <span className="text-xs font-semibold text-slate-300">
          {safeValue.toFixed(0)}
          {suffix}
        </span>
      </div>

      <div
        className="h-1.5 overflow-hidden rounded-full bg-white/[0.05]"
        role="progressbar"
        aria-label={`${label}: ${safeValue.toFixed(0)}${suffix}`}
        aria-valuenow={safeValue}
        aria-valuemin="0"
        aria-valuemax="100"
      >
        <div
          className="h-full rounded-full bg-gradient-to-r from-blue-600 to-indigo-400 transition-all duration-1000"
          style={{ width: `${safeValue}%` }}
        />
      </div>
    </div>
  );
}

/* ================================================================
   STAT CARD
================================================================ */

function StatCard({
  label,
  value,
  unit,
  description,
  icon,
  accent,
}) {
  const accentClasses = {
    blue: "bg-blue-500/10 text-blue-400",
    emerald: "bg-emerald-500/10 text-emerald-400",
    indigo: "bg-indigo-500/10 text-indigo-400",
    amber: "bg-amber-500/10 text-amber-400",
  };

  return (
    <div className="group rounded-2xl border border-white/[0.07] bg-[#090e1a] p-5 shadow-xl shadow-black/5 transition-all duration-200 hover:-translate-y-0.5 hover:border-white/[0.11] hover:shadow-black/20">
      <div className="flex items-start justify-between">
        <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-600">
          {label}
        </p>

        <span
          aria-hidden="true"
          className={`flex h-8 w-8 items-center justify-center rounded-lg text-sm ${
            accentClasses[accent] || accentClasses.blue
          }`}
        >
          {icon}
        </span>
      </div>

      <div className="mt-5 flex items-end gap-1">
        <span className="text-3xl font-bold tracking-tight text-white">
          {value}
        </span>

        {unit && (
          <span className="mb-1 text-xs text-slate-600">
            {unit}
          </span>
        )}
      </div>

      <p className="mt-1.5 text-[10px] text-slate-600">
        {description}
      </p>
    </div>
  );
}

/* ================================================================
   RECOMMENDATION
================================================================ */

function Recommendation({ number, text }) {
  return (
    <div className="group flex gap-4 rounded-xl border border-white/[0.05] bg-white/[0.015] p-4 transition-all duration-200 hover:border-blue-500/10 hover:bg-blue-500/[0.02]">
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-[10px] font-bold text-blue-400">
        {String(number).padStart(2, "0")}
      </span>

      <p className="text-xs leading-5 text-slate-400">
        {text}
      </p>
    </div>
  );
}

/* ================================================================
   INSIGHT PILL
================================================================ */

function InsightPill({ label }) {
  return (
    <span className="rounded-lg border border-white/[0.06] bg-white/[0.025] px-3 py-2 text-[9px] font-medium text-slate-500">
      {label}
    </span>
  );
}

/* ================================================================
   MINI CAPABILITY
================================================================ */

function MiniCapability({ number, title, text }) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3.5 transition-colors hover:border-white/[0.1]">
      <span className="text-[9px] font-bold tracking-wider text-blue-400">
        {number}
      </span>

      <p className="mt-2 text-xs font-semibold text-slate-300">
        {title}
      </p>

      <p className="mt-1 text-[9px] text-slate-600">
        {text}
      </p>
    </div>
  );
}

/* ================================================================
   CAPABILITY CARD
================================================================ */

function CapabilityCard({
  index,
  title,
  description,
}) {
  return (
    <div className="group rounded-[22px] border border-white/[0.06] bg-[#090e1a] p-6 shadow-xl shadow-black/5 transition-all duration-200 hover:-translate-y-1 hover:border-blue-500/15 hover:shadow-black/20">
      <span className="text-[10px] font-bold tracking-[0.18em] text-blue-400">
        {index}
      </span>

      <h3 className="mt-5 text-sm font-semibold text-slate-200">
        {title}
      </h3>

      <p className="mt-2 text-xs leading-5 text-slate-600">
        {description}
      </p>

      <div className="mt-5 h-px w-8 bg-blue-500/30 transition-all duration-300 group-hover:w-14" />
    </div>
  );
}

/* ================================================================
   EMPTY INSIGHT
================================================================ */

function EmptyInsight({ text }) {
  return (
    <div className="rounded-xl border border-dashed border-white/[0.06] p-5 text-center text-xs text-slate-600">
      {text}
    </div>
  );
}

export default Dashboard;