import {
  LayoutDashboard,
  FileText,
  Target,
  Briefcase,
  Settings,
  Sparkles,
} from "lucide-react";

function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r border-white/10 bg-slate-950 p-5">
      <div className="mb-10 flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600">
          <Sparkles size={20} />
        </div>

        <div>
          <h1 className="text-lg font-bold">ResumeIQ</h1>
          <p className="text-xs text-slate-500">AI Career Intelligence</p>
        </div>
      </div>

      <nav className="space-y-2">
        <SidebarItem
          icon={<LayoutDashboard size={19} />}
          label="Dashboard"
          active
        />

        <SidebarItem
          icon={<FileText size={19} />}
          label="My Resumes"
        />

        <SidebarItem
          icon={<Target size={19} />}
          label="ATS Analyzer"
        />

        <SidebarItem
          icon={<Briefcase size={19} />}
          label="Job Matches"
        />

        <SidebarItem
          icon={<Settings size={19} />}
          label="Settings"
        />
      </nav>

      <div className="absolute bottom-5 left-5 right-5 rounded-2xl border border-indigo-500/20 bg-indigo-500/10 p-4">
        <p className="text-sm font-semibold">Unlock ResumeIQ Pro</p>

        <p className="mt-1 text-xs text-slate-400">
          Get deeper insights and unlimited analysis.
        </p>

        <button className="mt-3 w-full rounded-lg bg-indigo-600 py-2 text-sm font-medium transition hover:bg-indigo-500">
          Upgrade
        </button>
      </div>
    </aside>
  );
}

function SidebarItem({ icon, label, active = false }) {
  return (
    <button
      className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm transition ${
        active
          ? "bg-indigo-600/15 text-indigo-400"
          : "text-slate-400 hover:bg-white/5 hover:text-white"
      }`}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}

export default Sidebar;