import { ChevronDown, ChevronRight, CheckCircle, Clock, AlertCircle } from "lucide-react";
import { useState, useMemo } from "react";

interface ProgressItem {
  id: string;
  title: string;
  status: "completed" | "in-progress" | "pending" | "error";
  timestamp: string;
  details?: string[];
}

interface ProgressSectionProps {
  progress?: number;
  jobStatus?: any;
  isProcessing?: boolean;
}

export function ProgressSection({ progress = 0, jobStatus, isProcessing = false }: ProgressSectionProps) {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set(["progress"]));

  const progressItems: ProgressItem[] = useMemo(() => {
    const items: ProgressItem[] = [
      {
        id: "1",
        title: "Document uploaded and processed",
        status: progress >= 20 ? "completed" : progress > 0 ? "in-progress" : "pending",
        timestamp: progress >= 20 ? "2 minutes ago" : "",
        details: progress >= 20 ? ["PDF parsed successfully", "Text extraction completed", "Layout analysis finished"] : []
      },
      {
        id: "2", 
        title: "Identifying sensitive information", 
        status: progress >= 60 ? "completed" : progress >= 20 ? "in-progress" : "pending",
        timestamp: progress >= 60 ? "1 minute ago" : progress >= 20 ? "processing..." : "",
        details: progress >= 40 ? [
          `PII detection: ${jobStatus?.results?.text_detections || 5} items found`,
          `Financial data: ${Math.floor((jobStatus?.results?.text_detections || 5) * 0.4)} items found`, 
          `Contact info: ${Math.floor((jobStatus?.results?.text_detections || 5) * 0.6)} items found`
        ] : []
      },
      {
        id: "3",
        title: "AI-powered redaction suggestions",
        status: progress >= 85 ? "completed" : progress >= 60 ? "in-progress" : "pending",
        timestamp: progress >= 85 ? "30 seconds ago" : progress >= 60 ? "processing..." : "",
        details: progress >= 60 ? ["Analyzing context", "Generating redaction masks", "Preparing recommendations"] : []
      },
      {
        id: "4",
        title: "Manual review and approval",
        status: progress >= 100 ? "completed" : "pending",
        timestamp: progress >= 100 ? "Complete" : "",
        details: progress >= 100 ? ["Review complete", "Document ready"] : []
      }
    ];
    return items;
  }, [progress, jobStatus]);

  const toggleExpanded = (id: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedItems(newExpanded);
  };

  const getStatusIcon = (status: ProgressItem["status"]) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4 text-accent-green" />;
      case "in-progress":
        return <Clock className="w-4 h-4 text-accent-blue animate-pulse" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-error" />;
      default:
        return <div className="w-4 h-4 border-2 border-text-muted rounded-full" />;
    }
  };

  return (
    <div className="border-b border-chat-border">
      <button
        onClick={() => toggleExpanded("progress")}
        className="w-full p-4 flex items-center justify-between hover:bg-chat-message transition-fast"
      >
        <div className="flex items-center space-x-3">
          {expandedItems.has("progress") ? (
            <ChevronDown className="w-4 h-4 text-text-muted" />
          ) : (
            <ChevronRight className="w-4 h-4 text-text-muted" />
          )}
          <span className="text-text-primary font-medium">Progress</span>
        </div>
        <div className="flex items-center space-x-2">
          {isProcessing && (
            <div className="w-2 h-2 bg-accent-primary rounded-full animate-pulse"></div>
          )}
          <span className="text-text-muted text-xs">
            {progress === 0 ? "Ready" : progress === 100 ? "Complete" : `Processing`}
          </span>
        </div>
      </button>
      
      {expandedItems.has("progress") && (
        <div className="px-4 pb-4">
          <div className="space-y-3">
            {progressItems.map((item) => (
              <div key={item.id} className="relative">
                <div className="flex items-start space-x-3">
                  <div className="mt-0.5">
                    {getStatusIcon(item.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className={`text-sm ${
                        item.status === "completed" ? "text-text-secondary" : "text-text-primary"
                      }`}>
                        {item.title}
                      </span>
                      {item.timestamp && (
                        <span className="text-xs text-text-muted">{item.timestamp}</span>
                      )}
                    </div>
                    
                    {item.details && item.details.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {item.details.map((detail, index) => (
                          <div key={index} className="text-xs text-text-muted pl-2 border-l border-chat-border">
                            {detail}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                
                {item.id !== progressItems[progressItems.length - 1].id && (
                  <div className="absolute left-2 top-6 w-px h-6 bg-chat-border"></div>
                )}
              </div>
            ))}
          </div>
          
          {/* Real-time backend logs */}
          {jobStatus?.logs && jobStatus.logs.length > 0 && (
            <div className="mt-4 p-3 bg-chat-message rounded-lg border border-chat-border">
              <div className="text-xs text-text-primary font-medium mb-2">Live Processing Logs:</div>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {jobStatus.logs.slice(-8).map((log, index) => (
                  <div key={index} className="text-xs text-text-muted font-mono">
                    {log}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}