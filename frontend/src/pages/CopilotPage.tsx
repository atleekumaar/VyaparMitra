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
    <div className="h-[calc(100vh-8.5rem)] flex flex-col bg-surface rounded-2xl border border-border shadow-fintech overflow-hidden animate-in fade-in-50 duration-200 transition-colors">
      {/* Copilot Header */}
      <div className="px-6 py-4 border-b border-border bg-gradient-to-r from-brand to-brand-hover text-brand-contrast flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/15 flex items-center justify-center text-white ring-1 ring-white/20">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-sm lg:text-base font-bold text-white tracking-tight">
              VyaparMitra AI Business Copilot
            </h2>
            <p className="text-[11px] opacity-80 font-medium">
              {t('copilot_subtext', 'Grounded exclusively in Verified Store & Benchmark Data')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleGenerateDailyBrief}
            className="text-xs bg-white/10 hover:bg-white/20 text-white border-white/20 font-semibold gap-1.5"
            disabled={loading}
          >
            <Sparkles className="w-3.5 h-3.5 text-white" />
            <span>Daily Morning Brief</span>
          </Button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-surface-muted/50 transition-colors">
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
                    ? 'bg-brand text-brand-contrast'
                    : 'bg-surface-muted border border-border text-brand'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div className={`max-w-xl space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
                {/* Bubble */}
                <div
                  className={`p-4 rounded-2xl text-xs leading-relaxed font-medium shadow-fintech ${
                    isUser
                      ? 'bg-brand text-brand-contrast rounded-tr-xs'
                      : 'bg-surface border border-border text-text rounded-tl-xs'
                  }`}
                >
                  <p className="whitespace-pre-line">{m.text}</p>
                </div>

                {/* Assistant Metadata / Citations Pill */}
                {!isUser && m.sources && m.sources.length > 0 && (
                  <div className="text-[11px] bg-surface border border-border rounded-xl p-3 shadow-xs space-y-1.5">
                    <button
                      onClick={() => toggleSource(m.id)}
                      className="w-full flex items-center justify-between text-text-muted hover:text-brand font-semibold"
                    >
                      <span className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider font-bold text-success">
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
                            <span className="font-bold text-brand">{s.source}</span> &rarr; {s.artifact}
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
            <div className="w-9 h-9 rounded-xl bg-surface-muted border border-border text-brand flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 animate-spin text-brand" />
            </div>
            <div className="bg-surface border border-border rounded-2xl rounded-tl-xs p-3.5 text-xs text-text font-semibold flex items-center gap-2 shadow-fintech">
              <span>{currentLanguage === 'hindi' ? 'दुकान के डेटा से उत्तर तैयार किया जा रहा है...' : 'Dukaan ke verified data se uttar tayar kiya ja raha hai...'}</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Chips */}
      <div className="px-6 py-3 bg-surface-muted border-t border-border flex items-center gap-2 overflow-x-auto text-xs transition-colors">
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
            className="px-3 py-1.5 rounded-xl bg-surface border border-border text-text font-medium hover:text-brand-contrast hover:bg-brand hover:border-brand transition-all whitespace-nowrap text-[11px] shadow-xs"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="p-4 border-t border-border bg-surface transition-colors">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2.5"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={
              currentLanguage === 'hindi'
                ? 'अपनी दुकान के बारे में कोई भी प्रश्न पूछें (उदा. कल कितनी बिक्री हुई?)...'
                : 'Poochiye apni dukaan ke baare mein koi bhi sawaal (e.g. Meri dukaan dusron se kaisi hai?)...'
            }
            disabled={loading}
            className="flex-1 px-4 py-2.5 text-xs rounded-xl border border-border bg-surface-muted/60 focus:bg-surface focus:outline-none focus:ring-2 focus:ring-brand text-text font-medium"
          />
          <Button
            type="submit"
            variant="primary"
            disabled={loading || !inputValue.trim()}
            className="px-4 py-2.5 shadow-xs"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
};
