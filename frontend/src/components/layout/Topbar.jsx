import { Bell, Search } from "lucide-react";

function Topbar() {
  return (
    <header className="flex h-20 items-center justify-between border-b border-white/10 bg-slate-950/80 px-8 backdrop-blur-xl">
      <div>
        <h2 className="text-xl font-semibold">Dashboard</h2>
        <p className="text-sm text-slate-500">
          Track and improve your career profile.
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2">
          <Search size={17} className="text-slate-500" />

          <input
            type="text"
            placeholder="Search..."
            className="w-32 bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
          />
        </div>

        <button className="rounded-xl border border-white/10 p-2.5 text-slate-400 transition hover:bg-white/5 hover:text-white">
          <Bell size={18} />
        </button>

        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-sm font-semibold">
          A
        </div>
      </div>
    </header>
  );
}

export default Topbar;