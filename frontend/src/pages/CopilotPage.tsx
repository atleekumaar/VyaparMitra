import React, { useEffect, useRef, useState } from 'react';
import { Bot, Send, Sparkles, User, ShieldCheck, ChevronDown, ChevronUp, RefreshCw, Volume2 } from 'lucide-react';
import { api } from '../api/client';
import { CopilotMessage } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { useLanguage } from '../i18n/LanguageContext';

interface CopilotPageProps {
  initialQuery?: string | null;
  currentLanguage?: string;
  onLanguageChange?: (lang: string) => void;
}

export const CopilotPage: React.FC<CopilotPageProps> = ({
  initialQuery,
  currentLanguage: propLanguage,
  onLanguageChange,
}) => {
  const { language: contextLanguage, setLanguage, t } = useLanguage();
  const currentLanguage = propLanguage || contextLanguage;
  const [messages, setMessages] = useState<CopilotMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Namaste Merchant Ji! 🙏\nMain VyaparMitra AI business copilot hoon. Aap mujhse apni dukaan ki sales, agle 7 dino ka forecast, churn risk grahak, benchmarking, ya inventory restock ke baare mein Hindi ya Hinglish mein pooch sakte hain.',
      intent: 'GREETING',
      language: currentLanguage,
      timestamp: new Date().toISOString(),
    },
  ]);
  const [inputValue, setInputValue] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    if (initialQuery) {
      handleSend(initialQuery);
    }
  }, [initialQuery]);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || inputValue;
    if (!textToSend.trim() || loading) return;

    const userMsg: CopilotMessage = {
      id: Math.random().toString(36).substring(7),
      sender: 'user',
      text: textToSend.trim(),
      language: currentLanguage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInputValue('');
    setLoading(true);

    try {
      const resp = await api.askCopilot(textToSend.trim(), 'merchant_session_1', currentLanguage);
      setMessages((prev) => [...prev, resp]);
    } catch (err: any) {
      const errMsg: CopilotMessage = {
        id: Math.random().toString(36).substring(7),
        sender: 'assistant',
        text: `Kshama karein, uttar prapt karne mein samasya aayi: ${err?.message || 'Server error'}. Kripya punah prayas karein.`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDailyBrief = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const resp = await api.getDailyBrief('merchant_session_1', currentLanguage);
      setMessages((prev) => [...prev, resp]);
    } catch (err: any) {
      alert(`Could not generate daily brief: ${err?.message}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleSource = (msgId: string) => {
    setExpandedSources((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  return (
    <div className="h-[calc(100vh-8.5rem)] flex flex-col bg-surface rounded-2xl border border-border shadow-fintech overflow-hidden animate-in fade-in-50 duration-200 transition-colors relative">
      {/* Ambient pastel glow in top right */}
      <div className="absolute top-0 right-0 w-80 h-40 bg-purple-500/10 dark:bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Copilot Header */}
      <div className="px-6 py-4 border-b border-border bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 text-white flex items-center justify-between relative z-10 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center text-white ring-1 ring-white/30 shadow-xs">
            <Sparkles className="w-5 h-5 text-amber-300" />
          </div>
          <div>
            <h2 className="text-sm lg:text-base font-extrabold text-white tracking-tight flex items-center gap-2">
              <span>AI Copilot</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white/20 text-white uppercase tracking-wider">
                Multi-Lingual
              </span>
            </h2>
            <p className="text-[11px] text-white/80 font-medium">
              Your business assistant, now in Hindi, Hinglish and English.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleGenerateDailyBrief}
            className="text-xs bg-white/15 hover:bg-white/25 text-white border-white/30 font-semibold gap-1.5 shadow-xs"
            disabled={loading}
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>Daily Morning Brief</span>
          </Button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-6 overflow-y-auto space-y-5 bg-surface-muted/40 transition-colors">
        {/* Hero Prompt Starter (Shown if <= 2 messages) */}
        {messages.length <= 2 && (
          <div className="py-6 px-4 my-2 text-center max-w-xl mx-auto space-y-4 animate-in fade-in-50">
            <div className="w-12 h-12 rounded-2xl bg-purple-100 dark:bg-purple-950/60 text-purple-600 dark:text-purple-300 flex items-center justify-center mx-auto shadow-xs border border-purple-200 dark:border-purple-800">
              <Sparkles className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-extrabold text-text tracking-tight">
                How can I help your business today?
              </h3>
              <p className="text-xs text-text-muted mt-1">
                Ask about sales trends, inventory restock alerts, or growth opportunities.
              </p>
            </div>

            {/* 3 Quick Prompt Pill Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-2">
              {[
                { icon: '📝', prompt: 'Kal ki sales kaisi rahi?' },
                { icon: '📦', prompt: 'Kya stock restock karna chahiye?' },
                { icon: '🎯', prompt: 'Sales badhane ke liye tips do.' },
              ].map((card, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSend(card.prompt)}
                  disabled={loading}
                  className="p-3 rounded-xl bg-surface-card hover:bg-purple-50 dark:hover:bg-purple-950/30 border border-border hover:border-purple-300 dark:hover:border-purple-700 text-left transition-all shadow-2xs hover:shadow-xs group"
                >
                  <span className="text-base block mb-1">{card.icon}</span>
                  <span className="text-xs font-semibold text-text group-hover:text-purple-600 dark:group-hover:text-purple-300 block leading-tight">
                    {card.prompt}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) => {
          const isUser = m.sender === 'user';

          return (
            <div
              key={m.id}
              className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div
                className={`w-9 h-9 rounded-xl shrink-0 flex items-center justify-center text-xs font-bold shadow-xs ${
                  isUser
                    ? 'bg-purple-600 text-white'
                    : 'bg-surface-card border border-border text-purple-600 dark:text-purple-400'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div className={`max-w-xl space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
                {/* Bubble */}
                <div
                  className={`p-4 rounded-2xl text-xs leading-relaxed font-medium shadow-fintech ${
                    isUser
                      ? 'bg-purple-600 text-white rounded-tr-xs'
                      : 'bg-surface-card border border-border text-text rounded-tl-xs'
                  }`}
                >
                  <p className="whitespace-pre-line">{m.text}</p>
                </div>

                {/* Assistant Metadata / Citations Pill */}
                {!isUser && m.sources && m.sources.length > 0 && (
                  <div className="text-[11px] bg-surface-card border border-border rounded-xl p-3 shadow-xs space-y-1.5">
                    <button
                      onClick={() => toggleSource(m.id)}
                      className="w-full flex items-center justify-between text-text-muted hover:text-purple-600 font-semibold"
                    >
                      <span className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider font-bold text-emerald-600 dark:text-emerald-400">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        Grounded Sources ({m.sources.length} Verified Artifacts)
                      </span>
                      {expandedSources[m.id] ? (
                        <ChevronUp className="w-3.5 h-3.5" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5" />
                      )}
                    </button>

                    {expandedSources[m.id] && (
                      <div className="pt-2 border-t border-border space-y-1 text-[10px]">
                        {m.sources.map((s, idx) => (
                          <div
                            key={idx}
                            className="p-1.5 rounded-lg bg-surface-muted font-mono text-text font-semibold border border-border"
                          >
                            <span className="font-bold text-purple-600">{s.source}</span> &rarr; {s.artifact}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-surface-card border border-border text-purple-600 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 animate-spin text-purple-600" />
            </div>
            <div className="bg-surface-card border border-border rounded-2xl rounded-tl-xs p-3.5 text-xs text-text font-semibold flex items-center gap-2 shadow-fintech">
              <span>{currentLanguage === 'hindi' ? 'दुकान के डेटा से उत्तर तैयार किया जा रहा है...' : 'Dukaan ke verified data se uttar tayar kiya ja raha hai...'}</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Chips */}
      <div className="px-6 py-2.5 bg-surface-muted/60 border-t border-border flex items-center gap-2 overflow-x-auto text-xs transition-colors">
        <span className="text-[10px] uppercase font-bold text-text-muted whitespace-nowrap">Suggested:</span>
        {[
          'Meri dukaan dusron se kaisi hai?',
          'Kal kitni bikri hui thi?',
          'Agle hafte ka sales forecast?',
          'Kaunsa maal restock karna hai?',
          'At-risk grahak kaun hain?',
        ].map((prompt, i) => (
          <button
            key={i}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="px-3 py-1.2 rounded-full bg-surface-card border border-border text-text-muted font-medium hover:text-purple-600 hover:border-purple-300 transition-all whitespace-nowrap text-[11px] shadow-2xs"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Bar with Circular Purple Send Button */}
      <div className="p-4 border-t border-border bg-surface-card transition-colors">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2 bg-surface-muted/70 border border-border rounded-2xl p-1.5 pl-4 focus-within:border-purple-500 focus-within:ring-2 focus-within:ring-purple-500/20 transition-all shadow-inner"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={
              currentLanguage === 'hindi'
                ? 'अपनी दुकान के बारे में कुछ भी पूछें...'
                : 'Ask anything about your business...'
            }
            disabled={loading}
            className="flex-1 bg-transparent text-xs font-medium text-text placeholder-text-muted focus:outline-none"
          />

          <button
            type="submit"
            disabled={!inputValue.trim() || loading}
            className="w-9 h-9 rounded-full bg-purple-600 hover:bg-purple-700 disabled:opacity-40 text-white flex items-center justify-center transition-all shadow-xs shrink-0 cursor-pointer disabled:cursor-not-allowed hover:scale-105 active:scale-95"
            title="Send Message"
          >
            <Send className="w-4 h-4 ml-0.5" />
          </button>
        </form>
      </div>
    </div>
  );
};
