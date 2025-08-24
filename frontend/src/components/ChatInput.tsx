import { Send, Paperclip, Mic } from "lucide-react";
import { useState } from "react";

interface ChatInputProps {
  onSendMessage?: (message: string) => void;
  onStartProcessing?: () => void;
  isProcessing?: boolean;
  selectedFile?: File | null;
}

export function ChatInput({ 
  onSendMessage, 
  onStartProcessing, 
  isProcessing = false, 
  selectedFile 
}: ChatInputProps) {
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      const msg = message.toLowerCase();
      
      // Always send the message to chat
      onSendMessage?.(message);
      
      // ChatInput doesn't need to handle processing - that's done by the handleSendMessage
      
      setMessage("");
    }
  };

  return (
    <div className="p-6 border-t border-chat-border/50" style={{ background: 'var(--chat-panel)' }}>
      <form onSubmit={handleSubmit} className="flex items-end space-x-4">
        <div className="flex-1">
          <div className="relative glass-panel rounded-xl overflow-hidden">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask Assistant, use @ to include specific files..."
              className="w-full bg-transparent border-0 px-5 py-4 pr-16 text-text-primary placeholder-text-muted resize-none focus:outline-none font-medium"
              style={{ background: 'var(--chat-input)' }}
              rows={1}
            />
            <div className="absolute right-4 bottom-4 flex items-center space-x-3">
              <button
                type="button"
                className="text-text-muted hover:text-accent-primary transition-all duration-200 hover:scale-110"
              >
                <Paperclip className="w-5 h-5" />
              </button>
              <button
                type="button"
                className="text-text-muted hover:text-accent-primary transition-all duration-200 hover:scale-110"
              >
                <Mic className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={!message.trim() || isProcessing}
          className="w-12 h-12 bg-gradient-to-br from-accent-primary to-accent-secondary hover:from-accent-secondary hover:to-accent-primary disabled:from-gray-600 disabled:to-gray-700 disabled:text-gray-400 text-white rounded-xl flex items-center justify-center transition-all duration-300 hover:scale-105 glow-strong disabled:shadow-none group"
        >
          <Send className="w-5 h-5 group-hover:scale-110 transition-transform duration-200" />
        </button>
      </form>
      
      <div className="mt-3 flex items-center justify-between text-xs">
        <div className="text-text-muted font-mono">
          Have feedback?{" "}
          <button className="text-accent-primary hover:text-accent-secondary transition-colors duration-200 font-medium">
            Let us know
          </button>
        </div>
        <div className="text-text-muted font-mono">
          Ctrl + Enter to send
        </div>
      </div>
    </div>
  );
}