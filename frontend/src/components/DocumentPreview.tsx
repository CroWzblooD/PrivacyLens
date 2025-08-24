import { ZoomIn, ZoomOut, RotateCw, Download, Search, Eye, EyeOff, Upload, FileText, ExternalLink } from "lucide-react";
import { useState, useRef, useMemo, useEffect } from "react";

interface DocumentPreviewProps {
  selectedFile?: File | null;
  onFileSelect?: (file: File) => void;
  isProcessing?: boolean;
  jobStatus?: any;
  onDownload?: () => void;
}

export function DocumentPreview({ 
  selectedFile, 
  onFileSelect, 
  isProcessing = false, 
  jobStatus, 
  onDownload 
}: DocumentPreviewProps) {
  const [zoom, setZoom] = useState(100);
  const [showRedactions, setShowRedactions] = useState(true);
  const [currentPdfUrl, setCurrentPdfUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const objectRef = useRef<HTMLObjectElement>(null);

  // Memoize URLs to prevent iframe refresh
  const originalPdfUrl = useMemo(() => {
    console.log('🔄 Creating originalPdfUrl for selectedFile:', selectedFile?.name);
    return selectedFile ? URL.createObjectURL(selectedFile) : null;
  }, [selectedFile]);

  const redactedPdfUrl = useMemo(() => {
    if (jobStatus?.job_id && jobStatus?.status === 'completed') {
      // Use a simpler URL without cache busting to maintain iframe stability
      return `http://localhost:8001/api/download/${jobStatus.job_id}`;
    }
    return null;
  }, [jobStatus?.job_id, jobStatus?.status]);

  // Debug jobStatus changes
  useEffect(() => {
    console.log('📊 JobStatus changed:', jobStatus);
    if (jobStatus?.status) {
      console.log('📊 Status:', jobStatus.status);
      console.log('📊 Job ID:', jobStatus.job_id);
      console.log('📊 Progress:', jobStatus.progress);
    }
  }, [jobStatus]);

  // Initialize PDF URL - sync with originalPdfUrl  
  useEffect(() => {
    console.log('🔄 Original PDF URL changed:', originalPdfUrl);
    console.log('🔄 Selected file:', selectedFile?.name, selectedFile?.type);
    if (originalPdfUrl) {
      console.log('✅ Setting current PDF URL to original:', originalPdfUrl);
      setCurrentPdfUrl(originalPdfUrl);
      
      // Show loading indicator
      const loadingDiv = document.getElementById('pdf-loading');
      if (loadingDiv) {
        console.log('📥 Showing loading indicator');
        loadingDiv.style.display = 'flex';
      }
    } else {
      console.log('❌ No original PDF URL, clearing current URL');
      setCurrentPdfUrl(null);
    }
  }, [originalPdfUrl]);

  // Update iframe when redaction completes - SIMPLE approach
  useEffect(() => {
    console.log('🚨 REDACTION UPDATE CHECK - Status:', jobStatus?.status, 'Job ID:', jobStatus?.job_id);
    
        if (jobStatus?.status === 'completed' && jobStatus?.job_id) {
      const previewUrl = `http://localhost:8001/api/preview/${jobStatus.job_id}`;
      
      console.log('🔥 REDACTION COMPLETE: Updating iframe to show redacted PDF:', previewUrl);
      
      // Show loading while switching to redacted PDF
      const loadingDiv = document.getElementById('pdf-loading');
      if (loadingDiv) {
        loadingDiv.style.display = 'flex';
      }
      
      // Update the PDF URL state to trigger re-render with iframe
      setCurrentPdfUrl(previewUrl);
      console.log('✅ PDF URL updated to redacted version:', previewUrl);
    }
  }, [jobStatus?.status, jobStatus?.job_id]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      onFileSelect?.(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files[0] && files[0].type === 'application/pdf') {
      onFileSelect?.(files[0]);
    }
  };

  return (
    <div className="h-screen bg-preview-bg border-l-2 border-preview-border flex flex-col">
      {/* Header */}
      <div className="h-14 border-b border-preview-border flex items-center justify-between px-6" style={{ background: 'var(--preview-header)' }}>
        <div className="flex items-center space-x-3">
          <span className="text-gray-800 font-semibold text-sm">Document Preview</span>
          {selectedFile && (
            <span className="text-gray-600 text-xs font-mono">{selectedFile.name}</span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {selectedFile && (
            <>
              <button 
                className="p-2 hover:bg-gray-100 rounded-lg transition-all duration-200 hover:scale-105"
                title="Search document"
              >
                <Search className="w-4 h-4 text-gray-600" />
              </button>
              
            <button 
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setShowRedactions(!showRedactions);
                }}
              className={`p-2 rounded-lg transition-all duration-200 hover:scale-105 ${
                  showRedactions 
                    ? "bg-gradient-to-r from-accent-primary to-accent-secondary text-white shadow-medium glow" 
                  : "hover:bg-gray-100 text-gray-600"
              }`}
                title={showRedactions ? "Hide redactions" : "Show redactions"}
            >
                {showRedactions ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>
              
          <div className="w-px h-4 bg-gray-300 mx-2"></div>
              
          <button 
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setZoom(Math.max(25, zoom - 25));
            }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-all duration-200 hover:scale-105"
                title="Zoom out"
          >
            <ZoomOut className="w-4 h-4 text-gray-600" />
          </button>
              
              <span className="text-xs text-gray-600 min-w-[3rem] text-center font-mono font-semibold bg-gray-100 px-2 py-1 rounded">
                {zoom}%
              </span>
              
          <button 
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setZoom(Math.min(200, zoom + 25));
            }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-all duration-200 hover:scale-105"
                title="Zoom in"
          >
            <ZoomIn className="w-4 h-4 text-gray-600" />
          </button>
              
              <button 
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  console.log('🔄🔄🔄 MANUAL REFRESH TRIGGERED 🔄🔄🔄');
                  
                                      // Manual refresh - iframe update
                    if (iframeRef.current) {
                      let targetUrl = '';
                      if (jobStatus?.status === 'completed' && jobStatus?.job_id) {
                        targetUrl = `http://localhost:8001/api/v1/download/${jobStatus.job_id}`;
                        console.log('🔄 Manual: Refreshing to redacted PDF');
                      } else if (originalPdfUrl) {
                        targetUrl = originalPdfUrl;
                        console.log('🔄 Manual: Refreshing to original PDF');
                      }
                      
                      if (targetUrl) {
                        const cacheBuster = `?manual=${Date.now()}`;
                        const finalUrl = targetUrl + cacheBuster + '#toolbar=1&navpanes=0&scrollbar=0&view=FitH';
                        console.log('🔄🔄🔄 MANUAL REFRESH:', finalUrl);
                        iframeRef.current.src = finalUrl;
                      }
                    }
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-all duration-200 hover:scale-105"
                title="Force refresh PDF viewer"
              >
                <RotateCw className="w-4 h-4 text-gray-600" />
              </button>

              {/* View Redacted PDF Button - Shows when processing is complete */}
              {jobStatus?.status === 'completed' && jobStatus?.job_id && (
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const redactedUrl = `http://localhost:8001/api/v1/download/${jobStatus.job_id}?view=${Date.now()}`;
                    console.log('🔗 Opening redacted PDF in new tab:', redactedUrl);
                    window.open(redactedUrl, '_blank');
                  }}
                  className="p-2 hover:bg-green-100 rounded-lg transition-all duration-200 hover:scale-105 bg-green-50"
                  title="View Redacted PDF in New Tab"
                >
                  <ExternalLink className="w-4 h-4 text-green-600" />
                </button>
              )}
              
              <button 
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  
                  // Don't update iframe on download - just trigger download
                  console.log('📥 Download button clicked');
                  
                  // Then trigger download
                  if (onDownload) {
                    onDownload();
                  }
                }}
                disabled={!jobStatus?.status || jobStatus.status !== 'completed'}
                className={`p-2 rounded-lg transition-all duration-200 hover:scale-105 ${
                  jobStatus?.status === 'completed'
                    ? "bg-gradient-to-r from-success to-accent-primary text-white shadow-medium glow hover:glow-strong"
                    : "bg-gray-100 text-gray-400 cursor-not-allowed"
                }`}
                title={jobStatus?.status === 'completed' ? "Download protected document" : "Processing required"}
              >
                <Download className="w-4 h-4" />
            </button>
            </>
          )}
        </div>
      </div>
      
      {/* Document Viewer */}
      <div className="flex-1 overflow-auto bg-gray-50 p-6">
        {!selectedFile ? (
          // Simple Upload Area
          <div 
            className="h-full border-2 border-dashed border-gray-300 rounded-xl flex flex-col items-center justify-center cursor-pointer hover:border-orange-500 hover:bg-orange-50 transition-all duration-200"
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-orange-100 rounded-full flex items-center justify-center">
                <Upload className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Upload your PDF</h3>
              <p className="text-gray-500 mb-4">Drag and drop your file here, or click to browse</p>
              <div className="px-4 py-2 bg-orange-600 text-white rounded-lg text-sm hover:bg-orange-700 transition-colors">
                Choose File
              </div>
              </div>
              
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
                ) : (
          // Real PDF Preview
          <div className="h-full">
                        <div
              className="bg-white shadow-lg rounded-lg border border-gray-200 h-full overflow-auto"
              style={{ transform: `scale(${zoom / 100})`, transformOrigin: "top center" }}
            >
              <div className="w-full h-full">
                {/* PDF viewer with proper blob URL handling */}
                {currentPdfUrl ? (
                  <div className="w-full h-full relative">
                    {/* Universal iframe PDF viewer */}
                    <iframe
                      ref={iframeRef}
                      src={currentPdfUrl}
                      className="w-full h-full border-0"
                      style={{ 
                        minHeight: '600px',
                        width: '100%',
                        height: '100%',
                        backgroundColor: '#ffffff',
                        border: 'none'
                      }}
                      title={`PDF Document Viewer - ${currentPdfUrl?.substring(0, 50)}...`}
                      allowFullScreen
                      onLoad={() => {
                        console.log('📄 PDF iframe loaded successfully with URL:', currentPdfUrl);
                        const loadingDiv = document.getElementById('pdf-loading');
                        if (loadingDiv) {
                          setTimeout(() => {
                            if (loadingDiv) {
                              loadingDiv.style.display = 'none';
                            }
                          }, 1000); // Wait 1 second before hiding loading
                        }
                      }}
                      onError={(e) => {
                        console.error('❌ PDF iframe failed to load', e);
                        console.error('❌ Failed URL was:', currentPdfUrl);
                        const loadingDiv = document.getElementById('pdf-loading');
                        if (loadingDiv) {
                          loadingDiv.style.display = 'none';
                        }
                      }}
                    />
                    
                    {/* Loading indicator */}
                    <div 
                      id="pdf-loading"
                      className="absolute inset-0 bg-white border border-gray-200 rounded-lg flex items-center justify-center z-10"
                      style={{ display: 'flex' }}
                    >
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                        <p className="text-gray-600">Loading PDF...</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  // Upload placeholder when no file
                  <div className="flex items-center justify-center h-full text-gray-500 bg-gray-50">
                    <div className="text-center">
                      <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                      <p className="text-lg font-medium">PDF Preview</p>
                      <p className="text-sm">Your PDF will appear here after upload</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Status Bar */}
      <div className="h-10 bg-white border-t border-gray-200 flex items-center justify-between px-6 text-xs">
        <div className="flex items-center space-x-4">
          {selectedFile ? (
            <>
          <span className="text-gray-600 font-mono">Page 1 of 1</span>
          <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  jobStatus?.status === 'completed' 
                    ? (showRedactions ? 'bg-red-500' : 'bg-green-500')
                    : 'bg-amber-500 animate-pulse'
                }`}></div>
                <span className="text-gray-600 font-medium">
                  {jobStatus?.status === 'completed'
                    ? (showRedactions ? "Redactions visible" : "Protected document")
                    : isProcessing
                    ? "Processing..."
                    : "Ready for processing"
                  }
                </span>
              </div>
              {jobStatus?.results?.redactions_applied > 0 && (
                <div className="flex items-center space-x-2">
                  <span className="text-accent-primary font-semibold">
                    {jobStatus.results.redactions_applied} items protected
                  </span>
          </div>
              )}
            </>
          ) : (
            <span className="text-gray-500 font-medium">No document selected</span>
          )}
        </div>
        <div className="flex items-center space-x-4">
          {selectedFile && (
        <span className="text-gray-500 font-mono">Zoom: {zoom}%</span>
          )}
          <span className="text-gray-400 font-mono text-xs">PrivacyLens v2.0</span>
        </div>
      </div>
    </div>
  );
}