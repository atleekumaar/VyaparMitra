import React, { useEffect, useRef, useState } from 'react';
import { Bot, Send, Sparkles, User, ShieldCheck, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';
import { api } from '../api/client';
import { CopilotMessage } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';

interface CopilotPageProps {
  initialQuery?: string | null;
  currentLanguage: string;
  onLanguageChange: (lang: string) => void;
}

export const CopilotPage: React.FC<CopilotPageProps> = ({
  initialQuery,
  currentLanguage,
  onLanguageChange,
}) => {
  const [messages, setMessages] = useState<CopilotMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Namaste! Main VyaparMitra AI business copilot hoon. Aap mujhse apni dukaan ki sales, agle 7 dino ka forecast, churn risk grahak, ya inventory restock ke baare mein pooch sakte hain.',
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
    <div className="h-[calc(100vh-8.5rem)] flex flex-col bg-white rounded-2xl border border-paytm-border shadow-xs overflow-hidden animate-in fade-in-50 duration-200">
      {/* Copilot Header */}
      <div className="px-6 py-3.5 border-b border-paytm-border bg-slate-50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-paytm-dark flex items-center justify-center text-white shadow-xs">
            <Bot className="w-5 h-5 text-paytm-blue" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-paytm-dark">VyaparMitra AI Copilot</h2>
              <Badge variant="info">Multi-Turn Memory</Badge>
            </div>
            <p className="text-[11px] text-paytm-muted">
              Grounded exclusively in Phase 1-4 Parquet data marts &bull; Zero Number Hallucination
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleGenerateDailyBrief}
            className="text-xs"
            disabled={loading}
          >
            <Sparkles className="w-3.5 h-3.5 mr-1.5 text-paytm-blue" />
            Daily Morning Brief
          </Button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-50/30">
        {messages.map((m) => {
          const isUser = m.sender === 'user';

          return (
            <div
              key={m.id}
              className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div
                className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-xs font-bold ${
                  isUser
                    ? 'bg-paytm-blue text-white shadow-xs'
                    : 'bg-paytm-dark text-paytm-blue shadow-xs'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div className={`max-w-xl space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
                {/* Bubble */}
                <div
                  className={`p-4 rounded-2xl text-xs leading-relaxed ${
                    isUser
                      ? 'bg-paytm-dark text-white rounded-tr-none shadow-xs'
                      : 'bg-white border border-paytm-border text-paytm-dark rounded-tl-none shadow-xs'
                  }`}
                >
                  <p className="whitespace-pre-line">{m.text}</p>
                </div>

                {/* Assistant Metadata / Citations Pill */}
                {!isUser && m.sources && m.sources.length > 0 && (
                  <div className="text-[11px] bg-white border border-paytm-border rounded-xl p-3 shadow-2xs space-y-1.5">
                    <button
                      onClick={() => toggleSource(m.id)}
                      className="w-full flex items-center justify-between text-paytm-muted hover:text-paytm-blue font-medium"
                    >
                      <span className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider font-semibold text-emerald-700">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        Grounded Sources ({m.sources.length} Artifacts)
                      </span>
                      {expandedSources[m.id] ? (
                        <ChevronUp className="w-3.5 h-3.5" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5" />
                      )}
                    </button>

                    {expandedSources[m.id] && (
                      <div className="pt-2 border-t border-slate-100 space-y-1 text-[10px]">
                        {m.sources.map((s, idx) => (
                          <div key={idx} className="p-1.5 rounded bg-slate-50 font-mono text-slate-600">
                            <span className="font-bold text-paytm-dark">{s.source}</span> &rarr; {s.artifact}
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
            <div className="w-8 h-8 rounded-full bg-paytm-dark text-paytm-blue flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 animate-spin" />
            </div>
            <div className="bg-white border border-paytm-border rounded-2xl rounded-tl-none p-3.5 text-xs text-paytm-muted flex items-center gap-2 shadow-xs">
              <span className="inline-block w-2 h-2 rounded-full bg-paytm-blue animate-ping" />
              <span>Synthesizing grounded answer from Phase 1-4 data marts...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Chips */}
      <div className="px-6 py-2.5 bg-slate-50 border-t border-paytm-border flex items-center gap-2 overflow-x-auto text-xs">
        <span className="text-[10px] uppercase font-bold text-paytm-muted whitespace-nowrap">Suggested:</span>
        {[
          'Kal kitni bikri hui thi?',
          'Agle hafte ka sales forecast?',
          'Kaunsa maal restock karna hai?',
          'At-risk grahak kaun hain?',
          'Sabse zyada bikne wala product?',
        ].map((prompt, i) => (
          <button
            key={i}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="px-2.5 py-1 rounded-full bg-white border border-paytm-border text-paytm-text hover:text-paytm-blue hover:border-paytm-blue transition-colors whitespace-nowrap text-[11px]"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="p-4 border-t border-paytm-border bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={
              currentLanguage === 'hindi'
                ? 'अपनी दुकान के बारे में कोई भी प्रश्न पूछें (उदा. कल कितनी बिक्री हुई?)...'
                : 'Poochiye apni dukaan ke baare mein koi bhi sawaal...'
            }
            disabled={loading}
            className="flex-1 px-4 py-2.5 text-xs rounded-xl border border-paytm-border bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-paytm-blue"
          />
          <Button
            type="submit"
            variant="primary"
            disabled={loading || !inputValue.trim()}
            className="px-4 py-2.5"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
};
