import { useEffect, useMemo, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { useResumeContext } from "../../context/ResumeContext";

/* ========================================================================== */
/* Helper Functions                                                          */
/* ========================================================================== */

function hasValidScore(value) {
  return typeof value === "number" && !isNaN(value) && value >= 0;
}

function clampScore(value) {
  if (!hasValidScore(value)) return 0;
  return Math.max(0, Math.min(100, value));
}

function asObject(value) {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value;
  }
  return {};
}

function toArray(...values) {
  for (const value of values) {
    if (Array.isArray(value)) {
      return value;
    }
  }
  return [];
}

function getArray(primary, fallback) {
  if (Array.isArray(primary)) return primary;
  if (Array.isArray(fallback)) return fallback;
  return [];
}

function toNumber(value) {
  if (value === null || value === undefined || value === "") return 0;
  if (typeof value === "string" && value.trim() === "") return 0;
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
}

function getDisplayValue(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) {
    return value.map(getDisplayValue).filter(Boolean).join(", ");
  }
  if (typeof value === "object") {
    return (
      getDisplayValue(value.text) ||
      getDisplayValue(value.description) ||
      getDisplayValue(value.name) ||
      getDisplayValue(value.title) ||
      getDisplayValue(value.skill) ||
      getDisplayValue(value.recommendation) ||
      getDisplayValue(value.label) ||
      getDisplayValue(value.url) ||
      getDisplayValue(value.href) ||
      ""
    );
  }
  return String(value);
}

function getScoreLabel(score) {
  if (!hasValidScore(score)) return "Unavailable";
  const value = clampScore(score);
  if (value >= 85) return "Excellent";
  if (value >= 70) return "Good";
  if (value >= 55) return "Needs improvement";
  return "Needs attention";
}

function getIntelligenceHeadline(score) {
  if (!hasValidScore(score)) return "Score unavailable";
  const value = clampScore(score);
  if (value >= 85) return "Your resume is highly competitive";
  if (value >= 70) return "Your resume has a strong foundation";
  if (value >= 55) return "Your resume has a workable foundation";
  return "Your resume has several areas to strengthen";
}

function getInitials(name) {
  const normalizedName = getDisplayValue(name);
  if (!normalizedName) return "RI";
  const parts = normalizedName.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase();
  }
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

function truncateText(text, maxLength = 100) {
  const str = getDisplayValue(text);
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength) + "…";
}

function getFirstProfileValue(...values) {
  for (const value of values) {
    const normalized = getDisplayValue(value).trim();
    if (normalized) return normalized;
  }
  return "";
}

function normalizeBoolean(value) {
  if (typeof value === "boolean") return value;
  if (typeof value === "string") return value.toLowerCase() === "true";
  return false;
}

function isValidEmail(email) {
  if (!email || typeof email !== "string") return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
}

function isValidPhone(phone) {
  if (!phone || typeof phone !== "string") return false;
  const digits = phone.replace(/\D/g, "");
  return digits.length >= 7 && digits.length <= 15;
}

function normalizeExternalUrl(value) {
  const raw = getDisplayValue(value).trim();
  if (!raw) return "#";

  let url = raw.replace(/^[\s<>"']+|[\s<>"']+$/g, "");

  // If no scheme, try to prepend https:// for likely domains or social handles
  if (!/^[a-z][a-z0-9+.-]*:/i.test(url)) {
    if (url.includes(".") ||
        url.startsWith("in/") ||
        url.startsWith("pub/") ||
        url.startsWith("@") ||
        url.startsWith("linkedin.com") ||
        url.startsWith("github.com")) {
      url = `https://${url.replace(/^\/+/, "")}`;
    } else {
      return "#";
    }
  }

  // Validate and enforce HTTPS protocol
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== "https:") {
      return "#";
    }
    return parsed.href;
  } catch {
    return "#";
  }
}

function normalizePhone(value) {
  return getDisplayValue(value).replace(/[^\d+]/g, "");
}

function classifyProfileLink(value) {
  const normalized = getDisplayValue(value).trim();
  if (!normalized) return { type: "other", value: "" };

  const clean = normalized.replace(/^https?:\/\//i, "").replace(/^www\./, "");

  if (
    clean.includes("github.com") ||
    /^github\.com/.test(clean) ||
    /^@?[a-zA-Z0-9_-]+$/.test(clean)
  ) {
    return { type: "github", value: normalized };
  }

  if (
    clean.includes("linkedin.com") ||
    /^linkedin\.com/.test(clean) ||
    /^in\/[a-zA-Z0-9_-]+/.test(clean)
  ) {
    return { type: "linkedin", value: normalized };
  }

  return { type: "other", value: normalized };
}

function getRawResumeText(analysis) {
  if (!analysis || typeof analysis !== "object") return "";

  const candidates = [
    analysis.resume_text,
    analysis.resumeText,
    analysis.raw_text,
    analysis.rawText,
    analysis.resume_content,
    analysis.resumeContent,
    analysis.text,
    analysis.content,
    analysis.data?.resume_text,
    analysis.data?.resumeText,
    analysis.data?.raw_text,
    analysis.data?.rawText,
    analysis.data?.text,
    analysis.data?.content,
    analysis.resume,
  ];

  for (const value of candidates) {
    if (typeof value === "string") {
      const text = value.trim();
      if (text) return text;
    }
  }
  return "";
}

function cleanProfileValue(value) {
  return getDisplayValue(value)
    .trim()
    .replace(/[),.;:}\]]+$/g, "");
}

function extractProfileUrlFromText(text, type) {
  const source = getDisplayValue(text);
  if (!source) return "";

  const patterns = {
    github:
      /(?:https?:\/\/)?(?:www\.)?github\.com\/[A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)?/i,
    linkedin:
      /(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|pub)\/[A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)*/i,
  };

  const pattern = patterns[type];
  if (!pattern) return "";
  const match = source.match(pattern);
  return match ? cleanProfileValue(match[0]) : "";
}

function findProfileLink(type, ...sources) {
  const targetDomains = {
    github: ["github.com"],
    linkedin: ["linkedin.com"],
  };

  const domains = targetDomains[type] || [];
  const seen = new Set();

  const search = (value, depth = 0) => {
    if (depth > 10 || value === null || value === undefined) return "";

    if (typeof value === "string") {
      const text = value.trim();
      if (!text) return "";
      const lower = text.toLowerCase();

      if (domains.some((domain) => lower.includes(domain))) {
        const extracted = extractProfileUrlFromText(text, type);
        if (extracted) return extracted;
        const classified = classifyProfileLink(text);
        if (classified.type === type) return cleanProfileValue(text);
      }
      return "";
    }

    if (typeof value !== "object") return "";
    if (seen.has(value)) return "";
    seen.add(value);

    if (Array.isArray(value)) {
      for (const item of value) {
        const found = search(item, depth + 1);
        if (found) return found;
      }
      return "";
    }

    const prioritizedKeys =
      type === "github"
        ? [
            "github",
            "github_url",
            "githubUrl",
            "github_link",
            "githubLink",
            "github_profile",
            "githubProfile",
            "git",
            "git_url",
            "git_link",
          ]
        : [
            "linkedin",
            "linkedin_url",
            "linkedinUrl",
            "linkedin_link",
            "linkedIn",
            "linkedInUrl",
            "linkedin_profile",
            "linkedinProfile",
          ];

    for (const key of prioritizedKeys) {
      if (Object.prototype.hasOwnProperty.call(value, key)) {
        const found = search(value[key], depth + 1);
        if (found) return found;
      }
    }

    for (const child of Object.values(value)) {
      const found = search(child, depth + 1);
      if (found) return found;
    }

    return "";
  };

  for (const source of sources) {
    const found = search(source);
    if (found) return found;
  }
  return "";
}

function findPatternInSources(pattern, ...sources) {
  const seen = new Set();

  const search = (value, depth = 0) => {
    if (depth > 10 || value === null || value === undefined) return "";
    if (typeof value === "string") {
      const match = value.match(pattern);
      return match ? cleanProfileValue(match[0]) : "";
    }
    if (typeof value !== "object") return "";
    if (seen.has(value)) return "";
    seen.add(value);

    if (Array.isArray(value)) {
      for (const item of value) {
        const found = search(item, depth + 1);
        if (found) return found;
      }
      return "";
    }

    for (const child of Object.values(value)) {
      const found = search(child, depth + 1);
      if (found) return found;
    }
    return "";
  };

  for (const source of sources) {
    const found = search(source);
    if (found) return found;
  }
  return "";
}

function findEmailInSources(...sources) {
  return findPatternInSources(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i, ...sources);
}

function findPhoneInSources(...sources) {
  const match = findPatternInSources(/(?:\+?\d[\d\s().-]{8,}\d)/, ...sources);
  return match ? match.replace(/\s+/g, " ").trim() : "";
}

/* ========================================================================== */
/* Sub‑Components                                                            */
/* ========================================================================== */

function ExternalUrlDisplay({ url, label, icon }) {
  const cleanUrl = normalizeExternalUrl(url);
  if (!cleanUrl || cleanUrl === "#") return null;

  return (
    <a
      href={cleanUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="mt-2 flex items-center gap-2 break-all text-xs text-blue-400/90 transition hover:text-blue-300 overflow-hidden"
    >
      <span className="shrink-0 font-bold">{icon}</span>
      <span className="truncate">{cleanUrl}</span>
      <span className="shrink-0 text-[9px] text-slate-600">↗</span>
    </a>
  );
}

function ScoreRing({ score, size = "small" }) {
  const isValid = hasValidScore(score);
  const normalized = isValid ? clampScore(score) : 0;
  const isLarge = size === "large";

  const percentage = normalized / 100;
  const radius = isLarge ? 64 : 35;
  const center = 80;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - percentage);

  const dimension = isLarge ? "h-40 w-40" : "h-20 w-20";
  const textSize = isLarge ? "text-4xl" : "text-lg";

  return (
    <div className={`relative shrink-0 ${dimension}`}>
      <svg
        className="h-full w-full -rotate-90"
        viewBox="0 0 160 160"
        role="img"
        aria-label={
          isValid
            ? `Score ${normalized.toFixed(0)} out of 100`
            : "Score not available"
        }
      >
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.055)"
          strokeWidth={isLarge ? 8 : 7}
        />
        {isValid && (
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={isLarge ? 8 : 7}
            strokeLinecap="round"
            strokeDasharray={`${circumference} ${circumference}`}
            strokeDashoffset={dashOffset}
            className="text-blue-500 transition-[stroke-dashoffset] duration-1000 ease-out"
          />
        )}
      </svg>

      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`${textSize} font-bold tracking-tight text-white`}>
          {isValid ? normalized.toFixed(0) : "—"}
        </span>
        {isLarge && (
          <span className="mt-0.5 text-[8px] font-semibold uppercase tracking-wider text-slate-600">
            {isValid ? "/ 100" : "N/A"}
          </span>
        )}
      </div>
    </div>
  );
}

function ScorePill({ label, score }) {
  const isValid = hasValidScore(score);

  return (
    <div className="flex items-center gap-2 rounded-xl border border-white/[0.07] bg-white/[0.025] px-3 py-2">
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          isValid ? "bg-blue-400" : "bg-slate-600"
        }`}
      />
      <span className="text-[10px] font-semibold text-slate-400">{label}</span>
      <span className="text-xs font-bold text-white">
        {isValid ? clampScore(score).toFixed(0) : "—"}
      </span>
    </div>
  );
}

function ScoreBar({ score, label }) {
  const isValid = hasValidScore(score);
  const value = isValid ? clampScore(score) : 0;

  return (
    <div>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-300">{label}</span>
        <span className="text-xs font-bold text-blue-400">
          {isValid ? `${value.toFixed(0)}%` : "—"}
        </span>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/[0.05]">
        <div
          className="h-full rounded-full bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-400 transition-[width] duration-1000 ease-out"
          style={{ width: isValid ? `${value}%` : "0%" }}
        />
      </div>
    </div>
  );
}

function ScoreCard({ label, score }) {
  const isValid = hasValidScore(score);
  const normalized = isValid ? clampScore(score) : null;

  const getStatus = (value) => {
    if (value === null) return { label: "Unavailable", color: "bg-slate-600" };
    if (value >= 70) return { label: "Good", color: "bg-emerald-400" };
    if (value >= 55) return { label: "Fair", color: "bg-amber-400" };
    return { label: "Needs attention", color: "bg-red-400" };
  };

  const status = getStatus(normalized);

  return (
    <div className="rounded-2xl border border-white/[0.07] bg-[#090f1c] p-4 transition hover:border-white/[0.12]">
      <div className="flex items-center justify-between gap-3">
        <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
          {label}
        </p>
        <span
          className={`h-1.5 w-1.5 rounded-full ${status.color}`}
          aria-label={`Score status: ${status.label}`}
        />
      </div>
      <p className="mt-3 text-2xl font-bold tracking-tight text-white">
        {normalized !== null ? normalized.toFixed(0) : "—"}
      </p>
      <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/[0.05]">
        <div
          className="h-full rounded-full bg-blue-500 transition-[width] duration-700 ease-out"
          style={{ width: normalized !== null ? `${normalized}%` : "0%" }}
          aria-hidden="true"
        />
      </div>
    </div>
  );
}

function MiniMetric({ label, value }) {
  const numericValue = toNumber(value);
  const hasValue = value !== null && value !== undefined;

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.018] p-3.5">
      <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
        {label}
      </p>
      <p className="mt-2 text-lg font-bold text-slate-200">
        {hasValue ? numericValue.toFixed(0) : "—"}
      </p>
    </div>
  );
}

function InsightBadge({ label }) {
  return (
    <span className="rounded-lg border border-white/[0.07] bg-white/[0.025] px-2.5 py-1.5 text-[9px] font-medium text-slate-500">
      {label}
    </span>
  );
}

function InsightPanel({ eyebrow, title, icon, iconClass, items, emptyText }) {
  return (
    <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
      <div className="flex items-start gap-3">
        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-sm font-bold ${iconClass}`}
        >
          {icon}
        </div>
        <div className="min-w-0">
          <p className="text-[9px] font-bold uppercase tracking-[0.18em] text-slate-600">
            {eyebrow}
          </p>
          <h3 className="mt-1 text-lg font-bold text-white">{title}</h3>
        </div>
      </div>

      <div className="mt-5 space-y-2">
        {items.length ? (
          items.map((item, index) => (
            <div
              key={`${getDisplayValue(item)}-${index}`}
              className="rounded-xl border border-white/[0.05] bg-white/[0.018] px-4 py-3"
            >
              <p className="text-xs leading-5 text-slate-400">
                {getDisplayValue(item)}
              </p>
            </div>
          ))
        ) : (
          <p className="text-xs text-slate-600">{emptyText}</p>
        )}
      </div>
    </div>
  );
}

function SectionHeader({ eyebrow, title, description, action, onAction }) {
  return (
    <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-blue-400">
          {eyebrow}
        </p>
        <h2 className="mt-2 text-xl font-bold tracking-tight text-white sm:text-2xl">
          {title}
        </h2>
        <p className="mt-1 max-w-3xl text-xs leading-5 text-slate-600">
          {description}
        </p>
      </div>
      {action && (
        <button
          type="button"
          onClick={onAction}
          className="self-start rounded-xl border border-white/[0.07] bg-white/[0.025] px-4 py-2.5 text-[10px] font-semibold text-slate-400 transition hover:border-blue-500/20 hover:bg-blue-500/[0.04] hover:text-blue-300 sm:self-auto"
          aria-label={`View ${action}`}
        >
          {action}
          <span className="ml-2" aria-hidden="true">
            →
          </span>
        </button>
      )}
    </div>
  );
}

function PanelLabel({ title, value, suffix }) {
  return (
    <div className="flex items-end justify-between gap-4">
      <div>
        <p className="text-[9px] font-bold uppercase tracking-wider text-slate-600">
          {title}
        </p>
        <p className="mt-2 text-2xl font-bold text-white">{value}</p>
      </div>
      <span className="text-[9px] font-medium text-slate-600">{suffix}</span>
    </div>
  );
}

function KeywordChip({ label, positive = false }) {
  return (
    <span
      className={`rounded-lg border px-2.5 py-1.5 text-[9px] font-medium ${
        positive
          ? "border-emerald-500/10 bg-emerald-500/[0.05] text-emerald-300"
          : "border-amber-500/10 bg-amber-500/[0.04] text-amber-300/80"
      }`}
    >
      {positive ? "✓ " : "＋ "}
      {getDisplayValue(label)}
    </span>
  );
}

function SignalRow({ label, value, status, suffix = "" }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-white/[0.05] bg-white/[0.018] px-3.5 py-3">
      <div className="flex items-center gap-2">
        <span
          className={`h-1.5 w-1.5 rounded-full ${
            status === "good"
              ? "bg-emerald-400"
              : status === "weak"
              ? "bg-amber-400"
              : "bg-blue-400"
          }`}
        />
        <span className="text-[10px] font-medium text-slate-500">{label}</span>
      </div>
      <span className="text-xs font-bold text-slate-300">
        {getDisplayValue(value)}
        {suffix}
      </span>
    </div>
  );
}

function PriorityCard({ title, description, data = {}, level }) {
  const safeData = asObject(data);
  const matched = toArray(safeData.matched);
  const missing = toArray(safeData.missing);

  const styles = {
    critical: "border-red-500/10 bg-red-500/[0.025] text-red-300",
    high: "border-orange-500/10 bg-orange-500/[0.025] text-orange-300",
    important: "border-amber-500/10 bg-amber-500/[0.025] text-amber-300",
    supporting: "border-blue-500/10 bg-blue-500/[0.025] text-blue-300",
    optional: "border-slate-500/10 bg-white/[0.018] text-slate-400",
  };

  return (
    <div
      className={`rounded-[22px] border p-5 ${
        styles[level] || styles.optional
      }`}
    >
      <div>
        <h3 className="text-sm font-bold text-slate-200">{title}</h3>
        <p className="mt-1 text-[9px] text-slate-600">{description}</p>
      </div>
      <div className="mt-5 flex items-center gap-2">
        <span className="text-lg font-bold text-emerald-400">
          {matched.length}
        </span>
        <span className="text-[9px] text-slate-600">matched</span>
        <span className="mx-1 text-slate-700">·</span>
        <span className="text-lg font-bold text-amber-400">
          {missing.length}
        </span>
        <span className="text-[9px] text-slate-600">missing</span>
      </div>
      {missing.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {missing.slice(0, 5).map((item, index) => (
            <span
              key={`${getDisplayValue(item)}-${index}`}
              className="rounded-md border border-white/[0.05] bg-black/10 px-2 py-1 text-[8px] text-slate-500"
            >
              {getDisplayValue(item)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function SkillCategory({ category, skills }) {
  const values = toArray(skills);

  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.018] p-5">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold text-slate-200">{category}</h3>
        <span className="text-[9px] font-semibold text-slate-600">
          {values.length}
        </span>
      </div>
      <div className="mt-4 flex flex-wrap gap-1.5">
        {values.map((skill, index) => (
          <span
            key={`${getDisplayValue(skill)}-${index}`}
            className="rounded-lg border border-white/[0.06] bg-white/[0.025] px-2.5 py-1.5 text-[9px] capitalize text-slate-500"
          >
            {getDisplayValue(skill)}
          </span>
        ))}
      </div>
    </div>
  );
}

function MetricHighlight({ label, value, suffix = "%", text = false }) {
  const isValid = hasValidScore(value);

  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.018] p-4">
      <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
        {label}
      </p>
      <p
        className={`mt-2 font-bold text-slate-200 ${
          text ? "text-sm" : "text-2xl"
        }`}
      >
        {text
          ? getDisplayValue(value)
          : isValid
          ? `${clampScore(value).toFixed(0)}${suffix}`
          : "—"}
      </p>
    </div>
  );
}

function ProjectCard({ project, index }) {
  const safeProject = asObject(project);
  const technologies = toArray(safeProject.technologies);
  const actions = toArray(safeProject.actions, safeProject.bullets);
  const strengths = toArray(safeProject.strengths);
  const complexity = asObject(safeProject.complexity);
  const impact = asObject(safeProject.impact);
  const metricsAnalysis = asObject(safeProject.metrics_analysis);
  const deploymentAnalysis = asObject(safeProject.deployment_analysis);
  const engineeringAnalysis = asObject(safeProject.engineering_analysis);

  const deploymentFeatures = toArray(deploymentAnalysis.features);
  const engineeringFeatures = toArray(engineeringAnalysis.features);
  const impactKeywords = toArray(impact.keywords);
  const impactEvidence = toArray(impact.evidence);
  const complexityFeatures = toArray(complexity.features);
  const projectMetrics = toArray(metricsAnalysis.metrics_found);

  const score = hasValidScore(safeProject.score)
    ? clampScore(safeProject.score)
    : null;

  return (
    <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6 transition hover:border-white/[0.11] sm:p-7">
      <div className="flex flex-col gap-6 lg:flex-row">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-blue-500/10 text-sm font-bold text-blue-400">
          {String(index + 1).padStart(2, "0")}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <p className="text-[9px] font-bold uppercase tracking-wider text-slate-600">
                Project {index + 1}
              </p>
              <h3 className="mt-1 break-words text-lg font-bold text-white">
                {getDisplayValue(safeProject.title) || "Untitled project"}
              </h3>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <span className="rounded-xl bg-blue-500/10 px-3 py-2 text-xs font-bold text-blue-400">
                {score !== null ? score.toFixed(0) : "—"}
              </span>
              <span className="rounded-xl border border-white/[0.06] bg-white/[0.02] px-3 py-2 text-[9px] font-semibold text-slate-500">
                {score !== null ? getScoreLabel(score) : "Unavailable"}
              </span>
            </div>
          </div>

          {actions.length > 0 && (
            <div className="mt-5">
              <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
                Project evidence
              </p>
              <div className="mt-3 space-y-2">
                {actions.map((action, actionIndex) => (
                  <div
                    key={`${actionIndex}-${getDisplayValue(action)}`}
                    className="flex gap-3 rounded-xl border border-white/[0.05] bg-white/[0.018] p-3.5"
                  >
                    <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />
                    <p className="text-xs leading-5 text-slate-400">
                      {getDisplayValue(action)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <ProjectSignal
              label="Complexity"
              score={complexity.score}
              features={complexityFeatures}
            />
            <ProjectSignal
              label="Impact"
              score={impact.score}
              features={impactKeywords}
            />
            <ProjectSignal
              label="Metrics"
              score={metricsAnalysis.score}
              features={projectMetrics}
            />
            <ProjectSignal
              label="Engineering"
              score={engineeringAnalysis.score}
              features={engineeringFeatures}
            />
          </div>

          {complexityFeatures.length > 0 && (
            <div className="mt-5 rounded-xl border border-violet-500/10 bg-violet-500/[0.025] p-4">
              <p className="text-[9px] font-semibold uppercase tracking-wider text-violet-400">
                Technical complexity
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                {complexityFeatures.map((feature, featureIndex) => (
                  <SmallTag
                    key={`${getDisplayValue(feature)}-${featureIndex}`}
                    text={getDisplayValue(feature)}
                  />
                ))}
              </div>
            </div>
          )}

          {technologies.length > 0 && (
            <div className="mt-5">
              <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
                Technologies
              </p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {technologies.map((technology, technologyIndex) => (
                  <span
                    key={`${getDisplayValue(technology)}-${technologyIndex}`}
                    className="rounded-lg bg-white/[0.025] px-2.5 py-1.5 text-[9px] capitalize text-slate-500"
                  >
                    {getDisplayValue(technology)}
                  </span>
                ))}
              </div>
            </div>
          )}

          {strengths.length > 0 && (
            <div className="mt-5 flex flex-wrap gap-2">
              {strengths.map((strength, strengthIndex) => (
                <span
                  key={`${getDisplayValue(strength)}-${strengthIndex}`}
                  className="rounded-lg border border-emerald-500/10 bg-emerald-500/[0.035] px-2.5 py-1.5 text-[9px] text-emerald-300/80"
                >
                  ✓ {getDisplayValue(strength)}
                </span>
              ))}
            </div>
          )}

          {impactEvidence.length > 0 && (
            <div className="mt-5 rounded-xl border border-emerald-500/10 bg-emerald-500/[0.025] p-4">
              <p className="text-[9px] font-semibold uppercase tracking-wider text-emerald-400">
                Impact evidence
              </p>
              <div className="mt-3 space-y-2">
                {impactEvidence.slice(0, 5).map((evidence, evidenceIndex) => (
                  <p
                    key={`${evidenceIndex}-${getDisplayValue(evidence)}`}
                    className="text-xs leading-5 text-slate-500"
                  >
                    {getDisplayValue(evidence)}
                  </p>
                ))}
              </div>
            </div>
          )}

          <div className="mt-5 grid gap-3 lg:grid-cols-2">
            <div className="rounded-xl border border-amber-500/10 bg-amber-500/[0.025] p-3.5">
              <p className="text-[9px] font-semibold uppercase tracking-wider text-amber-400">
                Metric evidence
              </p>
              <p className="mt-1 text-[10px] leading-5 text-slate-500">
                {projectMetrics.length
                  ? projectMetrics.map(getDisplayValue).filter(Boolean).join(", ")
                  : "No measurable project outcomes detected."}
              </p>
            </div>
            <div className="rounded-xl border border-blue-500/10 bg-blue-500/[0.025] p-3.5">
              <p className="text-[9px] font-semibold uppercase tracking-wider text-blue-400">
                Deployment evidence
              </p>
              <p className="mt-1 text-[10px] leading-5 text-slate-500">
                {deploymentFeatures.length
                  ? deploymentFeatures
                      .map(getDisplayValue)
                      .filter(Boolean)
                      .join(", ")
                  : "No deployment evidence detected for this project."}
              </p>
            </div>
          </div>

          {engineeringFeatures.length > 0 && (
            <div className="mt-3 rounded-xl border border-white/[0.06] bg-white/[0.018] p-3.5">
              <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
                Engineering practices
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                {engineeringFeatures.map((feature, featureIndex) => (
                  <SmallTag
                    key={`${getDisplayValue(feature)}-${featureIndex}`}
                    text={getDisplayValue(feature)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ProjectSignal({ label, score, features }) {
  const values = toArray(features);
  const isValid = hasValidScore(score);

  return (
    <div className="rounded-xl border border-white/[0.05] bg-white/[0.018] p-3.5">
      <div className="flex items-center justify-between">
        <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
          {label}
        </p>
        <span className="text-[10px] font-bold text-slate-400">
          {isValid ? clampScore(score).toFixed(0) : "—"}
        </span>
      </div>
      <div className="mt-2 flex flex-wrap gap-1">
        {values.slice(0, 4).map((feature, index) => (
          <span
            key={`${getDisplayValue(feature)}-${index}`}
            className="text-[8px] text-slate-600"
          >
            {getDisplayValue(feature)}
          </span>
        ))}
      </div>
    </div>
  );
}

function ExperienceItem({ item }) {
  if (typeof item === "string") {
    return (
      <div className="rounded-xl border border-white/[0.06] bg-white/[0.018] p-4 text-xs text-slate-400">
        {item}
      </div>
    );
  }

  if (!item || typeof item !== "object") {
    return null;
  }

  const title =
    item.title ||
    item.role ||
    item.position ||
    item.job_title ||
    "Professional experience";

  const company = item.company || item.organization || item.employer || "";
  const startDate = item.start_date || item.start || "";
  const endDate = item.end_date || item.end || "";
  const description = item.description || item.summary || "";
  const actions = toArray(item.actions, item.bullets);

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.018] p-5">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-200">
            {getDisplayValue(title)}
          </p>
          {company && (
            <p className="mt-1 text-xs text-slate-500">
              {getDisplayValue(company)}
            </p>
          )}
        </div>
        {(startDate || endDate) && (
          <span className="text-[9px] text-slate-600">
            {getDisplayValue(startDate) || "—"}{" "}
            {endDate ? `– ${getDisplayValue(endDate)}` : ""}
          </span>
        )}
      </div>

      {description && (
        <p className="mt-4 text-xs leading-5 text-slate-500">
          {getDisplayValue(description)}
        </p>
      )}

      {actions.length > 0 && (
        <div className="mt-4 space-y-2">
          {actions.map((action, index) => (
            <div key={`${index}-${getDisplayValue(action)}`} className="flex gap-2">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />
              <p className="text-xs leading-5 text-slate-500">
                {getDisplayValue(action)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function EducationEntry({ entry }) {
  if (!entry || typeof entry !== "object") {
    return null;
  }

  const institution =
    entry.institution || entry.school || entry.university || "Institution not specified";
  const degree = entry.degree || entry.qualification || "";
  const field = entry.field || entry.specialization || entry.major || "";
  const startYear = entry.start_year ?? entry.start ?? "";
  const endYear = entry.end_year ?? entry.end ?? "";
  const cgpa = entry.cgpa ?? entry.gpa ?? null;
  const percentage = entry.percentage ?? entry.percent ?? null;

  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.018] p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-sm font-semibold leading-5 text-slate-200">
            {getDisplayValue(institution)}
          </p>
          {degree && (
            <p className="mt-1 text-xs font-medium text-slate-400">
              {getDisplayValue(degree)}
            </p>
          )}
          {field && (
            <p className="mt-1 text-[10px] leading-5 text-slate-600">
              {getDisplayValue(field)}
            </p>
          )}
        </div>
        {(startYear || endYear) && (
          <span className="shrink-0 rounded-lg border border-white/[0.06] bg-white/[0.02] px-2.5 py-1.5 text-[9px] font-medium text-slate-500">
            {getDisplayValue(startYear) || "—"}{" "}
            {endYear ? `– ${getDisplayValue(endYear)}` : ""}
          </span>
        )}
      </div>

      {(cgpa !== null || percentage !== null) && (
        <div className="mt-4 flex flex-wrap gap-2">
          {cgpa !== null && <SmallTag text={`CGPA: ${getDisplayValue(cgpa)}`} />}
          {percentage !== null && (
            <SmallTag text={`Percentage: ${getDisplayValue(percentage)}%`} />
          )}
        </div>
      )}
    </div>
  );
}

function CertificationItem({ certification }) {
  const safeCertification = asObject(certification);
  const name = safeCertification.name || "Certification";
  const provider = safeCertification.provider || "";
  const issueDate = safeCertification.issue_date || "";
  const credentialId = safeCertification.credential_id || "";
  const verified = safeCertification.verified === true;

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.018] p-3.5">
      <div className="flex items-start gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400">
          ✓
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium leading-5 text-slate-300">
            {getDisplayValue(name)}
          </p>
          <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-[9px] text-slate-600">
            {provider && <span>Provider: {getDisplayValue(provider)}</span>}
            {issueDate && <span>Issued: {getDisplayValue(issueDate)}</span>}
            {credentialId && <span>Credential: {getDisplayValue(credentialId)}</span>}
          </div>
          <span
            className={`mt-2 inline-flex rounded-md border px-2 py-1 text-[8px] font-medium ${
              verified
                ? "border-emerald-500/10 bg-emerald-500/[0.04] text-emerald-300"
                : "border-slate-500/10 bg-white/[0.02] text-slate-600"
            }`}
          >
            {verified ? "Externally verified" : "Detected from resume"}
          </span>
        </div>
      </div>
    </div>
  );
}

function DeploymentCard({ title, description, items, tone = "blue", emptyText }) {
  const safeItems = toArray(items);

  const tones = {
    blue: {
      border: "border-blue-500/10",
      bg: "bg-blue-500/[0.025]",
      icon: "bg-blue-500/10",
      text: "text-blue-400",
    },
    emerald: {
      border: "border-emerald-500/10",
      bg: "bg-emerald-500/[0.025]",
      icon: "bg-emerald-500/10",
      text: "text-emerald-400",
    },
  };

  const style = tones[tone] || tones.blue;

  return (
    <div className={`rounded-[26px] border ${style.border} bg-[#090f1c] p-6`}>
      <div className="flex items-start gap-4">
        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${style.icon} ${style.text}`}
        >
          {safeItems.length > 0 ? "✓" : "—"}
        </div>
        <div className="min-w-0">
          <p className={`text-[9px] font-bold uppercase tracking-[0.18em] ${style.text}`}>
            Deployment evidence
          </p>
          <h3 className="mt-2 text-lg font-bold text-white">{title}</h3>
          <p className="mt-2 text-xs leading-5 text-slate-600">{description}</p>
        </div>
      </div>

      <div className="mt-5">
        {safeItems.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {safeItems.map((item, index) => (
              <span
                key={`${getDisplayValue(item)}-${index}`}
                className={`rounded-lg border ${style.border} ${style.bg} px-3 py-2 text-[9px] font-medium capitalize ${style.text}`}
              >
                {getDisplayValue(item)}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-600">{emptyText}</p>
        )}
      </div>
    </div>
  );
}

function DataRow({ label, value, suffix = "" }) {
  const displayValue = getDisplayValue(value);
  return (
    <div className="flex items-center justify-between border-b border-white/[0.05] py-3 last:border-0">
      <span className="text-xs text-slate-600">{label}</span>
      <span className="max-w-[60%] text-right text-xs font-bold text-slate-300 truncate" title={displayValue}>
        {truncateText(displayValue || "—", 50)}
        {suffix}
      </span>
    </div>
  );
}

function RecommendationItem({ number, text }) {
  const normalizedText =
    typeof text === "string"
      ? text
      : text?.text || text?.recommendation || getDisplayValue(text);

  return (
    <div className="flex gap-4 rounded-2xl border border-white/[0.06] bg-white/[0.018] p-4">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-[9px] font-bold text-blue-400">
        {String(number).padStart(2, "0")}
      </div>
      <div>
        <p className="text-xs leading-5 text-slate-300">{normalizedText}</p>
      </div>
    </div>
  );
}

function FocusItem({ number, title, description }) {
  return (
    <div className="flex gap-3">
      <span className="text-[9px] font-bold text-blue-400">{number}</span>
      <div>
        <p className="text-xs font-semibold text-slate-300">{title}</p>
        <p className="mt-1 text-[10px] leading-5 text-slate-600">{description}</p>
      </div>
    </div>
  );
}

function SmallTag({ text }) {
  return (
    <span className="rounded-lg border border-white/[0.06] bg-white/[0.02] px-2.5 py-1.5 text-[9px] capitalize text-slate-500">
      {getDisplayValue(text)}
    </span>
  );
}

function EmptyPanel({ text }) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.018] p-5 text-xs text-slate-600">
      {getDisplayValue(text)}
    </div>
  );
}

/* ========================================================================== */
/* Main Component                                                            */
/* ========================================================================== */

function ResumeAnalysis() {
  const navigate = useNavigate();
  const { analysis, clearAnalysis } = useResumeContext();

  const [activeSection, setActiveSection] = useState("overview");

  /* ---------------------------------------------------------------------- */
  /* Normalized metrics                                                     */
  /* ---------------------------------------------------------------------- */

  const metrics = useMemo(() => {
    if (!analysis || typeof analysis !== "object") {
      return null;
    }

    const getScore = (value) => {
      if (typeof value === "number" && !isNaN(value) && value >= 0) {
        return clampScore(value);
      }
      return null;
    };

    return {
      intelligence: getScore(analysis.resume_intelligence_score),
      ats: getScore(analysis.ats_analysis?.ats_score),
      skills: getScore(analysis.skills_analysis?.skill_score),
      projects: getScore(analysis.project_analysis?.score),
      experience: getScore(analysis.experience_analysis?.experience_score),
      certifications: getScore(analysis.certifications?.score),
      education: getScore(
        analysis.education?.score ?? analysis.education?.education_score
      ),
      achievements: getScore(analysis.achievement_analysis?.score),
    };
  }, [analysis]);

  /* ---------------------------------------------------------------------- */
  /* Safe backend objects                                                   */
  /* ---------------------------------------------------------------------- */

  const safeData = useMemo(() => {
    if (!analysis || typeof analysis !== "object") {
      return null;
    }

    return {
      ats: asObject(analysis.ats_analysis),
      skills: asObject(analysis.skills_analysis),
      projects: asObject(analysis.project_analysis),
      experience: asObject(analysis.experience_analysis),
      certifications: asObject(analysis.certifications),
      education: asObject(analysis.education),
      achievements: asObject(analysis.achievement_analysis),
      candidateProfile: asObject(analysis.candidate_profile),
      metadata: asObject(analysis.metadata),
      sections: asObject(analysis.sections_detected),
      scoreBreakdown: asObject(
        analysis.score_breakdown?.score_breakdown ?? analysis.score_breakdown
      ),
    };
  }, [analysis]);

  /* ---------------------------------------------------------------------- */
  /* Empty state                                                            */
  /* ---------------------------------------------------------------------- */

  if (!analysis || !metrics || !safeData) {
    return (
      <div className="min-h-screen bg-[#050816] text-white">
        <div className="pointer-events-none fixed inset-0 overflow-hidden">
          <div className="absolute -right-40 -top-40 h-[500px] w-[500px] rounded-full bg-blue-600/[0.07] blur-[140px]" />
          <div className="absolute -bottom-40 -left-40 h-[500px] w-[500px] rounded-full bg-indigo-600/[0.06] blur-[140px]" />
        </div>

        <div className="relative mx-auto flex min-h-screen max-w-4xl items-center justify-center px-6">
          <div className="w-full rounded-[32px] border border-white/[0.08] bg-[#0a1020] p-8 text-center shadow-2xl shadow-black/30 sm:p-12">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-blue-500/20 bg-blue-500/10">
              <svg
                width="28"
                height="28"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <path d="M14 2v6h6" />
                <path d="M8 13h8" />
                <path d="M8 17h5" />
              </svg>
            </div>

            <p className="mt-6 text-[10px] font-semibold uppercase tracking-[0.22em] text-blue-400">
              Resume intelligence
            </p>

            <h1 className="mt-3 text-2xl font-bold tracking-tight text-white sm:text-3xl">
              No analysis available
            </h1>

            <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-slate-500">
              Upload your resume from the dashboard to
              generate your complete ResumeIQ
              intelligence report.
            </p>

            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              className="mt-8 inline-flex items-center gap-3 rounded-xl bg-blue-600 px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-blue-600/20 transition hover:-translate-y-0.5 hover:bg-blue-500"
            >
              Analyze a resume
              <span aria-hidden="true">→</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  const {
    ats,
    skills,
    projects,
    experience,
    certifications,
    education,
    achievements,
    candidateProfile,
    metadata,
    sections,
    scoreBreakdown,
  } = safeData;

  const rawResumeText = getRawResumeText(analysis);
  const strengths = toArray(ats.strengths);
  const issues = toArray(ats.issues);
  const recommendations = toArray(analysis.recommendations);
  const matchedKeywords = getArray(
    ats.matched_keywords,
    ats.keyword_analysis?.matched
  );
  const missingKeywords = getArray(
    ats.missing_keywords,
    ats.keyword_analysis?.missing
  );
  const priorities = asObject(ats.keyword_analysis?.priorities);
  const technologyCoverage = asObject(ats.technology_coverage);
  const categories = asObject(skills.categories);
  const categoryEntries = Object.entries(categories);

  // Section detection - only count real sections
  const detectedSections = Object.entries(sections).filter(([, value]) => {
    if (value === null || value === undefined || value === false) return false;
    if (Array.isArray(value) && value.length === 0) return false;
    if (typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === 0)
      return false;
    return true;
  });

  const presentSectionCount = detectedSections.length;
  const totalSectionCount = Object.keys(sections).length;
  const hasSectionData = totalSectionCount > 0;

  const readinessLabel = getScoreLabel(metrics.intelligence);
  const atsLabel = getScoreLabel(metrics.ats);

  /* ---------------------------------------------------------------------- */
  /* Education                                                              */
  /* ---------------------------------------------------------------------- */

  const educationEntries = getArray(education.entries, education.education);

  /* ---------------------------------------------------------------------- */
  /* Projects - Normalize                                                   */
  /* ---------------------------------------------------------------------- */

  const normalizeProject = (project) => {
    if (typeof project === "string") {
      return {
        title: project,
        actions: [],
        technologies: [],
        score: null,
        strengths: [],
      };
    }
    if (!project || typeof project !== "object") {
      return {
        title: "Untitled project",
        actions: [],
        technologies: [],
        score: null,
        strengths: [],
      };
    }
    return {
      title: project.title || project.name || "Untitled project",
      actions: toArray(project.actions, project.bullets, project.points),
      technologies: toArray(project.technologies, project.tech, project.tech_stack),
      strengths: toArray(project.strengths),
      score: project.score || project.project_score,
      complexity: asObject(project.complexity),
      impact: asObject(project.impact),
      metrics_analysis: asObject(project.metrics_analysis),
      deployment_analysis: asObject(project.deployment_analysis),
      engineering_analysis: asObject(project.engineering_analysis),
    };
  };

  const projectEntries = getArray(projects.projects).map(normalizeProject);

  /* ---------------------------------------------------------------------- */
  /* Experience                                                             */
  /* ---------------------------------------------------------------------- */

  const normalizeExperience = (item) => {
    if (typeof item === "string") {
      return { title: item, company: "", description: "", actions: [] };
    }
    if (!item || typeof item !== "object") {
      return { title: "Professional experience", company: "", description: "", actions: [] };
    }
    return {
      title:
        item.title || item.role || item.position || item.job_title || "Professional experience",
      company: item.company || item.organization || item.employer || "",
      start_date: item.start_date || item.start || "",
      end_date: item.end_date || item.end || "",
      description: item.description || item.summary || "",
      actions: toArray(item.actions, item.bullets),
    };
  };

  const experienceItems = getArray(experience.items, experience.experience).map(
    normalizeExperience
  );

  /* ---------------------------------------------------------------------- */
  /* Certifications                                                         */
  /* ---------------------------------------------------------------------- */

  const normalizeCertification = (cert) => {
    if (typeof cert === "string") {
      return { name: cert, provider: "", issue_date: "", credential_id: "", verified: false };
    }
    if (!cert || typeof cert !== "object") {
      return { name: "Certification", provider: "", issue_date: "", credential_id: "", verified: false };
    }
    return {
      name: cert.name || cert.title || "Certification",
      provider: cert.provider || cert.issuer || "",
      issue_date: cert.issue_date || cert.issueDate || cert.date || "",
      credential_id: cert.credential_id || cert.credentialId || cert.id || "",
      verified: cert.verified === true,
    };
  };

  const certificationDetails = toArray(certifications.certification_details).map(
    normalizeCertification
  );
  const certificationNames = toArray(certifications.certifications);

  /* ---------------------------------------------------------------------- */
  /* Candidate profile                                                      */
  /* ---------------------------------------------------------------------- */

  const profileSkills = toArray(candidateProfile.skills);
  const profileName = getFirstProfileValue(
    candidateProfile.name,
    candidateProfile.full_name,
    candidateProfile.fullName,
    analysis.name,
    analysis.full_name,
    metadata.name,
    metadata.full_name
  );

  /* ---------------------------------------------------------------------- */
  /* Candidate contact extraction                                           */
  /* ---------------------------------------------------------------------- */

  const profileEmail =
    getFirstProfileValue(
      candidateProfile.email,
      candidateProfile.email_address,
      candidateProfile.emailAddress,
      analysis.email,
      analysis.email_address,
      metadata.email
    ) || findEmailInSources(candidateProfile, metadata, analysis, rawResumeText);

  const profilePhone =
    getFirstProfileValue(
      candidateProfile.phone,
      candidateProfile.phone_number,
      candidateProfile.phoneNumber,
      candidateProfile.mobile,
      candidateProfile.mobile_number,
      candidateProfile.mobileNumber,
      analysis.phone,
      analysis.phone_number,
      metadata.phone,
      metadata.mobile
    ) || findPhoneInSources(candidateProfile, metadata, analysis, rawResumeText);

  const profileLinkedIn =
    getFirstProfileValue(
      candidateProfile.linkedin,
      candidateProfile.linkedin_url,
      candidateProfile.linkedinUrl,
      candidateProfile.linkedin_link,
      candidateProfile.linkedIn,
      candidateProfile.linkedInUrl,
      candidateProfile.linkedin_profile,
      candidateProfile.linkedinProfile,
      analysis.linkedin,
      analysis.linkedin_url,
      metadata.linkedin,
      metadata.linkedin_url
    ) || findProfileLink("linkedin", candidateProfile, metadata, analysis, rawResumeText);

  const profileGitHub =
    getFirstProfileValue(
      candidateProfile.github,
      candidateProfile.github_url,
      candidateProfile.githubUrl,
      candidateProfile.github_link,
      candidateProfile.githubLink,
      candidateProfile.github_profile,
      candidateProfile.githubProfile,
      candidateProfile.git,
      candidateProfile.git_url,
      candidateProfile.git_link,
      candidateProfile.gitHub,
      candidateProfile.gitHubUrl,
      analysis.github,
      analysis.github_url,
      analysis.github_link,
      metadata.github,
      metadata.github_url
    ) || findProfileLink("github", candidateProfile, metadata, analysis, rawResumeText);

  const genericProfileLink = getFirstProfileValue(
    candidateProfile.link,
    candidateProfile.links,
    candidateProfile.social_links,
    candidateProfile.socialLinks,
    analysis.link,
    analysis.links,
    metadata.link,
    metadata.links
  );

  const classifiedGenericLink = classifyProfileLink(genericProfileLink);
  const finalLinkedIn =
    profileLinkedIn || (classifiedGenericLink.type === "linkedin" ? classifiedGenericLink.value : "");
  const finalGitHub =
    profileGitHub || (classifiedGenericLink.type === "github" ? classifiedGenericLink.value : "");

  const hasProfileContact = Boolean(profileEmail || profilePhone || finalLinkedIn || finalGitHub);

  /* ---------------------------------------------------------------------- */
  /* Deployment                                                             */
  /* ---------------------------------------------------------------------- */

  const deploymentAnalysis = asObject(ats.deployment_analysis);
  const applicationServing = toArray(deploymentAnalysis.application_serving);
  const productionDeployment = toArray(deploymentAnalysis.production_deployment);
  const hasProductionDeployment = normalizeBoolean(deploymentAnalysis.has_production_deployment);

  /* ---------------------------------------------------------------------- */
  /* ATS section analysis                                                   */
  /* ---------------------------------------------------------------------- */

  const sectionAnalysis = asObject(ats.section_analysis);
  const sectionsPresent = toArray(sectionAnalysis.present);
  const sectionsMissing = toArray(sectionAnalysis.missing);
  const actionVerbs = toArray(ats.action_verbs_found);
  const atsMetrics = toArray(ats.metrics_found);

  /* ---------------------------------------------------------------------- */
  /* Achievement analysis                                                   */
  /* ---------------------------------------------------------------------- */

  const achievementSignals = toArray(achievements.signals);
  const achievementItems = toArray(achievements.achievements);

  /* ---------------------------------------------------------------------- */
  /* Navigation                                                             */
  /* ---------------------------------------------------------------------- */

  const scrollToSection = useCallback((id) => {
    setActiveSection(id);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  }, []);

  const handleClearAnalysis = useCallback(() => {
    clearAnalysis();
    navigate("/dashboard");
  }, [clearAnalysis, navigate]);

  /* ---------------------------------------------------------------------- */
  /* Active section tracking                                                */
  /* ---------------------------------------------------------------------- */

  useEffect(() => {
    const sectionIds = [
      "overview",
      "profile",
      "ats",
      "skills",
      "projects",
      "experience",
      "education",
      "deployment",
      "achievements",
      "recommendations",
    ];

    const elements = sectionIds
      .map((id) => document.getElementById(id))
      .filter(Boolean);

    if (!elements.length) {
      return undefined;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const visibleEntries = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);

        if (visibleEntries.length > 0) {
          const visibleId = visibleEntries[0].target.id;
          if (visibleId) {
            setActiveSection(visibleId);
          }
        }
      },
      {
        root: null,
        rootMargin: "-80px 0px -30% 0px",
        threshold: [0, 0.2, 0.4, 0.6, 0.8],
      }
    );

    elements.forEach((element) => observer.observe(element));

    return () => {
      observer.disconnect();
    };
  }, [analysis]);

  // Scroll to the top when the component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen bg-[#050816] text-white">
      {/* Background */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -right-48 -top-48 h-[650px] w-[650px] rounded-full bg-blue-600/[0.055] blur-[160px]" />
        <div className="absolute -bottom-64 -left-48 h-[650px] w-[650px] rounded-full bg-indigo-600/[0.05] blur-[160px]" />
        <div className="absolute left-1/2 top-1/2 h-[450px] w-[450px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/[0.018] blur-[150px]" />
      </div>

      {/* ============================================================== */}
      {/* STICKY HEADER – placed outside the main container             */}
      {/* ============================================================== */}
      <header className="sticky top-0 z-30 border-b border-white/[0.06] bg-[#050816]/90 px-4 py-4 backdrop-blur-xl sm:px-6 lg:px-8 xl:px-10">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.025] text-slate-400 transition hover:border-blue-500/20 hover:bg-blue-500/[0.06] hover:text-white"
              aria-label="Back to dashboard"
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M19 12H5" />
                <path d="m12 19-7-7 7-7" />
              </svg>
            </button>

            <div>
              <p className="text-[9px] font-semibold uppercase tracking-[0.22em] text-blue-400">
                ResumeIQ Intelligence
              </p>
              <h1 className="mt-1 text-lg font-bold tracking-tight text-white">
                Resume analysis
              </h1>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="hidden items-center gap-2 rounded-xl border border-white/[0.07] bg-white/[0.025] px-3 py-2 sm:flex">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              <span className="text-[10px] font-medium text-slate-500">
                Analysis complete
              </span>
            </div>

            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              className="rounded-xl border border-white/[0.08] bg-white/[0.025] px-4 py-2.5 text-xs font-semibold text-slate-300 transition hover:border-blue-500/20 hover:bg-blue-500/[0.05] hover:text-white"
            >
              Analyze another
            </button>

            <button
              type="button"
              onClick={handleClearAnalysis}
              className="rounded-xl border border-red-500/10 bg-red-500/[0.025] px-4 py-2.5 text-xs font-medium text-red-300/70 transition hover:border-red-500/25 hover:bg-red-500/[0.06] hover:text-red-300"
            >
              Clear report
            </button>
          </div>
        </div>
      </header>

      {/* ============================================================== */}
      {/* NAVIGATION – moved outside main to allow its own scroll        */}
      {/* ============================================================== */}
      <nav
        aria-label="Resume report sections"
        className="mb-7 overflow-x-auto w-full rounded-2xl border border-white/[0.07] bg-[#080d1a]/90 p-1.5 backdrop-blur-xl"
      >
        <div className="flex min-w-max gap-1">
          {[
            ["overview", "Overview"],
            ["profile", "Candidate"],
            ["ats", "ATS Intelligence"],
            ["skills", "Skills"],
            ["projects", "Projects"],
            ["experience", "Experience"],
            ["education", "Education"],
            ["deployment", "Deployment"],
            ["achievements", "Achievements"],
            ["recommendations", "Action plan"],
          ].map(([id, label]) => (
            <button
              key={id}
              type="button"
              onClick={() => scrollToSection(id)}
              aria-current={activeSection === id ? "location" : undefined}
              className={`rounded-xl px-4 py-2.5 text-xs font-semibold transition ${
                activeSection === id
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/15"
                  : "text-slate-500 hover:bg-white/[0.035] hover:text-slate-200"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </nav>

      {/* ============================================================== */}
      {/* MAIN CONTENT – fully visible, no clipping                     */}
      {/* ============================================================== */}
      <main className="relative mx-auto max-w-[1600px] px-4 py-5 sm:px-6 lg:px-8 xl:px-10">
        {/* Heading */}
        <section className="mb-7">
          <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-blue-400">
                Executive assessment
              </p>
              <h2 className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Your resume intelligence report
              </h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                A comprehensive assessment of your
                resume&apos;s structure, ATS readiness,
                skills, projects, experience and
                career signals.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <ScorePill label={readinessLabel} score={metrics.intelligence} />
              <div className="hidden h-10 w-px bg-white/[0.07] sm:block" />
              <div className="text-right">
                <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
                  Analysis confidence
                </p>
                <p className="mt-1 text-sm font-bold text-slate-300">
                  {hasValidScore(analysis.confidence)
                    ? clampScore(analysis.confidence).toFixed(0)
                    : "—"}
                  %
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Overview */}
        <section id="overview" className="scroll-mt-28">
          <div className="grid gap-5 xl:grid-cols-[1.25fr_0.75fr]">
            <div className="relative overflow-hidden rounded-[28px] border border-white/[0.08] bg-gradient-to-br from-[#0c1529] via-[#09111f] to-[#080d19] p-6 shadow-2xl shadow-black/20 sm:p-8">
              <div className="pointer-events-none absolute -right-32 -top-32 h-72 w-72 rounded-full bg-blue-500/[0.08] blur-[90px]" />

              <div className="relative">
                <div className="flex flex-col gap-8 lg:flex-row lg:items-center">
                  <ScoreRing score={metrics.intelligence} size="large" />
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full border border-blue-400/15 bg-blue-500/10 px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider text-blue-300">
                        Resume intelligence
                      </span>
                      <span className="rounded-full border border-emerald-400/10 bg-emerald-400/[0.06] px-2.5 py-1 text-[9px] font-semibold text-emerald-300">
                        {readinessLabel}
                      </span>
                    </div>

                    <h3 className="mt-4 text-2xl font-bold tracking-tight text-white">
                      {getIntelligenceHeadline(metrics.intelligence)}
                    </h3>

                    <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
                      ResumeIQ evaluated your resume
                      across skills, projects, ATS
                      readiness, education,
                      certifications, experience and
                      measurable career signals.
                    </p>

                    <div className="mt-6 flex flex-wrap gap-2">
                      <InsightBadge
                        label={
                          hasSectionData
                            ? `${presentSectionCount}/${totalSectionCount} sections detected`
                            : "Section analysis unavailable"
                        }
                      />
                      <InsightBadge
                        label={`${toNumber(skills.total_skills)} skills detected`}
                      />
                      <InsightBadge
                        label={`${toNumber(projects.project_count) || projectEntries.length} projects analyzed`}
                      />
                      <InsightBadge
                        label={`${toNumber(certifications.count)} certifications`}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-[28px] border border-white/[0.08] bg-[#0a101e] p-6 shadow-2xl shadow-black/20 sm:p-7">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-slate-600">
                    ATS readiness
                  </p>
                  <h3 className="mt-2 text-lg font-bold text-white">
                    Screening performance
                  </h3>
                </div>
                <span className="rounded-xl bg-blue-500/10 px-3 py-2 text-xs font-bold text-blue-400">
                  {hasValidScore(metrics.ats) ? metrics.ats.toFixed(0) : "—"}
                </span>
              </div>

              <div className="mt-7">
                <ScoreBar score={metrics.ats} label={atsLabel} />
              </div>

              <div className="mt-7 grid grid-cols-2 gap-3">
                <MiniMetric
                  label="Keyword score"
                  value={ats.keyword_analysis?.score}
                />
                <MiniMetric
                  label="Section quality"
                  value={ats.section_analysis?.score}
                />
                <MiniMetric
                  label="Technical context"
                  value={ats.analysis?.technical_context}
                />
                <MiniMetric
                  label="Readability"
                  value={ats.analysis?.readability}
                />
              </div>
            </div>
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
            <ScoreCard
              label="Skills"
              score={scoreBreakdown.skills ?? metrics.skills}
            />
            <ScoreCard
              label="Projects"
              score={scoreBreakdown.projects ?? metrics.projects}
            />
            <ScoreCard
              label="Experience"
              score={scoreBreakdown.experience ?? metrics.experience}
            />
            <ScoreCard label="ATS" score={scoreBreakdown.ats ?? metrics.ats} />
            <ScoreCard
              label="Certifications"
              score={scoreBreakdown.certifications ?? metrics.certifications}
            />
            <ScoreCard
              label="Education"
              score={scoreBreakdown.education ?? metrics.education}
            />
            <ScoreCard
              label="Achievements"
              score={scoreBreakdown.achievements ?? metrics.achievements}
            />
          </div>
        </section>

        {/* Strengths / Issues */}
        <section className="mt-7 grid gap-5 lg:grid-cols-2">
          <InsightPanel
            title="What is working"
            eyebrow="Strengths"
            icon="✓"
            iconClass="bg-emerald-500/10 text-emerald-400"
            items={strengths}
            emptyText="No major strengths were detected."
          />
          <InsightPanel
            title="What needs attention"
            eyebrow="Issues detected"
            icon="!"
            iconClass="bg-amber-500/10 text-amber-400"
            items={issues}
            emptyText="No significant issues were detected."
          />
        </section>

        {/* Candidate Profile */}
        <section id="profile" className="mt-12 scroll-mt-28">
          <SectionHeader
            eyebrow="Candidate intelligence"
            title="Candidate profile"
            description="Core identity, professional summary and resume-level profile signals extracted from your resume."
          />

          <div className="grid gap-5 lg:grid-cols-[0.75fr_1.25fr]">
            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6 sm:p-7">
              <div className="flex items-start gap-4">
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-blue-500/10 text-lg font-bold text-blue-400">
                  {getInitials(profileName)}
                </div>

                <div className="min-w-0 flex-1">
                  <p className="text-[9px] font-bold uppercase tracking-[0.18em] text-blue-400">
                    Candidate
                  </p>
                  <h3 className="mt-1 break-words text-xl font-bold text-white">
                    {profileName || "Candidate profile"}
                  </h3>

                  {profileEmail && isValidEmail(profileEmail) && (
                    <a
                      href={`mailto:${profileEmail}`}
                      className="mt-3 flex items-center gap-2 break-all text-xs text-slate-400 transition hover:text-blue-300"
                    >
                      <span className="shrink-0 text-blue-400">✉</span>
                      <span className="truncate">{profileEmail}</span>
                    </a>
                  )}

                  {profilePhone && isValidPhone(profilePhone) && (
                    <a
                      href={`tel:${normalizePhone(profilePhone)}`}
                      className="mt-2 flex items-center gap-2 text-xs text-slate-500 transition hover:text-blue-300"
                    >
                      <span className="shrink-0 text-blue-400">☎</span>
                      <span className="truncate">{profilePhone}</span>
                    </a>
                  )}

                  {finalLinkedIn && (
                    <ExternalUrlDisplay url={finalLinkedIn} label="LinkedIn" icon="in" />
                  )}

                  {finalGitHub && (
                    <ExternalUrlDisplay url={finalGitHub} label="GitHub" icon="◉" />
                  )}

                  {!hasProfileContact && (
                    <p className="mt-3 text-xs text-slate-600">
                      No contact information was extracted from the resume.
                    </p>
                  )}
                </div>
              </div>

              <div className="mt-6 space-y-3">
                <DataRow
                  label="Profile extraction confidence"
                  value={candidateProfile.confidence}
                  suffix="%"
                />
                <DataRow label="Skills in profile" value={profileSkills.length} />
                <DataRow
                  label="Projects in profile"
                  value={toArray(candidateProfile.projects).length}
                />
                <DataRow
                  label="Experience entries"
                  value={toArray(candidateProfile.experience).length}
                />
              </div>
            </div>

            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6 sm:p-7">
              <p className="text-[9px] font-bold uppercase tracking-[0.18em] text-slate-600">
                Professional summary
              </p>
              <p className="mt-4 text-sm leading-7 text-slate-400">
                {getDisplayValue(candidateProfile.summary) ||
                  "No professional summary was extracted from the candidate profile."}
              </p>

              {profileSkills.length > 0 && (
                <div className="mt-7">
                  <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
                    Profile skills
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {profileSkills.slice(0, 20).map((skill, index) => {
                      const label = getDisplayValue(skill);
                      if (!label) return null;
                      return (
                        <span
                          key={`${label}-${index}`}
                          className="rounded-lg border border-white/[0.06] bg-white/[0.025] px-2.5 py-1.5 text-[9px] capitalize text-slate-500"
                        >
                          {label}
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* ATS */}
        <section id="ats" className="mt-12 scroll-mt-28">
          <SectionHeader
            eyebrow="ATS intelligence"
            title="How your resume is being interpreted"
            description="The most important ATS signals detected from your current resume."
            action="Open ATS Intelligence"
            onAction={() => navigate("/ats-intelligence")}
          />

          <div className="grid gap-5 lg:grid-cols-3">
            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
              <PanelLabel
                title="Keyword coverage"
                value={`${matchedKeywords.length}`}
                suffix="matched"
              />
              <div className="mt-5 flex flex-wrap gap-2">
                {matchedKeywords.slice(0, 12).map((keyword, index) => (
                  <KeywordChip
                    key={`${getDisplayValue(keyword)}-${index}`}
                    label={getDisplayValue(keyword)}
                    positive
                  />
                ))}
              </div>
              {!matchedKeywords.length && (
                <EmptyPanel text="No matched keywords were detected." />
              )}
              {matchedKeywords.length > 12 && (
                <p className="mt-4 text-[10px] text-slate-600">
                  +{matchedKeywords.length - 12} additional matched keywords
                </p>
              )}
            </div>

            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
              <PanelLabel
                title="Keyword gaps"
                value={`${missingKeywords.length}`}
                suffix="identified"
              />
              <div className="mt-5 flex flex-wrap gap-2">
                {missingKeywords.slice(0, 12).map((keyword, index) => (
                  <KeywordChip
                    key={`${getDisplayValue(keyword)}-${index}`}
                    label={getDisplayValue(keyword)}
                  />
                ))}
              </div>
              {!missingKeywords.length && (
                <EmptyPanel text="No keyword gaps were identified." />
              )}
              {missingKeywords.length > 12 && (
                <p className="mt-4 text-[10px] text-slate-600">
                  +{missingKeywords.length - 12} additional gaps identified
                </p>
              )}
            </div>

            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
              <PanelLabel
                title="Content signals"
                value={`${atsMetrics.length}`}
                suffix="metrics"
              />
              <div className="mt-5 space-y-3">
                <SignalRow
                  label="Action verbs"
                  value={actionVerbs.length}
                  status={actionVerbs.length > 3 ? "good" : "weak"}
                />
                <SignalRow
                  label="Quantified results"
                  value={atsMetrics.length}
                  status={atsMetrics.length > 0 ? "good" : "weak"}
                />
                <SignalRow
                  label="Word count"
                  value={toNumber(ats.word_count)}
                  status={
                    toNumber(ats.word_count) >= 250 &&
                    toNumber(ats.word_count) <= 800
                      ? "good"
                      : "neutral"
                  }
                />
                <SignalRow
                  label="Technical context"
                  value={toNumber(ats.analysis?.technical_context)}
                  suffix="/20"
                  status="good"
                />
              </div>
            </div>
          </div>

          <div className="mt-5 grid gap-5 lg:grid-cols-2">
            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.18em] text-slate-600">
                    Section coverage
                  </p>
                  <h3 className="mt-2 text-lg font-bold text-white">
                    Resume structure
                  </h3>
                </div>
                <span className="rounded-xl bg-blue-500/10 px-3 py-2 text-xs font-bold text-blue-400">
                  {hasValidScore(sectionAnalysis.score)
                    ? clampScore(sectionAnalysis.score).toFixed(0)
                    : "—"}
                </span>
              </div>

              <div className="mt-5 flex flex-wrap gap-2">
                {sectionsPresent.map((section, index) => (
                  <SmallTag
                    key={`${getDisplayValue(section)}-${index}`}
                    text={`✓ ${getDisplayValue(section)}`}
                  />
                ))}
              </div>

              {sectionsMissing.length > 0 && (
                <div className="mt-5">
                  <p className="text-[9px] font-semibold uppercase tracking-wider text-amber-400">
                    Missing sections
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {sectionsMissing.map((section, index) => (
                      <KeywordChip
                        key={`${getDisplayValue(section)}-${index}`}
                        label={getDisplayValue(section)}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.18em] text-slate-600">
                    ATS analysis
                  </p>
                  <h3 className="mt-2 text-lg font-bold text-white">
                    Scoring context
                  </h3>
                </div>
                <span className="rounded-xl bg-blue-500/10 px-3 py-2 text-xs font-bold text-blue-400">
                  {hasValidScore(ats.keyword_analysis?.score)
                    ? clampScore(ats.keyword_analysis.score).toFixed(0)
                    : "—"}
                </span>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <DataRow
                  label="Keyword strength"
                  value={ats.analysis?.keyword_strength}
                />
                <DataRow label="Readability" value={ats.analysis?.readability} />
                <DataRow
                  label="Technical context"
                  value={ats.analysis?.technical_context}
                />
                <DataRow label="Impact score" value={ats.analysis?.impact_score} />
              </div>
            </div>
          </div>
        </section>

        {/* Keyword priorities */}
        <section className="mt-7">
          <SectionHeader
            eyebrow="Keyword intelligence"
            title="Keyword priorities"
            description="Not every missing keyword deserves equal attention. ResumeIQ ranks keyword gaps by importance."
          />

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            <PriorityCard
              title="Critical"
              description="Core capabilities"
              data={priorities.critical}
              level="critical"
            />
            <PriorityCard
              title="High"
              description="Strongly relevant skills"
              data={priorities.high}
              level="high"
            />
            <PriorityCard
              title="Important"
              description="Useful role alignment"
              data={priorities.important}
              level="important"
            />
            <PriorityCard
              title="Supporting"
              description="Additional signals"
              data={priorities.supporting}
              level="supporting"
            />
            <PriorityCard
              title="Optional"
              description="Lower priority terms"
              data={priorities.optional}
              level="optional"
            />
          </div>
        </section>

        {/* Skills */}
        <section id="skills" className="mt-12 scroll-mt-28">
          <SectionHeader
            eyebrow="Skills intelligence"
            title="Your technical profile"
            description="Skills detected from your resume, grouped by technical domain."
          />

          <div className="grid gap-5 xl:grid-cols-[0.75fr_1.25fr]">
            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6 sm:p-7">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-wider text-slate-600">
                    Skill score
                  </p>
                  <p className="mt-2 text-4xl font-bold text-white">
                    {hasValidScore(metrics.skills)
                      ? metrics.skills.toFixed(0)
                      : "—"}
                  </p>
                </div>
                <ScoreRing score={metrics.skills} size="small" />
              </div>

              <div className="mt-7 space-y-3">
                <DataRow label="Total skills" value={toNumber(skills.total_skills)} />
                <DataRow
                  label="Skill categories"
                  value={toNumber(skills.category_count)}
                />
                <DataRow
                  label="Strong signals"
                  value={toNumber(skills.confidence_summary?.strong)}
                />
                <DataRow
                  label="Moderate signals"
                  value={toNumber(skills.confidence_summary?.moderate)}
                />
              </div>

              <div className="mt-6 rounded-2xl border border-blue-500/10 bg-blue-500/[0.035] p-4">
                <p className="text-[9px] font-bold uppercase tracking-wider text-blue-400">
                  Strongest domain
                </p>
                <p className="mt-2 text-sm font-semibold text-slate-200">
                  {getDisplayValue(skills.strongest_category) || "Not determined"}
                </p>
              </div>
            </div>

            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6 sm:p-7">
              {categoryEntries.length > 0 ? (
                <div className="grid gap-5 md:grid-cols-2">
                  {categoryEntries.map(([category, values]) => (
                    <SkillCategory
                      key={category}
                      category={category}
                      skills={toArray(values)}
                    />
                  ))}
                </div>
              ) : (
                <EmptyPanel text="No skill categories were detected." />
              )}
            </div>
          </div>

          {toArray(skills.missing_industry_skills).length > 0 && (
            <div className="mt-5 rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.18em] text-amber-400">
                    Industry skill gaps
                  </p>
                  <h3 className="mt-2 text-lg font-bold text-white">
                    Skills worth considering
                  </h3>
                  <p className="mt-1 max-w-2xl text-xs leading-5 text-slate-600">
                    These are industry-relevant
                    capabilities not detected in
                    your current resume. Only add
                    skills you genuinely know or have
                    experience with.
                  </p>
                </div>
              </div>

              <div className="mt-5 flex flex-wrap gap-2">
                {toArray(skills.missing_industry_skills).map((skill, index) => (
                  <KeywordChip
                    key={`${getDisplayValue(skill)}-${index}`}
                    label={getDisplayValue(skill)}
                  />
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Technology coverage */}
        {toArray(technologyCoverage.technologies).length > 0 && (
          <section className="mt-7">
            <SectionHeader
              eyebrow="Technology coverage"
              title="Technical footprint"
              description="Technologies identified across your resume."
            />

            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
              <div className="flex flex-wrap gap-2">
                {toArray(technologyCoverage.technologies).map(
                  (technology, index) => (
                    <span
                      key={`${getDisplayValue(technology)}-${index}`}
                      className="rounded-xl border border-white/[0.07] bg-white/[0.025] px-3 py-2 text-[10px] font-medium capitalize text-slate-400 transition hover:border-blue-500/20 hover:bg-blue-500/[0.04] hover:text-blue-300"
                    >
                      {getDisplayValue(technology)}
                    </span>
                  )
                )}
              </div>

              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                {Object.entries(asObject(technologyCoverage.categories)).map(
                  ([category, count]) => (
                    <div
                      key={category}
                      className="rounded-xl border border-white/[0.06] bg-white/[0.018] p-4"
                    >
                      <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
                        {category}
                      </p>
                      <p className="mt-2 text-xl font-bold text-slate-200">
                        {toNumber(count)}
                      </p>
                    </div>
                  )
                )}
              </div>
            </div>
          </section>
        )}

        {/* Projects */}
        <section id="projects" className="mt-12 scroll-mt-28">
          <SectionHeader
            eyebrow="Project intelligence"
            title="How your projects perform"
            description="ResumeIQ evaluates technical complexity, impact, metrics, deployment and engineering evidence."
          />

          <div className="mb-5 grid gap-4 sm:grid-cols-3">
            <MetricHighlight label="Project score" value={metrics.projects} />
            <MetricHighlight
              label="Projects analyzed"
              value={toNumber(projects.project_count) || projectEntries.length}
              suffix=""
            />
            <MetricHighlight
              label="Technologies used"
              value={toArray(projects.technologies).length}
              suffix=""
            />
          </div>

          <div className="space-y-4">
            {projectEntries.map((project, index) => (
              <ProjectCard
                key={`${index}-${getDisplayValue(project?.title) || "project"}`}
                project={project}
                index={index}
              />
            ))}
            {!projectEntries.length && (
              <EmptyPanel text="No projects were detected in this analysis." />
            )}
          </div>
        </section>

        {/* Experience */}
        <section id="experience" className="mt-12 scroll-mt-28">
          <SectionHeader
            eyebrow="Experience intelligence"
            title="Professional experience"
            description="Internships, work experience and professional evidence detected from your resume."
          />

          {toNumber(experience.count) > 0 || experienceItems.length > 0 ? (
            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
              <div className="grid gap-4 sm:grid-cols-3">
                <MetricHighlight label="Experience score" value={metrics.experience} />
                <MetricHighlight
                  label="Experience items"
                  value={toNumber(experience.count) || experienceItems.length}
                  suffix=""
                />
                <MetricHighlight
                  label="Type"
                  value={getDisplayValue(experience.experience_type) || "Professional"}
                  text
                />
              </div>

              <div className="mt-6 space-y-3">
                {experienceItems.length > 0 ? (
                  experienceItems.map((item, index) => (
                    <ExperienceItem key={index} item={item} />
                  ))
                ) : (
                  <EmptyPanel text="Experience was detected, but no detailed experience items were returned." />
                )}
              </div>
            </div>
          ) : (
            <div className="rounded-[26px] border border-amber-500/10 bg-[#090f1c] p-7">
              <div className="flex flex-col gap-5 sm:flex-row sm:items-start">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-amber-500/10 text-amber-400">
                  !
                </div>
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.18em] text-amber-400">
                    Opportunity
                  </p>
                  <h3 className="mt-2 text-lg font-bold text-white">
                    No professional experience detected
                  </h3>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500 break-words">
                    {getDisplayValue(experience.message) ||
                      "Your resume does not currently contain detectable internship or work experience."}
                  </p>
                  <div className="mt-5 flex flex-wrap gap-2">
                    <SmallTag text="Internships" />
                    <SmallTag text="Freelance work" />
                    <SmallTag text="Open source" />
                    <SmallTag text="Relevant experience" />
                  </div>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Education + Certifications */}
        <section id="education" className="mt-12 scroll-mt-28">
          <SectionHeader
            eyebrow="Credentials"
            title="Education & certifications"
            description="Academic background and credential signals detected in your resume."
          />

          <div className="grid gap-5 lg:grid-cols-2">
            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.18em] text-violet-400">
                    Education
                  </p>
                  <h3 className="mt-2 text-lg font-bold text-white">
                    Academic profile
                  </h3>
                </div>
                <span className="rounded-xl bg-emerald-500/10 px-3 py-2 text-xs font-bold text-emerald-400">
                  {hasValidScore(metrics.education)
                    ? metrics.education.toFixed(0)
                    : "—"}
                </span>
              </div>

              <div className="mt-6 space-y-3">
                {educationEntries.length > 0 ? (
                  educationEntries.map((entry, index) => (
                    <EducationEntry
                      key={`${getDisplayValue(entry?.institution || entry?.school) || "education"}-${index}`}
                      entry={entry}
                    />
                  ))
                ) : (
                  <EmptyPanel text="No education entries were detected." />
                )}
              </div>
            </div>

            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.18em] text-emerald-400">
                    Certifications
                  </p>
                  <h3 className="mt-2 text-lg font-bold text-white">
                    Professional credentials
                  </h3>
                </div>
                <span className="rounded-xl bg-emerald-500/10 px-3 py-2 text-xs font-bold text-emerald-400">
                  {toNumber(certifications.count) ||
                    certificationDetails.length ||
                    certificationNames.length}
                </span>
              </div>

              <div className="mt-6 space-y-2">
                {certificationDetails.length > 0 ? (
                  certificationDetails.map((certification, index) => (
                    <CertificationItem
                      key={`${getDisplayValue(certification?.name) || "certification"}-${index}`}
                      certification={certification}
                    />
                  ))
                ) : certificationNames.length > 0 ? (
                  certificationNames.map((certification, index) => (
                    <CertificationItem
                      key={`${getDisplayValue(certification)}-${index}`}
                      certification={{ name: getDisplayValue(certification) }}
                    />
                  ))
                ) : (
                  <EmptyPanel text="No certifications were detected." />
                )}
              </div>

              {toArray(certifications.trusted_providers).length > 0 && (
                <div className="mt-5">
                  <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
                    Recognized providers
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {toArray(certifications.trusted_providers).map(
                      (provider, index) => (
                        <SmallTag
                          key={`${getDisplayValue(provider)}-${index}`}
                          text={getDisplayValue(provider)}
                        />
                      )
                    )}
                  </div>
                </div>
              )}

              <div className="mt-5 rounded-xl border border-blue-500/10 bg-blue-500/[0.025] p-3.5">
                <p className="text-[9px] font-semibold uppercase tracking-wider text-blue-400">
                  Verification status
                </p>
                <p className="mt-1 text-[10px] leading-5 text-slate-500">
                  Certifications are detected from
                  the resume. ResumeIQ does not treat
                  them as externally verified unless
                  explicit verification evidence is
                  available.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Deployment */}
        <section id="deployment" className="mt-12 scroll-mt-28">
          <SectionHeader
            eyebrow="Deployment intelligence"
            title="Deployment evidence"
            description="ResumeIQ distinguishes application-serving technologies from evidence of actual production deployment."
          />

          <div className="grid gap-5 lg:grid-cols-2">
            <DeploymentCard
              title="Application serving"
              description="Frameworks or technologies used to serve an application or expose functionality."
              items={applicationServing}
              tone="blue"
              emptyText="No application-serving technology was detected."
            />
            <DeploymentCard
              title="Production deployment"
              description="Evidence that a project or application was actually deployed to a production environment."
              items={productionDeployment}
              tone="emerald"
              emptyText="No production deployment evidence was detected."
            />
          </div>

          <div className="mt-5 rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
            <div className="grid gap-4 sm:grid-cols-3">
              <MetricHighlight
                label="Application serving signals"
                value={applicationServing.length}
                suffix=""
              />
              <MetricHighlight
                label="Production deployment signals"
                value={productionDeployment.length}
                suffix=""
              />
              <MetricHighlight
                label="Production deployment detected"
                value={hasProductionDeployment ? "Yes" : "No"}
                text
              />
            </div>

            {applicationServing.length > 0 && productionDeployment.length === 0 && (
              <div className="mt-5 rounded-xl border border-blue-500/10 bg-blue-500/[0.025] p-4">
                <p className="text-[9px] font-bold uppercase tracking-wider text-blue-400">
                  Interpretation
                </p>
                <p className="mt-2 text-xs leading-5 text-slate-500">
                  Your resume shows application-serving
                  technology, but ResumeIQ did not find
                  evidence of a production deployment.
                  For example, Flask indicates that an
                  application can serve functionality;
                  it does not by itself prove production
                  hosting.
                </p>
              </div>
            )}
          </div>
        </section>

        {/* Achievements */}
        <section id="achievements" className="mt-12 scroll-mt-28">
          <SectionHeader
            eyebrow="Achievement signals"
            title="Evidence of measurable impact"
            description="Quantified outcomes and achievement signals make resume claims more credible."
          />

          <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6">
            {toNumber(achievements.count) > 0 ||
            achievementSignals.length > 0 ||
            achievementItems.length > 0 ? (
              <>
                <div className="grid gap-5 sm:grid-cols-3">
                  <MetricHighlight
                    label="Achievement score"
                    value={metrics.achievements}
                  />
                  <MetricHighlight
                    label="Signals"
                    value={achievementSignals.length}
                    suffix=""
                  />
                  <MetricHighlight
                    label="Detected metrics"
                    value={atsMetrics.length}
                    suffix=""
                  />
                </div>

                {achievementItems.length > 0 && (
                  <div className="mt-6 space-y-2">
                    {achievementItems.map((item, index) => (
                      <div
                        key={index}
                        className="rounded-xl border border-white/[0.06] bg-white/[0.018] p-4"
                      >
                        <p className="text-xs leading-5 text-slate-400">
                          {getDisplayValue(item)}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-500/10 text-amber-400">
                  !
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-200">
                    Achievement evidence is limited
                  </p>
                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    Consider strengthening project and
                    experience bullets with measurable
                    outcomes such as accuracy, performance,
                    scale, users, time saved or other
                    meaningful results.
                  </p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Recommendations */}
        <section id="recommendations" className="mt-12 scroll-mt-28">
          <SectionHeader
            eyebrow="Optimization plan"
            title="What you should improve next"
            description="ResumeIQ's recommendations prioritized around the biggest opportunities in your current resume."
          />

          <div className="grid gap-5 lg:grid-cols-[1fr_0.8fr]">
            <div className="rounded-[26px] border border-white/[0.07] bg-[#090f1c] p-6 sm:p-7">
              <div className="space-y-3">
                {recommendations.map((recommendation, index) => (
                  <RecommendationItem
                    key={`${getDisplayValue(recommendation)}-${index}`}
                    number={index + 1}
                    text={recommendation}
                  />
                ))}
                {!recommendations.length && (
                  <EmptyPanel text="No recommendations were generated." />
                )}
              </div>
            </div>

            <div className="rounded-[26px] border border-blue-500/10 bg-gradient-to-br from-blue-500/[0.07] to-transparent p-6 sm:p-7">
              <p className="text-[9px] font-bold uppercase tracking-[0.18em] text-blue-400">
                Recommended focus
              </p>
              <h3 className="mt-3 text-xl font-bold tracking-tight text-white">
                Improve the highest-impact areas first.
              </h3>
              <p className="mt-3 text-sm leading-6 text-slate-500">
                Resume improvement is most effective
                when you focus on evidence and relevance
                instead of adding keywords indiscriminately.
              </p>

              <div className="mt-6 space-y-3">
                <FocusItem
                  number="01"
                  title="Strengthen impact"
                  description="Add measurable outcomes to project and experience bullets."
                />
                <FocusItem
                  number="02"
                  title="Improve ATS alignment"
                  description="Address relevant keyword gaps that genuinely match your capabilities."
                />
                <FocusItem
                  number="03"
                  title="Build experience signals"
                  description="Show internships, freelance work, open source or relevant professional work when applicable."
                />
              </div>
            </div>
          </div>
        </section>

        {/* Bottom CTA */}
        <section className="mt-12 pb-10">
          <div className="relative overflow-hidden rounded-[30px] border border-blue-500/10 bg-gradient-to-r from-[#0b1427] to-[#09101e] p-7 sm:p-9">
            <div className="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full bg-blue-500/[0.08] blur-[80px]" />

            <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-blue-400">
                  Next step
                </p>
                <h3 className="mt-2 text-2xl font-bold tracking-tight text-white">
                  Ready to optimize your resume?
                </h3>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  Use your analysis to identify the biggest
                  gaps before moving into job-specific matching
                  and targeted optimization.
                </p>
              </div>

              <button
                type="button"
                onClick={() => navigate("/dashboard")}
                className="inline-flex shrink-0 items-center justify-center gap-3 rounded-xl bg-blue-600 px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-blue-600/20 transition hover:-translate-y-0.5 hover:bg-blue-500"
              >
                Analyze another resume
                <span aria-hidden="true">→</span>
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default ResumeAnalysis;