import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useResumeContext } from "../../context/ResumeContext";
import useJobMatching from "../../hooks/useJobMatching";

// ============================================================================
// Helpers
// ============================================================================

function toArray(value) {
  return Array.isArray(value) ? value : [];
}

function toObject(value) {
  return value &&
    typeof value === "object" &&
    !Array.isArray(value)
    ? value
    : {};
}

function toNumber(value, fallback = 0) {
  const number = Number(value);

  return Number.isFinite(number) ? number : fallback;
}

function formatLabel(value) {
  if (!value) {
    return "";
  }

  return String(value)
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatRequirement(requirement) {
  if (typeof requirement === "string") {
    return requirement;
  }

  if (requirement && typeof requirement === "object") {
    return (
      requirement.skill ||
      requirement.name ||
      requirement.requirement ||
      requirement.title ||
      ""
    );
  }

  return "";
}

function getRequirementMatched(requirement) {
  if (!requirement || typeof requirement !== "object") {
    return false;
  }

  return (
    requirement.matched === true ||
    requirement.is_matched === true ||
    requirement.match === true
  );
}

function getScoreLabel(score) {
  if (score >= 85) {
    return "Excellent match";
  }

  if (score >= 70) {
    return "Strong match";
  }

  if (score >= 55) {
    return "Moderate match";
  }

  if (score > 0) {
    return "Needs improvement";
  }

  return "No match";
}

function getReadinessLabel(value) {
  if (!value) {
    return "Not available";
  }

  return String(value);
}

function getPriorityClasses(priority) {
  const normalized = String(priority || "").toLowerCase();

  if (normalized === "critical") {
    return "border-red-500/20 bg-red-500/10 text-red-300";
  }

  if (normalized === "high") {
    return "border-orange-500/20 bg-orange-500/10 text-orange-300";
  }

  if (normalized === "important") {
    return "border-yellow-500/20 bg-yellow-500/10 text-yellow-300";
  }

  if (normalized === "supporting") {
    return "border-blue-500/20 bg-blue-500/10 text-blue-300";
  }

  return "border-white/10 bg-white/5 text-slate-400";
}

// ============================================================================
// Small UI Components
// ============================================================================

function StatCard({
  label,
  value,
  helper,
  icon,
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-5 shadow-lg shadow-black/10">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-400">
            {label}
          </p>

          <p className="mt-2 text-2xl font-bold text-white">
            {value}
          </p>

          {helper && (
            <p className="mt-1 text-xs text-slate-500">
              {helper}
            </p>
          )}
        </div>

        {icon && (
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-lg">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}

function SkillBadge({
  children,
  matched = false,
  critical = false,
}) {
  return (
    <span
      className={[
        "inline-flex items-center rounded-full border px-3 py-1.5 text-xs font-medium",
        matched
          ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-300"
          : critical
            ? "border-red-500/20 bg-red-500/10 text-red-300"
            : "border-amber-500/20 bg-amber-500/10 text-amber-300",
      ].join(" ")}
    >
      {matched ? "✓ " : critical ? "⚠ " : ""}
      {children}
    </span>
  );
}

function Section({
  title,
  description,
  children,
  right,
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900/70 shadow-lg shadow-black/10">
      <div className="flex flex-col gap-3 border-b border-white/10 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">
            {title}
          </h2>

          {description && (
            <p className="mt-1 text-sm leading-6 text-slate-400">
              {description}
            </p>
          )}
        </div>

        {right}
      </div>

      <div className="p-6">
        {children}
      </div>
    </section>
  );
}

function EmptyState({
  icon = "📄",
  title,
  description,
  action,
}) {
  return (
    <div className="rounded-2xl border border-dashed border-white/10 bg-slate-950/40 px-6 py-10 text-center">
      <div className="text-3xl">{icon}</div>

      <h3 className="mt-3 text-base font-semibold text-white">
        {title}
      </h3>

      <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-400">
        {description}
      </p>

      {action && (
        <div className="mt-5">
          {action}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Requirement Row
// ============================================================================

function RequirementRow({
  requirement,
}) {
  const name =
    formatRequirement(requirement) ||
    "Unnamed requirement";

  const matched =
    getRequirementMatched(requirement);

  const priority =
    requirement &&
    typeof requirement === "object"
      ? requirement.priority
      : null;

  const weight =
    requirement &&
    typeof requirement === "object"
      ? requirement.weight
      : null;

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-white/10 bg-slate-950/30 p-4 transition hover:border-white/15 hover:bg-slate-950/50 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex min-w-0 items-start gap-3">
        <div
          className={[
            "mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm font-bold",
            matched
              ? "bg-emerald-500/10 text-emerald-300"
              : "bg-red-500/10 text-red-300",
          ].join(" ")}
        >
          {matched ? "✓" : "×"}
        </div>

        <div className="min-w-0">
          <p className="break-words text-sm font-semibold text-white">
            {name}
          </p>

          <div className="mt-2 flex flex-wrap gap-2">
            {priority && (
              <span
                className={[
                  "rounded-full border px-2 py-0.5 text-[11px] font-medium",
                  getPriorityClasses(priority),
                ].join(" ")}
              >
                {formatLabel(priority)}
              </span>
            )}

            {weight !== null &&
              weight !== undefined && (
                <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-[11px] font-medium text-slate-400">
                  Weight {weight}
                </span>
              )}
          </div>
        </div>
      </div>

      <span
        className={[
          "shrink-0 text-xs font-semibold",
          matched
            ? "text-emerald-300"
            : "text-red-300",
        ].join(" ")}
      >
        {matched ? "Matched" : "Missing"}
      </span>
    </div>
  );
}

// ============================================================================
// Category Coverage
// ============================================================================

function CategoryCoverage({
  categoryCoverage,
}) {
  const entries =
    Object.entries(categoryCoverage);

  if (!entries.length) {
    return (
      <p className="text-sm text-slate-500">
        Category coverage data is not available for
        this match.
      </p>
    );
  }

  return (
    <div className="space-y-5">
      {entries.map(
        ([category, value]) => {
          const objectValue =
            toObject(value);

          const percentage = toNumber(
            objectValue.percentage ??
              objectValue.coverage ??
              objectValue.score ??
              value,
            0
          );

          const matched = toNumber(
            objectValue.matched,
            0
          );

          const total = toNumber(
            objectValue.total,
            0
          );

          const displayPercentage =
            Math.max(
              0,
              Math.min(100, percentage)
            );

          return (
            <div
              key={category}
              className="space-y-2"
            >
              <div className="flex items-center justify-between gap-4">
                <span className="text-sm font-medium text-slate-300">
                  {formatLabel(category)}
                </span>

                <div className="flex items-center gap-2">
                  {total > 0 && (
                    <span className="text-xs text-slate-500">
                      {matched}/{total}
                    </span>
                  )}

                  <span className="text-sm font-semibold text-white">
                    {Math.round(
                      displayPercentage
                    )}
                    %
                  </span>
                </div>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full bg-white transition-all"
                  style={{
                    width: `${displayPercentage}%`,
                  }}
                />
              </div>
            </div>
          );
        }
      )}
    </div>
  );
}

// ============================================================================
// Category Skill Groups
// ============================================================================

function CategorySkills({
  categories,
  emptyMessage,
}) {
  const entries =
    Object.entries(categories);

  if (!entries.length) {
    return (
      <p className="text-sm text-slate-500">
        {emptyMessage}
      </p>
    );
  }

  return (
    <div className="space-y-5">
      {entries.map(
        ([category, skills]) => {
          const normalizedSkills =
            toArray(skills);

          if (!normalizedSkills.length) {
            return null;
          }

          return (
            <div key={category}>
              <h3 className="mb-2 text-sm font-semibold text-slate-300">
                {formatLabel(category)}
              </h3>

              <div className="flex flex-wrap gap-2">
                {normalizedSkills.map(
                  (skill, index) => (
                    <span
                      key={`${category}-${skill}-${index}`}
                      className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-400"
                    >
                      {skill}
                    </span>
                  )
                )}
              </div>
            </div>
          );
        }
      )}
    </div>
  );
}

// ============================================================================
// Main Page
// ============================================================================

function JobMatching() {
  const navigate = useNavigate();

  const {
    resumeFile,
    analysis,
  } = useResumeContext();

  const {
    result,
    loading,
    error,
    matchJob,
    clearResult,
  } = useJobMatching();

  const [
    jobDescription,
    setJobDescription,
  ] = useState("");

  const normalizedResult =
    result &&
    typeof result === "object"
      ? result
      : null;

  const matchScore = toNumber(
    normalizedResult?.match_score,
    0
  );

  const matchLevel =
    normalizedResult?.match_level ||
    getScoreLabel(matchScore);

  const applicationReadiness =
    normalizedResult?.application_readiness ||
    "Not available";

  const matchedSkills = toArray(
    normalizedResult?.matched_skills
  );

  const missingSkills = toArray(
    normalizedResult?.missing_skills
  );

  const criticalMissingSkills =
    toArray(
      normalizedResult?.critical_missing_skills
    );

  const requirements = toArray(
    normalizedResult?.requirements
  );

  const categoryCoverage =
    toObject(
      normalizedResult?.category_coverage
    );

  const resumeCategories =
    toObject(
      normalizedResult?.resume_categories
    );

  const jobCategories =
    toObject(
      normalizedResult?.job_categories
    );

  const requirementCoverage =
    toObject(
      normalizedResult?.requirement_coverage
    );

  const requirementPriorities =
    toObject(
      normalizedResult?.requirement_priorities
    );

  const requirementWeights =
    toObject(
      normalizedResult?.requirement_weights
    );

  const requirementPriorityCounts =
    toObject(
      normalizedResult?.requirement_priority_counts
    );

  const suggestions = toArray(
    normalizedResult?.suggestions
  );

  const matchedRequirementCount =
    toNumber(
      requirementCoverage.matched,
      matchedSkills.length
    );

  const totalRequirementCount =
    toNumber(
      requirementCoverage.total,
      requirements.length
    );

  const weightedScore = toNumber(
    requirementCoverage.weighted_score,
    0
  );

  const coveragePercentage = toNumber(
    requirementCoverage.percentage,
    totalRequirementCount > 0
      ? (matchedRequirementCount /
          totalRequirementCount) *
          100
      : 0
  );

  const normalizedCoveragePercentage =
    Math.max(
      0,
      Math.min(100, coveragePercentage)
    );

  const priorityEntries = useMemo(
    () =>
      Object.entries(
        requirementPriorityCounts
      ),
    [requirementPriorityCounts]
  );

  const hasStoredAnalysis =
    Boolean(analysis);

  const handleAnalyze = async () => {
    if (!resumeFile) {
      return;
    }

    if (!jobDescription.trim()) {
      return;
    }

    await matchJob(
      resumeFile,
      jobDescription.trim()
    );
  };

  const handleDescriptionChange = (
    event
  ) => {
    setJobDescription(event.target.value);

    if (result) {
      clearResult();
    }
  };

  const handleUploadResume = () => {
    navigate("/dashboard");
  };

  return (
    <div className="min-h-full bg-slate-950 text-slate-200">
      {/* ================================================================= */}
      {/* Header                                                           */}
      {/* ================================================================= */}

      <div className="border-b border-white/10 bg-slate-950">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-400">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                Resume Intelligence
              </div>

              <h1 className="text-3xl font-bold tracking-tight text-white">
                Job Matching
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                Compare your resume against a
                target job description to identify
                matched requirements, skill gaps,
                priorities, and application
                readiness.
              </p>
            </div>

            {resumeFile && (
              <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3">
                <div className="flex items-center gap-2">
                  <span className="text-emerald-300">
                    ✓
                  </span>

                  <div>
                    <p className="text-xs font-semibold text-emerald-300">
                      Resume ready
                    </p>

                    <p className="max-w-xs truncate text-xs text-emerald-400/80">
                      {resumeFile.name}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6 lg:px-8">
        {/* ================================================================= */}
        {/* Input                                                            */}
        {/* ================================================================= */}

        <Section
          title="Match your resume to a job"
          description="Paste the target job description below."
          right={
            resumeFile ? (
              <span className="text-xs font-medium text-emerald-300">
                Resume attached
              </span>
            ) : (
              <span className="text-xs font-medium text-amber-300">
                Resume file required
              </span>
            )
          }
        >
          {!resumeFile ? (
            <EmptyState
              icon="📄"
              title={
                hasStoredAnalysis
                  ? "Your analysis is saved, but the original resume file is not available"
                  : "Upload a resume first"
              }
              description={
                hasStoredAnalysis
                  ? "Your previous resume analysis is still available. Job Matching requires the original PDF, DOC, or DOCX file because the backend extracts the uploaded document before matching it against the job description."
                  : "Upload and analyze your resume from the Dashboard before running a job match."
              }
              action={
                <button
                  type="button"
                  onClick={
                    handleUploadResume
                  }
                  className="rounded-xl bg-white px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
                >
                  Go to Dashboard
                </button>
              }
            />
          ) : (
            <div className="space-y-5">
              <div>
                <label
                  htmlFor="job-description"
                  className="mb-2 block text-sm font-semibold text-slate-200"
                >
                  Job description
                </label>

                <textarea
                  id="job-description"
                  value={jobDescription}
                  onChange={
                    handleDescriptionChange
                  }
                  placeholder="Paste the complete job description here..."
                  rows={12}
                  className="w-full resize-y rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm leading-6 text-white outline-none transition placeholder:text-slate-600 focus:border-white/20 focus:ring-2 focus:ring-white/10"
                />

                <div className="mt-2 flex justify-between gap-4 text-xs text-slate-600">
                  <span>
                    Include responsibilities,
                    requirements, and preferred
                    qualifications when available.
                  </span>

                  <span className="shrink-0">
                    {jobDescription.length} chars
                  </span>
                </div>
              </div>

              {error && (
                <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                  {error}
                </div>
              )}

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-xs text-slate-500">
                  The backend will extract the
                  resume text and compare it with
                  the job requirements.
                </p>

                <button
                  type="button"
                  onClick={handleAnalyze}
                  disabled={
                    loading ||
                    !jobDescription.trim()
                  }
                  className={[
                    "rounded-xl px-6 py-3 text-sm font-semibold transition",
                    loading ||
                    !jobDescription.trim()
                      ? "cursor-not-allowed bg-white/10 text-slate-600"
                      : "bg-white text-slate-950 hover:bg-slate-200",
                  ].join(" ")}
                >
                  {loading
                    ? "Analyzing..."
                    : "Analyze Match"}
                </button>
              </div>
            </div>
          )}
        </Section>

        {/* ================================================================= */}
        {/* Results                                                          */}
        {/* ================================================================= */}

        {normalizedResult && (
          <>
            {/* ============================================================= */}
            {/* Score Overview                                                */}
            {/* ============================================================= */}

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard
                label="Match Score"
                value={`${Math.round(
                  matchScore
                )}%`}
                helper={matchLevel}
                icon="🎯"
              />

              <StatCard
                label="Requirements"
                value={`${matchedRequirementCount}/${totalRequirementCount}`}
                helper={`${Math.round(
                  normalizedCoveragePercentage
                )}% coverage`}
                icon="✓"
              />

              <StatCard
                label="Missing Skills"
                value={missingSkills.length}
                helper={`${criticalMissingSkills.length} critical`}
                icon="⚠"
              />

              <StatCard
                label="Weighted Score"
                value={`${Math.round(
                  weightedScore
                )}`}
                helper="Requirement weighting"
                icon="⚖"
              />
            </div>

            {/* ============================================================= */}
            {/* Match Summary                                                 */}
            {/* ============================================================= */}

            <Section
              title="Match summary"
              description="High-level compatibility between your resume and the target role."
            >
              <div className="grid gap-6 lg:grid-cols-[220px_1fr]">
                <div className="flex flex-col items-center justify-center rounded-2xl border border-white/10 bg-slate-950/40 p-6 text-center">
                  <div className="flex h-36 w-36 items-center justify-center rounded-full border-[12px] border-white/10">
                    <div>
                      <p className="text-3xl font-bold text-white">
                        {Math.round(
                          matchScore
                        )}
                        %
                      </p>

                      <p className="mt-1 text-xs font-medium text-slate-500">
                        Match
                      </p>
                    </div>
                  </div>

                  <p className="mt-4 text-sm font-semibold text-white">
                    {matchLevel}
                  </p>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-xl border border-white/10 bg-slate-950/30 p-5">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Application readiness
                    </p>

                    <p className="mt-2 text-lg font-bold text-white">
                      {getReadinessLabel(
                        applicationReadiness
                      )}
                    </p>

                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      This reflects the alignment
                      returned by the job matching
                      engine.
                    </p>
                  </div>

                  <div className="rounded-xl border border-white/10 bg-slate-950/30 p-5">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Requirement coverage
                    </p>

                    <p className="mt-2 text-lg font-bold text-white">
                      {Math.round(
                        normalizedCoveragePercentage
                      )}
                      %
                    </p>

                    <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
                      <div
                        className="h-full rounded-full bg-white"
                        style={{
                          width: `${normalizedCoveragePercentage}%`,
                        }}
                      />
                    </div>

                    <p className="mt-2 text-xs text-slate-500">
                      {matchedRequirementCount} of{" "}
                      {totalRequirementCount}{" "}
                      requirements matched.
                    </p>
                  </div>
                </div>
              </div>
            </Section>

            {/* ============================================================= */}
            {/* Skills                                                        */}
            {/* ============================================================= */}

            <div className="grid gap-6 lg:grid-cols-2">
              <Section
                title="Matched skills"
                description="Requirements demonstrated by the resume."
                right={
                  <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-300">
                    {matchedSkills.length} matched
                  </span>
                }
              >
                {matchedSkills.length ? (
                  <div className="flex flex-wrap gap-2">
                    {matchedSkills.map(
                      (skill, index) => (
                        <SkillBadge
                          key={`${skill}-${index}`}
                          matched
                        >
                          {skill}
                        </SkillBadge>
                      )
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">
                    No matched skills were returned
                    for this job.
                  </p>
                )}
              </Section>

              <Section
                title="Missing skills"
                description="Requirements not demonstrated by the resume."
                right={
                  <span className="rounded-full border border-amber-500/20 bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-300">
                    {missingSkills.length} missing
                  </span>
                }
              >
                {missingSkills.length ? (
                  <div className="flex flex-wrap gap-2">
                    {missingSkills.map(
                      (skill, index) => (
                        <SkillBadge
                          key={`${skill}-${index}`}
                        >
                          {skill}
                        </SkillBadge>
                      )
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">
                    No missing skills were returned.
                  </p>
                )}
              </Section>
            </div>

            {/* ============================================================= */}
            {/* Critical Gaps                                                 */}
            {/* ============================================================= */}

            <Section
              title="Critical skill gaps"
              description="Missing requirements identified as must-have or high-priority gaps."
              right={
                <span
                  className={[
                    "rounded-full px-3 py-1 text-xs font-semibold",
                    criticalMissingSkills.length
                      ? "border border-red-500/20 bg-red-500/10 text-red-300"
                      : "border border-emerald-500/20 bg-emerald-500/10 text-emerald-300",
                  ].join(" ")}
                >
                  {criticalMissingSkills.length
                    ? `${criticalMissingSkills.length} critical gap${
                        criticalMissingSkills.length ===
                        1
                          ? ""
                          : "s"
                      }`
                    : "No critical gaps"}
                </span>
              }
            >
              {criticalMissingSkills.length ? (
                <div className="flex flex-wrap gap-2">
                  {criticalMissingSkills.map(
                    (skill, index) => (
                      <SkillBadge
                        key={`${skill}-${index}`}
                        critical
                      >
                        {skill}
                      </SkillBadge>
                    )
                  )}
                </div>
              ) : (
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4">
                  <p className="text-sm font-medium text-emerald-300">
                    No critical missing
                    requirements were returned by
                    the matching engine.
                  </p>
                </div>
              )}
            </Section>

            {/* ============================================================= */}
            {/* Requirement Coverage                                          */}
            {/* ============================================================= */}

            <Section
              title="Requirement intelligence"
              description="Detailed requirement-by-requirement comparison."
            >
              {requirements.length ? (
                <div className="space-y-3">
                  {requirements.map(
                    (requirement, index) => (
                      <RequirementRow
                        key={`requirement-${index}`}
                        requirement={
                          requirement
                        }
                      />
                    )
                  )}
                </div>
              ) : (
                <p className="text-sm text-slate-500">
                  No detailed requirement records
                  were returned.
                </p>
              )}
            </Section>

            {/* ============================================================= */}
            {/* Requirement Priorities                                        */}
            {/* ============================================================= */}

            <Section
              title="Requirement priorities"
              description="How the matching engine grouped the job requirements."
            >
              {priorityEntries.length ? (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  {priorityEntries.map(
                    ([priority, count]) => (
                      <div
                        key={priority}
                        className="rounded-xl border border-white/10 bg-slate-950/30 p-4"
                      >
                        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                          {formatLabel(
                            priority
                          )}
                        </p>

                        <p className="mt-2 text-2xl font-bold text-white">
                          {count}
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          requirement
                          {Number(count) ===
                          1
                            ? ""
                            : "s"}
                        </p>
                      </div>
                    )
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  {Object.keys(
                    requirementPriorities
                  ).length ? (
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                      {Object.entries(
                        requirementPriorities
                      ).map(
                        ([
                          priority,
                          values,
                        ]) => (
                          <div
                            key={priority}
                            className="rounded-xl border border-white/10 bg-slate-950/30 p-4"
                          >
                            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                              {formatLabel(
                                priority
                              )}
                            </p>

                            <p className="mt-2 text-2xl font-bold text-white">
                              {toArray(
                                values
                              ).length}
                            </p>
                          </div>
                        )
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500">
                      Requirement priority data is
                      not available.
                    </p>
                  )}
                </div>
              )}

              {Object.keys(
                requirementWeights
              ).length > 0 && (
                <div className="mt-6">
                  <h3 className="mb-3 text-sm font-semibold text-slate-300">
                    Requirement weights
                  </h3>

                  <div className="flex flex-wrap gap-2">
                    {Object.entries(
                      requirementWeights
                    ).map(
                      ([skill, weight]) => (
                        <span
                          key={skill}
                          className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-400"
                        >
                          {skill}: {weight}
                        </span>
                      )
                    )}
                  </div>
                </div>
              )}
            </Section>

            {/* ============================================================= */}
            {/* Category Coverage                                             */}
            {/* ============================================================= */}

            <Section
              title="Category coverage"
              description="Coverage across technical and professional requirement categories."
            >
              <CategoryCoverage
                categoryCoverage={
                  categoryCoverage
                }
              />
            </Section>

            {/* ============================================================= */}
            {/* Resume vs Job Categories                                      */}
            {/* ============================================================= */}

            <div className="grid gap-6 lg:grid-cols-2">
              <Section
                title="Resume skill profile"
                description="Skills grouped by the matching engine's categories."
              >
                <CategorySkills
                  categories={
                    resumeCategories
                  }
                  emptyMessage="No resume category data was returned."
                />
              </Section>

              <Section
                title="Job requirement profile"
                description="Requirements grouped by the matching engine's categories."
              >
                <CategorySkills
                  categories={
                    jobCategories
                  }
                  emptyMessage="No job category data was returned."
                />
              </Section>
            </div>

            {/* ============================================================= */}
            {/* Suggestions                                                   */}
            {/* ============================================================= */}

            <Section
              title="Recommended next steps"
              description="Actions returned by the job matching engine."
            >
              {suggestions.length ? (
                <div className="space-y-3">
                  {suggestions.map(
                    (suggestion, index) => {
                      const text =
                        typeof suggestion ===
                        "string"
                          ? suggestion
                          : suggestion &&
                              typeof suggestion ===
                                "object"
                            ? suggestion.text ||
                              suggestion.message ||
                              suggestion.recommendation ||
                              suggestion.title ||
                              ""
                            : "";

                      if (!text) {
                        return null;
                      }

                      return (
                        <div
                          key={`suggestion-${index}`}
                          className="flex gap-3 rounded-xl border border-white/10 bg-slate-950/30 p-4"
                        >
                          <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-sm font-semibold text-slate-300">
                            {index + 1}
                          </div>

                          <p className="text-sm leading-6 text-slate-300">
                            {text}
                          </p>
                        </div>
                      );
                    }
                  )}
                </div>
              ) : (
                <p className="text-sm text-slate-500">
                  No additional suggestions were
                  returned for this match.
                </p>
              )}
            </Section>

            {/* ============================================================= */}
            {/* Footer Action                                                 */}
            {/* ============================================================= */}

            <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-slate-900/70 p-5 shadow-lg shadow-black/10 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-white">
                  Want to improve your match?
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Use the missing and critical
                  requirements above to strengthen
                  your resume where the experience is
                  genuine.
                </p>
              </div>

              <button
                type="button"
                onClick={() =>
                  navigate(
                    "/resume-analysis"
                  )
                }
                className="rounded-xl border border-white/10 bg-white/5 px-5 py-2.5 text-sm font-semibold text-slate-300 transition hover:bg-white/10 hover:text-white"
              >
                Review Resume Analysis
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default JobMatching;