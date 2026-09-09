import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  BrainCircuit,
  Check,
  Eye,
  EyeOff,
  FileSearch,
  LockKeyhole,
  Mail,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  UserRound,
  Zap,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));

    if (error) {
      setError("");
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");

    const name = form.name.trim();
    const email = form.email.trim();
    const password = form.password;
    const confirmPassword = form.confirmPassword;

    if (!name || !email || !password || !confirmPassword) {
      setError("Please complete all fields.");
      return;
    }

    if (name.length < 2) {
      setError("Name must be at least 2 characters.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await register({
        name,
        email,
        password,
      });

      navigate("/dashboard", {
        replace: true,
      });
    } catch (err) {
      console.error("Registration failed:", err);

      setError(
        err?.message ||
          "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#050816] text-white">
      <div className="grid min-h-screen lg:grid-cols-[1.05fr_0.95fr]">

        {/* =====================================================
            LEFT — PRODUCT EXPERIENCE
        ====================================================== */}

        <section className="relative hidden overflow-hidden border-r border-white/[0.06] lg:flex">

          <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_20%,rgba(59,130,246,0.18),transparent_34%),radial-gradient(circle_at_80%_75%,rgba(99,102,241,0.12),transparent_32%)]" />

          <div
            className="absolute inset-0 opacity-[0.035]"
            style={{
              backgroundImage:
                "linear-gradient(rgba(255,255,255,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.8) 1px, transparent 1px)",
              backgroundSize: "44px 44px",
            }}
          />

          <div className="relative z-10 flex w-full flex-col justify-between p-10 xl:p-14">

            {/* Brand */}

            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 ring-1 ring-blue-400/20">
                <BrainCircuit
                  size={21}
                  className="text-blue-400"
                />
              </div>

              <div>
                <div className="text-[17px] font-semibold tracking-tight">
                  Resume<span className="text-blue-400">IQ</span>
                </div>

                <div className="text-[10px] uppercase tracking-[0.18em] text-slate-500">
                  Resume Intelligence
                </div>
              </div>
            </div>

            {/* Main message */}

            <div className="max-w-xl">

              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-400/15 bg-blue-400/[0.06] px-3 py-1.5 text-xs text-blue-300">
                <Sparkles size={13} />
                AI-powered career intelligence
              </div>

              <h1 className="text-5xl font-semibold leading-[1.08] tracking-[-0.04em] xl:text-6xl">
                Build a resume
                <br />
                that creates an{" "}
                <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-cyan-300 bg-clip-text text-transparent">
                  advantage.
                </span>
              </h1>

              <p className="mt-6 max-w-lg text-[15px] leading-7 text-slate-400">
                Create your ResumeIQ account and turn your resume
                into actionable career intelligence across ATS,
                skills, experience, projects and opportunities.
              </p>

              {/* Intelligence cards */}

              <div className="mt-10 grid max-w-lg grid-cols-2 gap-3">

                <FeatureCard
                  icon={FileSearch}
                  title="Deep Analysis"
                  description="Understand what your resume is really saying."
                />

                <FeatureCard
                  icon={TrendingUp}
                  title="Career Signals"
                  description="Identify strengths and improvement opportunities."
                />

                <FeatureCard
                  icon={Zap}
                  title="ATS Intelligence"
                  description="Improve your visibility to hiring systems."
                />

                <FeatureCard
                  icon={ShieldCheck}
                  title="Private by Design"
                  description="Your career data stays protected."
                />

              </div>
            </div>

            {/* Bottom */}

            <div className="flex items-center gap-6 text-xs text-slate-600">
              <span>© {new Date().getFullYear()} ResumeIQ</span>

              <span className="h-1 w-1 rounded-full bg-slate-700" />

              <span>Built for ambitious careers</span>
            </div>
          </div>
        </section>

        {/* =====================================================
            RIGHT — REGISTER
        ====================================================== */}

        <section className="relative flex min-h-screen items-center justify-center overflow-hidden px-5 py-10 sm:px-8">

          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(59,130,246,0.12),transparent_35%)] lg:hidden" />

          <div className="relative z-10 w-full max-w-[430px]">

            {/* Mobile brand */}

            <div className="mb-10 flex items-center justify-center gap-3 lg:hidden">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 ring-1 ring-blue-400/20">
                <BrainCircuit
                  size={21}
                  className="text-blue-400"
                />
              </div>

              <div className="text-lg font-semibold">
                Resume<span className="text-blue-400">IQ</span>
              </div>
            </div>

            {/* Header */}

            <div className="mb-7">
              <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-white/[0.04] ring-1 ring-white/[0.08]">
                <UserRound
                  size={20}
                  className="text-blue-400"
                />
              </div>

              <h2 className="text-3xl font-semibold tracking-[-0.03em]">
                Create your account
              </h2>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                Start turning your resume into career intelligence.
              </p>
            </div>

            {/* Form card */}

            <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6 shadow-2xl shadow-black/20 sm:p-7">

              {error && (
                <div
                  role="alert"
                  className="mb-5 rounded-xl border border-red-400/15 bg-red-400/[0.06] px-4 py-3 text-sm leading-5 text-red-300"
                >
                  {error}
                </div>
              )}

              <form
                onSubmit={handleSubmit}
                className="space-y-4"
              >

                {/* Name */}

                <div>
                  <label
                    htmlFor="name"
                    className="mb-2 block text-xs font-medium text-slate-300"
                  >
                    Full name
                  </label>

                  <div className="relative">
                    <UserRound
                      size={17}
                      className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-600"
                    />

                    <input
                      id="name"
                      name="name"
                      type="text"
                      autoComplete="name"
                      value={form.name}
                      onChange={handleChange}
                      placeholder="Your full name"
                      disabled={loading}
                      className="h-12 w-full rounded-xl border border-white/[0.09] bg-black/20 pl-11 pr-4 text-sm text-white outline-none transition placeholder:text-slate-700 hover:border-white/[0.14] focus:border-blue-400/50 focus:bg-blue-400/[0.02] focus:ring-4 focus:ring-blue-500/[0.06] disabled:cursor-not-allowed disabled:opacity-60"
                    />
                  </div>
                </div>

                {/* Email */}

                <div>
                  <label
                    htmlFor="email"
                    className="mb-2 block text-xs font-medium text-slate-300"
                  >
                    Email address
                  </label>

                  <div className="relative">
                    <Mail
                      size={17}
                      className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-600"
                    />

                    <input
                      id="email"
                      name="email"
                      type="email"
                      autoComplete="email"
                      value={form.email}
                      onChange={handleChange}
                      placeholder="you@example.com"
                      disabled={loading}
                      className="h-12 w-full rounded-xl border border-white/[0.09] bg-black/20 pl-11 pr-4 text-sm text-white outline-none transition placeholder:text-slate-700 hover:border-white/[0.14] focus:border-blue-400/50 focus:bg-blue-400/[0.02] focus:ring-4 focus:ring-blue-500/[0.06] disabled:cursor-not-allowed disabled:opacity-60"
                    />
                  </div>
                </div>

                {/* Password */}

                <div>
                  <label
                    htmlFor="password"
                    className="mb-2 block text-xs font-medium text-slate-300"
                  >
                    Password
                  </label>

                  <div className="relative">
                    <LockKeyhole
                      size={17}
                      className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-600"
                    />

                    <input
                      id="password"
                      name="password"
                      type={
                        showPassword
                          ? "text"
                          : "password"
                      }
                      autoComplete="new-password"
                      value={form.password}
                      onChange={handleChange}
                      placeholder="At least 8 characters"
                      disabled={loading}
                      className="h-12 w-full rounded-xl border border-white/[0.09] bg-black/20 pl-11 pr-12 text-sm text-white outline-none transition placeholder:text-slate-700 hover:border-white/[0.14] focus:border-blue-400/50 focus:bg-blue-400/[0.02] focus:ring-4 focus:ring-blue-500/[0.06] disabled:cursor-not-allowed disabled:opacity-60"
                    />

                    <button
                      type="button"
                      onClick={() =>
                        setShowPassword(
                          (current) => !current
                        )
                      }
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-600 transition hover:text-slate-300"
                      aria-label={
                        showPassword
                          ? "Hide password"
                          : "Show password"
                      }
                    >
                      {showPassword ? (
                        <EyeOff size={17} />
                      ) : (
                        <Eye size={17} />
                      )}
                    </button>
                  </div>
                </div>

                {/* Confirm password */}

                <div>
                  <label
                    htmlFor="confirmPassword"
                    className="mb-2 block text-xs font-medium text-slate-300"
                  >
                    Confirm password
                  </label>

                  <div className="relative">
                    <LockKeyhole
                      size={17}
                      className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-600"
                    />

                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={
                        showConfirmPassword
                          ? "text"
                          : "password"
                      }
                      autoComplete="new-password"
                      value={form.confirmPassword}
                      onChange={handleChange}
                      placeholder="Repeat your password"
                      disabled={loading}
                      className="h-12 w-full rounded-xl border border-white/[0.09] bg-black/20 pl-11 pr-12 text-sm text-white outline-none transition placeholder:text-slate-700 hover:border-white/[0.14] focus:border-blue-400/50 focus:bg-blue-400/[0.02] focus:ring-4 focus:ring-blue-500/[0.06] disabled:cursor-not-allowed disabled:opacity-60"
                    />

                    <button
                      type="button"
                      onClick={() =>
                        setShowConfirmPassword(
                          (current) => !current
                        )
                      }
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-600 transition hover:text-slate-300"
                      aria-label={
                        showConfirmPassword
                          ? "Hide password"
                          : "Show password"
                      }
                    >
                      {showConfirmPassword ? (
                        <EyeOff size={17} />
                      ) : (
                        <Eye size={17} />
                      )}
                    </button>
                  </div>
                </div>

                {/* Submit */}

                <button
                  type="submit"
                  disabled={loading}
                  className="group mt-2 flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-blue-500 px-5 text-sm font-semibold text-white shadow-lg shadow-blue-500/15 transition hover:bg-blue-400 hover:shadow-blue-500/25 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? (
                    <>
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                      Creating your account...
                    </>
                  ) : (
                    <>
                      Create account

                      <ArrowRight
                        size={16}
                        className="transition-transform duration-200 group-hover:translate-x-0.5"
                      />
                    </>
                  )}
                </button>
              </form>

              {/* Security */}

              <div className="mt-5 flex items-center justify-center gap-2 text-[11px] text-slate-600">
                <ShieldCheck size={13} />
                Secure authentication
              </div>
            </div>

            {/* Existing account */}

            <p className="mt-7 text-center text-sm text-slate-600">
              Already have a ResumeIQ account?{" "}
              <button
                type="button"
                className="font-medium text-blue-400 transition hover:text-blue-300"
                onClick={() =>
                  navigate("/login")
                }
              >
                Sign in
              </button>
            </p>

            {/* Trust */}

            <div className="mt-8 flex items-center justify-center gap-5 text-[10px] uppercase tracking-[0.12em] text-slate-700">
              <span className="flex items-center gap-1.5">
                <Check size={12} />
                Secure
              </span>

              <span className="h-1 w-1 rounded-full bg-slate-800" />

              <span className="flex items-center gap-1.5">
                <Check size={12} />
                Private
              </span>

              <span className="h-1 w-1 rounded-full bg-slate-800" />

              <span className="flex items-center gap-1.5">
                <Check size={12} />
                AI powered
              </span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function FeatureCard({
  icon: Icon,
  title,
  description,
}) {
  return (
    <div className="group rounded-xl border border-white/[0.06] bg-white/[0.025] p-4 transition duration-200 hover:border-blue-400/15 hover:bg-white/[0.04]">
      <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-lg bg-blue-400/[0.07] text-blue-400">
        <Icon size={15} />
      </div>

      <h3 className="text-xs font-semibold text-slate-200">
        {title}
      </h3>

      <p className="mt-1 text-[11px] leading-5 text-slate-600">
        {description}
      </p>
    </div>
  );
}

export default Register;