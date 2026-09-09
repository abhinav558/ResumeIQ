import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

const AuthContext = createContext(null);

/*
|--------------------------------------------------------------------------
| API configuration
|--------------------------------------------------------------------------
|
| VITE_API_URL is the same environment variable used by
| frontend/src/services/api.js.
|
| Local development:
|   VITE_API_URL=http://127.0.0.1:8000
|
| Production:
|   VITE_API_URL=https://resumeiq-sopb.onrender.com
|
*/

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000"
).replace(/\/+$/, "");

const TOKEN_KEY = "resumeiq_access_token";
const USER_KEY = "resumeiq_user";

/*
|--------------------------------------------------------------------------
| Storage helpers
|--------------------------------------------------------------------------
*/

function loadStoredUser() {
  try {
    const stored = localStorage.getItem(USER_KEY);

    if (!stored) {
      return null;
    }

    const parsed = JSON.parse(stored);

    if (!parsed || typeof parsed !== "object") {
      localStorage.removeItem(USER_KEY);
      return null;
    }

    return parsed;
  } catch (error) {
    console.error(
      "Failed to load stored user:",
      error
    );

    return null;
  }
}

function loadStoredToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || "";
  } catch (error) {
    console.error(
      "Failed to load stored authentication token:",
      error
    );

    return "";
  }
}

/*
|--------------------------------------------------------------------------
| Auth Provider
|--------------------------------------------------------------------------
*/

export function AuthProvider({ children }) {
  const [token, setToken] = useState(loadStoredToken);
  const [user, setUser] = useState(loadStoredUser);
  const [loading, setLoading] = useState(true);

  /*
  |--------------------------------------------------------------------------
  | Clear authentication state
  |--------------------------------------------------------------------------
  */

  const clearAuth = useCallback(() => {
    setToken("");
    setUser(null);

    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    } catch (error) {
      console.error(
        "Failed to clear authentication data:",
        error
      );
    }
  }, []);

  /*
  |--------------------------------------------------------------------------
  | Store authentication state
  |--------------------------------------------------------------------------
  */

  const storeAuth = useCallback((authResponse) => {
    if (
      !authResponse ||
      typeof authResponse !== "object" ||
      !authResponse.access_token ||
      !authResponse.user
    ) {
      throw new Error(
        "Invalid authentication response."
      );
    }

    const nextToken = authResponse.access_token;
    const nextUser = authResponse.user;

    setToken(nextToken);
    setUser(nextUser);

    try {
      localStorage.setItem(
        TOKEN_KEY,
        nextToken
      );

      localStorage.setItem(
        USER_KEY,
        JSON.stringify(nextUser)
      );
    } catch (error) {
      console.error(
        "Failed to persist authentication data:",
        error
      );
    }

    return nextUser;
  }, []);

  /*
  |--------------------------------------------------------------------------
  | API request helper
  |--------------------------------------------------------------------------
  */

  const request = useCallback(
    async (endpoint, options = {}) => {
      const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
          ...options,
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            ...(options.headers || {}),
          },
        }
      );

      let data = null;

      try {
        data = await response.json();
      } catch {
        data = null;
      }

      if (!response.ok) {
        const message =
          data?.detail ||
          "Something went wrong. Please try again.";

        const error = new Error(message);
        error.status = response.status;

        throw error;
      }

      return data;
    },
    []
  );

  /*
  |--------------------------------------------------------------------------
  | Register
  |--------------------------------------------------------------------------
  */

  const register = useCallback(
    async ({
      name,
      email,
      password,
    }) => {
      const data = await request(
        "/auth/register",
        {
          method: "POST",
          body: JSON.stringify({
            name,
            email,
            password,
          }),
        }
      );

      return storeAuth(data);
    },
    [request, storeAuth]
  );

  /*
  |--------------------------------------------------------------------------
  | Login
  |--------------------------------------------------------------------------
  */

  const login = useCallback(
    async ({
      email,
      password,
    }) => {
      const data = await request(
        "/auth/login",
        {
          method: "POST",
          body: JSON.stringify({
            email,
            password,
          }),
        }
      );

      return storeAuth(data);
    },
    [request, storeAuth]
  );

  /*
  |--------------------------------------------------------------------------
  | Logout
  |--------------------------------------------------------------------------
  */

  const logout = useCallback(() => {
    clearAuth();
  }, [clearAuth]);

  /*
  |--------------------------------------------------------------------------
  | Restore / validate existing session
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    let cancelled = false;

    async function restoreSession() {
      const storedToken = loadStoredToken();

      if (!storedToken) {
        if (!cancelled) {
          setLoading(false);
        }

        return;
      }

      try {
        const response = await fetch(
          `${API_BASE_URL}/auth/me`,
          {
            method: "GET",
            headers: {
              Accept: "application/json",
              Authorization: `Bearer ${storedToken}`,
            },
          }
        );

        let data = null;

        try {
          data = await response.json();
        } catch {
          data = null;
        }

        if (!response.ok) {
          const message =
            data?.detail ||
            "Authentication session is no longer valid.";

          const error = new Error(message);
          error.status = response.status;

          throw error;
        }

        const currentUser = data;

        if (cancelled) {
          return;
        }

        setToken(storedToken);
        setUser(currentUser);

        try {
          localStorage.setItem(
            USER_KEY,
            JSON.stringify(currentUser)
          );
        } catch (error) {
          console.error(
            "Failed to refresh stored user:",
            error
          );
        }
      } catch (error) {
        console.error(
          "Failed to restore authentication session:",
          error
        );

        if (!cancelled) {
          clearAuth();
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    restoreSession();

    return () => {
      cancelled = true;
    };
  }, [clearAuth]);

  /*
  |--------------------------------------------------------------------------
  | Derived authentication state
  |--------------------------------------------------------------------------
  */

  const isAuthenticated = Boolean(
    token && user
  );

  /*
  |--------------------------------------------------------------------------
  | Context value
  |--------------------------------------------------------------------------
  */

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthenticated,
      login,
      register,
      logout,
    }),
    [
      token,
      user,
      loading,
      isAuthenticated,
      login,
      register,
      logout,
    ]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/*
|--------------------------------------------------------------------------
| Auth Hook
|--------------------------------------------------------------------------
*/

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}

export default AuthContext;

