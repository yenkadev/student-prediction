import type { View } from "../App";
import "./Sidebar.css";

interface NavItemProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}

function NavItem({ active, onClick, icon, label }: NavItemProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`nav-item${active ? " nav-item--active" : ""}`}
    >
      {icon}
      {label}
    </button>
  );
}

interface SidebarProps {
  view: View;
  onNavigate: (view: View) => void;
}

export function Sidebar({ view, onNavigate }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <svg width="30" height="30" viewBox="0 0 30 30" fill="none">
          <circle cx="15" cy="15" r="4.5" fill="#B8892B" />
          <circle cx="15" cy="15" r="9" stroke="#B8892B" strokeWidth="1.4" opacity="0.55" />
          <circle cx="15" cy="15" r="13.5" stroke="#B8892B" strokeWidth="1.2" opacity="0.3" />
        </svg>
        <div>
          <div className="sidebar__title">Early Risk Warning</div>
          <div className="sidebar__subtitle">Academic Risk Detection</div>
        </div>
      </div>

      <nav className="sidebar__nav">
        <NavItem
          active={view === "dashboard"}
          onClick={() => onNavigate("dashboard")}
          label="Overview"
          icon={
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="7" height="9" rx="1.5" />
              <rect x="14" y="3" width="7" height="5" rx="1.5" />
              <rect x="14" y="12" width="7" height="9" rx="1.5" />
              <rect x="3" y="16" width="7" height="5" rx="1.5" />
            </svg>
          }
        />
        <NavItem
          active={view === "new"}
          onClick={() => onNavigate("new")}
          label="New Assessment"
          icon={
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
            </svg>
          }
        />
        <NavItem
          active={view === "batch"}
          onClick={() => onNavigate("batch")}
          label="Batch Results"
          icon={
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 3h18v18H3z" />
              <path d="M3 9h18M3 15h18M9 3v18" />
            </svg>
          }
        />
      </nav>

      <div className="sidebar__footer">Early Academic Risk Warning System</div>
    </aside>
  );
}
