import { Outlet, NavLink, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";

import GlobalSearch from "../search/GlobalSearch";
import NotificationBell from "../notifications/NotificationBell";
import ProfileMenu from "../profile/ProfileMenu";

function Icon({ name, size = 19 }) {
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
    dashboard: (
      <svg {...common}>
        <rect x="3" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" />
        <rect x="14" y="14" width="7" height="7" rx="1.5" />
      </svg>
    ),

    analysis: (
      <svg {...common}>
        <path d="M6 3.5h8l4 4V20a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z" />
        <path d="M14 3.5V8h4" />
        <path d="M8 12h8" />
        <path d="M8 16h5" />
      </svg>
    ),

    library: (
      <svg {...common}>
        <path d="M5 4.5A1.5 1.5 0 0 1 6.5 3H19v16H6.5A1.5 1.5 0 0 0 5 20.5v-16Z" />
        <path d="M5 20.5A1.5 1.5 0 0 1 6.5 19H19" />
        <path d="M8.5 7h7" />
        <path d="M8.5 10.5h7" />
        <path d="M8.5 14h4.5" />
      </svg>
    ),

    ats: (
      <svg {...common}>
        <circle cx="11" cy="11" r="6.5" />
        <path d="m16 16 4.5 4.5" />
        <path d="M8.5 11h5" />
        <path d="M11 8.5v5" />
      </svg>
    ),

    matching: (
      <svg {...common}>
        <rect x="3" y="5" width="18" height="15" rx="2" />
        <path d="M8 5V3h8v2" />
        <path d="M3 10h18" />
        <path d="M9 14h6" />
      </svg>
    ),

    settings: (
      <svg {...common}>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-1.7 1.7-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V20h-2.4v-.2a1.7 1.7 0 0 0-1.03-1.56 1.7 1.7 0 0 0-1.88.34l-.06.06-1.7-1.7.06-.06A1.7 1.7 0 0 0 8.46 15a1.7 1.7 0 0 0-1.56-1.03h-.2v-2.4h.2A1.7 1.7 0 0 0 8.46 10a1.7 1.7 0 0 0-.34-1.88l-.06-.06 1.7-1.7.06.06a1.7 1.7 0 0 0 1.88.34A1.7 1.7 0 0 0 12.73 5.2V5h2.4v.2a1.7 1.7 0 0 0 1.03 1.56 1.7 1.7 0 0 0 1.88-.34l.06-.06 1.7 1.7-.06.06A1.7 1.7 0 0 0 19.4 10a1.7 1.7 0 0 0 1.56 1.03h.2v2.4h-.2A1.7 1.7 0 0 0 19.4 15Z" />
      </svg>
    ),

    bell: (
      <svg {...common}>
        <path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
        <path d="M10 21h4" />
      </svg>
    ),

    search: (
      <svg {...common}>
        <circle cx="11" cy="11" r="6.5" />
        <path d="m16 16 4.5 4.5" />
      </svg>
    ),

    menu: (
      <svg {...common}>
        <path d="M4 7h16" />
        <path d="M4 12h16" />
        <path d="M4 17h16" />
      </svg>
    ),

    close: (
      <svg {...common}>
        <path d="m6 6 12 12" />
        <path d="m18 6-12 12" />
      </svg>
    ),

    chevron: (
      <svg {...common}>
        <path d="m9 18 6-6-6-6" />
      </svg>
    ),

    shield: (
      <svg {...common}>
        <path d="M12 3 20 6v5c0 5-3.3 8.6-8 10-4.7-1.4-8-5-8-10V6l8-3Z" />
        <path d="m9 12 2 2 4-4" />
      </svg>
    ),
  };

  return icons[name] || null;
}

const navigation = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: "dashboard",
  },
  {
    label: "Resume Analysis",
    path: "/resume-analysis",
    icon: "analysis",
  },
  {
    label: "Resume Library",
    path: "/resume-library",
    icon: "library",
  },
  {
    label: "ATS Intelligence",
    path: "/ats-intelligence",
    icon: "ats",
  },
  {
    label: "Job Matching",
    path: "/job-matching",
    icon: "matching",
  },
];

function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  const location = useLocation();

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (
        event.key === "/" &&
        !event.ctrlKey &&
        !event.metaKey &&
        !event.altKey
      ) {
        const target = event.target;

        if (
          target instanceof HTMLInputElement ||
          target instanceof HTMLTextAreaElement ||
          target instanceof HTMLSelectElement ||
          target?.isContentEditable
        ) {
          return;
        }

        event.preventDefault();
        setSearchOpen(true);
      }

      if (event.key === "Escape") {
        setSearchOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  const pageTitle = getPageTitle(location.pathname);

  return (
    <div className="min-h-screen bg-[#060914] text-white">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-64 -top-64 h-[700px] w-[700px] rounded-full bg-blue-600/[0.035] blur-[150px]" />

        <div className="absolute -bottom-72 -right-72 h-[700px] w-[700px] rounded-full bg-indigo-600/[0.03] blur-[150px]" />
      </div>

      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-[260px] border-r border-white/[0.06] bg-[#080c18]/95 backdrop-blur-2xl lg:flex lg:flex-col">
        <Sidebar />
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <button
          type="button"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm lg:hidden"
        />
      )}

      {/* Mobile sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-[60] w-[280px] border-r border-white/[0.08] bg-[#080c18] shadow-2xl transition-transform duration-300 lg:hidden ${
          mobileOpen
            ? "translate-x-0"
            : "-translate-x-full"
        }`}
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-5">
            <Brand />

            <button
              type="button"
              aria-label="Close navigation"
              onClick={() => setMobileOpen(false)}
              className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-500 hover:bg-white/[0.05] hover:text-white"
            >
              <Icon name="close" size={18} />
            </button>
          </div>

          <Navigation
            onNavigate={() => setMobileOpen(false)}
          />

          <SidebarFooter />
        </div>
      </aside>

      {/* Global search */}
      {searchOpen && (
        <GlobalSearch
          onClose={() => setSearchOpen(false)}
        />
      )}

      {/* Main */}
      <div className="relative min-h-screen lg:pl-[260px]">
        <header className="sticky top-0 z-30 border-b border-white/[0.06] bg-[#060914]/85 backdrop-blur-2xl">
          <div className="flex h-[72px] items-center justify-between px-5 sm:px-7 lg:px-9">
            <div className="flex min-w-0 items-center gap-4">
              {/* Mobile menu */}
              <button
                type="button"
                aria-label="Open navigation"
                aria-expanded={mobileOpen}
                onClick={() => setMobileOpen(true)}
                className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.07] bg-white/[0.025] text-slate-400 hover:bg-white/[0.05] hover:text-white lg:hidden"
              >
                <Icon name="menu" size={19} />
              </button>

              <div className="min-w-0">
                <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-blue-400">
                  ResumeIQ
                </p>

                <h1 className="mt-0.5 truncate text-sm font-semibold text-white sm:text-base">
                  {pageTitle}
                </h1>
              </div>
            </div>

            <div className="flex items-center gap-2 sm:gap-3">
              {/* Search */}
              <button
                type="button"
                aria-label="Open search"
                onClick={() => setSearchOpen(true)}
                className="hidden h-10 items-center gap-3 rounded-xl border border-white/[0.07] bg-white/[0.025] px-3.5 text-xs text-slate-500 hover:border-white/[0.12] hover:text-slate-300 md:flex"
              >
                <Icon name="search" size={16} />

                <span>Search</span>

                <kbd className="ml-3 rounded-md border border-white/[0.07] bg-white/[0.03] px-1.5 py-0.5 text-[9px] text-slate-600">
                  /
                </kbd>
              </button>

              {/* Notifications */}
              <NotificationBell />

              {/* Profile */}
              <ProfileMenu />
            </div>
          </div>
        </header>

        <main className="relative min-h-[calc(100vh-72px)]">
          <div className="mx-auto w-full max-w-[1600px]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

function Sidebar() {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-white/[0.06] px-5 py-6">
        <Brand />
      </div>

      <Navigation />

      <SidebarFooter />
    </div>
  );
}

function Brand() {
  return (
    <div className="flex items-center gap-3">
      <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-900/25">
        <span className="relative text-sm font-black tracking-tight text-white">
          R
        </span>
      </div>

      <div>
        <div className="flex items-center gap-1.5">
          <span className="text-[17px] font-bold tracking-tight text-white">
            ResumeIQ
          </span>

          <span className="rounded-md border border-blue-400/15 bg-blue-400/[0.08] px-1.5 py-0.5 text-[7px] font-bold uppercase tracking-wider text-blue-400">
            AI
          </span>
        </div>

        <p className="mt-0.5 text-[9px] font-medium uppercase tracking-[0.16em] text-slate-600">
          Career intelligence
        </p>
      </div>
    </div>
  );
}

function Navigation({ onNavigate }) {
  return (
    <nav
      aria-label="Primary navigation"
      className="flex-1 overflow-y-auto px-3 py-6"
    >
      <p className="px-3 pb-3 text-[9px] font-bold uppercase tracking-[0.18em] text-slate-600">
        Workspace
      </p>

      <div className="space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            onClick={onNavigate}
            className={({ isActive }) =>
              `group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-medium transition-all ${
                isActive
                  ? "bg-blue-500/[0.10] text-blue-300"
                  : "text-slate-500 hover:bg-white/[0.035] hover:text-slate-200"
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <span className="absolute left-0 top-1/2 h-5 w-[2px] -translate-y-1/2 rounded-r-full bg-blue-400 shadow-[0_0_10px_rgba(96,165,250,0.7)]" />
                )}

                <span
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                    isActive
                      ? "bg-blue-500/[0.12] text-blue-400"
                      : "bg-white/[0.025] text-slate-600 group-hover:text-slate-300"
                  }`}
                >
                  <Icon
                    name={item.icon}
                    size={17}
                  />
                </span>

                <span className="flex-1">
                  {item.label}
                </span>

                {isActive && (
                  <span className="h-1.5 w-1.5 rounded-full bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.8)]" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </div>

      <div className="my-7 h-px bg-white/[0.05]" />

      <p className="px-3 pb-3 text-[9px] font-bold uppercase tracking-[0.18em] text-slate-600">
        Account
      </p>

      <NavLink
        to="/settings"
        onClick={onNavigate}
        className={({ isActive }) =>
          `group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-medium transition-all ${
            isActive
              ? "bg-blue-500/[0.10] text-blue-300"
              : "text-slate-500 hover:bg-white/[0.035] hover:text-slate-200"
          }`
        }
      >
        {({ isActive }) => (
          <>
            {isActive && (
              <span className="absolute left-0 top-1/2 h-5 w-[2px] -translate-y-1/2 rounded-r-full bg-blue-400 shadow-[0_0_10px_rgba(96,165,250,0.7)]" />
            )}

            <span
              className={`flex h-8 w-8 items-center justify-center rounded-lg ${
                isActive
                  ? "bg-blue-500/[0.12] text-blue-400"
                  : "bg-white/[0.025] text-slate-600 group-hover:text-slate-300"
              }`}
            >
              <Icon name="settings" size={17} />
            </span>

            <span className="flex-1">
              Settings
            </span>

            {isActive && (
              <span className="h-1.5 w-1.5 rounded-full bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.8)]" />
            )}
          </>
        )}
      </NavLink>
    </nav>
  );
}

function SidebarFooter() {
  return (
    <div className="border-t border-white/[0.06] p-4">
      <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3.5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/[0.08] text-emerald-400">
            <Icon name="shield" size={15} />
          </div>

          <div>
            <p className="text-[10px] font-semibold text-slate-300">
              Secure workspace
            </p>

            <p className="mt-0.5 text-[9px] text-slate-600">
              Your resume stays protected
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function getPageTitle(pathname) {
  if (pathname.startsWith("/resume-analysis")) {
    return "Resume Analysis";
  }

  if (pathname.startsWith("/resume-library")) {
    return "Resume Library";
  }

  if (pathname.startsWith("/ats-intelligence")) {
    return "ATS Intelligence";
  }

  if (pathname.startsWith("/job-matching")) {
    return "Job Matching";
  }

  if (pathname.startsWith("/settings")) {
    return "Settings";
  }

  return "Dashboard";
}

export default DashboardLayout;

