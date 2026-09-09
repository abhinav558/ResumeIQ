import { useEffect, useRef } from "react";

function NotificationPanel({ notifications, onClose }) {
  const panelRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        panelRef.current &&
        !panelRef.current.contains(event.target)
      ) {
        onClose();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [onClose]);

  return (
    <div
      ref={panelRef}
      className="absolute right-0 top-12 z-[80] w-[340px] overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0b1020] shadow-2xl shadow-black/40"
    >
      <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-3.5">
        <div>
          <p className="text-sm font-semibold text-white">
            Notifications
          </p>

          <p className="mt-0.5 text-[10px] text-slate-600">
            ResumeIQ updates
          </p>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="rounded-md px-2 py-1 text-xs text-slate-600 hover:bg-white/[0.04] hover:text-slate-300"
        >
          Close
        </button>
      </div>

      <div className="max-h-[360px] overflow-y-auto p-2">
        {notifications.length > 0 ? (
          notifications.map((notification) => (
            <div
              key={notification.id}
              className="rounded-xl px-3 py-3 transition hover:bg-white/[0.035]"
            >
              <div className="flex gap-3">
                <span
                  aria-hidden="true"
                  className="mt-1 h-2 w-2 shrink-0 rounded-full bg-blue-400"
                />

                <div className="min-w-0">
                  <p className="text-xs font-semibold text-slate-200">
                    {notification.title}
                  </p>

                  <p className="mt-1 text-[11px] leading-relaxed text-slate-600">
                    {notification.message}
                  </p>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="px-4 py-8 text-center">
            <p className="text-xs text-slate-600">
              You're all caught up.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default NotificationPanel;