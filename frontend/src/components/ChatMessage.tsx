import { Bot, User, ChevronDown, ChevronRight, CheckCircle, Circle, FileText, AlertCircle } from "lucide-react";
import { useState } from "react";

interface ChatMessageProps {
  type: "user" | "agent";
  content: string;
  timestamp?: string;
  expandable?: boolean;
  status?: "pending" | "completed" | "error" | "in-progress";
  files?: string[];
  children?: React.ReactNode;
}

export function ChatMessage({ 
  type, 
  content, 
  timestamp, 
  expandable = false, 
  status,
  files,
  children 
}: ChatMessageProps) {
  const [isExpanded, setIsExpanded] = useState(expandable);

  const getStatusIcon = () => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4 text-accent-green" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-error" />;
      default:
        return <Circle className="w-4 h-4 text-text-muted" />;
    }
  };

  return (
    <div className={`p-6 border-b border-chat-border/50 hover:bg-gradient-to-r hover:from-transparent hover:to-accent-primary/5 transition-all duration-300 ${
      type === "user" ? "" : ""
    }`} 
    style={{ background: type === "user" ? 'var(--chat-user)' : 'transparent' }}>
      <div className="flex space-x-4">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-medium transition-all duration-300 ${
          type === "agent" 
            ? "bg-gradient-to-br from-accent-primary to-accent-secondary text-white glow" 
            : "glass-panel text-text-primary"
        }`}>
          {type === "agent" ? (
            <Bot className="w-5 h-5" />
          ) : (
            <User className="w-5 h-5" />
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-3 mb-2">
            <span className="text-text-primary font-semibold text-sm">
              {type === "agent" ? "Assistant" : "You"}
            </span>
            {timestamp && (
              <span className="text-text-muted text-xs font-mono">{timestamp}</span>
            )}
            {status && (
              <div className="flex items-center">
                {getStatusIcon()}
              </div>
            )}
          </div>
          
          <div className="text-text-secondary text-sm leading-relaxed font-medium">
            {content}
          </div>
          
          {files && files.length > 0 && (
            <div className="mt-3 space-y-2">
              {files.map((file, index) => (
                <div key={index} className="glass-panel rounded-lg p-3 border border-glass-border">
                  <div className="flex items-center space-x-3 text-xs">
                    <FileText className="w-4 h-4 text-accent-primary" />
                    <span className="font-mono text-text-secondary">{file}</span>
                    <div className="flex items-center space-x-2 ml-auto">
                      <span className="text-success font-mono">+14</span>
                      <span className="text-error font-mono">-8</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {expandable && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center space-x-2 mt-3 text-text-muted hover:text-accent-primary transition-all duration-200 group"
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4 group-hover:scale-110 transition-transform" />
              ) : (
                <ChevronRight className="w-4 h-4 group-hover:scale-110 transition-transform" />
              )}
              <span className="text-xs font-medium">
                {isExpanded ? "Collapse" : "Expand details"}
              </span>
            </button>
          )}
          
          {isExpanded && children && (
            <div className="mt-4 glass-panel rounded-xl p-4 border border-glass-border animate-fade-in">
              {children}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}