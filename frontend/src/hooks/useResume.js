
import { useState } from "react";

import { analyzeResume } from "../services/api";
import { useResumeContext } from "../context/ResumeContext";

function useResume() {
  const {
    setAnalysis,
    setFile,
    setResumeText,
  } = useResumeContext();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyze = async (file) => {
    if (!file) {
      setError("Please select a resume file.");
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await analyzeResume(file);

      if (!result) {
        throw new Error(
          "Resume analysis returned an empty response."
        );
      }

      /*
       * Store the uploaded file.
       */
      setFile(file);

      /*
       * Store the complete analysis result.
       */
      setAnalysis(result);

      /*
       * Store the extracted resume text.
       *
       * This is required by Job Matching because
       * the job matching engine compares:
       *
       * resume text + job description
       */
      if (
        typeof result.resume_text === "string" &&
        result.resume_text.trim()
      ) {
        setResumeText(result.resume_text);
      } else {
        /*
         * Do not silently use analysis fields as resume text.
         * The backend should provide the actual extracted text.
         */
        setResumeText("");
      }

      return result;
    } catch (err) {
      console.error(
        "Resume analysis failed:",
        err
      );

      const detail =
        err?.response?.data?.detail;

      let message =
        "Unable to analyze your resume. Please try again.";

      if (
        typeof detail === "string" &&
        detail.trim()
      ) {
        message = detail;
      } else if (
        typeof err?.message === "string" &&
        err.message.trim()
      ) {
        message = err.message;
      }

      setError(message);

      return null;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setError(null);
    setLoading(false);
  };

  return {
    loading,
    error,
    analyze,
    reset,
  };
}

export default useResume;

