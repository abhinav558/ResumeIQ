import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useResumeContext } from "../../context/ResumeContext";

// ============================================================================
// Helpers
// ============================================================================

function toArray(value) {
  return Array.isArray(value) ? value : [];
}

function toObject(value) {
  return value && typeof value === "object" && !Array.isArray(value) ? value : {};
}

function toNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function toBoolean(value) {
  return value === true;
}

function formatLabel(value) {
  if (!value) return "";
  return String(value)
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatSignal(value) {
  if (typeof value === "string") return value;
  if (value && typeof value === "object") {
    return value.text || value.message || value.description || value.recommendation || value.title || value.name || "";
  }
  return String(value ?? "");
}

// ============================================================================
// Main Component
// ============================================================================

function ATSIntelligence() {
  const navigate = useNavigate();
  const { analysis } = useResumeContext();

  const ats = toObject(analysis?.ats_analysis);
  const keywordAnalysis = toObject(ats.keyword_analysis);
  const priorities = toObject(keywordAnalysis.priorities);

  const atsScore = toNumber(ats.ats_score, 0);
  const keywordScore = toNumber(keywordAnalysis.score, 0);

  const matchedKeywords = toArray(ats.matched_keywords?.length ? ats.matched_keywords : keywordAnalysis.matched);
  const missingKeywords = toArray(ats.missing_keywords?.length ? ats.missing_keywords : keywordAnalysis.missing);

  const strengths = toArray(ats.strengths);
  const issues = toArray(ats.issues);
  const recommendations = toArray(ats.recommendations);
  const actionVerbs = toArray(ats.action_verbs_found);
  const metrics = toArray(ats.metrics_found);

  const technologyCoverage = toObject(ats.technology_coverage);
  const technologies = toArray(technologyCoverage.technologies);
  const technologyCategories = toObject(technologyCoverage.categories);

  const sectionAnalysis = toObject(ats.section_analysis);
  const sectionsPresent = toArray(sectionAnalysis.present);
  const sectionsMissing = toArray(sectionAnalysis.missing);
  const hasExperience = toBoolean(sectionAnalysis.has_experience);

  const deploymentAnalysis = toObject(ats.deployment_analysis);
  const applicationServing = toArray(deploymentAnalysis.application_serving);
  const productionDeployment = toArray(deploymentAnalysis.production_deployment);
  const hasApplicationServing = toBoolean(deploymentAnalysis.has_application_serving);
  const hasProductionDeployment = toBoolean(deploymentAnalysis.has_production_deployment);

  const scoringAnalysis = toObject(ats.analysis);
  const keywordStrength = toNumber(scoringAnalysis.keyword_strength, 0);
  const sectionQuality = toNumber(scoringAnalysis.section_quality, 0);
  const technicalContext = toNumber(scoringAnalysis.technical_context, 0);
  const readability = toNumber(scoringAnalysis.readability, 0);
  const contentImpact = toNumber(scoringAnalysis.impact_score, 0);
  const contributionTotal = toNumber(scoringAnalysis.contribution_total, atsScore);
  const scoreConsistent = toBoolean(scoringAnalysis.score_consistent);
  const wordCount = toNumber(ats.word_count, 0);

  const atsStatus = useMemo(() => {
    if (atsScore >= 85)
      return {
        label: "Excellent",
        description: "Your resume is strongly optimized for automated screening systems.",
      };
    if (atsScore >= 70)
      return {
        label: "Good",
        description: "Your resume has a solid ATS foundation but still has optimization opportunities.",
      };
    if (atsScore >= 55)
      return {
        label: "Needs improvement",
        description: "Your resume may pass some automated screens, but important optimization gaps remain.",
      };
    return {
      label: "Needs attention",
      description: "Your resume has significant ATS weaknesses that could reduce screening performance.",
    };
  }, [atsScore]);

  const keywordStatus = useMemo(() => {
    if (keywordScore >= 80) return "Excellent";
    if (keywordScore >= 65) return "Strong";
    if (keywordScore >= 50) return "Moderate";
    return "Weak";
  }, [keywordScore]);

  const priorityGroups = [
    {
      key: "critical",
      label: "Critical",
      description: "Core technologies and competencies that strongly influence role relevance.",
      data: toObject(priorities.critical),
    },
    {
      key: "high",
      label: "High priority",
      description: "Frequently valuable skills that can materially improve matching.",
      data: toObject(priorities.high),
    },
    {
      key: "important",
      label: "Important",
      description: "Relevant skills that can strengthen broader job compatibility.",
      data: toObject(priorities.important),
    },
    {
      key: "supporting",
      label: "Supporting",
      description: "Additional technologies and tools that improve technical coverage.",
      data: toObject(priorities.supporting),
    },
    {
      key: "optional",
      label: "Optional",
      description: "Lower-priority terms that may provide additional role alignment.",
      data: toObject(priorities.optional),
    },
  ];

  const keywordPriorityMap = useMemo(() => {
    const map = new Map();
    priorityGroups.forEach((group) => {
      const missing = toArray(group.data.missing);
      missing.forEach((keyword) => {
        const normalized = String(keyword).trim().toLowerCase();
        if (normalized) map.set(normalized, group.label);
      });
    });
    return map;
  }, [priorities]);

  const recommendationItems = recommendations.map(formatSignal).filter(Boolean);
  const issueItems = issues.map(formatSignal).filter(Boolean);
  const strengthItems = strengths.map(formatSignal).filter(Boolean);

  if (!analysis) {
    return (
      <div className="min-h-screen bg-[#050816] text-white">
        <div className="mx-auto flex min-h-screen max-w-4xl items-center justify-center px-6">
          <div className="w-full rounded-[32px] border border-white/[0.08] bg-[#0a1020] p-10 text-center shadow-2xl">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-blue-400/10 bg-blue-500/10 text-2xl text-blue-400">◈</div>
            <h1 className="mt-6 text-2xl font-bold tracking-tight">ATS Intelligence is waiting</h1>
            <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-slate-500">
              Upload and analyze your resume first. ResumeIQ will then build your ATS intelligence profile using the analysis
              results.
            </p>
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              className="mt-7 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:-translate-y-0.5 hover:bg-blue-500"
            >
              Analyze resume
              <span className="ml-2">→</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050816] text-white">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -right-56 -top-56 h-[650px] w-[650px] rounded-full bg-blue-600/[0.06] blur-[160px]" />
        <div className="absolute -bottom-64 -left-56 h-[650px] w-[650px] rounded-full bg-indigo-600/[0.05] blur-[160px]" />
      </div>

      <main className="relative mx-auto max-w-[1500px] px-5 py-7 sm:px-8 lg:px-10">
        {/* Header */}
        <header className="mb-8">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="mb-3 flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => navigate("/dashboard")}
                  className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.025] text-slate-400 transition hover:border-blue-500/20 hover:bg-blue-500/[0.06] hover:text-white"
                  aria-label="Back to dashboard"
                >
                  ←
                </button>
                <span className="text-[10px] font-semibold uppercase tracking-[0.22em] text-blue-400">ResumeIQ Intelligence</span>
              </div>
              <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">ATS Intelligence</h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                Understand how automated hiring systems interpret your resume, where your keyword coverage is strong, and which
                optimization opportunities can improve your screening performance.
              </p>
            </div>
            <button
              type="button"
              onClick={() => navigate("/resume-analysis")}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.025] px-5 py-3 text-xs font-semibold text-slate-300 transition hover:border-blue-500/20 hover:bg-blue-500/[0.05] hover:text-white"
            >
              Resume analysis
              <span>→</span>
            </button>
          </div>
        </header>

        {/* Hero score */}
        <section className="mb-6 grid gap-5 lg:grid-cols-[1.35fr_0.65fr]">
          <div className="relative overflow-hidden rounded-[28px] border border-white/[0.08] bg-[#0a1020] p-7 shadow-2xl">
            <div className="absolute right-0 top-0 h-72 w-72 rounded-full bg-blue-500/[0.06] blur-[100px]" />
            <div className="relative">
              <div className="flex flex-col gap-7 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">ATS readiness score</p>
                  <div className="mt-4 flex items-end gap-3">
                    <span className="text-6xl font-bold tracking-tight text-white">{atsScore.toFixed(0)}</span>
                    <span className="mb-2 text-lg text-slate-600">/ 100</span>
                  </div>
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    <span className="rounded-full border border-blue-400/10 bg-blue-500/10 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-blue-400">
                      {atsStatus.label}
                    </span>
                    <span className="text-xs text-slate-600">Automated screening readiness</span>
                  </div>
                </div>
                <ScoreRing score={atsScore} />
              </div>
              <div className="mt-7 h-2 overflow-hidden rounded-full bg-white/[0.05]">
                <div
                  className="h-full rounded-full bg-blue-500 transition-all duration-700"
                  style={{ width: `${Math.min(Math.max(atsScore, 0), 100)}%` }}
                />
              </div>
              <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-500">{atsStatus.description}</p>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/[0.08] bg-[#0a1020] p-7">
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">Keyword intelligence</p>
            <div className="mt-5 flex items-end justify-between">
              <div>
                <p className="text-4xl font-bold text-white">{keywordScore.toFixed(0)}</p>
                <p className="mt-1 text-xs text-slate-600">Keyword coverage score</p>
              </div>
              <span className="rounded-full bg-white/[0.04] px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                {keywordStatus}
              </span>
            </div>
            <div className="mt-6 grid grid-cols-2 gap-3">
              <MiniMetric label="Matched" value={matchedKeywords.length} />
              <MiniMetric label="Potential gaps" value={missingKeywords.length} />
              <MiniMetric label="Action verbs" value={actionVerbs.length} />
              <MiniMetric label="Metrics" value={metrics.length} />
            </div>
          </div>
        </section>

        {/* Executive snapshot */}
        <section className="mb-6 grid gap-4 md:grid-cols-3">
          <InsightCard
            eyebrow="Keyword coverage"
            title={`${matchedKeywords.length} relevant keywords detected`}
            description="These terms are already present in your resume and can contribute to job relevance."
            icon="✓"
          />
          <InsightCard
            eyebrow="Optimization gap"
            title={`${missingKeywords.length} potential keywords absent`}
            description="These terms are not detected in the resume. Review them for relevance and add them only when you genuinely have the skill or experience."
            icon="!"
          />
          <InsightCard
            eyebrow="Evidence quality"
            title={`${metrics.length} measurable signals found`}
            description="Metrics help demonstrate impact and can improve the credibility of experience and project claims."
            icon="↗"
          />
        </section>

        {/* ATS score composition */}
        <section className="mb-6 rounded-[28px] border border-white/[0.08] bg-[#0a1020] p-6 sm:p-7">
          <SectionHeading
            eyebrow="ATS score composition"
            title="How the ATS score is supported"
            description="ResumeIQ evaluates multiple dimensions of ATS readiness rather than relying only on keyword counts."
          />
          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <ScoreSignal label="Keyword strength" score={keywordStrength} />
            <ScoreSignal label="Section quality" score={sectionQuality} />
            <ScoreSignal label="Technical context" score={technicalContext} />
            <ScoreSignal label="Readability" score={readability} />
            <ScoreSignal label="Impact evidence" score={contentImpact} />
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <MiniMetric label="Resume words" value={wordCount} />
            <MiniMetric label="Sections detected" value={sectionsPresent.length} />
            <MiniMetric label="Technologies" value={technologies.length} />
            <MiniMetric label="Contribution total" value={contributionTotal.toFixed(2)} />
            <MiniMetric label="Score consistency" value={scoreConsistent ? "Verified" : "Check"} />
          </div>
          <div className="mt-5 rounded-2xl border border-blue-400/[0.08] bg-blue-400/[0.025] p-4">
            <div className="flex gap-3">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-xs font-bold text-blue-400">
                i
              </span>
              <div>
                <p className="text-xs font-semibold text-slate-300">Score interpretation</p>
                <p className="mt-1 text-[11px] leading-5 text-slate-600">
                  The values above are contribution signals used by the ATS engine. They are not independent percentages and should
                  not be interpreted as separate ATS scores.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Keyword priorities */}
        <section className="mb-6 rounded-[28px] border border-white/[0.08] bg-[#0a1020] p-6 sm:p-7">
          <SectionHeading
            eyebrow="Keyword strategy"
            title="Priority keyword map"
            description="Not every missing keyword deserves equal attention. ResumeIQ ranks opportunities by potential relevance."
          />
          <div className="mt-5 rounded-2xl border border-amber-400/[0.08] bg-amber-400/[0.025] p-4">
            <div className="flex gap-3">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-400/10 text-xs font-bold text-amber-400">
                !
              </span>
              <div>
                <p className="text-xs font-semibold text-slate-300">Missing does not mean mandatory</p>
                <p className="mt-1 text-[11px] leading-5 text-slate-600">
                  A keyword is marked as missing when the ATS engine does not detect it in your resume. Add it only if you actually
                  have relevant knowledge or experience. For job-specific importance, use Job Matching with an actual job
                  description.
                </p>
              </div>
            </div>
          </div>
          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            {priorityGroups.map((group) => {
              const matched = toArray(group.data.matched);
              const missing = toArray(group.data.missing);
              return (
                <PriorityCard
                  key={group.key}
                  label={group.label}
                  description={group.description}
                  matched={matched}
                  missing={missing}
                />
              );
            })}
          </div>
        </section>

        {/* Matched vs missing */}
        <section className="mb-6 grid gap-5 lg:grid-cols-2">
          <KeywordPanel
            title="Detected keywords"
            description="Keywords currently supported by your resume content."
            items={matchedKeywords}
            type="matched"
          />
          <KeywordPanel
            title="Potential keyword gaps"
            description="Terms not currently detected in your resume. These are opportunities to review, not instructions to add unsupported skills."
            items={missingKeywords}
            type="missing"
            priorityMap={keywordPriorityMap}
          />
        </section>

        {/* ATS signals */}
        <section className="mb-6 grid gap-5 lg:grid-cols-2">
          <div className="rounded-[28px] border border-white/[0.08] bg-[#0a1020] p-6">
            <SectionHeading
              eyebrow="Content signals"
              title="Evidence ATS systems can interpret"
              description="Strong resumes combine technical relevance with clear evidence of execution."
            />
            <div className="mt-6 space-y-3">
              <SignalRow
                label="Action verbs"
                value={actionVerbs.length}
                description={actionVerbs.length ? actionVerbs.slice(0, 8).join(", ") : "No strong action verbs detected"}
              />
              <SignalRow
                label="Quantifiable metrics"
                value={metrics.length}
                description={metrics.length ? metrics.slice(0, 8).join(", ") : "No measurable outcomes detected"}
              />
              <SignalRow
                label="Technical technologies"
                value={technologies.length}
                description={technologies.length ? technologies.slice(0, 8).join(", ") : "No technology coverage detected"}
              />
            </div>
          </div>

          <div className="rounded-[28px] border border-white/[0.08] bg-[#0a1020] p-6">
            <SectionHeading
              eyebrow="Resume structure"
              title="ATS section coverage"
              description="Clear section structure helps automated systems classify resume information."
            />
            {/* ✅ FIX: 2 columns on all screens (removed lg:grid-cols-3) */}
            <div className="mt-6 grid list-none gap-3 sm:grid-cols-2">
              <StructureCard label="Detected" value={sectionsPresent.length} items={sectionsPresent} positive />
              <StructureCard label="Missing" value={sectionsMissing.length} items={sectionsMissing} />
              <StructureStatusCard label="Experience" detected={hasExperience} />
            </div>
            <div className="mt-4 rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-600">Section quality score</p>
                  <p className="mt-1 text-xs text-slate-500">Backend ATS section assessment</p>
                </div>
                <span className="text-lg font-bold text-white">{sectionQuality.toFixed(0)}</span>
              </div>
              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                <div
                  className="h-full rounded-full bg-blue-500"
                  style={{ width: `${Math.min(Math.max(sectionQuality, 0), 100)}%` }}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Technology coverage */}
        <section className="mb-6 rounded-[28px] border border-white/[0.08] bg-[#0a1020] p-6 sm:p-7">
          <SectionHeading
            eyebrow="Technology intelligence"
            title="Technical coverage"
            description="Technologies detected by the ATS engine across the resume."
          />
          <div className="mt-6">
            {technologies.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {technologies.map((technology, index) => (
                  <span
                    key={`${technology}-${index}`}
                    className="rounded-lg border border-blue-400/[0.10] bg-blue-400/[0.04] px-3 py-2 text-[10px] font-medium text-blue-300"
                  >
                    {technology}
                  </span>
                ))}
              </div>
            ) : (
              <EmptyState
                title="No technology coverage detected"
                description="The ATS engine did not identify technical technologies in the current analysis."
              />
            )}
          </div>
          {Object.keys(technologyCategories).length > 0 && (
            <div className="mt-6">
              <div className="mb-4">
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600">Category coverage</p>
                <p className="mt-1 text-xs text-slate-500">Technology signals grouped by ATS category.</p>
              </div>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {Object.entries(technologyCategories).map(([category, values]) => (
                  <TechnologyCategory key={category} category={category} values={toArray(values)} />
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Deployment evidence */}
        <section className="mb-6 rounded-[28px] border border-white/[0.08] bg-[#0a1020] p-6 sm:p-7">
          <SectionHeading
            eyebrow="Deployment intelligence"
            title="Application serving vs production deployment"
            description="ResumeIQ distinguishes between technologies used to serve an application and evidence that the application was actually deployed to a production environment."
          />
          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            <DeploymentCard
              title="Application serving"
              description="Frameworks or technologies explicitly used to serve an application."
              items={applicationServing}
              detected={hasApplicationServing}
              type="serving"
            />
            <DeploymentCard
              title="Production deployment"
              description="Evidence of an actual production deployment, hosting platform, or deployed environment."
              items={productionDeployment}
              detected={hasProductionDeployment}
              type="production"
            />
          </div>
          <div className="mt-5 rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4">
            <div className="flex gap-3">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-xs font-bold text-blue-400">
                i
              </span>
              <div>
                <p className="text-xs font-semibold text-slate-300">How to interpret this</p>
                <p className="mt-1 text-[11px] leading-5 text-slate-600">
                  A framework such as Flask can indicate application serving, but it does not by itself prove that the application
                  was deployed to production. Production deployment should only be claimed when the resume contains genuine
                  deployment evidence.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Recommendations */}
        <section className="mb-6 rounded-[28px] border border-white/[0.08] bg-[#0a1020] p-6 sm:p-7">
          <SectionHeading
            eyebrow="Optimization engine"
            title="What should you improve?"
            description="Prioritized recommendations generated from your current ATS profile."
          />
          <div className="mt-6 space-y-3">
            {recommendationItems.length > 0 ? (
              recommendationItems.map((recommendation, index) => (
                <Recommendation key={`${recommendation}-${index}`} number={index + 1} text={recommendation} />
              ))
            ) : issueItems.length > 0 ? (
              issueItems.map((issue, index) => (
                <Recommendation key={`${issue}-${index}`} number={index + 1} text={issue} />
              ))
            ) : (
              <EmptyState title="No major ATS issues detected" description="Your current resume has a relatively healthy ATS profile." />
            )}
          </div>
        </section>

        {/* Issues */}
        {issueItems.length > 0 && (
          <section className="mb-6 rounded-[28px] border border-amber-400/[0.08] bg-[#0a1020] p-6 sm:p-7">
            <SectionHeading
              eyebrow="Attention required"
              title="ATS issues"
              description="Areas identified by ResumeIQ that may reduce automated screening performance."
            />
            <div className="mt-6 grid gap-3 md:grid-cols-2">
              {issueItems.map((issue, index) => (
                <div key={`${issue}-${index}`} className="rounded-2xl border border-amber-400/[0.08] bg-amber-400/[0.025] p-4">
                  <div className="flex gap-3">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-amber-400/10 text-xs font-bold text-amber-400">
                      !
                    </span>
                    <p className="text-sm leading-6 text-slate-300">{issue}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Strengths */}
        {strengthItems.length > 0 && (
          <section className="mb-6 rounded-[28px] border border-white/[0.08] bg-[#0a1020] p-6 sm:p-7">
            <SectionHeading
              eyebrow="What is working"
              title="ATS strengths"
              description="Signals that are currently helping your resume."
            />
            <div className="mt-6 grid gap-3 md:grid-cols-2">
              {strengthItems.map((strength, index) => (
                <div key={`${strength}-${index}`} className="rounded-2xl border border-emerald-400/[0.08] bg-emerald-400/[0.025] p-4">
                  <div className="flex gap-3">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-emerald-400/10 text-xs font-bold text-emerald-400">
                      ✓
                    </span>
                    <p className="text-sm leading-6 text-slate-300">{strength}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Bottom actions */}
        <section className="rounded-[28px] border border-blue-400/[0.10] bg-gradient-to-br from-blue-500/[0.08] to-indigo-500/[0.04] p-7">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-400">Next step</p>
              <h2 className="mt-2 text-xl font-bold text-white">Turn ATS insights into job-specific intelligence</h2>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Compare your resume against an actual job description to understand role-specific fit,
                keyword alignment, skill gaps, and application priorities.
              </p>
            </div>
            <button
              type="button"
              onClick={() => navigate("/job-matching")}
              className="shrink-0 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:-translate-y-0.5 hover:bg-blue-500"
            >
              Match a job
              <span className="ml-2">→</span>
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

// ============================================================================
// UI Components
// ============================================================================

function ScoreRing({ score }) {
  const normalized = Math.min(Math.max(score, 0), 100);
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (normalized / 100) * circumference;

  return (
    <div className="relative h-32 w-32 shrink-0">
      <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90">
        <circle cx="60" cy="60" r={radius} fill="none" stroke="currentColor" strokeWidth="8" className="text-white/[0.05]" />
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
          className="text-blue-500 transition-all duration-700"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-white">{normalized.toFixed(0)}</span>
        <span className="text-[9px] uppercase tracking-wider text-slate-600">score</span>
      </div>
    </div>
  );
}

function MiniMetric({ label, value }) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
      <p className="text-xl font-bold text-white">{value}</p>
      <p className="mt-1 text-[10px] uppercase tracking-wider text-slate-600">{label}</p>
    </div>
  );
}

function ScoreSignal({ label, score }) {
  const normalized = Math.min(Math.max(Number(score) || 0, 0), 100);
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-600">{label}</p>
        <span className="text-sm font-bold text-white">{normalized.toFixed(0)}</span>
      </div>
      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
        <div className="h-full rounded-full bg-blue-500 transition-all duration-500" style={{ width: `${normalized}%` }} />
      </div>
    </div>
  );
}

function InsightCard({ eyebrow, title, description, icon }) {
  return (
    <div className="rounded-[24px] border border-white/[0.08] bg-[#0a1020] p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-600">{eyebrow}</p>
          <h3 className="mt-3 text-sm font-semibold leading-6 text-slate-200">{title}</h3>
        </div>
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-sm text-blue-400">
          {icon}
        </span>
      </div>
      <p className="mt-3 text-xs leading-5 text-slate-600">{description}</p>
    </div>
  );
}

function SectionHeading({ eyebrow, title, description }) {
  return (
    <div>
      <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-blue-400">{eyebrow}</p>
      <h2 className="mt-2 text-xl font-bold tracking-tight text-white">{title}</h2>
      <p className="mt-2 max-w-3xl text-xs leading-5 text-slate-600">{description}</p>
    </div>
  );
}

function PriorityCard({ label, description, matched, missing }) {
  const total = matched.length + missing.length;
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">{label}</h3>
          <p className="mt-1 text-[11px] leading-5 text-slate-600">{description}</p>
        </div>
        <span className="shrink-0 rounded-lg border border-white/[0.06] bg-white/[0.03] px-2 py-1 text-[9px] font-bold uppercase tracking-wider text-slate-500">
          {matched.length} / {total}
        </span>
      </div>
      <div className="mt-5">
        {matched.length > 0 && (
          <div className="mb-4">
            <p className="mb-2 text-[9px] font-semibold uppercase tracking-wider text-emerald-500">Already covered</p>
            <div className="flex flex-wrap gap-2">
              {matched.map((item, index) => (
                <KeywordBadge key={`${item}-${index}`} label={item} type="matched" />
              ))}
            </div>
          </div>
        )}
        {missing.length > 0 && (
          <div>
            <p className="mb-2 text-[9px] font-semibold uppercase tracking-wider text-amber-500">Potential opportunities</p>
            <div className="flex flex-wrap gap-2">
              {missing.map((item, index) => (
                <KeywordBadge key={`${item}-${index}`} label={item} type="missing" />
              ))}
            </div>
          </div>
        )}
        {matched.length === 0 && missing.length === 0 && (
          <p className="text-xs text-slate-700">No keyword data available.</p>
        )}
      </div>
    </div>
  );
}

function KeywordPanel({ title, description, items, type, priorityMap = new Map() }) {
  const visibleItems = items.slice(0, 30);
  return (
    <div className="rounded-[28px] border border-white/[0.08] bg-[#0a1020] p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white">{title}</h2>
          <p className="mt-1 text-xs leading-5 text-slate-600">{description}</p>
        </div>
        <span className="rounded-lg bg-white/[0.03] px-3 py-1 text-[10px] font-bold text-slate-500">{items.length}</span>
      </div>
      <div className="mt-5 rounded-xl border border-white/[0.05] bg-white/[0.015] px-3 py-2.5">
        <p className="text-[10px] leading-5 text-slate-600">
          {type === "missing"
            ? "These keywords are absent from the current resume. They are not automatically required. Add them only when supported by genuine skills, experience, or the target job."
            : "These keywords were detected in the current resume and contribute to its ATS keyword coverage."}
        </p>
      </div>
      <div className="mt-5 flex max-h-[300px] flex-wrap content-start gap-2 overflow-y-auto pr-1">
        {visibleItems.length > 0 ? (
          visibleItems.map((item, index) => {
            const priority =
              type === "missing" ? priorityMap.get(String(item).trim().toLowerCase()) : null;
            return <KeywordBadge key={`${item}-${index}`} label={item} type={type} priority={priority} />;
          })
        ) : (
          <p className="text-xs text-slate-700">No keywords detected.</p>
        )}
      </div>
      {items.length > 30 && <p className="mt-4 text-[10px] text-slate-700">Showing the first 30 keywords.</p>}
    </div>
  );
}

function KeywordBadge({ label, type, priority }) {
  const styles =
    type === "matched"
      ? "border-emerald-400/[0.10] bg-emerald-400/[0.04] text-emerald-300"
      : "border-amber-400/[0.10] bg-amber-400/[0.04] text-amber-300";

  return (
    <span
      title={type === "missing" && priority ? `${priority} keyword opportunity` : undefined}
      className={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-[10px] font-medium ${styles}`}
    >
      {type === "missing" && <span className="text-amber-500">+</span>}
      <span>{label}</span>
      {type === "missing" && priority && (
        <span className="rounded-md bg-white/[0.06] px-1.5 py-0.5 text-[8px] font-semibold uppercase tracking-wide text-slate-500">
          {priority}
        </span>
      )}
    </span>
  );
}

function SignalRow({ label, value, description }) {
  return (
    <div className="flex items-center gap-4 rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-sm font-bold text-blue-400">
        {value}
      </div>
      <div className="min-w-0">
        <p className="text-xs font-semibold text-slate-300">{label}</p>
        <p className="mt-1 truncate text-[10px] text-slate-600" title={description}>
          {description}
        </p>
      </div>
    </div>
  );
}

function StructureCard({ label, value, items, positive = false }) {
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4 overflow-hidden">
      <div className="flex items-center justify-between">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-600">{label}</p>
        <span className={positive ? "text-sm font-bold text-emerald-400" : "text-sm font-bold text-amber-400"}>{value}</span>
      </div>
      <div className="mt-4 space-y-2">
        {items.length > 0 ? (
          items.map((item, index) => (
            <div key={`${item}-${index}`} className="flex items-center gap-2 text-[11px] text-slate-500 break-words">
              <span className={positive ? "h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" : "h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400"} />
              {item}
            </div>
          ))
        ) : (
          <p className="text-[10px] text-slate-700">None detected</p>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// ✅ FIXED: StructureStatusCard – compact, no overflow, stays on one line
// ============================================================================
function StructureStatusCard({ label, detected }) {
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-3">
      <div className="flex items-center justify-between gap-1">
        <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
          {label}
        </p>
        <span
          className={`whitespace-nowrap text-[9px] font-bold ${
            detected ? "text-emerald-400" : "text-slate-500"
          }`}
        >
          {detected ? "Detected" : "Not detected"}
        </span>
      </div>
      <p className="mt-3 text-[9px] leading-4 text-slate-700 break-words">
        {detected
          ? "Professional experience evidence is present in the ATS section analysis."
          : "No professional experience section was detected in the current resume."}
      </p>
    </div>
  );
}

function TechnologyCategory({ category, values }) {
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-semibold text-slate-300">{formatLabel(category)}</p>
        <span className="text-[10px] font-bold text-slate-600">{values.length}</span>
      </div>
      {values.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {values.map((value, index) => (
            <span key={`${value}-${index}`} className="rounded-md bg-white/[0.035] px-2 py-1 text-[9px] text-slate-500">
              {value}
            </span>
          ))}
        </div>
      ) : (
        <p className="mt-3 text-[10px] text-slate-700">No technologies detected.</p>
      )}
    </div>
  );
}

function DeploymentCard({ title, description, items, detected, type }) {
  const isProduction = type === "production";
  return (
    <div
      className={
        isProduction
          ? "rounded-2xl border border-indigo-400/[0.08] bg-indigo-400/[0.025] p-5"
          : "rounded-2xl border border-blue-400/[0.08] bg-blue-400/[0.025] p-5"
      }
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
          <p className="mt-1 text-[11px] leading-5 text-slate-600">{description}</p>
        </div>
        <span
          className={
            detected
              ? "rounded-full bg-emerald-400/10 px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider text-emerald-400"
              : "rounded-full bg-white/[0.04] px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider text-slate-600"
          }
        >
          {detected ? "Detected" : "Not detected"}
        </span>
      </div>
      <div className="mt-5">
        {items.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {items.map((item, index) => (
              <span key={`${item}-${index}`} className="rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-[10px] font-medium text-slate-300">
                {item}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-xs leading-5 text-slate-700">No evidence detected in the resume.</p>
        )}
      </div>
    </div>
  );
}

function Recommendation({ number, text }) {
  return (
    <div className="flex gap-4 rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-[10px] font-bold text-blue-400">
        {String(number).padStart(2, "0")}
      </div>
      <p className="pt-1 text-sm leading-6 text-slate-400">{text}</p>
    </div>
  );
}

function EmptyState({ title, description }) {
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-6 text-center">
      <p className="text-sm font-semibold text-slate-300">{title}</p>
      <p className="mt-2 text-xs text-slate-600">{description}</p>
    </div>
  );
}

export default ATSIntelligence;