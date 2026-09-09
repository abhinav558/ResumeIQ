import { useNavigate } from "react-router-dom";

/* =========================================================
   RESUME REPORT
========================================================= */

function ResumeReport({
  analysis,
  activeTab = "overview",
  setActiveTab,
  onAnalyzeAgain,
}) {
  const navigate = useNavigate();

  const score = normalizeScore(
    analysis?.resume_intelligence_score
  );

  const atsScore = normalizeScore(
    analysis?.ats_analysis?.ats_score
  );

  const skillsScore = normalizeScore(
    analysis?.skills_analysis?.skill_score
  );

  const projectScore = normalizeScore(
    analysis?.project_analysis?.score
  );

  const experienceScore = normalizeScore(
    analysis?.experience_analysis?.experience_score
  );

  const educationScore = normalizeScore(
    analysis?.education?.score
  );

  const certificationScore = normalizeScore(
    analysis?.certifications?.score
  );

  const achievementScore = normalizeScore(
    analysis?.achievement_analysis?.score
  );

  const confidence = normalizeScore(
    analysis?.confidence
  );

  const recommendations = Array.isArray(
    analysis?.recommendations
  )
    ? analysis.recommendations
    : [];

  const tabs = [
    ["overview", "Overview"],
    ["skills", "Skills"],
    ["ats", "ATS Intelligence"],
    ["projects", "Projects"],
    ["experience", "Experience"],
    ["education", "Education"],
    ["recommendations", "Recommendations"],
  ];

  const changeTab = (tab) => {
    if (typeof setActiveTab === "function") {
      setActiveTab(tab);
    }
  };

  return (
    <section
      id="resume-report"
      className="w-full"
    >
      {/* =====================================================
          REPORT HEADER
      ===================================================== */}

      <div className="mx-auto w-full max-w-[1440px] px-5 pt-10 sm:px-8 lg:px-10 xl:px-12">
        <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-400/10 bg-emerald-400/[0.05] px-3 py-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />

              <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-300">
                Analysis complete
              </span>
            </div>

            <h1 className="mt-4 text-3xl font-semibold tracking-[-0.035em] text-white sm:text-4xl">
              Your ResumeIQ report
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
              A structured assessment of your resume's strengths,
              weaknesses and opportunities.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            {onAnalyzeAgain && (
              <button
                type="button"
                onClick={onAnalyzeAgain}
                className="rounded-xl border border-white/[0.08] bg-white/[0.03] px-4 py-2.5 text-xs font-medium text-slate-300 transition hover:border-blue-400/20 hover:bg-blue-400/[0.05] hover:text-white"
              >
                Analyze another resume
              </button>
            )}

            <button
              type="button"
              onClick={() => navigate("/resume-analysis")}
              className="rounded-xl bg-blue-500 px-4 py-2.5 text-xs font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-400"
            >
              Resume Analysis
            </button>
          </div>
        </div>
      </div>

      {/* =====================================================
          CONTENT
      ===================================================== */}

      <div className="mx-auto w-full max-w-[1440px] px-5 pb-16 pt-6 sm:px-8 lg:px-10 xl:px-12">
        {/* ===================================================
            TOP METRICS
        =================================================== */}

        <div className="grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            label="ResumeIQ Score"
            value={score}
            suffix="/100"
            status={
              analysis?.rating ||
              getScoreLabel(score)
            }
            accent="blue"
          />

          <MetricCard
            label="ATS Compatibility"
            value={atsScore}
            suffix="/100"
            status={getScoreLabel(atsScore)}
            accent="violet"
          />

          <MetricCard
            label="Skills Strength"
            value={skillsScore}
            suffix="/100"
            status={`${analysis?.skills_analysis?.total_skills || 0} detected skills`}
            accent="cyan"
          />

          <MetricCard
            label="Project Strength"
            value={projectScore}
            suffix="/100"
            status={`${analysis?.project_analysis?.project_count || 0} projects analyzed`}
            accent="amber"
          />
        </div>

        {/* ===================================================
            TABS
        =================================================== */}

        <div className="mt-5 overflow-x-auto rounded-xl border border-white/[0.07] bg-[#080d18]">
          <div className="flex min-w-max p-1">
            {tabs.map(([id, label]) => (
              <button
                key={id}
                type="button"
                onClick={() => changeTab(id)}
                className={`rounded-lg px-4 py-2.5 text-xs font-medium transition ${
                  activeTab === id
                    ? "bg-blue-500 text-white shadow-lg shadow-blue-500/15"
                    : "text-slate-500 hover:bg-white/[0.04] hover:text-slate-200"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* ===================================================
            TAB CONTENT
        =================================================== */}

        {activeTab === "overview" && (
          <OverviewTab
            analysis={analysis}
            score={score}
            atsScore={atsScore}
            skillsScore={skillsScore}
            projectScore={projectScore}
            experienceScore={experienceScore}
            educationScore={educationScore}
            certificationScore={certificationScore}
            achievementScore={achievementScore}
            confidence={confidence}
            recommendations={recommendations}
          />
        )}

        {activeTab === "skills" && (
          <SkillsTab
            skills={analysis?.skills_analysis}
          />
        )}

        {activeTab === "ats" && (
          <ATSTab
            ats={analysis?.ats_analysis}
          />
        )}

        {activeTab === "projects" && (
          <ProjectsTab
            projects={analysis?.project_analysis}
          />
        )}

        {activeTab === "experience" && (
          <ExperienceTab
            experience={analysis?.experience_analysis}
          />
        )}

        {activeTab === "education" && (
          <EducationTab
            education={analysis?.education}
            certifications={analysis?.certifications}
          />
        )}

        {activeTab === "recommendations" && (
          <RecommendationsTab
            recommendations={recommendations}
          />
        )}
      </div>
    </section>
  );
}

/* =========================================================
   OVERVIEW
========================================================= */

function OverviewTab({
  analysis,
  score,
  atsScore,
  skillsScore,
  projectScore,
  experienceScore,
  educationScore,
  certificationScore,
  achievementScore,
  confidence,
  recommendations,
}) {
  const matched = getKeywordArray(
    analysis?.ats_analysis?.matched_keywords,
    analysis?.ats_analysis?.keyword_analysis?.matched
  );

  const missing = getKeywordArray(
    analysis?.ats_analysis?.missing_keywords,
    analysis?.ats_analysis?.keyword_analysis?.missing
  );

  const projects =
    Array.isArray(
      analysis?.project_analysis?.projects
    )
      ? analysis.project_analysis.projects
      : [];

  return (
    <div className="space-y-5">
      {/* SCORE OVERVIEW */}

      <section className="mt-7 rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <div className="grid min-w-0 gap-7 md:grid-cols-[190px_minmax(0,1fr)] md:items-center">
          <ScoreRing score={score} />

          <div className="min-w-0">
            <div className="rounded-xl border border-white/[0.06] bg-white/[0.025] p-4">
              <p className="text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-600">
                Current assessment
              </p>

              <p className="mt-2 text-xl font-semibold text-blue-300">
                {analysis?.rating ||
                  getScoreLabel(score)}
              </p>

              <p className="mt-2 text-xs leading-5 text-slate-500">
                ResumeIQ evaluates your technical profile,
                ATS readiness, projects, education and
                professional signals together.
              </p>
            </div>

            <div className="mt-5 space-y-3">
              <ScoreBar
                label="Skills"
                value={skillsScore}
              />

              <ScoreBar
                label="ATS"
                value={atsScore}
              />

              <ScoreBar
                label="Projects"
                value={projectScore}
              />

              <ScoreBar
                label="Experience"
                value={experienceScore}
              />

              <ScoreBar
                label="Education"
                value={educationScore}
              />

              <ScoreBar
                label="Certifications"
                value={certificationScore}
              />

              <ScoreBar
                label="Achievements"
                value={achievementScore}
              />
            </div>
          </div>
        </div>
      </section>

      {/* CANDIDATE PROFILE */}

      <CandidateProfileCard
        profile={analysis?.candidate_profile}
      />

      {/* SKILLS + ATS */}

      <div className="grid min-w-0 gap-5 lg:grid-cols-2">
        <section className="min-w-0 rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-6">
          <SkillsPreview
            skills={analysis?.skills_analysis}
          />
        </section>

        <section className="min-w-0 rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-6">
          <SectionHeader
            eyebrow="ATS intelligence"
            title="Screening compatibility"
            description="Keyword coverage and ATS-related signals detected in your resume."
            score={atsScore}
          />

          <div className="mt-6 grid min-w-0 gap-4">
            <KeywordPanel
              title="Detected keywords"
              subtitle={`${matched.length} matched`}
              keywords={matched.slice(0, 12)}
              variant="positive"
            />

            <KeywordPanel
              title="Potential gaps"
              subtitle={`${missing.length} not detected`}
              keywords={missing.slice(0, 12)}
              variant="warning"
            />
          </div>
        </section>
      </div>

      {/* PROJECT + EXPERIENCE */}

      <div className="grid min-w-0 gap-5 lg:grid-cols-2">
        <section className="min-w-0 rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-6">
          <ProjectsPreview
            projects={projects}
          />
        </section>

        <section className="min-w-0 rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-6">
          <ExperienceCard
            experience={analysis?.experience_analysis}
          />
        </section>
      </div>

      {/* EDUCATION + CERTIFICATIONS */}

      <div className="grid min-w-0 gap-5 lg:grid-cols-2">
        <section className="min-w-0 rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-6">
          <EducationCard
            education={analysis?.education}
          />
        </section>

        <section className="min-w-0 rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-6">
          <CertificationCard
            certifications={analysis?.certifications}
          />
        </section>
      </div>

      {/* DEPLOYMENT */}

      <DeploymentEvidenceCard
        deployment={analysis?.ats_analysis?.deployment_analysis}
        projects={projects}
      />

      {/* CONFIDENCE */}

      <ConfidenceCard
        confidence={confidence}
        sections={analysis?.sections_detected}
      />

      {/* RECOMMENDATIONS */}

      <RecommendationsPreview
        recommendations={recommendations}
      />
    </div>
  );
}

/* =========================================================
   CANDIDATE PROFILE
========================================================= */

function CandidateProfileCard({
  profile,
}) {
  if (!profile || typeof profile !== "object") {
    return null;
  }

  const name =
    profile.name ||
    "Candidate";

  const email =
    profile.email ||
    "";

  const phone =
    profile.phone ||
    "";

  const link =
    profile.link ||
    "";

  const summary =
    profile.summary ||
    "";

  const hasContact =
    Boolean(email || phone || link);

  return (
    <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
      <SectionHeader
        eyebrow="Candidate profile"
        title={name}
        description="Structured candidate information extracted from the resume."
      />

      {summary && (
        <div className="mt-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
          <p className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-600">
            Professional summary
          </p>

          <p className="mt-3 text-xs leading-6 text-slate-400">
            {summary}
          </p>
        </div>
      )}

      {hasContact && (
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {email && (
            <ProfileField
              label="Email"
              value={email}
            />
          )}

          {phone && (
            <ProfileField
              label="Phone"
              value={phone}
            />
          )}

          {link && (
            <ProfileField
              label="Professional link"
              value={link}
            />
          )}
        </div>
      )}
    </section>
  );
}

function ProfileField({
  label,
  value,
}) {
  return (
    <div className="min-w-0 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <p className="text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-600">
        {label}
      </p>

      <p className="mt-2 truncate text-xs text-slate-300">
        {value}
      </p>
    </div>
  );
}

/* =========================================================
   SKILLS
========================================================= */

function SkillsTab({
  skills,
}) {
  const categories =
    skills?.categories || {};

  const found = Array.isArray(
    skills?.skills_found
  )
    ? skills.skills_found
    : [];

  const missing = Array.isArray(
    skills?.missing_industry_skills
  )
    ? skills.missing_industry_skills
    : [];

  const confidenceSummary =
    skills?.confidence_summary || {};

  return (
    <div className="mt-7 space-y-5">
      {/* SKILL SCORE */}

      <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <SectionHeader
          eyebrow="Skills intelligence"
          title="Technical capability profile"
          description="A structured view of the technical and professional skills detected across your resume."
          score={normalizeScore(
            skills?.skill_score
          )}
        />

        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <ATSMini
            label="Total skills"
            value={skills?.total_skills || 0}
          />

          <ATSMini
            label="Categories"
            value={skills?.category_count || 0}
          />

          <ATSMini
            label="Strong evidence"
            value={
              confidenceSummary.strong || 0
            }
          />

          <ATSMini
            label="Moderate evidence"
            value={
              confidenceSummary.moderate || 0
            }
          />
        </div>

        {skills?.strongest_category && (
          <div className="mt-5 rounded-xl border border-blue-400/10 bg-blue-400/[0.03] p-4">
            <p className="text-[9px] font-semibold uppercase tracking-[0.15em] text-blue-300/70">
              Strongest category
            </p>

            <p className="mt-2 text-sm font-semibold text-white">
              {skills.strongest_category}
            </p>
          </div>
        )}
      </section>

      {/* CATEGORIES */}

      <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <SectionHeader
          eyebrow="Skills intelligence"
          title="Skills by category"
          description="Technical capabilities detected across your resume."
        />

        <div className="mt-8 grid min-w-0 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Object.entries(categories).length ? (
            Object.entries(categories).map(
              ([category, values]) => (
                <SkillCategory
                  key={category}
                  category={category}
                  skills={
                    Array.isArray(values)
                      ? values
                      : []
                  }
                />
              )
            )
          ) : (
            <EmptyState text="No skill categories detected." />
          )}
        </div>
      </section>

      {/* ALL SKILLS */}

      <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <SectionHeader
          eyebrow="Detected skills"
          title={`${found.length} skills identified`}
          description="Technologies and capabilities explicitly detected in your resume."
        />

        <div className="mt-6 flex flex-wrap gap-2">
          {found.length ? (
            found.map((skill) => (
              <span
                key={skill}
                className="rounded-lg border border-blue-400/10 bg-blue-400/[0.05] px-3 py-2 text-xs font-medium text-slate-300"
              >
                {skill}
              </span>
            ))
          ) : (
            <EmptyState text="No skills detected." />
          )}
        </div>
      </section>

      {/* GAPS */}

      <section className="rounded-2xl border border-amber-400/10 bg-amber-400/[0.025] p-5 sm:p-7">
        <SectionHeader
          eyebrow="Potential gaps"
          title="Skills worth considering"
          description="Only add these skills if you genuinely have the experience."
        />

        <div className="mt-6 flex flex-wrap gap-2">
          {missing.length ? (
            missing.map((skill) => (
              <span
                key={skill}
                className="rounded-lg border border-amber-400/10 bg-black/10 px-3 py-2 text-xs text-amber-200/80"
              >
                {skill}
              </span>
            ))
          ) : (
            <p className="text-xs text-slate-600">
              No major skill gaps detected.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}

function SkillsPreview({
  skills,
}) {
  const categories =
    skills?.categories || {};

  return (
    <>
      <SectionHeader
        eyebrow="Skills profile"
        title="Your technical strengths"
        description={`${skills?.total_skills || 0} skills detected across your resume.`}
        score={normalizeScore(
          skills?.skill_score
        )}
      />

      <div className="mt-6 space-y-4">
        {Object.entries(categories)
          .slice(0, 6)
          .map(([category, values]) => {
            const list = Array.isArray(values)
              ? values
              : [];

            return (
              <div key={category}>
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-300">
                    {category}
                  </span>

                  <span className="text-[10px] text-slate-600">
                    {list.length} skills
                  </span>
                </div>

                <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-400"
                    style={{
                      width: `${Math.min(
                        100,
                        25 + list.length * 12
                      )}%`,
                    }}
                  />
                </div>
              </div>
            );
          })}
      </div>

      <div className="mt-6 border-t border-white/[0.06] pt-5">
        <p className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-600">
          Top detected skills
        </p>

        <div className="mt-3 flex flex-wrap gap-2">
          {(skills?.skills_found || [])
            .slice(0, 10)
            .map((skill) => (
              <span
                key={skill}
                className="rounded-md border border-white/[0.07] bg-white/[0.025] px-2.5 py-1.5 text-[10px] text-slate-400"
              >
                {skill}
              </span>
            ))}
        </div>
      </div>
    </>
  );
}

function SkillCategory({
  category,
  skills,
}) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-slate-300">
          {category}
        </h3>

        <span className="rounded-full bg-blue-400/[0.08] px-2 py-1 text-[9px] font-semibold text-blue-300">
          {skills.length}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {skills.map((skill) => (
          <span
            key={skill}
            className="rounded-md border border-white/[0.06] px-2 py-1 text-[10px] text-slate-500"
          >
            {skill}
          </span>
        ))}
      </div>
    </div>
  );
}

/* =========================================================
   ATS
========================================================= */

function ATSTab({
  ats,
}) {
  const matched = getKeywordArray(
    ats?.matched_keywords,
    ats?.keyword_analysis?.matched
  );

  const missing = getKeywordArray(
    ats?.missing_keywords,
    ats?.keyword_analysis?.missing
  );

  const priorities =
    ats?.keyword_analysis?.priorities || {};

  const technologyCoverage =
    ats?.technology_coverage || {};

  const technologies = Array.isArray(
    technologyCoverage.technologies
  )
    ? technologyCoverage.technologies
    : [];

  const sectionAnalysis =
    ats?.section_analysis || {};

  const sectionsPresent = Array.isArray(
    sectionAnalysis.present
  )
    ? sectionAnalysis.present
    : [];

  const sectionsMissing = Array.isArray(
    sectionAnalysis.missing
  )
    ? sectionAnalysis.missing
    : [];

  return (
    <div className="mt-7 space-y-5">
      {/* ATS SCORE */}

      <section className="rounded-2xl border border-violet-400/10 bg-[#080d18] p-5 sm:p-7">
        <div className="flex items-start justify-between gap-5">
          <div>
            <SectionHeader
              eyebrow="ATS intelligence"
              title="Applicant tracking compatibility"
              description="Understand how automated screening systems may interpret your resume."
            />
          </div>

          <div className="shrink-0 text-right">
            <span className="text-4xl font-semibold text-white">
              {normalizeScore(
                ats?.ats_score
              )}
            </span>

            <span className="text-sm text-slate-600">
              /100
            </span>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <ATSMini
            label="Matched keywords"
            value={matched.length}
          />

          <ATSMini
            label="Potential gaps"
            value={missing.length}
          />

          <ATSMini
            label="Resume words"
            value={ats?.word_count || 0}
          />
        </div>
      </section>

      {/* KEYWORDS */}

      <div className="grid min-w-0 gap-5 lg:grid-cols-2">
        <KeywordPanel
          title="Detected keywords"
          subtitle={`${matched.length} found`}
          keywords={matched}
          variant="positive"
        />

        <KeywordPanel
          title="Potential keyword gaps"
          subtitle={`${missing.length} not detected`}
          keywords={missing}
          variant="warning"
        />
      </div>

      {/* ATS SIGNALS */}

      <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <SectionHeader
          eyebrow="Resume signals"
          title="ATS-friendly signals detected"
          description="Signals that can help demonstrate measurable and action-oriented experience."
        />

        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {(ats?.action_verbs_found || []).map(
            (item) => (
              <SignalItem
                key={`verb-${item}`}
                label={item}
                positive
              />
            )
          )}

          {(ats?.metrics_found || []).map(
            (item) => (
              <SignalItem
                key={`metric-${item}`}
                label={`${item} measurable result`}
                positive
              />
            )
          )}

          {!ats?.action_verbs_found?.length &&
            !ats?.metrics_found?.length && (
              <EmptyState text="No additional content signals detected." />
            )}
        </div>
      </section>

      {/* KEYWORD PRIORITIES */}

      <KeywordPrioritySection
        priorities={priorities}
      />

      {/* TECHNOLOGY COVERAGE */}

      <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <SectionHeader
          eyebrow="Technology coverage"
          title={`${technologyCoverage.count || technologies.length || 0} technologies detected`}
          description="Technical technologies recognized by the ATS analysis."
        />

        <div className="mt-6 flex flex-wrap gap-2">
          {technologies.length ? (
            technologies.map((technology) => (
              <span
                key={technology}
                className="rounded-lg border border-cyan-400/10 bg-cyan-400/[0.04] px-3 py-2 text-xs text-cyan-200/80"
              >
                {technology}
              </span>
            ))
          ) : (
            <EmptyState text="No technology coverage data available." />
          )}
        </div>
      </section>

      {/* SECTION COVERAGE */}

      <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <SectionHeader
          eyebrow="Section coverage"
          title="Resume structure"
          description="Sections recognized by the ATS engine."
          score={
            sectionAnalysis.score !== undefined
              ? sectionAnalysis.score
              : undefined
          }
        />

        <div className="mt-6 grid gap-5 lg:grid-cols-2">
          <KeywordPanel
            title="Detected sections"
            subtitle={`${sectionsPresent.length} present`}
            keywords={sectionsPresent}
            variant="positive"
          />

          <KeywordPanel
            title="Missing sections"
            subtitle={`${sectionsMissing.length} missing`}
            keywords={sectionsMissing}
            variant="warning"
          />
        </div>
      </section>

      {/* DEPLOYMENT */}

      <DeploymentEvidenceCard
        deployment={ats?.deployment_analysis}
      />
    </div>
  );
}

function KeywordPrioritySection({
  priorities,
}) {
  const groups = [
    ["critical", "Critical"],
    ["high", "High"],
    ["important", "Important"],
    ["supporting", "Supporting"],
    ["optional", "Optional"],
  ];

  const available = groups.filter(
    ([key]) =>
      priorities?.[key] &&
      (
        priorities[key]?.matched?.length ||
        priorities[key]?.missing?.length
      )
  );

  if (!available.length) {
    return null;
  }

  return (
    <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
      <SectionHeader
        eyebrow="Keyword priorities"
        title="Keyword importance breakdown"
        description="Keyword evidence grouped by its importance to ATS alignment."
      />

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {available.map(
          ([key, label]) => {
            const group =
              priorities[key] || {};

            const groupMatched =
              Array.isArray(group.matched)
                ? group.matched
                : [];

            const groupMissing =
              Array.isArray(group.missing)
                ? group.missing
                : [];

            return (
              <div
                key={key}
                className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-slate-300">
                    {label}
                  </p>

                  <span className="rounded-full bg-blue-400/[0.08] px-2 py-1 text-[9px] font-semibold text-blue-300">
                    {groupMatched.length}
                  </span>
                </div>

                {groupMatched.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-1.5">
                    {groupMatched.map(
                      (keyword) => (
                        <span
                          key={`matched-${keyword}`}
                          className="rounded-md bg-emerald-400/[0.05] px-2 py-1 text-[9px] text-emerald-200/80"
                        >
                          {keyword}
                        </span>
                      )
                    )}
                  </div>
                )}

                {groupMissing.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {groupMissing.map(
                      (keyword) => (
                        <span
                          key={`missing-${keyword}`}
                          className="rounded-md bg-amber-400/[0.05] px-2 py-1 text-[9px] text-amber-200/80"
                        >
                          {keyword}
                        </span>
                      )
                    )}
                  </div>
                )}
              </div>
            );
          }
        )}
      </div>
    </section>
  );
}

/* =========================================================
   PROJECTS
========================================================= */

function ProjectsTab({
  projects,
}) {
  const items = Array.isArray(
    projects?.projects
  )
    ? projects.projects
    : [];

  return (
    <div className="mt-7 space-y-5">
      <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <SectionHeader
          eyebrow="Project intelligence"
          title="Project strength"
          description="How effectively your projects demonstrate technical ability, complexity and engineering depth."
        />

        <div className="mt-4 text-right">
          <span className="text-4xl font-semibold text-white">
            {normalizeScore(projects?.score)}
          </span>

          <span className="text-sm text-slate-600">
            /100
          </span>
        </div>

        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          <ATSMini
            label="Projects"
            value={
              projects?.project_count ||
              items.length
            }
          />

          <ATSMini
            label="Average score"
            value={normalizeScore(
              projects?.score
            )}
          />

          <ATSMini
            label="Technologies"
            value={
              Array.isArray(
                projects?.technologies
              )
                ? projects.technologies.length
                : 0
            }
          />
        </div>
      </section>

      {items.length ? (
        <div className="grid min-w-0 gap-4">
          {items.map((project, index) => (
            <ProjectCard
              key={`${project?.title || "project"}-${index}`}
              project={project}
              index={index}
            />
          ))}
        </div>
      ) : (
        <EmptyState text="No projects were detected." />
      )}
    </div>
  );
}

function ProjectsPreview({
  projects,
}) {
  const items = Array.isArray(projects)
    ? projects
    : [];

  return (
    <>
      <SectionHeader
        eyebrow="Project intelligence"
        title="Are your projects proving your ability?"
        description={`${items.length} projects analyzed.`}
      />

      <div className="mt-6 space-y-3">
        {items.length ? (
          items.slice(0, 2).map(
            (project, index) => (
              <div
                key={`${project?.title || "project"}-${index}`}
                className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-200">
                      {project?.title ||
                        `Project ${index + 1}`}
                    </p>

                    <p className="mt-1 text-[10px] text-slate-600">
                      {project?.technologies?.length || 0}{" "}
                      technologies detected
                    </p>
                  </div>

                  <span className="shrink-0 text-lg font-semibold text-blue-300">
                    {normalizeScore(
                      project?.score
                    )}
                  </span>
                </div>

                <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
                  <div
                    className="h-full rounded-full bg-blue-500"
                    style={{
                      width: `${Math.min(
                        normalizeScore(
                          project?.score
                        ),
                        100
                      )}%`,
                    }}
                  />
                </div>
              </div>
            )
          )
        ) : (
          <p className="text-xs text-slate-600">
            No projects detected.
          </p>
        )}
      </div>
    </>
  );
}

function ProjectCard({
  project,
  index,
}) {
  const actions = Array.isArray(
    project?.actions
  )
    ? project.actions
    : [];

  const technologies = Array.isArray(
    project?.technologies
  )
    ? project.technologies
    : [];

  const strengths = Array.isArray(
    project?.strengths
  )
    ? project.strengths
    : [];

  const complexityFeatures =
    Array.isArray(
      project?.complexity?.features
    )
      ? project.complexity.features
      : [];

  const impactKeywords =
    Array.isArray(
      project?.impact?.keywords
    )
      ? project.impact.keywords
      : [];

  const impactEvidence =
    Array.isArray(
      project?.impact?.evidence
    )
      ? project.impact.evidence
      : [];

  const metricsFound =
    Array.isArray(
      project?.metrics_analysis?.metrics_found
    )
      ? project.metrics_analysis.metrics_found
      : Array.isArray(project?.metrics)
        ? project.metrics
        : [];

  const deploymentFeatures =
    Array.isArray(
      project?.deployment_analysis?.features
    )
      ? project.deployment_analysis.features
      : [];

  const engineeringFeatures =
    Array.isArray(
      project?.engineering_analysis?.features
    )
      ? project.engineering_analysis.features
      : [];

  const projectDeploymentScore =
    project?.deployment_analysis?.score;

  const engineeringScore =
    project?.engineering_analysis?.score;

  return (
    <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
      {/* PROJECT HEADER */}

      <div className="flex items-start justify-between gap-5">
        <div className="min-w-0">
          <p className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-600">
            Project {index + 1}
          </p>

          <h3 className="mt-1 text-lg font-semibold leading-6 text-white">
            {project?.title ||
              `Technical Project ${index + 1}`}
          </h3>

          {project?.quality && (
            <span className="mt-2 inline-flex rounded-full border border-white/[0.06] bg-white/[0.025] px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.12em] text-slate-500">
              {project.quality}
            </span>
          )}
        </div>

        <div className="shrink-0 text-right">
          <span className="text-3xl font-semibold text-white">
            {normalizeScore(
              project?.score
            )}
          </span>

          <span className="text-sm text-slate-600">
            /100
          </span>
        </div>
      </div>

      {/* PROJECT METRICS */}

      <div className="mt-6 grid min-w-0 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <ProjectMetric
          label="Complexity"
          value={
            project?.complexity?.score
          }
        />

        <ProjectMetric
          label="Impact"
          value={
            project?.impact?.score
          }
        />

        <ProjectMetric
          label="Deployment"
          value={
            projectDeploymentScore
          }
        />

        <ProjectMetric
          label="Engineering"
          value={
            engineeringScore
          }
        />
      </div>

      {/* ACTIONS */}

      {actions.length > 0 && (
        <ProjectEvidenceList
          title="Implementation evidence"
          items={actions}
          variant="blue"
        />
      )}

      {/* TECHNOLOGIES */}

      {technologies.length > 0 && (
        <div className="mt-6">
          <p className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-600">
            Technologies
          </p>

          <div className="mt-3 flex flex-wrap gap-2">
            {technologies.map(
              (tech) => (
                <span
                  key={tech}
                  className="rounded-md border border-white/[0.06] bg-white/[0.02] px-2.5 py-1.5 text-[10px] text-slate-400"
                >
                  {tech}
                </span>
              )
            )}
          </div>
        </div>
      )}

      {/* COMPLEXITY */}

      {complexityFeatures.length > 0 && (
        <ProjectEvidenceList
          title="Technical complexity"
          items={complexityFeatures}
          variant="violet"
        />
      )}

      {/* IMPACT */}

      {(impactKeywords.length > 0 ||
        impactEvidence.length > 0) && (
        <div className="mt-6">
          <p className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-600">
            Impact evidence
          </p>

          {impactKeywords.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {impactKeywords.map(
                (keyword) => (
                  <span
                    key={keyword}
                    className="rounded-md border border-emerald-400/10 bg-emerald-400/[0.04] px-2.5 py-1.5 text-[10px] text-emerald-200/80"
                  >
                    {keyword}
                  </span>
                )
              )}
            </div>
          )}

          {impactEvidence.length > 0 && (
            <div className="mt-3 space-y-2">
              {impactEvidence
                .slice(0, 4)
                .map(
                  (evidence, evidenceIndex) => (
                    <div
                      key={`${evidence}-${evidenceIndex}`}
                      className="rounded-lg border border-white/[0.05] bg-white/[0.015] p-3"
                    >
                      <p className="text-[10px] leading-5 text-slate-500">
                        {evidence}
                      </p>
                    </div>
                  )
                )}
            </div>
          )}
        </div>
      )}

      {/* METRICS */}

      <ProjectEvidenceList
        title="Measured outcomes"
        items={metricsFound}
        emptyText="No quantitative metrics were detected for this project."
        variant="amber"
      />

      {/* DEPLOYMENT */}

      <ProjectEvidenceList
        title="Deployment evidence"
        items={deploymentFeatures}
        emptyText="No production deployment evidence detected."
        variant="cyan"
      />

      {/* ENGINEERING */}

      <ProjectEvidenceList
        title="Engineering practices"
        items={engineeringFeatures}
        variant="blue"
      />

      {/* STRENGTHS */}

      <ProjectEvidenceList
        title="Detected strengths"
        items={strengths}
        variant="green"
      />

      {/* CONFIDENCE */}

      {project?.confidence !== undefined && (
        <div className="mt-6 border-t border-white/[0.06] pt-4">
          <div className="flex items-center justify-between gap-3">
            <span className="text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-600">
              Project detection confidence
            </span>

            <span className="text-xs font-medium text-slate-400">
              {normalizeScore(
                Number(project.confidence) *
                  100 <= 1
                  ? Number(project.confidence) *
                      100
                  : project.confidence
              )}
              %
            </span>
          </div>
        </div>
      )}
    </section>
  );
}

function ProjectEvidenceList({
  title,
  items,
  emptyText,
  variant = "blue",
}) {
  const list = Array.isArray(items)
    ? items
    : [];

  const variantClasses = {
    blue:
      "border-blue-400/10 bg-blue-400/[0.025]",
    violet:
      "border-violet-400/10 bg-violet-400/[0.025]",
    amber:
      "border-amber-400/10 bg-amber-400/[0.025]",
    cyan:
      "border-cyan-400/10 bg-cyan-400/[0.025]",
    green:
      "border-emerald-400/10 bg-emerald-400/[0.025]",
  };

  return (
    <div className="mt-6">
      <p className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-600">
        {title}
      </p>

      {list.length ? (
        <div className="mt-3 space-y-2">
          {list.map(
            (item, index) => (
              <div
                key={`${item}-${index}`}
                className={`rounded-lg border p-3 ${
                  variantClasses[variant] ||
                  variantClasses.blue
                }`}
              >
                <div className="flex items-start gap-2.5">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />

                  <p className="min-w-0 text-[10px] leading-5 text-slate-400">
                    {item}
                  </p>
                </div>
              </div>
            )
          )}
        </div>
      ) : (
        emptyText && (
          <p className="mt-3 text-[10px] text-slate-600">
            {emptyText}
          </p>
        )
      )}
    </div>
  );
}

/* =========================================================
   EDUCATION
========================================================= */

function EducationTab({
  education,
  certifications,
}) {
  return (
    <div className="mt-7 space-y-5">
      <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <EducationCard
          education={education}
        />
      </section>

      <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <CertificationCard
          certifications={certifications}
        />
      </section>
    </div>
  );
}

function EducationCard({
  education,
}) {
  const entries = Array.isArray(
    education?.entries
  )
    ? education.entries
    : [];

  return (
    <>
      <SectionHeader
        eyebrow="Education"
        title="Academic profile"
        description="Education information detected in your resume."
        score={
          education?.score !== undefined
            ? normalizeScore(
                education.score
              )
            : undefined
        }
      />

      <div className="mt-6 space-y-3">
        {entries.length ? (
          entries.map(
            (entry, index) => (
              <EducationEntry
                key={`${entry?.institution || "education"}-${index}`}
                entry={entry}
              />
            )
          )
        ) : (
          <EmptyState text="No education details detected." />
        )}
      </div>
    </>
  );
}

function EducationEntry({
  entry,
}) {
  const degree =
    entry?.degree ||
    entry?.qualification ||
    entry?.program ||
    "";

  const field =
    entry?.field ||
    entry?.specialization ||
    "";

  const institution =
    entry?.institution ||
    entry?.school ||
    "Institution not specified";

  const start =
    entry?.start_date ||
    entry?.start_year ||
    "";

  const end =
    entry?.end_date ||
    entry?.end_year ||
    "";

  const period =
    start || end
      ? `${start || "—"} – ${end || "Present"}`
      : "";

  const cgpa =
    entry?.cgpa ??
    entry?.gpa ??
    null;

  const percentage =
    entry?.percentage ??
    entry?.percent ??
    null;

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-200">
            {institution}
          </p>

          {degree && (
            <p className="mt-1 text-xs text-slate-400">
              {degree}
            </p>
          )}

          {field && (
            <p className="mt-1 text-[10px] text-slate-600">
              {field}
            </p>
          )}
        </div>

        {period && (
          <span className="shrink-0 rounded-full border border-white/[0.06] bg-white/[0.025] px-2.5 py-1 text-[9px] text-slate-500">
            {period}
          </span>
        )}
      </div>

      {(cgpa !== null ||
        percentage !== null) && (
        <div className="mt-4 flex flex-wrap gap-2">
          {cgpa !== null && (
            <span className="rounded-md bg-blue-400/[0.05] px-2.5 py-1.5 text-[10px] text-blue-200/80">
              CGPA {cgpa}
            </span>
          )}

          {percentage !== null && (
            <span className="rounded-md bg-emerald-400/[0.05] px-2.5 py-1.5 text-[10px] text-emerald-200/80">
              {percentage}%
            </span>
          )}
        </div>
      )}
    </div>
  );
}

function CertificationCard({
  certifications,
}) {
  const items = Array.isArray(
    certifications?.certifications
  )
    ? certifications.certifications
    : [];

  const details = Array.isArray(
    certifications?.certification_details
  )
    ? certifications.certification_details
    : [];

  return (
    <>
      <SectionHeader
        eyebrow="Certifications"
        title="Professional credentials"
        description="Certifications detected in your resume. ResumeIQ does not independently verify external credentials."
        score={
          certifications?.score !== undefined
            ? normalizeScore(
                certifications.score
              )
            : undefined
        }
      />

      <div className="mt-6 space-y-3">
        {items.length ? (
          items.map(
            (certification, index) => {
              const detail =
                details[index] || {};

              return (
                <div
                  key={`${certification}-${index}`}
                  className="flex items-start gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4"
                >
                  <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-emerald-400/[0.08] text-emerald-300">
                    <CheckIcon size={13} />
                  </span>

                  <div className="min-w-0">
                    <p className="text-xs font-medium leading-5 text-slate-300">
                      {certification}
                    </p>

                    {detail.provider && (
                      <p className="mt-1 text-[10px] text-slate-600">
                        Provider: {detail.provider}
                      </p>
                    )}

                    {detail.issue_date && (
                      <p className="mt-1 text-[10px] text-slate-600">
                        Issued: {detail.issue_date}
                      </p>
                    )}
                  </div>
                </div>
              );
            }
          )
        ) : (
          <EmptyState text="No certifications detected." />
        )}
      </div>

      {Array.isArray(
        certifications?.trusted_providers
      ) &&
        certifications.trusted_providers.length >
          0 && (
          <div className="mt-5 border-t border-white/[0.06] pt-4">
            <p className="text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-600">
              Recognized providers
            </p>

            <div className="mt-3 flex flex-wrap gap-2">
              {certifications.trusted_providers.map(
                (provider) => (
                  <span
                    key={provider}
                    className="rounded-md border border-white/[0.06] bg-white/[0.02] px-2.5 py-1.5 text-[10px] text-slate-500"
                  >
                    {provider}
                  </span>
                )
              )}
            </div>
          </div>
        )}
    </>
  );
}

/* =========================================================
   EXPERIENCE
========================================================= */

function ExperienceTab({
  experience,
}) {
  const items = Array.isArray(
    experience?.items
  )
    ? experience.items
    : [];

  return (
    <div className="mt-7 space-y-5">
      <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <SectionHeader
          eyebrow="Professional credibility"
          title="Experience analysis"
          description={
            experience?.message ||
            "Professional experience signals detected in your resume."
          }
          score={normalizeScore(
            experience?.experience_score
          )}
        />

        {items.length ? (
          <div className="mt-6 space-y-3">
            {items.map(
              (item, index) => (
                <ExperienceItem
                  key={index}
                  item={item}
                />
              )
            )}
          </div>
        ) : (
          <ExperienceEmptyState />
        )}
      </section>
    </div>
  );
}

function ExperienceCard({
  experience,
}) {
  const score = normalizeScore(
    experience?.experience_score
  );

  const count =
    Number(experience?.count) || 0;

  return (
    <>
      <SectionHeader
        eyebrow="Professional credibility"
        title="Experience"
        description={
          experience?.message ||
          "Professional experience signals detected in your resume."
        }
        score={score}
      />

      {count > 0 ? (
        <div className="mt-6 rounded-xl border border-blue-400/10 bg-blue-400/[0.025] p-5">
          <div className="flex items-start gap-3">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-400/[0.08] text-blue-300">
              <BriefcaseIcon size={15} />
            </span>

            <div>
              <p className="text-sm font-medium text-slate-300">
                {count} experience{" "}
                {count === 1
                  ? "record"
                  : "records"}{" "}
                detected
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-600">
                Professional experience signals
                are included in your overall resume
                intelligence score.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <ExperienceEmptyState compact />
      )}
    </>
  );
}

function ExperienceEmptyState({
  compact = false,
}) {
  return (
    <div
      className={`${
        compact ? "mt-6" : "mt-6"
      } rounded-xl border border-amber-400/10 bg-amber-400/[0.025] p-5`}
    >
      <div className="flex items-start gap-3">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-400/[0.08] text-amber-300">
          <BriefcaseIcon size={15} />
        </span>

        <div>
          <p className="text-sm font-medium text-slate-300">
            No professional experience detected
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-600">
            Internships, freelance work,
            open-source contributions and
            professional experience can
            strengthen this signal when they
            genuinely apply to you.
          </p>
        </div>
      </div>
    </div>
  );
}

function ExperienceItem({
  item,
}) {
  if (
    typeof item === "string"
  ) {
    return (
      <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
        <p className="text-xs leading-5 text-slate-400">
          {item}
        </p>
      </div>
    );
  }

  const role =
    item?.role ||
    item?.title ||
    item?.position ||
    "Professional experience";

  const company =
    item?.company ||
    item?.organization ||
    "";

  const start =
    item?.start_date ||
    item?.start_year ||
    "";

  const end =
    item?.end_date ||
    item?.end_year ||
    "";

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-slate-200">
            {role}
          </p>

          {company && (
            <p className="mt-1 text-xs text-slate-500">
              {company}
            </p>
          )}
        </div>

        {(start || end) && (
          <span className="shrink-0 text-[10px] text-slate-600">
            {start || "—"} – {end || "Present"}
          </span>
        )}
      </div>
    </div>
  );
}

/* =========================================================
   DEPLOYMENT EVIDENCE
========================================================= */

function DeploymentEvidenceCard({
  deployment,
  projects = [],
}) {
  const applicationServing =
    Array.isArray(
      deployment?.application_serving
    )
      ? deployment.application_serving
      : [];

  const productionDeployment =
    Array.isArray(
      deployment?.production_deployment
    )
      ? deployment.production_deployment
      : [];

  const projectDeployment = [];

  if (Array.isArray(projects)) {
    projects.forEach((project) => {
      const features =
        Array.isArray(
          project?.deployment_analysis?.features
        )
          ? project.deployment_analysis.features
          : [];

      features.forEach((feature) => {
        if (
          !projectDeployment.some(
            (item) =>
              item.feature === feature &&
              item.project === project?.title
          )
        ) {
          projectDeployment.push({
            feature,
            project:
              project?.title ||
              "Project",
          });
        }
      });
    });
  }

  const hasEvidence =
    applicationServing.length > 0 ||
    productionDeployment.length > 0 ||
    projectDeployment.length > 0;

  return (
    <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
      <SectionHeader
        eyebrow="Deployment evidence"
        title="How your resume demonstrates deployment"
        description="ResumeIQ separates application serving from actual production deployment evidence."
      />

      {!hasEvidence ? (
        <div className="mt-6 rounded-xl border border-amber-400/10 bg-amber-400/[0.025] p-5">
          <div className="flex items-start gap-3">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-400/[0.08] text-amber-300">
              !
            </span>

            <div>
              <p className="text-sm font-medium text-slate-300">
                No deployment evidence detected
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-600">
                ResumeIQ did not find explicit production
                deployment evidence in the analyzed resume.
                Application frameworks such as Flask are
                treated as application-serving evidence,
                not proof of production deployment.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          <DeploymentColumn
            title="Application serving"
            description="Frameworks or technologies used to serve an application."
            items={applicationServing}
            variant="blue"
            emptyText="No application-serving evidence detected."
          />

          <DeploymentColumn
            title="Production deployment"
            description="Explicit evidence that an application was deployed to a production environment."
            items={productionDeployment}
            variant="green"
            emptyText="No production deployment evidence detected."
          />

          {projectDeployment.length > 0 && (
            <div className="lg:col-span-2">
              <DeploymentProjectEvidence
                items={projectDeployment}
              />
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function DeploymentColumn({
  title,
  description,
  items,
  variant,
  emptyText,
}) {
  const variantClass =
    variant === "green"
      ? "border-emerald-400/10 bg-emerald-400/[0.025]"
      : "border-blue-400/10 bg-blue-400/[0.025]";

  return (
    <div
      className={`rounded-xl border p-5 ${variantClass}`}
    >
      <p className="text-sm font-semibold text-slate-200">
        {title}
      </p>

      <p className="mt-1 text-[10px] leading-5 text-slate-600">
        {description}
      </p>

      <div className="mt-4 space-y-2">
        {items.length ? (
          items.map(
            (item, index) => (
              <div
                key={`${item}-${index}`}
                className="flex items-center gap-2 rounded-lg border border-white/[0.05] bg-black/10 px-3 py-2.5"
              >
                <span
                  className={`h-1.5 w-1.5 rounded-full ${
                    variant === "green"
                      ? "bg-emerald-400"
                      : "bg-blue-400"
                  }`}
                />

                <span className="text-xs text-slate-400">
                  {item}
                </span>
              </div>
            )
          )
        ) : (
          <p className="text-[10px] text-slate-600">
            {emptyText}
          </p>
        )}
      </div>
    </div>
  );
}

function DeploymentProjectEvidence({
  items,
}) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
      <p className="text-sm font-semibold text-slate-200">
        Project deployment signals
      </p>

      <p className="mt-1 text-[10px] leading-5 text-slate-600">
        Deployment-related technologies or approaches
        identified within individual projects.
      </p>

      <div className="mt-4 grid gap-2 sm:grid-cols-2">
        {items.map(
          ({ feature, project }, index) => (
            <div
              key={`${project}-${feature}-${index}`}
              className="rounded-lg border border-white/[0.05] bg-black/10 p-3"
            >
              <p className="text-[10px] font-semibold text-slate-400">
                {feature}
              </p>

              <p className="mt-1 text-[9px] text-slate-600">
                {project}
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
}

/* =========================================================
   CONFIDENCE
========================================================= */

function ConfidenceCard({
  confidence,
  sections,
}) {
  const detected = Object.entries(
    sections || {}
  ).filter(([, value]) => value);

  return (
    <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
      <SectionHeader
        eyebrow="Analysis confidence"
        title={`${confidence}% confidence`}
        description="Confidence reflects how much structured resume information ResumeIQ was able to detect."
      />

      <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="w-full max-w-md">
          <div className="h-2 overflow-hidden rounded-full bg-white/[0.06]">
            <div
              className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-400 transition-all duration-700"
              style={{
                width: `${confidence}%`,
              }}
            />
          </div>
        </div>

        <p className="text-[10px] text-slate-600">
          {detected.length} resume signals detected
        </p>
      </div>
    </section>
  );
}

/* =========================================================
   RECOMMENDATIONS
========================================================= */

function RecommendationsPreview({
  recommendations,
}) {
  return (
    <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
      <SectionHeader
        eyebrow="Action plan"
        title="What you should improve next"
        description="Practical improvements generated from your resume analysis."
      />

      <div className="mt-6 grid min-w-0 gap-3 sm:grid-cols-2">
        {recommendations.length ? (
          recommendations
            .slice(0, 4)
            .map(
              (recommendation, index) => (
                <RecommendationCard
                  key={index}
                  index={index}
                  text={formatRecommendation(
                    recommendation
                  )}
                />
              )
            )
        ) : (
          <EmptyState text="No recommendations were returned." />
        )}
      </div>
    </section>
  );
}

function RecommendationsTab({
  recommendations,
}) {
  return (
    <div className="mt-7">
      <section className="rounded-2xl border border-white/[0.07] bg-[#080d18] p-5 sm:p-7">
        <SectionHeader
          eyebrow="Action plan"
          title="Resume improvement roadmap"
          description="Prioritized recommendations based on your current resume."
        />

        <div className="mt-7 grid gap-3">
          {recommendations.length ? (
            recommendations.map(
              (recommendation, index) => (
                <RecommendationCard
                  key={index}
                  index={index}
                  text={formatRecommendation(
                    recommendation
                  )}
                  large
                />
              )
            )
          ) : (
            <EmptyState text="No recommendations were returned." />
          )}
        </div>
      </section>
    </div>
  );
}

function RecommendationCard({
  index,
  text,
  large = false,
}) {
  return (
    <div
      className={`group flex gap-4 rounded-xl border border-white/[0.06] bg-black/10 transition hover:border-blue-400/15 hover:bg-blue-400/[0.025] ${
        large ? "p-5 sm:p-6" : "p-4"
      }`}
    >
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-500/[0.08] text-[10px] font-semibold text-blue-300">
        {index + 1}
      </span>

      <div className="min-w-0 flex-1">
        <p className="text-xs leading-6 text-slate-300">
          {text}
        </p>
      </div>

      <ArrowIcon
        size={14}
        className="mt-1 shrink-0 text-slate-700 transition-transform group-hover:translate-x-0.5 group-hover:text-blue-400"
      />
    </div>
  );
}

/* =========================================================
   SMALL COMPONENTS
========================================================= */

function MetricCard({
  label,
  value,
  suffix,
  status,
  accent = "blue",
}) {
  const accentClasses = {
    blue: "border-blue-400/10",
    violet: "border-violet-400/10",
    cyan: "border-cyan-400/10",
    amber: "border-amber-400/10",
  };

  return (
    <div
      className={`min-w-0 rounded-2xl border bg-[#080d18] p-5 ${
        accentClasses[accent] ||
        accentClasses.blue
      }`}
    >
      <p className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-600">
        {label}
      </p>

      <div className="mt-3 flex items-baseline gap-1">
        <span className="text-3xl font-semibold tracking-tight text-white">
          {value}
        </span>

        <span className="text-[10px] text-slate-600">
          {suffix}
        </span>
      </div>

      <p className="mt-2 truncate text-[10px] text-slate-600">
        {status}
      </p>
    </div>
  );
}

function SectionHeader({
  eyebrow,
  title,
  description,
  score,
}) {
  return (
    <div>
      {eyebrow && (
        <p className="text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-600">
          {eyebrow}
        </p>
      )}

      <div className="mt-1 flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h2 className="text-base font-semibold tracking-tight text-white sm:text-lg">
            {title}
          </h2>

          {description && (
            <p className="mt-1 max-w-2xl text-xs leading-5 text-slate-600">
              {description}
            </p>
          )}
        </div>

        {score !== undefined &&
          score !== null && (
            <span className="shrink-0 text-xl font-semibold text-white">
              {Math.round(
                normalizeScore(score)
              )}
            </span>
          )}
      </div>
    </div>
  );
}

function ScoreRing({
  score,
}) {
  const radius = 67;

  const circumference =
    2 * Math.PI * radius;

  const safeScore =
    normalizeScore(score);

  const offset =
    circumference -
    (safeScore / 100) *
      circumference;

  return (
    <div className="relative flex h-[170px] w-[170px] items-center justify-center">
      <svg
        width="170"
        height="170"
        viewBox="0 0 170 170"
        className="-rotate-90"
      >
        <circle
          cx="85"
          cy="85"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="7"
          className="text-white/[0.06]"
        />

        <circle
          cx="85"
          cy="85"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="7"
          strokeLinecap="round"
          className="text-blue-500 transition-all duration-1000"
          strokeDasharray={
            circumference
          }
          strokeDashoffset={offset}
        />
      </svg>

      <div className="absolute text-center">
        <p className="text-4xl font-semibold tracking-tight text-white">
          {safeScore}
        </p>

        <p className="mt-0.5 text-[9px] uppercase tracking-[0.12em] text-slate-600">
          out of 100
        </p>
      </div>
    </div>
  );
}

function ScoreBar({
  label,
  value,
}) {
  const safeValue =
    normalizeScore(value);

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400">
          {label}
        </span>

        <span className="text-[10px] font-medium text-slate-400">
          {safeValue}
        </span>
      </div>

      <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
        <div
          className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-400 transition-all duration-700"
          style={{
            width: `${safeValue}%`,
          }}
        />
      </div>
    </div>
  );
}

function KeywordPanel({
  title,
  subtitle,
  keywords,
  variant,
}) {
  const positive =
    variant === "positive";

  const list = Array.isArray(
    keywords
  )
    ? keywords
    : [];

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold text-slate-300">
            {title}
          </p>

          <p className="mt-1 text-[10px] text-slate-600">
            {subtitle}
          </p>
        </div>

        <span
          className={`h-2 w-2 shrink-0 rounded-full ${
            positive
              ? "bg-emerald-400"
              : "bg-amber-400"
          }`}
        />
      </div>

      <div className="mt-5 flex max-h-[260px] flex-wrap gap-2 overflow-hidden">
        {list.length ? (
          list.map((keyword) => (
            <span
              key={keyword}
              className={`rounded-md border px-2.5 py-1.5 text-[10px] ${
                positive
                  ? "border-emerald-400/10 bg-emerald-400/[0.04] text-emerald-200/80"
                  : "border-amber-400/10 bg-amber-400/[0.04] text-amber-200/80"
              }`}
            >
              {keyword}
            </span>
          ))
        ) : (
          <span className="text-xs text-slate-600">
            None detected.
          </span>
        )}
      </div>
    </div>
  );
}

function ATSMini({
  label,
  value,
}) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <p className="text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-600">
        {label}
      </p>

      <p className="mt-2 text-2xl font-semibold text-white">
        {value}
      </p>
    </div>
  );
}

function SignalItem({
  label,
  positive,
}) {
  return (
    <div className="flex min-w-0 items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
      <span
        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg ${
          positive
            ? "bg-emerald-400/[0.08] text-emerald-300"
            : "bg-amber-400/[0.08] text-amber-300"
        }`}
      >
        {positive ? (
          <CheckIcon size={13} />
        ) : (
          <span>!</span>
        )}
      </span>

      <span className="truncate text-xs text-slate-400">
        {label}
      </span>
    </div>
  );
}

function ProjectMetric({
  label,
  value,
}) {
  const safeValue =
    normalizeScore(value);

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <p className="text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-600">
        {label}
      </p>

      <p className="mt-2 text-xl font-semibold text-white">
        {safeValue}
      </p>

      <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/[0.06]">
        <div
          className="h-full rounded-full bg-blue-500"
          style={{
            width: `${safeValue}%`,
          }}
        />
      </div>
    </div>
  );
}

function EmptyState({
  text,
}) {
  return (
    <div className="flex min-h-[90px] items-center justify-center rounded-xl border border-dashed border-white/[0.06] bg-white/[0.015] px-4">
      <p className="text-xs text-slate-600">
        {text}
      </p>
    </div>
  );
}

/* =========================================================
   HELPERS
========================================================= */

function normalizeScore(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return 0;
  }

  return Math.max(
    0,
    Math.min(100, Math.round(number))
  );
}

function getScoreLabel(score) {
  if (score >= 85) {
    return "Excellent";
  }

  if (score >= 70) {
    return "Strong";
  }

  if (score >= 55) {
    return "Needs improvement";
  }

  return "Needs attention";
}

function formatRecommendation(item) {
  if (typeof item === "string") {
    return item;
  }

  return (
    item?.message ||
    item?.recommendation ||
    item?.title ||
    "Review this area of your resume."
  );
}

function getKeywordArray(
  primary,
  fallback
) {
  if (Array.isArray(primary)) {
    return primary;
  }

  if (Array.isArray(fallback)) {
    return fallback;
  }

  return [];
}

/* =========================================================
   ICONS
========================================================= */

function ArrowIcon({
  size = 16,
  className = "",
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M5 12h14" />
      <path d="m13 6 6 6-6 6" />
    </svg>
  );
}

function CheckIcon({
  size = 16,
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m5 12 4 4L19 6" />
    </svg>
  );
}

function BriefcaseIcon({
  size = 16,
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect
        width="18"
        height="14"
        x="3"
        y="7"
        rx="2"
      />

      <path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />

      <path d="M3 12h18" />

      <path d="M10 12v2h4v-2" />
    </svg>
  );
}

export default ResumeReport;