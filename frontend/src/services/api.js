import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: "application/json",
  },
  timeout: 60000,
});

/*
|--------------------------------------------------------------------------
| Authentication
|--------------------------------------------------------------------------
*/

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(
      "resumeiq_access_token"
    );

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

/*
|--------------------------------------------------------------------------
| Response handling
|--------------------------------------------------------------------------
*/

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn(
        "ResumeIQ authentication expired."
      );
    }

    return Promise.reject(error);
  }
);

/*
|--------------------------------------------------------------------------
| Resume Analysis
|--------------------------------------------------------------------------
*/

export const analyzeResume = async (file) => {
  if (!(file instanceof File)) {
    throw new Error(
      "A valid resume file is required."
    );
  }

  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post(
    "/resume/analyze",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

/*
|--------------------------------------------------------------------------
| Resume Library
|--------------------------------------------------------------------------
*/

export const saveResume = async ({
  name,
  resumeText,
  analysis,
}) => {
  if (!name?.trim()) {
    throw new Error(
      "A resume name is required."
    );
  }

  if (
    typeof resumeText !== "string" ||
    !resumeText.trim()
  ) {
    throw new Error(
      "Resume text is required."
    );
  }

  if (!analysis) {
    throw new Error(
      "Resume analysis is required."
    );
  }

  const response = await api.post(
    "/resumes",
    {
      name: name.trim(),
      resume_text: resumeText,
      analysis_json: JSON.stringify(analysis),
    }
  );

  return response.data;
};

/*
|--------------------------------------------------------------------------
| Resume Library - List
|--------------------------------------------------------------------------
*/

export const getSavedResumes = async () => {
  const response = await api.get(
    "/resumes"
  );

  return response.data;
};

/*
|--------------------------------------------------------------------------
| Resume Library - Get
|--------------------------------------------------------------------------
*/

export const getSavedResume = async (
  resumeId
) => {
  if (!resumeId?.trim()) {
    throw new Error(
      "A resume ID is required."
    );
  }

  const response = await api.get(
    `/resumes/${resumeId}`
  );

  return response.data;
};

/*
|--------------------------------------------------------------------------
| Resume Library - Update
|--------------------------------------------------------------------------
*/

export const updateSavedResume = async (
  resumeId,
  updates
) => {
  if (!resumeId?.trim()) {
    throw new Error(
      "A resume ID is required."
    );
  }

  if (!updates || typeof updates !== "object") {
    throw new Error(
      "Resume updates are required."
    );
  }

  const response = await api.put(
    `/resumes/${resumeId}`,
    updates
  );

  return response.data;
};

/*
|--------------------------------------------------------------------------
| Resume Library - Delete
|--------------------------------------------------------------------------
*/

export const deleteSavedResume = async (
  resumeId
) => {
  if (!resumeId?.trim()) {
    throw new Error(
      "A resume ID is required."
    );
  }

  await api.delete(
    `/resumes/${resumeId}`
  );
};

/*
|--------------------------------------------------------------------------
| Resume → Job Matching
|--------------------------------------------------------------------------
|
| Sends the original resume file to the backend.
| The backend is responsible for:
|
| 1. Validating the file
| 2. Extracting resume text
| 3. Analyzing job requirements
| 4. Calculating compatibility
| 5. Returning the JobMatchResponse
|
|--------------------------------------------------------------------------

*/

export const matchResumeToJob = async (
  file,
  jobDescription
) => {
  if (!(file instanceof File)) {
    throw new Error(
      "A valid resume file is required."
    );
  }

  if (!jobDescription?.trim()) {
    throw new Error(
      "Job description is required."
    );
  }

  const formData = new FormData();

  formData.append("file", file);

  formData.append(
    "job_description",
    jobDescription.trim()
  );

  const response = await api.post(
    "/resume/match",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

export default api;

