import React, { useState, useRef, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import { ChatMessage, KnowledgeDocument } from '../../types';
import { demoKnowledgeDocs } from '../../data/demoData';
import { RAGAssistantService } from '../../services/apiAdapters';
import {
  Bot,
  Send,
  Sparkles,
  Search,
  Plus,
  Trash2,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  BookOpen,
  FileText,
  Upload,
  Info,
  ExternalLink,
  MessageSquare,
  ShieldCheck,
  ChevronRight,
  Database,
  ArrowRight
} from 'lucide-react';

export const AIAssistantPage: React.FC = () => {
  const { profile, activeFarm, showToast } = useApp();
  const [searchParams] = useSearchParams();

  const [activeTab, setActiveTab] = useState<'chat' | 'knowledge'>('chat');

  // Messages state
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'msg-init-1',
      sender: 'assistant',
      content: `Namaste, **${profile.name}**! I am your **KisanMitra RAG Agricultural Knowledge Assistant**.\n\nI am grounded in verified agronomic guidelines from **GBPUAT Pantnagar**, **ICAR-VPKAS Almora**, and state department advisories.\n\nI have active context of your farm: **${activeFarm.name}** in **${activeFarm.district}, Uttarakhand** (${activeFarm.soilType} soil, pH ${activeFarm.soilPh}). How can I assist your farming decisions today?`,
      timestamp: '09:00 AM',
      citations: [
        {
          title: 'Uttarakhand Kharif Season Agricultural & Fisheries Advisory',
          source: 'Directorate of Extension Education, GBPUAT Pantnagar (p. 1, 2020-05-02)'
        }
      ],
      suggestedFollowUps: [
        'What are the sowing dates and seed rates for Rice in Uttarakhand?',
        'What are the recommended varieties for Mandua and Jhangora?',
        'How to manage fish pond water and organic manuring?',
        'What are the sowing windows for Hill vs Plain Maize?'
      ]
    }
  ]);

  const [inputQuery, setInputQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Knowledge base state
  const [documents, setDocuments] = useState<KnowledgeDocument[]>(demoKnowledgeDocs);
  const [isUploadDocOpen, setIsUploadDocOpen] = useState(false);
  const [newDocTitle, setNewDocTitle] = useState('');
  const [newDocCategory, setNewDocCategory] = useState<KnowledgeDocument['category']>('Crop Advisory');

  // Engine status
  const [engineStatus, setEngineStatus] = useState<{ provider: string; isReady: boolean }>({
    provider: 'Google Gemini (gemini-3.8-flash)',
    isReady: true
  });

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Load knowledge documents & check RAG health on mount
  useEffect(() => {
    let isMounted = true;
    RAGAssistantService.getKnowledgeDocuments()
      .then((docs) => {
        if (isMounted && docs && docs.length > 0) {
          setDocuments(docs);
        }
      })
      .catch(() => {});

    RAGAssistantService.checkHealth()
      .then((h) => {
        if (isMounted && h) {
          setEngineStatus({
            provider: h.llm_provider || 'Google Gemini',
            isReady: h.status === 'healthy'
          });
        }
      })
      .catch(() => {});

    return () => {
      isMounted = false;
    };
  }, []);

  // Pre-fill query if present in URL
  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      handleSendQuery(q);
    }
  }, [searchParams]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSendQuery = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || isTyping) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setIsTyping(true);

    try {
      const response = await RAGAssistantService.queryAgriculturalKnowledge(textToSend, {
        farmLocation: `${activeFarm.village}, ${activeFarm.district}`,
        soilType: activeFarm.soilType,
        cropType: activeFarm.previousCrops[0],
      });

      setMessages(prev => [...prev, response]);
    } catch (err) {
      showToast('Error querying RAG assistant service.', 'error');
    } finally {
      setIsTyping(false);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
    showToast('Copied answer to clipboard.', 'info');
  };

  const handleUploadDocument = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDocTitle.trim()) return;

    const newDoc: KnowledgeDocument = {
      id: `doc-${Date.now()}`,
      title: newDocTitle,
      category: newDocCategory,
      cropTag: 'General Hill Crops',
      language: 'English & Hindi',
      region: activeFarm.state,
      fileSize: '3.4 MB',
      uploadDate: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
      status: 'Indexed & Ready',
      vectorChunksCount: 184
    };

    setDocuments([newDoc, ...documents]);
    setIsUploadDocOpen(false);
    setNewDocTitle('');
    showToast(`Indexed "${newDoc.title}" into vector embeddings repository!`, 'success');
  };

  const clearChat = () => {
    setMessages([messages[0]]);
    showToast('Conversation cleared.', 'info');
  };

  return (
    <div className="space-y-6 pb-16 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-charcoal-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-xs font-bold text-forest-800 mb-1.5">
            <Bot className="w-3.5 h-3.5 text-saffron-500" />
            <span>Retrieval-Augmented Generation (RAG)</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
            Agricultural AI Knowledge Assistant
          </h1>
          <p className="text-xs text-charcoal-400 mt-1">
            Grounded in peer-reviewed ICAR publications, GBPUAT extension manuals, and government scheme compendiums
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex items-center p-1 bg-charcoal-100 rounded-2xl text-xs font-bold">
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 ${
              activeTab === 'chat' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Chat Workspace</span>
          </button>
          <button
            onClick={() => setActiveTab('knowledge')}
            className={`px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 ${
              activeTab === 'knowledge' ? 'bg-white text-forest-900 shadow-sm' : 'text-charcoal-600 hover:text-forest-900'
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span>Knowledge Base ({documents.length})</span>
          </button>
        </div>
      </div>

      {activeTab === 'chat' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Context & Suggested Prompts Sidebar (4 Cols) */}
          <div className="lg:col-span-4 space-y-4">
            {/* Active Farmer Context Bar */}
            <div className="p-5 rounded-3xl bg-forest-950 text-white shadow-soft space-y-3 text-xs">
              <div className="flex items-center gap-2 text-saffron-300 font-bold">
                <ShieldCheck className="w-4 h-4" />
                <span>Active Agronomic Context</span>
              </div>
              <p className="text-forest-200 text-[11px] leading-relaxed">
                Queries automatically inject your registered soil, elevation, and location parameters:
              </p>
              <div className="space-y-1.5 pt-2 border-t border-forest-800 text-[11px] text-forest-200">
                <div className="flex justify-between">
                  <span className="text-forest-400">Farm:</span>
                  <strong className="text-white">{activeFarm.name}</strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-forest-400">Location:</span>
                  <strong className="text-white">{activeFarm.district}, {activeFarm.elevation}m</strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-forest-400">Soil:</span>
                  <strong className="text-white">{activeFarm.soilType} (pH {activeFarm.soilPh})</strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-forest-400">Nutrients:</span>
                  <strong className="text-white">N:{activeFarm.nitrogen} P:{activeFarm.phosphorus} K:{activeFarm.potassium}</strong>
                </div>
              </div>
            </div>

            {/* Suggested Prompt Chips */}
            <div className="p-5 rounded-3xl bg-white border border-charcoal-100 shadow-soft space-y-3">
              <h4 className="text-xs font-extrabold text-forest-900 uppercase tracking-wider">
                Common Farmer Inquiries
              </h4>
              <div className="space-y-1.5">
                {[
                  'Which crop is suitable for my soil?',
                  'How can I improve nitrogen deficiency?',
                  'What is the correct sowing season for wheat in Uttarakhand?',
                  'How can I manage fungal infection in tomato?',
                  'What are the best irrigation practices?',
                  'Which government schemes are available for farmers?'
                ].map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendQuery(q)}
                    className="w-full text-left p-2.5 rounded-xl bg-charcoal-50 hover:bg-forest-50 border border-charcoal-100 hover:border-forest-200 text-xs font-semibold text-charcoal-700 hover:text-forest-900 transition-all flex items-center justify-between group"
                  >
                    <span className="truncate mr-2">{q}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-charcoal-400 group-hover:text-forest-800 shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Modern Chat Workspace (8 Cols) */}
          <div className="lg:col-span-8 rounded-3xl bg-white border border-charcoal-100 shadow-soft flex flex-col h-[75vh]">
            {/* Chat Topbar */}
            <div className="p-4 px-6 border-b border-charcoal-100 flex items-center justify-between bg-charcoal-50/50">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-forest-900 text-saffron-400 flex items-center justify-center">
                  <Bot className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center gap-1.5">
                    <h3 className="text-xs font-bold text-forest-900">KisanMitra Agricultural AI Advisor</h3>
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-100 text-amber-900 border border-amber-300">
                      Gemini RAG
                    </span>
                  </div>
                  <span className="text-[10px] text-emerald-700 font-semibold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    ChromaDB Vector Store & {engineStatus.provider} Connected
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={clearChat}
                  className="px-2.5 py-1 rounded-xl text-xs font-semibold text-charcoal-600 hover:text-forest-900 hover:bg-charcoal-100 transition-colors flex items-center gap-1 border border-charcoal-200"
                  title="Start new consultation"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">New Chat</span>
                </button>
                <button
                  onClick={clearChat}
                  className="p-1.5 rounded-lg text-charcoal-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                  title="Clear conversation"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Chat Messages Scrollable Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-5">
              {messages.map((msg) => {
                const isAssistant = msg.sender === 'assistant';
                return (
                  <div
                    key={msg.id}
                    className={`flex items-start gap-3 ${isAssistant ? '' : 'flex-row-reverse'}`}
                  >
                    <div
                      className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${
                        isAssistant
                          ? 'bg-forest-900 text-saffron-400'
                          : 'bg-forest-700 text-white'
                      }`}
                    >
                      {isAssistant ? <Bot className="w-4 h-4" /> : 'You'}
                    </div>

                    <div className={`max-w-[85%] space-y-2`}>
                      <div
                        className={`p-4 rounded-2xl text-xs leading-relaxed ${
                          isAssistant
                            ? 'bg-kisan-bg border border-charcoal-100 text-charcoal-900 whitespace-pre-wrap'
                            : 'bg-forest-900 text-white whitespace-pre-wrap'
                        }`}
                      >
                        {msg.content}
                      </div>

                      {/* RAG Citations Box */}
                      {isAssistant && msg.citations && msg.citations.length > 0 && (
                        <div className="p-3.5 rounded-2xl bg-forest-50/80 border border-forest-200/90 text-[11px] space-y-2">
                          <p className="font-bold text-forest-950 flex items-center justify-between">
                            <span className="flex items-center gap-1.5">
                              <BookOpen className="w-3.5 h-3.5 text-forest-700" />
                              <span>Verified Agricultural Evidence Citations:</span>
                            </span>
                            <span className="text-[10px] font-semibold text-forest-700">
                              GBPUAT Pantnagar Repository
                            </span>
                          </p>
                          <div className="space-y-1.5">
                            {msg.citations.map((c, i) => (
                              <div key={i} className="p-2.5 rounded-xl bg-white/90 border border-forest-100 text-charcoal-700 space-y-1">
                                <div className="flex items-start justify-between gap-2">
                                  <span className="font-bold text-forest-950">
                                    {c.sourceId ? `[${c.sourceId}]` : `[${i + 1}]`} {c.title}
                                  </span>
                                  {c.page && (
                                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-forest-100 text-forest-800 shrink-0">
                                      {c.page}
                                    </span>
                                  )}
                                </div>
                                <p className="text-[10px] text-charcoal-500 italic">
                                  {c.source}
                                </p>
                                {c.snippet && (
                                  <p className="text-[10px] text-charcoal-600 pt-0.5 border-t border-forest-50">
                                    "{c.snippet}"
                                  </p>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Suggested Follow-Ups */}
                      {isAssistant && msg.suggestedFollowUps && (
                        <div className="pt-1 flex flex-wrap gap-1.5">
                          {msg.suggestedFollowUps.map((fu, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleSendQuery(fu)}
                              className="px-2.5 py-1 rounded-lg bg-charcoal-50 hover:bg-forest-50 border border-charcoal-200 text-[11px] font-semibold text-charcoal-700 hover:text-forest-900 transition-colors"
                            >
                              {fu}
                            </button>
                          ))}
                        </div>
                      )}

                      {/* Assistant Actions Bar */}
                      {isAssistant && (
                        <div className="flex items-center gap-3 text-charcoal-400 text-[11px] px-1">
                          <span>{msg.timestamp}</span>
                          <button
                            onClick={() => handleCopy(msg.id, msg.content)}
                            className="hover:text-forest-900 flex items-center gap-1"
                          >
                            {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                            <span>{copiedId === msg.id ? 'Copied' : 'Copy'}</span>
                          </button>
                          <button
                            onClick={() => showToast('Thank you for your feedback!', 'success')}
                            className="hover:text-forest-900 flex items-center gap-1"
                          >
                            <ThumbsUp className="w-3.5 h-3.5" />
                            <span>Helpful</span>
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}

              {isTyping && (
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-forest-900 text-saffron-400 flex items-center justify-center text-xs font-bold">
                    <Bot className="w-4 h-4 animate-spin-slow" />
                  </div>
                  <div className="p-3.5 rounded-2xl bg-charcoal-50 border border-charcoal-100 flex items-center gap-2 text-xs text-charcoal-500">
                    <span className="w-2 h-2 rounded-full bg-forest-600 animate-bounce" />
                    <span className="w-2 h-2 rounded-full bg-forest-600 animate-bounce delay-150" />
                    <span className="w-2 h-2 rounded-full bg-forest-600 animate-bounce delay-300" />
                    <span className="ml-2 font-medium">Retrieving verified agricultural citations...</span>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Chat Input Bar */}
            <div className="p-4 border-t border-charcoal-100 bg-white">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendQuery();
                }}
                className="flex items-center gap-2"
              >
                <input
                  type="text"
                  placeholder="Ask any question about crops, fertilizers, pest remedies, or government schemes..."
                  value={inputQuery}
                  onChange={(e) => setInputQuery(e.target.value)}
                  className="flex-1 px-4 py-3 rounded-2xl border border-charcoal-200 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-forest-600 bg-charcoal-50/60 focus:bg-white"
                />
                <button
                  type="submit"
                  disabled={!inputQuery.trim() || isTyping}
                  className={`p-3 rounded-2xl font-bold shadow-md transition-all ${
                    !inputQuery.trim() || isTyping
                      ? 'bg-charcoal-200 text-charcoal-400 cursor-not-allowed'
                      : 'bg-forest-900 hover:bg-forest-800 text-saffron-400 active:scale-95'
                  }`}
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </div>
        </div>
      ) : (
        /* ================= TAB 2: KNOWLEDGE BASE REPOSITORY ================= */
        <div className="rounded-3xl bg-white border border-charcoal-100 p-6 sm:p-8 shadow-soft space-y-6 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-charcoal-100 gap-3">
            <div>
              <h3 className="text-base font-extrabold text-forest-900">
                Indexed Agricultural Document Repository
              </h3>
              <p className="text-xs text-charcoal-400">
                Vectorized PDF & DOCX research publications referenced by the RAG Assistant
              </p>
            </div>

            <button
              onClick={() => setIsUploadDocOpen(true)}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-forest-900 hover:bg-forest-800 text-white transition-all flex items-center gap-1.5 shadow-sm"
            >
              <Upload className="w-3.5 h-3.5 text-saffron-400" />
              <span>Upload Agronomic Document</span>
            </button>
          </div>

          {/* Upload Modal */}
          {isUploadDocOpen && (
            <div className="p-5 rounded-2xl bg-forest-50/70 border border-forest-200 text-xs space-y-3 animate-fade-in">
              <h4 className="font-bold text-forest-900">Add New Document to Vector Store</h4>
              <form onSubmit={handleUploadDocument} className="space-y-3">
                <div>
                  <label className="block font-bold text-charcoal-700 mb-1">Document Title</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. GBPUAT Bulletin No. 43: Terrace Organic Farming"
                    value={newDocTitle}
                    onChange={(e) => setNewDocTitle(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-charcoal-200 font-semibold focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-bold text-charcoal-700 mb-1">Category</label>
                    <select
                      value={newDocCategory}
                      onChange={(e) => setNewDocCategory(e.target.value as any)}
                      className="w-full px-3 py-2 rounded-xl border border-charcoal-200 font-semibold focus:outline-none"
                    >
                      <option value="Crop Advisory">Crop Advisory</option>
                      <option value="Soil Health">Soil Health</option>
                      <option value="Disease Management">Disease Management</option>
                      <option value="Government Scheme">Government Scheme</option>
                      <option value="Irrigation">Irrigation</option>
                    </select>
                  </div>
                  <div>
                    <label className="block font-bold text-charcoal-700 mb-1">Region Tag</label>
                    <input
                      type="text"
                      value="Uttarakhand"
                      readOnly
                      className="w-full px-3 py-2 rounded-xl border border-charcoal-200 bg-charcoal-100 font-semibold text-charcoal-500"
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setIsUploadDocOpen(false)}
                    className="px-3 py-1.5 rounded-lg text-charcoal-600 hover:bg-charcoal-100"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 rounded-lg font-bold bg-forest-900 text-white hover:bg-forest-800"
                  >
                    Process & Index
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Document Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse min-w-[650px]">
              <thead>
                <tr className="border-b border-charcoal-100 bg-charcoal-50/70 text-charcoal-500 font-bold uppercase text-[10px]">
                  <th className="py-3 px-4">Document Title</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Crops / Scope</th>
                  <th className="py-3 px-4">Vector Chunks</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-charcoal-100">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-forest-50/30 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-forest-900 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-forest-700 shrink-0" />
                      <span>{doc.title}</span>
                    </td>
                    <td className="py-3.5 px-4 text-charcoal-600 font-medium">{doc.category}</td>
                    <td className="py-3.5 px-4 text-charcoal-500">{doc.cropTag}</td>
                    <td className="py-3.5 px-4 font-mono font-bold text-forest-800">{doc.vectorChunksCount} Chunks</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                        {doc.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
