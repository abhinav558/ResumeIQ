import { useState } from "react";
import NotificationPanel from "./NotificationPanel";

function NotificationBell() {
  const [open, setOpen] = useState(false);

  const notifications = [
    {
      id: "resume-analysis",
      title: "Resume analysis ready",
      message: "Your latest resume analysis is available.",
      type: "info",
    },
    {
      id: "ats-review",
      title: "ATS review available",
      message: "Review your ATS intelligence to find improvement areas.",
      type: "info",
    },
  ];

  return (
    <div className="relative">
      <button
        type="button"
        aria-label="Notifications"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
        className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.07] bg-white/[0.025] text-slate-400 hover:border-white/[0.12] hover:text-white"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
          <path d="M10 21h4" />
        </svg>

        {notifications.length > 0 && (
          <span
            aria-hidden="true"
            className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-blue-400 ring-2 ring-[#060914]"
          />
        )}
      </button>

      {open && (
        <NotificationPanel
          notifications={notifications}
          onClose={() => setOpen(false)}
        />
      )}
    </div>
  );
}

export default NotificationBell;