import { useRef, useState } from "react";
import {
  CheckCircle2,
  FileText,
  Loader2,
  RefreshCw,
  ShieldCheck,
  UploadCloud,
  X,
} from "lucide-react";

import useResume from "../../hooks/useResume";
import { useResumeContext } from "../../context/ResumeContext";
import { saveResume } from "../../services/api";

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const ALLOWED_EXTENSIONS = [".pdf", ".doc", ".docx"];

const FILE_TYPES = {
  ".pdf": "PDF",
  ".doc": "DOC",
  ".docx": "DOCX",
};

function ResumeUploader({ onAnalysisComplete }) {
  const inputRef = useRef(null);

  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [validationError, setValidationError] = useState("");
  const [saveError, setSaveError] = useState("");
  const [saving, setSaving] = useState(false);

  const { analyze, loading, error } = useResume();

  const {
    setFile: setContextFile,
  } = useResumeContext();

  const currentError =
    validationError ||
    error ||
    saveError;

  const isBusy = loading || saving;

  const openFilePicker = () => {
    if (isBusy) return;

    inputRef.current?.click();
  };

  const validateFile = (selectedFile) => {
    if (!selectedFile) {
      return "Please select a resume file.";
    }

    if (selectedFile.size === 0) {
      return "This file appears to be empty. Please choose another resume.";
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      return "Your resume must be smaller than 10 MB.";
    }

    const fileName = selectedFile.name.toLowerCase();

    const extension = ALLOWED_EXTENSIONS.find((item) =>
      fileName.endsWith(item)
    );

    if (!extension) {
      return "ResumeIQ supports PDF, DOC, and DOCX files.";
    }

    return "";
  };

  const selectFile = (selectedFile) => {
    if (!selectedFile || isBusy) return;

    setValidationError("");
    setSaveError("");

    const validationMessage =
      validateFile(selectedFile);

    if (validationMessage) {
      setFile(null);
      setContextFile(null);
      setValidationError(validationMessage);
      return;
    }

    setFile(selectedFile);
    setContextFile(selectedFile);
  };

  const handleFileChange = (event) => {
    const selectedFile =
      event.target.files?.[0];

    selectFile(selectedFile);

    // Allows selecting the same file again later.
    event.target.value = "";
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();

    if (!isBusy) {
      setDragging(true);
    }
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();

    setDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();

    if (isBusy) return;

    setDragging(false);

    const droppedFile =
      event.dataTransfer.files?.[0];

    selectFile(droppedFile);
  };

  const handleAnalyze = async () => {
    if (!file || isBusy) return;

    setValidationError("");
    setSaveError("");

    // Keep context synchronized with the current file.
    setContextFile(file);

    const result = await analyze(file);

    if (!result) {
      return;
    }

    /*
     * The analysis endpoint already returns the extracted
     * resume text. Save the successful analysis as a persistent
     * Resume Library entry for the authenticated user.
     */
    if (
      typeof result.resume_text !== "string" ||
      !result.resume_text.trim()
    ) {
      setSaveError(
        "Analysis completed, but the extracted resume text was unavailable. The analysis result is still available."
      );

      onAnalysisComplete?.(result);

      return;
    }

    setSaving(true);

    try {
      await saveResume({
        name: getResumeDisplayName(file.name),
        resumeText: result.resume_text,
        analysis: result,
      });
    } catch (err) {
      console.error(
        "Resume library save failed:",
        err
      );

      const detail =
        err?.response?.data?.detail;

      if (
        typeof detail === "string" &&
        detail.trim()
      ) {
        setSaveError(
          `Analysis completed, but the resume could not be saved: ${detail}`
        );
      } else if (
        typeof err?.message === "string" &&
        err.message.trim()
      ) {
        setSaveError(
          `Analysis completed, but the resume could not be saved: ${err.message}`
        );
      } else {
        setSaveError(
          "Analysis completed, but the resume could not be saved to your Resume Library."
        );
      }
    } finally {
      setSaving(false);
    }

    /*
     * Always continue to the existing analysis flow after
     * analysis succeeds, even if library persistence fails.
     */
    onAnalysisComplete?.(result);
  };

  const removeFile = () => {
    if (isBusy) return;

    setFile(null);
    setContextFile(null);
    setValidationError("");
    setSaveError("");
  };

  const changeFile = () => {
    if (isBusy) return;

    setValidationError("");
    setSaveError("");
    openFilePicker();
  };

  return (
    <section
      aria-label="Resume analysis workspace"
      aria-busy={isBusy}
      className="relative overflow-hidden rounded-[30px] border border-white/[0.08] bg-[#090f1c] shadow-2xl shadow-black/30"
    >
      {/* Ambient lighting */}
      <div className="pointer-events-none absolute -right-40 -top-40 h-[420px] w-[420px] rounded-full bg-blue-600/[0.08] blur-[120px]" />

      <div className="pointer-events-none absolute -bottom-48 -left-40 h-[420px] w-[420px] rounded-full bg-indigo-600/[0.06] blur-[120px]" />

      <div className="relative p-6 sm:p-8 lg:p-10">
        {/* ============================================================
            HEADER
        ============================================================ */}

        <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/[0.08] text-blue-400">
                <FileText
                  size={15}
                  aria-hidden="true"
                />
              </div>

              <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-blue-400">
                Resume workspace
              </span>
            </div>

            <h2 className="mt-4 text-2xl font-semibold tracking-[-0.03em] text-white sm:text-3xl">
              Analyze your resume
            </h2>

            <p className="mt-2 max-w-xl text-sm leading-6 text-slate-500">
              Upload your resume to get a comprehensive
              analysis of ATS compatibility, skills,
              projects, experience, education, and
              improvement opportunities.
            </p>
          </div>

          {/* Supported formats */}
          <div
            className="flex shrink-0 items-center gap-2"
            aria-label="Supported file formats"
          >
            {["PDF", "DOC", "DOCX"].map(
              (format) => (
                <span
                  key={format}
                  className="rounded-lg border border-white/[0.07] bg-white/[0.025] px-2.5 py-1.5 text-[9px] font-semibold tracking-wide text-slate-500"
                >
                  {format}
                </span>
              )
            )}
          </div>
        </div>

        {/* ============================================================
            UPLOAD STATE
        ============================================================ */}

        {!file && (
          <button
            type="button"
            onClick={openFilePicker}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            disabled={isBusy}
            aria-label="Upload resume. Click to choose a file or drag and drop one here."
            className={[
              "group mt-8 w-full rounded-[24px] border border-dashed p-8 text-center",
              "transition-all duration-300",
              "focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-[#090f1c]",
              "disabled:cursor-not-allowed disabled:opacity-60",
              dragging
                ? "scale-[1.01] border-blue-400/50 bg-blue-500/[0.07] shadow-[0_0_60px_rgba(59,130,246,0.08)]"
                : "border-white/[0.10] bg-white/[0.015] hover:border-blue-500/30 hover:bg-blue-500/[0.025]",
              "sm:p-12",
              "motion-reduce:transition-none motion-reduce:hover:transform-none",
            ].join(" ")}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={handleFileChange}
              disabled={isBusy}
              aria-label="Choose resume file"
              className="hidden"
            />

            {/* Upload icon */}
            <div
              className={[
                "mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border",
                "transition-all duration-300",
                "motion-reduce:transition-none",
                dragging
                  ? "border-blue-400/30 bg-blue-500/10 text-blue-400"
                  : "border-white/[0.08] bg-white/[0.03] text-slate-500 group-hover:border-blue-500/20 group-hover:bg-blue-500/10 group-hover:text-blue-400",
              ].join(" ")}
            >
              <UploadCloud
                size={27}
                strokeWidth={1.6}
                aria-hidden="true"
              />
            </div>

            <h3 className="mt-6 text-lg font-semibold text-slate-200">
              {dragging
                ? "Drop your resume here"
                : "Upload your resume"}
            </h3>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-600">
              {dragging
                ? "Release the file to add it to your analysis."
                : "Drag and drop your resume here, or choose a file from your computer."}
            </p>

            {/* Primary action */}
            <span className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-xs font-semibold text-slate-950 shadow-lg transition-all group-hover:-translate-y-0.5 group-hover:bg-slate-100 motion-reduce:transition-none motion-reduce:transform-none">
              <UploadCloud
                size={15}
                aria-hidden="true"
              />
              Choose resume
            </span>

            {/* File constraints */}
            <div className="mt-5 flex flex-wrap items-center justify-center gap-x-2 gap-y-1 text-[10px] text-slate-700">
              <span>PDF, DOC, DOCX</span>
              <span aria-hidden="true">•</span>
              <span>Maximum 10 MB</span>
              <span aria-hidden="true">•</span>
              <span>Processed for analysis</span>
            </div>
          </button>
        )}

        {/* ============================================================
            SELECTED FILE
        ============================================================ */}

        {file && (
          <div
            className={[
              "mt-8 overflow-hidden rounded-[24px] border",
              loading
                ? "border-blue-500/20 bg-gradient-to-br from-blue-500/[0.08] via-blue-500/[0.025] to-transparent"
                : "border-blue-500/15 bg-gradient-to-br from-blue-500/[0.07] via-blue-500/[0.02] to-transparent",
            ].join(" ")}
          >
            <div className="p-5 sm:p-6">
              <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
                {/* File icon */}
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-blue-500/10 bg-blue-500/10 text-blue-400">
                  <FileText
                    size={24}
                    strokeWidth={1.6}
                    aria-hidden="true"
                  />
                </div>

                {/* File information */}
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3
                      title={file.name}
                      className="max-w-full truncate text-sm font-semibold text-slate-200 sm:max-w-[420px]"
                    >
                      {file.name}
                    </h3>

                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-1 text-[8px] font-bold uppercase tracking-wider text-emerald-400">
                      <CheckCircle2
                        size={10}
                        aria-hidden="true"
                      />
                      Ready
                    </span>
                  </div>

                  <p className="mt-1 text-xs text-slate-600">
                    {getFileType(file.name)} ·{" "}
                    {formatFileSize(file.size)}
                  </p>
                </div>

                {/* File actions */}
                <div className="flex shrink-0 items-center gap-2">
                  <button
                    type="button"
                    onClick={changeFile}
                    disabled={isBusy}
                    className="inline-flex items-center gap-2 rounded-xl border border-white/[0.07] bg-white/[0.02] px-4 py-2.5 text-xs font-medium text-slate-400 transition hover:border-blue-500/20 hover:bg-blue-500/[0.04] hover:text-blue-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/60 disabled:cursor-not-allowed disabled:opacity-40 motion-reduce:transition-none"
                  >
                    <RefreshCw
                      size={13}
                      aria-hidden="true"
                    />
                    Change
                  </button>

                  <button
                    type="button"
                    onClick={removeFile}
                    disabled={isBusy}
                    aria-label={`Remove ${file.name}`}
                    title="Remove resume"
                    className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.07] bg-white/[0.02] text-slate-600 transition hover:border-red-500/20 hover:bg-red-500/[0.04] hover:text-red-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500/60 disabled:cursor-not-allowed disabled:opacity-40 motion-reduce:transition-none"
                  >
                    <X
                      size={15}
                      aria-hidden="true"
                    />
                  </button>
                </div>
              </div>

              {/* ========================================================
                  ANALYSIS LOADING STATE
              ======================================================== */}

              {loading && (
                <div
                  className="mt-6 rounded-2xl border border-blue-500/10 bg-blue-500/[0.04] p-5"
                  role="status"
                  aria-live="polite"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400">
                      <Loader2
                        size={16}
                        className="animate-spin motion-reduce:animate-none"
                        aria-hidden="true"
                      />
                    </div>

                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-slate-300">
                        ResumeIQ is analyzing your resume
                      </p>

                      <p className="mt-1 text-[10px] leading-5 text-slate-600">
                        Evaluating structure, ATS compatibility,
                        skills, projects, experience, and
                        content quality.
                      </p>
                    </div>
                  </div>

                  {/* Indeterminate progress */}
                  <div
                    className="mt-5 h-1 overflow-hidden rounded-full bg-white/[0.05]"
                    aria-hidden="true"
                  >
                    <div className="h-full w-1/2 animate-pulse rounded-full bg-gradient-to-r from-blue-500 to-indigo-400 motion-reduce:animate-none" />
                  </div>

                  <p className="mt-3 text-[9px] text-slate-700">
                    This may take a few moments.
                  </p>
                </div>
              )}

              {/* ========================================================
                  LIBRARY SAVE STATE
              ======================================================== */}

              {saving && (
                <div
                  className="mt-6 rounded-2xl border border-emerald-500/10 bg-emerald-500/[0.035] p-5"
                  role="status"
                  aria-live="polite"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400">
                      <Loader2
                        size={16}
                        className="animate-spin motion-reduce:animate-none"
                        aria-hidden="true"
                      />
                    </div>

                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-slate-300">
                        Saving your resume
                      </p>

                      <p className="mt-1 text-[10px] leading-5 text-slate-600">
                        Adding this analysis to your Resume
                        Library.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ============================================================
            ERROR STATE
        ============================================================ */}

        {currentError && (
          <div
            className="mt-4 rounded-2xl border border-red-500/15 bg-red-500/[0.04] p-4"
            role="alert"
            aria-live="assertive"
          >
            <div className="flex items-start gap-3">
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-red-500/10 text-red-400">
                <X
                  size={14}
                  aria-hidden="true"
                />
              </div>

              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-red-300">
                  {validationError
                    ? "File couldn't be added"
                    : saveError
                    ? "Resume Library save failed"
                    : "Analysis couldn't be completed"}
                </p>

                <p className="mt-1 text-xs leading-5 text-red-300/60">
                  {currentError}
                </p>

                {!validationError &&
                  !saveError &&
                  !loading &&
                  !saving &&
                  file && (
                    <button
                      type="button"
                      onClick={handleAnalyze}
                      className="mt-3 text-[10px] font-semibold text-red-300 transition hover:text-white focus:outline-none focus-visible:underline motion-reduce:transition-none"
                    >
                      Try analysis again →
                    </button>
                  )}
              </div>
            </div>
          </div>
        )}

        {/* ============================================================
            FOOTER / ANALYZE ACTION
        ============================================================ */}

        <div className="mt-6 flex flex-col gap-4 border-t border-white/[0.05] pt-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2 text-[10px] text-slate-600">
            <ShieldCheck
              size={13}
              className="text-emerald-400"
              aria-hidden="true"
            />

            <span>
              Your resume is securely saved to your Resume
              Library after analysis.
            </span>
          </div>

          <button
            type="button"
            onClick={handleAnalyze}
            disabled={!file || isBusy}
            aria-busy={isBusy}
            className={[
              "group inline-flex items-center justify-center gap-3 rounded-xl px-6 py-3.5 text-sm font-semibold",
              "transition-all duration-300",
              "focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400/80 focus-visible:ring-offset-2 focus-visible:ring-offset-[#090f1c]",
              "disabled:cursor-not-allowed",
              file && !isBusy
                ? "bg-blue-600 text-white shadow-xl shadow-blue-600/20 hover:-translate-y-0.5 hover:bg-blue-500 active:translate-y-0"
                : "bg-white/[0.05] text-slate-600",
              "motion-reduce:transition-none motion-reduce:hover:transform-none",
            ].join(" ")}
          >
            {loading ? (
              <>
                <Loader2
                  size={16}
                  className="animate-spin motion-reduce:animate-none"
                  aria-hidden="true"
                />
                Analyzing...
              </>
            ) : saving ? (
              <>
                <Loader2
                  size={16}
                  className="animate-spin motion-reduce:animate-none"
                  aria-hidden="true"
                />
                Saving...
              </>
            ) : (
              <>
                Analyze my resume

                <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-white/10 transition-transform group-hover:translate-x-0.5 motion-reduce:transition-none">
                  →
                </span>
              </>
            )}
          </button>
        </div>
      </div>
    </section>
  );
}

/* ================================================================
   HELPERS
================================================================ */

function getFileType(filename) {
  const extension =
    "." + filename.split(".").pop().toLowerCase();

  return FILE_TYPES[extension] || "Document";
}

function formatFileSize(bytes) {
  if (!bytes || bytes <= 0) {
    return "0 KB";
  }

  const megabytes = bytes / (1024 * 1024);

  if (megabytes >= 1) {
    return `${megabytes.toFixed(2)} MB`;
  }

  return `${Math.max(
    1,
    Math.round(bytes / 1024)
  )} KB`;
}

function getResumeDisplayName(filename) {
  const name = filename
    .replace(/\.[^/.]+$/, "")
    .trim();

  return name || "Untitled Resume";
}

export default ResumeUploader;

