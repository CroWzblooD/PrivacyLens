import { Play, Square, MoreHorizontal } from "lucide-react";

export function ChatHeader() {
  return (
    <div className="h-14 glass-panel border-b border-chat-border" style={{ background: 'var(--chat-panel)' }}>
      <div className="flex items-center justify-between px-6 h-full">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-3 h-3 bg-accent-primary rounded-full animate-pulse glow" />
              <div className="absolute inset-0 w-3 h-3 bg-accent-primary rounded-full animate-ping opacity-75" />
            </div>
            <div>
              <span className="text-text-primary text-sm font-semibold">Agent</span>
              <div className="text-text-muted text-xs font-mono">PDF Redaction Assistant</div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {[Play, Square, MoreHorizontal].map((Icon, index) => (
            <button
              key={index}
              className="w-9 h-9 glass-panel rounded-lg flex items-center justify-center text-text-secondary hover:text-accent-primary transition-all duration-300 hover:scale-105 hover:glow group"
            >
              <Icon className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}