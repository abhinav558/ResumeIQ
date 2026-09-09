import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

const ResumeContext = createContext(null);

const STORAGE_KEY = "resumeiq_analysis";
const RESUME_TEXT_KEY = "resumeiq_resume_text";

function loadStoredAnalysis() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);

    if (!stored) {
      return null;
    }

    const parsed = JSON.parse(stored);

    if (!parsed || typeof parsed !== "object") {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }

    return parsed;
  } catch (error) {
    console.error(
      "Failed to load stored resume analysis:",
      error
    );

    return null;
  }
}

function loadStoredResumeText() {
  try {
    return localStorage.getItem(RESUME_TEXT_KEY) || "";
  } catch (error) {
    console.error(
      "Failed to load stored resume text:",
      error
    );

    return "";
  }
}

export function ResumeProvider({ children }) {
  /*
  |--------------------------------------------------------------------------
  | Stored resume analysis
  |--------------------------------------------------------------------------
  */

  const [analysis, setAnalysisState] = useState(
    loadStoredAnalysis
  );

  /*
  |--------------------------------------------------------------------------
  | Current uploaded file
  |--------------------------------------------------------------------------
  |
  | File objects cannot safely be persisted in localStorage.
  | The file therefore intentionally exists only for the current
  | browser session.
  |
  |--------------------------------------------------------------------------
  */

  const [resumeFile, setResumeFile] = useState(null);

  /*
  |--------------------------------------------------------------------------
  | Extracted resume text
  |--------------------------------------------------------------------------
  */

  const [resumeText, setResumeTextState] = useState(
    loadStoredResumeText
  );

  /*
  |--------------------------------------------------------------------------
  | Set analysis
  |--------------------------------------------------------------------------
  |
  | Stores the complete backend response.
  |
  | If the backend response contains resume_text, synchronize it
  | automatically with the resume text state.
  |
  |--------------------------------------------------------------------------
  */

  const setAnalysis = useCallback((result) => {
    if (!result || typeof result !== "object") {
      return;
    }

    setAnalysisState(result);

    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(result)
      );
    } catch (error) {
      console.error(
        "Failed to persist resume analysis:",
        error
      );
    }

    /*
     * The backend analysis response already contains
     * `resume_text`.
     *
     * Keep the dedicated resumeText state synchronized with
     * the latest analysis.
     */
    if (
      typeof result.resume_text === "string" &&
      result.resume_text.trim()
    ) {
      const normalizedText =
        result.resume_text;

      setResumeTextState(normalizedText);

      try {
        localStorage.setItem(
          RESUME_TEXT_KEY,
          normalizedText
        );
      } catch (error) {
        console.error(
          "Failed to persist resume text from analysis:",
          error
        );
      }
    }
  }, []);

  /*
  |--------------------------------------------------------------------------
  | Set resume text manually
  |--------------------------------------------------------------------------
  */

  const setResumeText = useCallback((text) => {
    const normalizedText =
      typeof text === "string"
        ? text
        : "";

    setResumeTextState(normalizedText);

    try {
      if (normalizedText.trim()) {
        localStorage.setItem(
          RESUME_TEXT_KEY,
          normalizedText
        );
      } else {
        localStorage.removeItem(
          RESUME_TEXT_KEY
        );
      }
    } catch (error) {
      console.error(
        "Failed to persist resume text:",
        error
      );
    }
  }, []);

  /*
  |--------------------------------------------------------------------------
  | Set current uploaded file
  |--------------------------------------------------------------------------
  */

  const setFile = useCallback((file) => {
    if (file instanceof File) {
      setResumeFile(file);
      return;
    }

    setResumeFile(null);
  }, []);

  /*
  |--------------------------------------------------------------------------
  | Clear all resume data
  |--------------------------------------------------------------------------
  */

  const clearAnalysis = useCallback(() => {
    setAnalysisState(null);
    setResumeFile(null);
    setResumeTextState("");

    try {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(RESUME_TEXT_KEY);
    } catch (error) {
      console.error(
        "Failed to clear resume data:",
        error
      );
    }
  }, []);

  /*
  |--------------------------------------------------------------------------
  | Derived state
  |--------------------------------------------------------------------------
  */

  const hasAnalysis = Boolean(
    analysis &&
      typeof analysis === "object"
  );

  const hasResumeText = Boolean(
    resumeText &&
      resumeText.trim()
  );

  /*
  |--------------------------------------------------------------------------
  | Context value
  |--------------------------------------------------------------------------
  */

  const value = useMemo(
    () => ({
      analysis,
      setAnalysis,

      resumeFile,
      setFile,

      resumeText,
      setResumeText,

      hasAnalysis,
      hasResumeText,

      clearAnalysis,
    }),
    [
      analysis,
      setAnalysis,
      resumeFile,
      setFile,
      resumeText,
      setResumeText,
      hasAnalysis,
      hasResumeText,
      clearAnalysis,
    ]
  );

  return (
    <ResumeContext.Provider value={value}>
      {children}
    </ResumeContext.Provider>
  );
}

export function useResumeContext() {
  const context = useContext(ResumeContext);

  if (!context) {
    throw new Error(
      "useResumeContext must be used inside ResumeProvider"
    );
  }

  return context;
}

export default ResumeContext;

