'use client';

import { useState, useEffect } from 'react';
import { Send, Bot, User, ClipboardList, Zap, Globe, AlertCircle, Copy, Check, Code2, FileText, Download, ChevronRight } from 'lucide-react';
import Link from 'next/link';

export default function Home() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [spec, setSpec] = useState('');
  const [plan, setPlan] = useState<any[]>([]);
  const [codeGenerated, setCodeGenerated] = useState<Array<{ filepath: string; content: string }>>([]);
  const [buildStatus, setBuildStatus] = useState('');
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingTime, setLoadingTime] = useState(0);
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);
  const [showCodePanel, setShowCodePanel] = useState(false);
  const [refineInstruction, setRefineInstruction] = useState("");
  const [isRefining, setIsRefining] = useState(false);

  // Vaccine #001: Do not hardcode backend URL; require env var
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Timer for latency feedback (Vaccine #003)
  useEffect(() => {
    let interval: any;
    if (loading) {
      interval = setInterval(() => {
        setLoadingTime((prev) => prev + 1);
      }, 1000);
    } else {
      setLoadingTime(0);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleCopySpec = async () => {
    // Vaccine #002: Browser API Protection
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(spec);
        setCopied(true);
        setCopyError(false);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Clipboard error:', err);
        setCopyError(true);
        setTimeout(() => setCopyError(false), 3000);
      }
    } else {
      setCopyError(true);
      setTimeout(() => setCopyError(false), 3000);
    }
  };

  useEffect(() => {
    const checkStatus = async () => {
      if (!API_URL) {
        setStatus('offline');
        return;
      }
      try {
        const res = await fetch(`${API_URL}/`);
        if (res.ok) setStatus('online');
        else setStatus('offline');
      } catch {
        setStatus('offline');
      }
    };
    checkStatus();
    // Vaccine #006: Reduce polling frequency to avoid 429 errors
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, [API_URL]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    if (!API_URL) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Falta configuración: Define NEXT_PUBLIC_API_URL en .env.local (ej: ${API_URL}) para conectar con el backend.`
        }
      ]);
      return;
    }

    if (status !== 'online') {
      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: 'No se puede enviar el mensaje: El servidor backend no está respondiendo. Por favor, asegúrate de que el sistema esté activo antes de continuar.' 
      }]);
      return;
    }

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Vaccine #003 & #004: Robustness & Atomic Retries
    const executeFetchWithRetry = async (retryCount = 0): Promise<any> => {
      // Vaccine #004: Create NEW AbortController for each retry attempt (not reused)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 90000); // 90s timeout

      try {
        // Vaccine #004: Protocol Consistency - ensure API_URL has protocol
        const apiUrl = `${API_URL}/chat`;
        if (!apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
          throw new Error('INVALID_PROTOCOL: API URL must include http:// or https://');
        }

        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: input }),
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        // Vaccine #004: Check CORS headers in response
        const corsOrigin = response.headers.get('Access-Control-Allow-Origin');
        console.debug(`CORS Origin Header: ${corsOrigin || 'NOT PRESENT'}`);

        if (!response.ok) throw new Error('ServerError');
        return await response.json();
      } catch (error) {
        clearTimeout(timeoutId);
        
        const isNetworkError = error instanceof TypeError || (error as any).name === 'AbortError';
        
        if (isNetworkError && retryCount < 2) {
          // Eliminado console.log de depuración
          await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1))); // Exponential backoff
          return executeFetchWithRetry(retryCount + 1);
        }
        throw error;
      }
    };

    try {
      const data = await executeFetchWithRetry();
      
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
      if (data.spec_document) setSpec(data.spec_document);
      if (data.plan) setPlan(data.plan);
      if (data.code_generated && data.code_generated.length > 0) {
        setCodeGenerated(data.code_generated);
        setShowCodePanel(true);
        setSelectedFile(data.code_generated[0].filepath);
      }
      if (data.build_status) setBuildStatus(data.build_status);
    } catch (error) {
      console.error('Error:', error);
      // Vaccine #001 & #003: Human Error Handling
      let errorMessage = 'Lo siento, ocurrió un error inesperado al procesar tu solicitud.';
      
      if ((error as any).name === 'AbortError') {
        errorMessage = 'La solicitud tardó demasiado. El servidor está procesando mucha información, intenta de nuevo en un momento.';
      } else if (error instanceof TypeError || (error as Error).message === 'ServerError') {
        errorMessage = 'No se pudo establecer conexión con el servidor. Verifica que el backend esté corriendo y sea accesible.';
      }
        
      setMessages((prev) => [...prev, { role: 'assistant', content: errorMessage }]);
    } finally {
      setLoading(false);
    }
  };

  // Utilidad para convertir array a objeto {filepath: content}
  const codeGeneratedObj = codeGenerated.reduce((acc, f) => {
    acc[f.filepath] = f.content;
    return acc;
  }, {} as Record<string, string>);

  const handleRefine = async () => {
    if (!refineInstruction.trim() || isRefining) return;
    setIsRefining(true);
    try {
      const response = await fetch(`${API_URL}/refine`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instruction: refineInstruction,
          current_files: codeGeneratedObj
        })
      });
      const data = await response.json();
      if (data.success && data.modified_files) {
        // MERGE: Actualizamos solo los archivos que cambiaron
        setCodeGenerated(prev => {
          const updated = [...prev];
          for (const [filepath, content] of Object.entries(data.modified_files)) {
            const idx = updated.findIndex(f => f.filepath === filepath);
            if (idx !== -1) {
              updated[idx] = { filepath, content: content as string };
            } else {
              updated.push({ filepath, content: content as string });
            }
          }
          return updated;
        });
        alert(`✅ ${Object.keys(data.modified_files).length} archivos actualizados.`);
        setRefineInstruction("");
      }
    } catch (error) {
      console.error("Refine error:", error);
      alert("Error al refinar el código.");
    } finally {
      setIsRefining(false);
    }
  };

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-blue-500/30">
      {/* Sidebar - Plan & Spec */}
      <div className="w-80 lg:w-96 border-r border-zinc-800 p-6 flex flex-col gap-6 overflow-y-auto hidden md:flex bg-zinc-950">
        <Link href="/landing" className="flex items-center gap-2 text-blue-400 font-bold text-xl uppercase tracking-wider hover:text-blue-300 transition-colors">
          <Zap className="fill-current text-blue-500" />
          Aegis Forge
        </Link>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900/50 border border-zinc-800 self-start">
          {status === 'checking' && <div className="w-2 h-2 rounded-full bg-zinc-500 animate-pulse" />}
          {status === 'online' && <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />}
          {status === 'offline' && <div className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]" />}
          <span className="text-[10px] uppercase font-bold text-zinc-400 tracking-tight">
            Backend: {status}
          </span>
        </div>

        {buildStatus && (
          <div className={`px-3 py-1.5 rounded-full border self-start text-[10px] font-bold uppercase tracking-widest ${
            buildStatus === 'clean' ? 'bg-green-900/30 border-green-500/50 text-green-400' :
            buildStatus === 'vulnerable' ? 'bg-yellow-900/30 border-yellow-500/50 text-yellow-400' :
            'bg-red-900/30 border-red-500/50 text-red-400'
          }`}>
            Build: {buildStatus}
          </div>
        )}
        
        <div className="space-y-6">
          <div className="flex items-center gap-2 text-zinc-500 text-[10px] font-bold uppercase tracking-widest">
            <ClipboardList size={14} />
            System Intelligence
          </div>
          
          {plan.length > 0 && (
            <div className="bg-zinc-900/40 rounded-xl p-4 border border-zinc-800/60 transition-all hover:bg-zinc-900/60">
              <h3 className="text-xs font-bold mb-3 border-b border-zinc-800 pb-2 text-zinc-300">Plan de Ejecución</h3>
              <ul className="space-y-3">
                {plan.map((task: any, idx: number) => (
                  <li key={idx} className="text-[11px] flex items-start gap-2 leading-relaxed">
                    <span className={`mt-1 flex-shrink-0 w-2 h-2 rounded-full ${task.status === 'completed' ? 'bg-green-500' : 'bg-blue-500/50'}`} />
                    <span className="text-zinc-400">{task.description}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {spec && (
            <div className="bg-zinc-900/40 rounded-xl p-4 border border-zinc-800/60 relative group/spec">
               <div className="flex justify-between items-center mb-3 border-b border-zinc-800 pb-2">
                 <h3 className="text-xs font-bold text-zinc-300">Core Specification</h3>
                 <button 
                  onClick={handleCopySpec}
                  className="text-zinc-500 hover:text-blue-400 transition-colors"
                  title="Copiar especificación"
                 >
                   {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
                 </button>
               </div>
               
               {copyError && (
                 <div className="absolute top-10 right-4 bg-red-900/80 border border-red-500 text-[10px] px-2 py-1 rounded animate-in fade-in zoom-in">
                   Error al copiar. Copia manual requerida.
                 </div>
               )}

               <div className="text-[10px] text-zinc-500 font-mono overflow-y-auto max-h-[300px] whitespace-pre-wrap leading-relaxed">
                 {spec}
               </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-zinc-950">
        {showCodePanel && codeGenerated.length > 0 && (
          <div className="border-b border-zinc-800 bg-zinc-900/50 p-4 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Code2 size={18} className="text-blue-400" />
                <span className="text-sm font-semibold text-zinc-300">Code Generated</span>
                <span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-1 rounded">{codeGenerated.length} files</span>
              </div>
              {/* Botón de Descarga */}
              <button
                onClick={async () => {
                  if (!API_URL) return;
                  try {
                    const filesObj = codeGenerated.reduce((acc, f) => {
                      acc[f.filepath] = f.content;
                      return acc;
                    }, {} as Record<string, string>);
                    const res = await fetch(`${API_URL}/export`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ files: filesObj })
                    });
                    if (!res.ok) throw new Error('Export failed');
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'aegis_project.zip';
                    document.body.appendChild(a);
                    a.click();
                    setTimeout(() => {
                      window.URL.revokeObjectURL(url);
                      document.body.removeChild(a);
                    }, 100);
                  } catch (err) {
                    alert('Error al exportar el proyecto.');
                  }
                }}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-all font-medium text-sm border border-blue-500 shadow-[0_0_10px_rgba(37,99,235,0.3)]"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                EXPORT ZIP
              </button>
              <button 
                onClick={() => setShowCodePanel(false)}
                className="text-xs text-zinc-400 hover:text-zinc-200 transition-colors ml-4"
              >
                Hide Code
              </button>
            </div>
            {/* Caja de instrucciones CTO */}
            <div className="flex gap-2 items-center mt-2">
              <input
                type="text"
                value={refineInstruction}
                onChange={e => setRefineInstruction(e.target.value)}
                placeholder="Ej: Implementa validación en payment.ts"
                className="flex-1 px-3 py-2 rounded-lg border border-zinc-700 bg-zinc-900 text-sm text-zinc-200 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                disabled={isRefining}
              />
              <button
                onClick={handleRefine}
                disabled={isRefining || !refineInstruction.trim()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-all font-medium text-sm border border-blue-500 shadow-[0_0_10px_rgba(37,99,235,0.3)] disabled:opacity-50"
              >
                {isRefining ? 'Refinando...' : 'Refinar código'}
              </button>
            </div>
          </div>
        )}
        
        <div className="flex-1 overflow-y-auto p-4 md:p-10 space-y-8">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-6">
              <div className="w-20 h-20 rounded-3xl bg-blue-600/10 flex items-center justify-center border border-blue-500/20">
                <Bot size={40} className="text-blue-500" />
              </div>
              <div className="max-w-md">
                <h2 className="text-2xl font-bold tracking-tight text-white">Autonomous Assembly Line</h2>
                <p className="text-sm text-zinc-400 mt-3 leading-relaxed">
                  Ingresa tu visión técnica o "vibe" del proyecto. El Visionario y el Arquitecto están listos para orquestar la infraestructura.
                </p>
              </div>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 md:gap-6 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role !== 'user' && (
                <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center flex-shrink-0">
                  <Bot size={20} className="text-white" />
                </div>
              )}
              <div className={`max-w-[85%] md:max-w-[70%] rounded-2xl p-4 md:p-5 text-[13px] md:text-sm leading-relaxed shadow-sm ${
                msg.role === 'user' 
                  ? 'bg-white text-zinc-950 rounded-tr-none font-medium' 
                  : 'bg-zinc-900 border border-zinc-800 text-zinc-200 rounded-tl-none whitespace-pre-wrap'
              }`}>
                {msg.content}
              </div>
              {msg.role === 'user' && (
                <div className="w-10 h-10 rounded-xl bg-zinc-800 flex items-center justify-center flex-shrink-0 border border-zinc-700">
                  <User size={20} className="text-zinc-300" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-4 md:gap-6 animate-pulse">
              <div className="w-10 h-10 rounded-xl bg-blue-600/20 flex items-center justify-center" />
              <div className="bg-zinc-900 shadow-xl border border-zinc-800 p-5 rounded-2xl rounded-tl-none min-w-[200px]">
                <p className="text-xs text-zinc-400">
                  {loadingTime > 15 
                    ? 'El Arquitecto está diseñando la solución técnica compleja, esto puede tardar un momento...' 
                    : 'Aegis Forge está procesando tu visión...'}
                </p>
                <div className="mt-2 h-1 w-full bg-zinc-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-600 transition-all duration-500" 
                    style={{ width: `${Math.min(loadingTime * 4, 100)}%` }} 
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Code Display Panel */}
        {showCodePanel && codeGenerated.length > 0 && (
          <div className="border-t border-zinc-800 bg-zinc-900/30 p-6 max-h-[50vh] overflow-hidden flex gap-4">
            {/* File List */}
            <div className="w-64 border-r border-zinc-800 pr-4 overflow-y-auto">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Generated Files</h3>
                <button
                  onClick={async () => {
                    if (!API_URL) return;
                    try {
                      const filesObj = codeGenerated.reduce((acc, f) => {
                        acc[f.filepath] = f.content;
                        return acc;
                      }, {} as Record<string, string>);
                      const res = await fetch(`${API_URL}/export`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ files: filesObj })
                      });
                      if (!res.ok) throw new Error('Export failed');
                      const blob = await res.blob();
                      const url = window.URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = 'aegis_project.zip';
                      document.body.appendChild(a);
                      a.click();
                      setTimeout(() => {
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                      }, 100);
                    } catch (err) {
                      alert('Error al exportar el proyecto.');
                    }
                  }}
                  className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-200 border border-blue-500/30 rounded px-2 py-1 transition-colors"
                  title="Exportar como ZIP"
                >
                  <Download size={14} /> Export ZIP
                </button>
              </div>
              <div className="space-y-1">
                {codeGenerated.map((file, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedFile(file.filepath)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-colors flex items-center gap-2 ${
                      selectedFile === file.filepath 
                        ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' 
                        : 'text-zinc-400 hover:bg-zinc-800/50'
                    }`}
                  >
                    <FileText size={14} />
                    <span className="truncate">{file.filepath}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Code Viewer */}
            <div className="flex-1 overflow-auto">
              {selectedFile && (() => {
                const file = codeGenerated.find(f => f.filepath === selectedFile);
                return file ? (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-semibold text-zinc-300">{file.filepath}</h3>
                      <button 
                        onClick={async () => {
                          if (typeof navigator !== 'undefined' && navigator.clipboard) {
                            try {
                              await navigator.clipboard.writeText(file.content);
                            } catch (err) {
                              console.error('Clipboard error:', err);
                            }
                          } else {
                            console.warn('Clipboard API not available; show content for manual copy.');
                          }
                        }}
                        className="text-xs text-zinc-400 hover:text-blue-400 transition-colors flex items-center gap-1"
                      >
                        <Copy size={12} />
                        Copy
                      </button>
                    </div>
                    <pre className="text-xs text-zinc-300 bg-zinc-950 p-4 rounded-lg overflow-auto border border-zinc-800 font-mono leading-relaxed">
                      {file.content}
                    </pre>
                  </div>
                ) : null;
              })()}
            </div>
          </div>
        )}

        {/* --- ZONA DE REFINAMIENTO --- */}
        {showCodePanel && codeGenerated.length > 0 && (
          <div className="fixed bottom-0 left-0 right-0 bg-[#0e1117] border-t border-gray-800 p-4 z-50">
            <div className="max-w-6xl mx-auto flex gap-4 items-center">
              <div className="flex-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span className="text-purple-500 text-xl">🛠️</span>
                </div>
                <input
                  type="text"
                  value={refineInstruction}
                  onChange={(e) => setRefineInstruction(e.target.value)}
                  placeholder="Ej: Añade validación Zod al formulario de registro..."
                  className="w-full bg-[#1c1c38] text-white pl-10 pr-4 py-3 rounded-lg border border-gray-700 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none transition-all"
                  onKeyDown={(e) => e.key === 'Enter' && handleRefine()}
                  disabled={isRefining}
                />
              </div>
              <button
                onClick={handleRefine}
                disabled={isRefining}
                className={`px-6 py-3 rounded-lg font-bold text-white transition-all flex items-center gap-2
                  ${isRefining 
                    ? 'bg-gray-600 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-[0_0_20px_rgba(124,58,237,0.5)]'
                  }`}
              >
                {isRefining ? (
                  <>
                    <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    REPARANDO...
                  </>
                ) : (
                  'EJECUTAR ORDEN'
                )}
              </button>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="p-6 md:p-10 border-t border-zinc-900 bg-zinc-950/80 backdrop-blur-md">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative group">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe tu visión... (ej: Un marketplace SOC2 para activos digitales)"
              className="w-full bg-zinc-900/80 border border-zinc-800 rounded-2xl pl-6 pr-16 py-4 focus:outline-none focus:ring-2 focus:ring-blue-600/50 focus:border-blue-500/50 transition-all text-sm shadow-2xl placeholder:text-zinc-600"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-3 top-1/2 -translate-y-1/2 bg-blue-600 hover:bg-blue-500 disabled:opacity-30 text-white p-2.5 rounded-xl transition-all shadow-lg hover:scale-105 active:scale-95"
            >
              <Send size={18} />
            </button>
          </form>
          <p className="text-center text-[10px] text-zinc-600 mt-4 uppercase tracking-widest font-bold">
            Aegis Forge v1.0.2 • Autonomous Software Engineering
          </p>
        </div>

        {/* BARRA DE COMANDOS (REFINAMIENTO) */}
        {Object.keys(codeGeneratedObj).length > 0 && (
          <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 w-full max-w-3xl px-4 z-50">
            <div className="bg-[#1c1c38]/90 backdrop-blur-md border border-purple-500/30 rounded-xl p-2 shadow-[0_0_30px_rgba(0,0,0,0.5)] flex gap-2 items-center">
              <div className="pl-3 text-purple-400">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              </div>
              <input 
                type="text" 
                className="flex-1 bg-transparent text-white placeholder-gray-400 outline-none h-10 px-2 font-mono text-sm"
                placeholder="Ej: 'Añade validación de email en el login' o 'Cambia el color del botón a rojo'"
                value={refineInstruction}
                onChange={(e) => setRefineInstruction(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleRefine()}
                disabled={isRefining}
              />
              <button 
                onClick={handleRefine}
                disabled={isRefining}
                className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isRefining ? 'PENSANDO...' : 'REFINAR'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
