import {
  useEffect,
  useRef,
  useState,
} from "react";
import { createPortal } from "react-dom";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

function ProfileMenu() {
  const [open, setOpen] = useState(false);
  const [menuPosition, setMenuPosition] = useState({
    top: 0,
    right: 0,
  });

  const wrapperRef = useRef(null);
  const buttonRef = useRef(null);
  const menuRef = useRef(null);

  const navigate = useNavigate();

  const { user, logout } = useAuth();

  const updateMenuPosition = () => {
    if (!buttonRef.current) return;

    const rect =
      buttonRef.current.getBoundingClientRect();

    setMenuPosition({
      top: rect.bottom + 8,
      right:
        Math.max(
          12,
          window.innerWidth - rect.right
        ),
    });
  };

  useEffect(() => {
    if (!open) return;

    updateMenuPosition();

    const handleResize = () => {
      updateMenuPosition();
    };

    const handleScroll = () => {
      updateMenuPosition();
    };

    window.addEventListener(
      "resize",
      handleResize
    );

    window.addEventListener(
      "scroll",
      handleScroll,
      true
    );

    return () => {
      window.removeEventListener(
        "resize",
        handleResize
      );

      window.removeEventListener(
        "scroll",
        handleScroll,
        true
      );
    };
  }, [open]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      const target = event.target;

      if (
        wrapperRef.current?.contains(target) ||
        menuRef.current?.contains(target)
      ) {
        return;
      }

      setOpen(false);
    };

    document.addEventListener(
      "mousedown",
      handleClickOutside
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleClickOutside
      );
    };
  }, []);

  const toggleMenu = () => {
    if (!open) {
      updateMenuPosition();
    }

    setOpen((value) => !value);
  };

  const goToSettings = () => {
    setOpen(false);
    navigate("/settings");
  };

  const handleLogout = () => {
    setOpen(false);
    logout();

    navigate("/login", {
      replace: true,
    });
  };

  const displayName =
    user?.name?.trim() || "User";

  const initial =
    displayName.charAt(0).toUpperCase() || "U";

  return (
    <>
      <div
        ref={wrapperRef}
        className="relative"
      >
        <button
          ref={buttonRef}
          type="button"
          aria-label="Open profile menu"
          aria-expanded={open}
          aria-haspopup="menu"
          onClick={toggleMenu}
          className="group flex items-center gap-2.5 rounded-xl border border-white/[0.07] bg-white/[0.025] py-1.5 pl-1.5 pr-2.5 transition-colors hover:border-white/[0.12] hover:bg-white/[0.05] focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/60"
        >
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-[10px] font-bold text-white">
            {initial}
          </div>

          <div className="hidden text-left sm:block">
            <p className="max-w-[110px] truncate text-[11px] font-semibold text-slate-200">
              {displayName}
            </p>

            <p className="text-[9px] text-slate-600">
              Resume workspace
            </p>
          </div>

          <span
            className={[
              "hidden text-slate-600 transition-transform duration-200 sm:block",
              open ? "rotate-90" : "",
            ].join(" ")}
          >
            <svg
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.7"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="m9 18 6-6-6-6" />
            </svg>
          </span>
        </button>
      </div>

      {open &&
        typeof document !== "undefined" &&
        createPortal(
          <div
            ref={menuRef}
            role="menu"
            aria-label="Profile menu"
            style={{
              position: "fixed",
              top: `${menuPosition.top}px`,
              right: `${menuPosition.right}px`,
            }}
            className="z-[9999] w-56 overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0b1020] shadow-2xl shadow-black/50 ring-1 ring-black/20"
          >
            <div className="border-b border-white/[0.06] px-4 py-3.5">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-xs font-bold text-white">
                  {initial}
                </div>

                <div className="min-w-0">
                  <p className="truncate text-xs font-semibold text-white">
                    {displayName}
                  </p>

                  <p className="mt-1 truncate text-[10px] text-slate-600">
                    {user?.email ||
                      "Resume workspace"}
                  </p>
                </div>
              </div>
            </div>

            <div className="p-2">
              <button
                type="button"
                role="menuitem"
                onClick={goToSettings}
                className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-xs text-slate-400 transition-colors hover:bg-white/[0.04] hover:text-white focus:outline-none focus-visible:bg-white/[0.05] focus-visible:text-white"
              >
                <span
                  className="flex h-7 w-7 items-center justify-center rounded-lg bg-white/[0.035] text-slate-500"
                  aria-hidden="true"
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.7"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z" />
                    <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-1.5 1.5-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V20h-2.12v-.4a1.7 1.7 0 0 0-1.03-1.56 1.7 1.7 0 0 0-1.88.34l-.06.06-1.5-1.5.06-.06A1.7 1.7 0 0 0 9.1 15a1.7 1.7 0 0 0-1.56-1.03H7.1v-2.12h.44A1.7 1.7 0 0 0 9.1 10.8a1.7 1.7 0 0 0-.34-1.88L8.7 8.86l1.5-1.5.06.06a1.7 1.7 0 0 0 1.88.34 1.7 1.7 0 0 0 1.03-1.56V5.8h2.12v.4a1.7 1.7 0 0 0 1.03 1.56 1.7 1.7 0 0 0 1.88-.34l.06-.06 1.5 1.5-.06.06A1.7 1.7 0 0 0 19.4 10.8a1.7 1.7 0 0 0 1.56 1.03h.44v2.12h-.44A1.7 1.7 0 0 0 19.4 15Z" />
                  </svg>
                </span>

                <span>Settings</span>
              </button>

              <button
                type="button"
                role="menuitem"
                onClick={handleLogout}
                className="mt-1 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-xs text-slate-400 transition-colors hover:bg-red-400/[0.06] hover:text-red-300 focus:outline-none focus-visible:bg-red-400/[0.07] focus-visible:text-red-300"
              >
                <span
                  className="flex h-7 w-7 items-center justify-center rounded-lg bg-white/[0.035] text-slate-500"
                  aria-hidden="true"
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.7"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M10 17l5-5-5-5" />
                    <path d="M15 12H3" />
                    <path d="M21 19V5a2 2 0 0 0-2-2h-6" />
                  </svg>
                </span>

                <span>Log out</span>
              </button>
            </div>
          </div>,
          document.body
        )}
    </>
  );
}

export default ProfileMenu;

