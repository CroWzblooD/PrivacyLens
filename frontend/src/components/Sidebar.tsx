import { MessageSquare, FileText, Settings, Bot, History, Zap } from "lucide-react";

const sidebarItems = [
  { icon: Bot, label: "Agent", active: true },
  { icon: MessageSquare, label: "Chat", active: false },
  { icon: FileText, label: "Files", active: false },
  { icon: History, label: "History", active: false },
  { icon: Zap, label: "Tools", active: false },
  { icon: Settings, label: "Settings", active: false },
];

export function Sidebar() {
  return (
    <div className="w-14 glass-panel" style={{ background: 'var(--sidebar-bg)' }}>
      <div className="flex flex-col items-center py-4 space-y-3">
        {sidebarItems.map((item, index) => (
          <button
            key={index}
            className={`relative w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 group ${
              item.active
                ? "text-white shadow-glow-strong scale-105"
                : "text-sidebar-text hover:text-white hover:scale-105"
            }`}
            style={item.active ? { background: 'var(--sidebar-active)' } : {}}
          >
            <item.icon className="w-5 h-5 relative z-10" />
            {!item.active && (
              <div className="absolute inset-0 bg-sidebar-item rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            )}
            {item.active && (
              <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-accent-primary/20 to-accent-secondary/30 animate-pulse" />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}