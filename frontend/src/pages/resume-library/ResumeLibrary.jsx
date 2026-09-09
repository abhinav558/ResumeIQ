import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  deleteSavedResume,
  getSavedResume,
  getSavedResumes,
  updateSavedResume,
} from "../../services/api";

import { useResumeContext } from "../../context/ResumeContext";

function Icon({ name, size = 20 }) {
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

    file: (
      <svg {...common}>
        <path d="M6 3.5h8l4 4V20a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z" />
        <path d="M14 3.5V8h4" />
        <path d="M8 12h8" />
        <path d="M8 16h5" />
      </svg>
    ),

    open: (
      <svg {...common}>
        <path d="M14 5h5v5" />
        <path d="m19 5-8 8" />
        <path d="M19 13v5a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5" />
      </svg>
    ),

    edit: (
      <svg {...common}>
        <path d="M12 20h9" />
        <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z" />
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

    search: (
      <svg {...common}>
        <circle cx="11" cy="11" r="6.5" />
        <path d="m16 16 4.5 4.5" />
      </svg>
    ),

    plus: (
      <svg {...common}>
        <path d="M12 5v14" />
        <path d="M5 12h14" />
      </svg>
    ),

    refresh: (
      <svg {...common}>
        <path d="M20 11a8 8 0 1 0 2 5" />
        <path d="M20 5v6h-6" />
      </svg>
    ),

    close: (
      <svg {...common}>
        <path d="m6 6 12 12" />
        <path d="m18 6-12 12" />
      </svg>
    ),

    check: (
      <svg {...common}>
        <path d="m5 12 4 4L19 6" />
      </svg>
    ),
  };

  return icons[name] || null;
}

function ResumeLibrary() {
  const navigate = useNavigate();

  const {
    setAnalysis,
    setResumeText,
    setFile,
  } = useResumeContext();

  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchQuery, setSearchQuery] = useState("");

  const [openingId, setOpeningId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [renamingId, setRenamingId] = useState(null);

  const [renameValue, setRenameValue] = useState("");
  const [actionError, setActionError] = useState("");

  useEffect(() => {
    loadResumes();
  }, []);

  async function loadResumes() {
    setLoading(true);
    setError("");
    setActionError("");

    try {
      const data = await getSavedResumes();

      setResumes(
        Array.isArray(data)
          ? data
          : []
      );
    } catch (err) {
      console.error(
        "Failed to load resume library:",
        err
      );

      const detail =
        err?.response?.data?.detail;

      setError(
        typeof detail === "string" && detail.trim()
          ? detail
          : "Unable to load your resume library. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleOpenResume(resumeId) {
    setOpeningId(resumeId);
    setActionError("");

    try {
      const savedResume = await getSavedResume(
        resumeId
      );

      if (!savedResume) {
        throw new Error(
          "Saved resume could not be loaded."
        );
      }

      let analysis;

      try {
        analysis =
          typeof savedResume.analysis_json ===
          "string"
            ? JSON.parse(
                savedResume.analysis_json
              )
            : savedResume.analysis_json;
      } catch {
        throw new Error(
          "The saved analysis could not be restored because its data is invalid."
        );
      }

      if (!analysis) {
        throw new Error(
          "The saved resume does not contain a valid analysis."
        );
      }

      setAnalysis(analysis);

      if (
        typeof savedResume.resume_text ===
          "string" &&
        savedResume.resume_text.trim()
      ) {
        setResumeText(
          savedResume.resume_text
        );
      } else {
        setResumeText("");
      }

      /*
       * A File object cannot be reconstructed from
       * the persisted library record. ResumeContext
       * intentionally does not persist File objects.
       */
      setFile(null);

      navigate("/resume-analysis");
    } catch (err) {
      console.error(
        "Failed to open saved resume:",
        err
      );

      setActionError(
        err?.message ||
          "Unable to open this saved resume. Please try again."
      );
    } finally {
      setOpeningId(null);
    }
  }

  async function handleDeleteResume(resume) {
    const confirmed = window.confirm(
      `Delete "${resume.name}" from your resume library? This action cannot be undone.`
    );

    if (!confirmed) {
      return;
    }

    setDeletingId(resume.id);
    setActionError("");

    try {
      await deleteSavedResume(
        resume.id
      );

      setResumes((current) =>
        current.filter(
          (item) =>
            item.id !== resume.id
        )
      );
    } catch (err) {
      console.error(
        "Failed to delete saved resume:",
        err
      );

      const detail =
        err?.response?.data?.detail;

      setActionError(
        typeof detail === "string" &&
          detail.trim()
          ? detail
          : "Unable to delete this resume. Please try again."
      );
    } finally {
      setDeletingId(null);
    }
  }

  function startRename(resume) {
    setRenamingId(resume.id);
    setRenameValue(resume.name);
    setActionError("");
  }

  function cancelRename() {
    setRenamingId(null);
    setRenameValue("");
  }

  async function handleRename(resume) {
    const nextName =
      renameValue.trim();

    if (!nextName) {
      setActionError(
        "Resume name cannot be empty."
      );
      return;
    }

    if (nextName === resume.name) {
      cancelRename();
      return;
    }

    setRenamingId(resume.id);
    setActionError("");

    try {
      const updatedResume =
        await updateSavedResume(
          resume.id,
          {
            name: nextName,
          }
        );

      setResumes((current) =>
        current.map((item) =>
          item.id === resume.id
            ? {
                ...item,
                name:
                  updatedResume?.name ||
                  nextName,
                updated_at:
                  updatedResume?.updated_at ||
                  item.updated_at,
              }
            : item
        )
      );

      cancelRename();
    } catch (err) {
      console.error(
        "Failed to rename saved resume:",
        err
      );

      const detail =
        err?.response?.data?.detail;

      setActionError(
        typeof detail === "string" &&
          detail.trim()
          ? detail
          : "Unable to rename this resume. Please try again."
      );
    }
  }

  function handleRenameKeyDown(
    event,
    resume
  ) {
    if (event.key === "Enter") {
      event.preventDefault();
      handleRename(resume);
    }

    if (event.key === "Escape") {
      event.preventDefault();
      cancelRename();
    }
  }

  function formatDate(value) {
    if (!value) {
      return "Unknown date";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return "Unknown date";
    }

    return new Intl.DateTimeFormat(
      undefined,
      {
        day: "numeric",
        month: "short",
        year: "numeric",
      }
    ).format(date);
  }

  const filteredResumes =
    resumes.filter((resume) =>
      resume.name
        ?.toLowerCase()
        .includes(
          searchQuery
            .trim()
            .toLowerCase()
        )
    );

  return (
    <section className="px-5 py-8 sm:px-7 lg:px-9 lg:py-10">
      <div className="mx-auto max-w-[1400px]">
        {/* Header */}
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl border border-blue-400/10 bg-blue-500/[0.08] text-blue-400">
              <Icon
                name="library"
                size={21}
              />
            </div>

            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-blue-400">
              Your workspace
            </p>

            <h2 className="mt-2 text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Resume Library
            </h2>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
              Access your saved resumes and
              continue working from your
              previous analyses.
            </p>
          </div>

          <button
            type="button"
            onClick={() =>
              navigate("/dashboard")
            }
            className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-xl border border-blue-400/10 bg-blue-500/[0.08] px-4 text-xs font-semibold text-blue-300 transition hover:border-blue-400/20 hover:bg-blue-500/[0.13] hover:text-blue-200"
          >
            <Icon
              name="plus"
              size={16}
            />

            Analyze New Resume
          </button>
        </div>

        {/* Search / count */}
        {!loading && resumes.length > 0 && (
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="relative w-full sm:max-w-[360px]">
              <span className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-600">
                <Icon
                  name="search"
                  size={16}
                />
              </span>

              <input
                type="text"
                value={searchQuery}
                onChange={(event) =>
                  setSearchQuery(
                    event.target.value
                  )
                }
                placeholder="Search resumes..."
                className="h-10 w-full rounded-xl border border-white/[0.07] bg-white/[0.025] pl-10 pr-4 text-xs text-white outline-none transition placeholder:text-slate-600 focus:border-blue-400/25 focus:bg-white/[0.035]"
              />
            </div>

            <p className="text-xs text-slate-600">
              {filteredResumes.length}{" "}
              {filteredResumes.length === 1
                ? "resume"
                : "resumes"}
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-8 rounded-2xl border border-red-400/10 bg-red-500/[0.05] p-5">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-red-300">
                  Unable to load your library
                </p>

                <p className="mt-1 text-xs leading-5 text-red-300/60">
                  {error}
                </p>
              </div>

              <button
                type="button"
                onClick={loadResumes}
                className="inline-flex h-9 shrink-0 items-center justify-center gap-2 rounded-lg border border-red-400/10 bg-red-400/[0.06] px-3 text-xs font-semibold text-red-300 hover:bg-red-400/[0.1]"
              >
                <Icon
                  name="refresh"
                  size={14}
                />

                Try Again
              </button>
            </div>
          </div>
        )}

        {/* Action error */}
        {actionError && (
          <div className="mt-5 flex items-start justify-between gap-4 rounded-xl border border-red-400/10 bg-red-500/[0.04] px-4 py-3">
            <p className="text-xs leading-5 text-red-300/80">
              {actionError}
            </p>

            <button
              type="button"
              onClick={() =>
                setActionError("")
              }
              aria-label="Dismiss error"
              className="shrink-0 text-red-300/50 transition hover:text-red-300"
            >
              <Icon
                name="close"
                size={15}
              />
            </button>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {Array.from({
              length: 6,
            }).map((_, index) => (
              <div
                key={index}
                className="animate-pulse rounded-2xl border border-white/[0.06] bg-white/[0.02] p-5"
              >
                <div className="flex items-start gap-4">
                  <div className="h-11 w-11 rounded-xl bg-white/[0.05]" />

                  <div className="flex-1">
                    <div className="h-3.5 w-3/4 rounded bg-white/[0.05]" />

                    <div className="mt-3 h-2.5 w-1/2 rounded bg-white/[0.04]" />
                  </div>
                </div>

                <div className="mt-6 h-9 rounded-lg bg-white/[0.04]" />
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading &&
          !error &&
          resumes.length === 0 && (
            <div className="mt-10 rounded-3xl border border-dashed border-white/[0.08] bg-white/[0.015] px-6 py-16 text-center sm:px-10">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-white/[0.07] bg-white/[0.025] text-slate-600">
                <Icon
                  name="library"
                  size={28}
                />
              </div>

              <h3 className="mt-6 text-base font-semibold text-white">
                Your resume library is empty
              </h3>

              <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-600">
                Analyze a resume and it will
                automatically be saved here so
                you can return to it later.
              </p>

              <button
                type="button"
                onClick={() =>
                  navigate("/dashboard")
                }
                className="mt-7 inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-blue-500 px-4 text-xs font-semibold text-white shadow-lg shadow-blue-950/30 transition hover:bg-blue-400"
              >
                <Icon
                  name="plus"
                  size={16}
                />

                Analyze Your First Resume
              </button>
            </div>
          )}

        {/* No search results */}
        {!loading &&
          !error &&
          resumes.length > 0 &&
          filteredResumes.length === 0 && (
            <div className="mt-10 rounded-2xl border border-white/[0.06] bg-white/[0.015] px-6 py-14 text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-white/[0.025] text-slate-600">
                <Icon
                  name="search"
                  size={21}
                />
              </div>

              <h3 className="mt-5 text-sm font-semibold text-white">
                No resumes found
              </h3>

              <p className="mt-1.5 text-xs text-slate-600">
                Try a different search term.
              </p>
            </div>
          )}

        {/* Resume cards */}
        {!loading &&
          !error &&
          filteredResumes.length > 0 && (
            <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {filteredResumes.map(
                (resume) => {
                  const isOpening =
                    openingId ===
                    resume.id;

                  const isDeleting =
                    deletingId ===
                    resume.id;

                  const isRenaming =
                    renamingId ===
                    resume.id;

                  return (
                    <article
                      key={resume.id}
                      className="group rounded-2xl border border-white/[0.06] bg-white/[0.02] p-5 transition hover:border-white/[0.1] hover:bg-white/[0.025]"
                    >
                      <div className="flex items-start gap-4">
                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-blue-400/10 bg-blue-500/[0.07] text-blue-400">
                          <Icon
                            name="file"
                            size={20}
                          />
                        </div>

                        <div className="min-w-0 flex-1">
                          {isRenaming ? (
                            <div className="flex gap-2">
                              <input
                                autoFocus
                                type="text"
                                value={
                                  renameValue
                                }
                                onChange={(
                                  event
                                ) =>
                                  setRenameValue(
                                    event
                                      .target
                                      .value
                                  )
                                }
                                onKeyDown={(
                                  event
                                ) =>
                                  handleRenameKeyDown(
                                    event,
                                    resume
                                  )
                                }
                                maxLength={
                                  255
                                }
                                className="min-w-0 flex-1 rounded-lg border border-blue-400/20 bg-white/[0.04] px-2.5 py-2 text-xs text-white outline-none focus:border-blue-400/40"
                              />

                              <button
                                type="button"
                                onClick={() =>
                                  handleRename(
                                    resume
                                  )
                                }
                                aria-label="Save name"
                                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-500/[0.08] text-emerald-400 hover:bg-emerald-500/[0.13]"
                              >
                                <Icon
                                  name="check"
                                  size={15}
                                />
                              </button>
                            </div>
                          ) : (
                            <h3 className="truncate text-sm font-semibold text-white">
                              {resume.name ||
                                "Untitled Resume"}
                            </h3>
                          )}

                          <p className="mt-1.5 text-[11px] text-slate-600">
                            Updated{" "}
                            {formatDate(
                              resume.updated_at
                            )}
                          </p>
                        </div>
                      </div>

                      <div className="mt-5 flex items-center justify-between border-t border-white/[0.05] pt-4">
                        <button
                          type="button"
                          disabled={
                            isOpening ||
                            isDeleting ||
                            isRenaming
                          }
                          onClick={() =>
                            handleOpenResume(
                              resume.id
                            )
                          }
                          className="inline-flex h-9 items-center justify-center gap-2 rounded-lg bg-blue-500/[0.08] px-3 text-xs font-semibold text-blue-300 transition hover:bg-blue-500/[0.13] hover:text-blue-200 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          <Icon
                            name="open"
                            size={14}
                          />

                          {isOpening
                            ? "Opening..."
                            : "Open Analysis"}
                        </button>

                        <div className="flex items-center gap-1">
                          <button
                            type="button"
                            disabled={
                              isOpening ||
                              isDeleting
                            }
                            onClick={() =>
                              startRename(
                                resume
                              )
                            }
                            aria-label={`Rename ${resume.name}`}
                            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-600 transition hover:bg-white/[0.04] hover:text-slate-300 disabled:cursor-not-allowed disabled:opacity-40"
                          >
                            <Icon
                              name="edit"
                              size={15}
                            />
                          </button>

                          <button
                            type="button"
                            disabled={
                              isOpening ||
                              isDeleting ||
                              isRenaming
                            }
                            onClick={() =>
                              handleDeleteResume(
                                resume
                              )
                            }
                            aria-label={`Delete ${resume.name}`}
                            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-600 transition hover:bg-red-500/[0.06] hover:text-red-400 disabled:cursor-not-allowed disabled:opacity-40"
                          >
                            <Icon
                              name="trash"
                              size={15}
                            />
                          </button>
                        </div>
                      </div>
                    </article>
                  );
                }
              )}
            </div>
          )}
      </div>
    </section>
  );
}

export default ResumeLibrary;