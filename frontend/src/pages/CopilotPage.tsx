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
    <div className="h-[calc(100vh-8.5rem)] flex flex-col bg-white dark:bg-[#0F1D38] rounded-2xl border-2 border-[#CDE5F7] dark:border-[#1E3A6E] shadow-paytm overflow-hidden animate-in fade-in-50 duration-200 transition-colors">
      {/* Copilot Header */}
      <div className="px-6 py-4 border-b border-[#CDE5F7] dark:border-[#1E3A6E] bg-gradient-to-r from-[#002970] via-[#00388F] to-[#001D4E] text-white flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00BAF2] to-[#008CC4] flex items-center justify-center text-white shadow-md shadow-[#00BAF2]/30 ring-2 ring-white/20">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm lg:text-base font-black text-white tracking-tight">
                VyaparMitra Hindi AI Copilot
              </h2>
            </div>
            <p className="text-[11px] text-blue-100 font-medium">
              {t('copilot_subtext', 'Grounded exclusively in Verified Store & Benchmark Data')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleGenerateDailyBrief}
            className="text-xs border-white/40 text-white hover:bg-white/15 font-bold"
            disabled={loading}
          >
            <Sparkles className="w-3.5 h-3.5 mr-1.5 text-[#00BAF2]" />
            Daily Morning Brief
          </Button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-[#F0F6FB] dark:bg-[#070E1A] transition-colors">
        {messages.map((m) => {
          const isUser = m.sender === 'user';

          return (
            <div
              key={m.id}
              className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div
                className={`w-9 h-9 rounded-xl shrink-0 flex items-center justify-center text-xs font-black shadow-md ${
                  isUser
                    ? 'bg-gradient-to-br from-[#00BAF2] to-[#008CC4] text-white ring-2 ring-[#00BAF2]/20'
                    : 'bg-gradient-to-br from-[#002970] to-[#001D4E] text-[#00BAF2] ring-2 ring-[#002970]/20'
                }`}
              >
                {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-[#00BAF2]" />}
              </div>

              <div className={`max-w-xl space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
                {/* Bubble */}
                <div
                  className={`p-4 rounded-2xl text-xs leading-relaxed font-medium shadow-paytm ${
                    isUser
                      ? 'bg-gradient-to-r from-[#002970] to-[#001D52] text-white rounded-tr-xs'
                      : 'bg-white dark:bg-[#132342] border-2 border-[#CDE5F7] dark:border-[#1E3A6E] text-[#0F2042] dark:text-white rounded-tl-xs'
                  }`}
                >
                  <p className="whitespace-pre-line">{m.text}</p>
                </div>

                {/* Assistant Metadata / Citations Pill */}
                {!isUser && m.sources && m.sources.length > 0 && (
                  <div className="text-[11px] bg-white dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E] rounded-xl p-3 shadow-2xs space-y-1.5">
                    <button
                      onClick={() => toggleSource(m.id)}
                      className="w-full flex items-center justify-between text-[#4F6A94] dark:text-blue-200 hover:text-[#00BAF2] font-semibold"
                    >
                      <span className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider font-bold text-[#008A54] dark:text-[#00E68A]">
                        <ShieldCheck className="w-3.5 h-3.5 text-[#00B970]" />
                        Grounded Sources ({m.sources.length} Verified Artifacts)
                      </span>
                      {expandedSources[m.id] ? (
                        <ChevronUp className="w-3.5 h-3.5" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5" />
                      )}
                    </button>

                    {expandedSources[m.id] && (
                      <div className="pt-2 border-t border-[#E8F4FD] dark:border-[#1E3A6E] space-y-1 text-[10px]">
                        {m.sources.map((s, idx) => (
                          <div key={idx} className="p-1.5 rounded-lg bg-[#F0F8FE] dark:bg-[#0F1D38] font-mono text-[#002970] dark:text-blue-100 font-semibold border border-[#CDE5F7] dark:border-[#1E3A6E]">
                            <span className="font-extrabold text-[#00BAF2]">{s.source}</span> &rarr; {s.artifact}
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
            <div className="w-9 h-9 rounded-xl bg-[#002970] text-[#00BAF2] flex items-center justify-center shrink-0 shadow-md">
              <Bot className="w-4 h-4 animate-spin text-[#00BAF2]" />
            </div>
            <div className="bg-white dark:bg-[#132342] border-2 border-[#CDE5F7] dark:border-[#1E3A6E] rounded-2xl rounded-tl-xs p-3.5 text-xs text-[#002970] dark:text-white font-bold flex items-center gap-2 shadow-paytm">
              <span>{currentLanguage === 'hindi' ? 'दुकान के डेटा से उत्तर तैयार किया जा रहा है...' : 'Dukaan ke verified data se uttar tayar kiya ja raha hai...'}</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Chips */}
      <div className="px-6 py-3 bg-[#F0F8FE] dark:bg-[#0B1528] border-t border-[#CDE5F7] dark:border-[#1E3A6E] flex items-center gap-2 overflow-x-auto text-xs transition-colors">
        <span className="text-[10px] uppercase font-black text-[#002970] dark:text-blue-200 whitespace-nowrap">Suggested:</span>
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
            className="px-3 py-1.5 rounded-xl bg-white dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E] text-[#002970] dark:text-white font-bold hover:text-white hover:bg-[#00BAF2] hover:border-[#00BAF2] transition-all whitespace-nowrap text-[11px] shadow-2xs"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="p-4 border-t border-[#CDE5F7] dark:border-[#1E3A6E] bg-white dark:bg-[#0B1528] transition-colors">
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
            className="flex-1 px-4 py-3 text-xs rounded-xl border-2 border-[#CDE5F7] dark:border-[#1E3A6E] bg-[#F0F8FE] dark:bg-[#132342] focus:bg-white dark:focus:bg-[#16274A] focus:outline-none focus:ring-2 focus:ring-[#00BAF2] text-[#002970] dark:text-white font-semibold"
          />
          <Button
            type="submit"
            variant="primary"
            disabled={loading || !inputValue.trim()}
            className="px-5 py-3 shadow-md"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
};
