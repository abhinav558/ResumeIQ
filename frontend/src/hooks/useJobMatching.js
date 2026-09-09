import { useCallback, useState } from "react";
import { matchResumeToJob } from "../services/api";

function useJobMatching() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const matchJob = useCallback(
    async (resumeFile, jobDescription) => {
      setLoading(true);
      setError("");

      try {
        if (!(resumeFile instanceof File)) {
          throw new Error(
            "Please analyze a resume before matching it to a job."
          );
        }

        if (!jobDescription?.trim()) {
          throw new Error(
            "Job description is required."
          );
        }

        const data = await matchResumeToJob(
          resumeFile,
          jobDescription
        );

        if (!data || typeof data !== "object") {
          throw new Error(
            "The job matching service returned an invalid response."
          );
        }

        setResult(data);

        return data;
      } catch (err) {
        console.error(
          "Job matching failed:",
          err
        );

        const detail =
          err?.response?.data?.detail;

        const message =
          typeof detail === "string" &&
          detail.trim()
            ? detail
            : err?.message ||
              "Unable to analyze this job description.";

        setResult(null);
        setError(message);

        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const clearResult = useCallback(() => {
    setResult(null);
    setError("");
  }, []);

  return {
    result,
    loading,
    error,
    matchJob,
    clearResult,
  };
}

export default useJobMatching;