import { useState, useRef, useEffect } from "react";
import { Sidebar } from "@/components/Sidebar";
import { ChatHeader } from "@/components/ChatHeader";
import { ChatMessage } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { DocumentPreview } from "@/components/DocumentPreview";
import { ProgressSection } from "@/components/ProgressSection";

interface ChatMsg {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: string;
  status?: 'pending' | 'completed' | 'error' | 'in-progress';
  expandable?: boolean;
  files?: string[];
}

interface JobStatus {
  job_id: string;
  status: string;
  progress: number;
  logs: string[];
  filename?: string;
  results?: any;
}

const Index = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [messages, setMessages] = useState<ChatMsg[]>([
    {
      id: '1',
      type: 'agent',
      content: 'Hello! I\'m your AI assistant for document protection. Upload a PDF and I\'ll help you detect and redact sensitive information.',
      timestamp: '5 minutes ago',
      status: 'completed'
    }
  ]);
  const [jobStatus, setJobStatus] = useState<JobStatus>({
    job_id: '',
    status: 'idle',
    progress: 0,
    logs: []
  });
  
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addMessage = (type: ChatMsg['type'], content: string, status?: ChatMsg['status'], options?: Partial<ChatMsg>) => {
    const newMessage: ChatMsg = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type,
      content,
      timestamp: new Date().toLocaleTimeString(),
      status,
      ...options
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const updateLastMessage = (updates: Partial<ChatMsg>) => {
    setMessages(prev => prev.map((msg, index) => 
      index === prev.length - 1 ? { ...msg, ...updates } : msg
    ));
  };

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    addMessage('user', `Uploaded: ${file.name}`, 'completed');
    addMessage('agent', 'Perfect! I can see your PDF. I can now redact specific information based on your preferences. Try commands like:\n\n• "start" - Hide all personal information\n• "hide only names" - Hide just names\n• "hide phone numbers and addresses" - Hide specific types\n• "hide name ASHISH" - Hide specific names\n\nWhat would you like me to redact?', 'completed');
  };

  const handleSendMessage = (message: string) => {
    addMessage('user', message, 'completed');
    
    const msg = message.toLowerCase().trim();
    
    // Check for processing trigger words
    if (msg.includes('start') || msg.includes('yes') || msg.includes('begin') || 
        msg.includes('process') || msg.includes('redaction') || msg.includes('analyze') ||
        msg.includes('hide') || msg.includes('redact')) {
      if (selectedFile) {
        // Use the user's message as the redaction prompt
        let redactionPrompt = message;
        
        // If it's a generic start command, use default
        if (msg.includes('start') || msg.includes('yes') || msg.includes('begin') || msg.includes('process')) {
          redactionPrompt = 'hide all personal information';
        }
        
        addMessage('agent', `🚀 Starting redaction with preferences: "${redactionPrompt}"`, 'in-progress');
        startProcessing(redactionPrompt);
      } else {
        addMessage('agent', 'Please upload a PDF document first before starting the redaction process.', 'error');
      }
    } else if (msg.includes('upload') || msg.includes('file')) {
      addMessage('agent', 'You can drag and drop your PDF file on the right side, or click the upload area.', 'completed');
    } else {
      addMessage('agent', 'I understand. Feel free to upload a PDF and I\'ll help protect your sensitive information.', 'completed');
    }
  };

  const startProcessing = async (redactionPrompt: string = 'hide all personal information') => {
    if (!selectedFile) {
      addMessage('agent', 'Please upload a PDF document first.', 'error');
      return;
    }

    setIsProcessing(true);
    addMessage('agent', 'Starting document analysis...', 'in-progress');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('redaction_prompt', redactionPrompt);

      console.log('Uploading to MODULAR backend:', 'http://localhost:8001/api/upload');
      console.log('Redaction prompt:', redactionPrompt);
      
      const uploadResponse = await fetch('http://localhost:8001/api/upload', {
        method: 'POST',
        body: formData,
      });

      console.log('Upload response:', uploadResponse.status, uploadResponse.statusText);

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.status} ${uploadResponse.statusText}`);
      }

      const uploadResult = await uploadResponse.json();
      console.log('Upload result:', uploadResult);
      
      if (!uploadResult.job_id) {
        throw new Error('No job ID received from server');
      }

      setJobStatus({
        job_id: uploadResult.job_id,
        status: 'processing',
        progress: 15,
        logs: ['Upload successful', 'Starting analysis...'],
        filename: uploadResult.filename
      });

      updateLastMessage({ 
        status: 'completed', 
        content: 'Upload successful! Starting AI analysis...' 
      });
      
      addMessage('agent', 'Analyzing document for PII detection...', 'in-progress');
      
      startPolling(uploadResult.job_id);

    } catch (error) {
      console.error('Upload error:', error);
      updateLastMessage({ 
        status: 'error', 
        content: `Upload failed: ${error.message}` 
      });
      setIsProcessing(false);
    }
  };

  const startPolling = (jobId: string) => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }

    let lastProgress = 0;
    let hasShownTextExtraction = false;
    let hasShownPIIDetection = false;
    let hasShownRedaction = false;
    let hasShownCompletion = false;

    pollIntervalRef.current = setInterval(async () => {
      try {
        console.log('🔄 Polling status for job:', jobId);
        const statusResponse = await fetch(`http://localhost:8001/api/status/${jobId}`);
        
        if (!statusResponse.ok) {
          throw new Error(`Status check failed: ${statusResponse.statusText}`);
        }

        const statusData = await statusResponse.json();
        console.log('📊 RAW Status data from backend:', statusData);
        console.log('📊 Status field specifically:', statusData.status);
        console.log('📊 Progress field specifically:', statusData.progress);

        setJobStatus(prev => {
          const newJobStatus = {
            ...prev,
            job_id: jobId,
            status: statusData.status,
            progress: statusData.progress || prev.progress,
            logs: statusData.logs || prev.logs,
            results: statusData.results
          };
          
          console.log('📊 Setting jobStatus to:', newJobStatus);
          return newJobStatus;
        });

        // Show real-time processing stages
        if (statusData.progress >= 20 && !hasShownTextExtraction) {
          updateLastMessage({ status: 'completed' });
          addMessage('agent', 'Text extraction complete! Found document content.', 'completed');
          addMessage('agent', 'Running AI PII detection algorithms...', 'in-progress');
          hasShownTextExtraction = true;
        }

        if (statusData.progress >= 60 && !hasShownPIIDetection) {
          updateLastMessage({ status: 'completed' });
          addMessage('agent', 'PII detection complete! Found sensitive information.', 'completed');
          addMessage('agent', 'Applying intelligent redaction...', 'in-progress');
          hasShownPIIDetection = true;
        }

        if (statusData.progress >= 85 && !hasShownRedaction) {
          updateLastMessage({ status: 'completed' });
          addMessage('agent', 'Redaction applied! Document secured.', 'completed');
          hasShownRedaction = true;
        }

        if (statusData.status === 'completed' && !hasShownCompletion) {
          console.log('🎉🎉🎉 COMPLETION DETECTED! 🎉🎉🎉');
          console.log('🎉 Status data when completed:', statusData);
          console.log('🎉 Job ID:', jobId);
          
          updateLastMessage({ status: 'completed' });
          const redactionsCount = statusData.results?.total_detections || statusData.results?.redactions_applied || 0;
          addMessage('agent', `Analysis Complete!\n\nProtected ${redactionsCount} sensitive items. Your secured document is ready for download.`, 'completed');
          hasShownCompletion = true;

          console.log('🛑 STOPPING POLLING - Processing completed');
          console.log('🛑 Job ID that should trigger iframe update:', jobId);
          
          // IMMEDIATELY stop polling when completed
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          setIsProcessing(false);
          
          // Stop this interval execution immediately
          return;
        } else if (statusData.status === 'failed') {
          updateLastMessage({ status: 'error' });
          addMessage('agent', 'Processing failed. Please try again or contact support.', 'error');
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          setIsProcessing(false);
        }

        lastProgress = statusData.progress || lastProgress;

      } catch (error) {
        console.error('Polling error:', error);
        addMessage('agent', 'Connection error. Retrying...', 'error');
      }
    }, 2000); // Poll every 2 seconds
  };

  const handleDownload = async () => {
    if (!jobStatus.job_id) return;

    try {
      const response = await fetch(`http://localhost:8001/api/download/${jobStatus.job_id}`);
      if (!response.ok) throw new Error('Download failed');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `protected_${jobStatus.filename || 'document.pdf'}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      addMessage('agent', 'Download started! Your protected document is ready.', 'completed');
    } catch (error) {
      console.error('Download error:', error);
      addMessage('agent', 'Download failed. Please try again.', 'error');
    }
  };
  return (
    <div className="h-screen bg-background text-foreground flex overflow-hidden">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content - 50% Chat, 50% Preview */}
      <div className="flex-1 flex">
        {/* Chat Section - 50% */}
        <div className="w-1/2" style={{ background: 'var(--chat-bg)' }}>
          <div className="h-full flex flex-col">
            <ChatHeader />
            
            {/* Chat Messages with custom scrollbar */}
            <div className="flex-1 overflow-y-auto scrollbar-thin">
              <ProgressSection 
                progress={jobStatus.progress} 
                jobStatus={jobStatus}
                isProcessing={isProcessing}
              />
              
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  type={message.type}
                  content={message.content}
                  timestamp={message.timestamp}
                  status={message.status}
                  expandable={message.expandable}
                  files={message.files}
                >
                  {message.expandable && (
                    <div className="space-y-3 text-xs">
                      <div className="text-text-primary font-semibold">Analysis Steps:</div>
                      <div className="space-y-1 text-text-secondary">
                        <div>1. Document parsing and text extraction</div>
                        <div>2. PII (Personally Identifiable Information) detection</div>
                        <div>3. Financial data identification</div>
                        <div>4. Contact information scanning</div>
                      </div>
                      
                      {jobStatus.logs.length > 0 && (
                        <div className="mt-4">
                          <div className="text-text-primary font-semibold mb-2">Live Processing Logs:</div>
                          <div className="space-y-1">
                            {jobStatus.logs.slice(-5).map((log, index) => (
                              <div key={index} className="text-text-muted font-mono text-xs">
                                {log}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </ChatMessage>
              ))}
              <div ref={messagesEndRef} />
        </div>

            <ChatInput 
              onSendMessage={handleSendMessage}
              onStartProcessing={startProcessing}
              isProcessing={isProcessing}
              selectedFile={selectedFile}
            />
          </div>
      </div>

        {/* Document Preview - 50% */}
        <div className="w-1/2">
          <DocumentPreview 
            selectedFile={selectedFile}
            onFileSelect={handleFileSelect}
            isProcessing={isProcessing}
            jobStatus={jobStatus}
            onDownload={handleDownload}
          />
      </div>
      </div>
    </div>
  );
};

export default Index;
