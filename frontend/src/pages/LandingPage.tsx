import React, { useEffect, useState } from 'react';
import {
  Store,
  ShoppingCart,
  TrendingUp,
  Volume2,
  Users,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Zap,
  Printer,
  Truck,
  MessageSquare,
  Sun,
  Moon,
  Bot,
  BarChart3,
  HelpCircle,
  PhoneCall,
  Clock,
} from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import { Button } from '../components/Button';
import { Badge } from '../components/Badge';

interface LandingPageProps {
  onGetStarted: () => void;
  onLogin: () => void;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onGetStarted,
  onLogin,
  isDarkMode,
  onToggleDarkMode,
}) => {
  const { language, setLanguage } = useLanguage();
  const [activeFaq, setActiveFaq] = useState<number | null>(null);
  const [backendWarmedUp, setBackendWarmedUp] = useState<boolean>(false);

  // Background warm-up ping to wake up sleeping Render backend instance immediately
  useEffect(() => {
    let isMounted = true;
    const warmUpBackend = async () => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s timeout for cold start
        const res = await fetch('/api/health', { signal: controller.signal });
        clearTimeout(timeoutId);
        if (res.ok && isMounted) {
          setBackendWarmedUp(true);
        }
      } catch {
        // Silently wait; user will see static landing page without interruption
      }
    };
    warmUpBackend();
    return () => {
      isMounted = false;
    };
  }, []);

  const toggleFaq = (index: number) => {
    setActiveFaq(activeFaq === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-surface bg-ambient-mesh text-text selection:bg-brand selection:text-white transition-colors duration-200">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-40 w-full backdrop-blur-md bg-surface/90 border-b border-border/80 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2.5 cursor-pointer">
            <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-fintech-sm">
              <Store className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-lg text-text tracking-tight">
                Vyapar<span className="text-blue-600 dark:text-blue-400">Mitra</span>
              </span>
              <span className="hidden sm:inline-block ml-2 px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                Merchant OS
              </span>
            </div>
          </div>

          {/* Navigation Links (Desktop) */}
          <nav className="hidden md:flex items-center gap-8 text-xs font-semibold text-text-muted">
            <a href="#features" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              Features
            </a>
            <a href="#solutions" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              Kirana Solutions
            </a>
            <a href="#pricing" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              Pricing
            </a>
            <a href="#faq" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              FAQ
            </a>
          </nav>

          {/* Right Action Controls */}
          <div className="flex items-center gap-2.5 sm:gap-3">
            {/* Language Switcher */}
            <div className="flex items-center bg-surface-muted border border-border rounded-xl p-0.5 text-xs font-semibold">
              {(['hinglish', 'hindi', 'english'] as const).map((lang) => (
                <button
                  key={lang}
                  type="button"
                  onClick={() => setLanguage(lang)}
                  className={`px-2 sm:px-2.5 py-1 rounded-lg transition-all text-[11px] sm:text-xs ${
                    language === lang
                      ? 'bg-surface-card text-text shadow-2xs font-bold'
                      : 'text-text-muted hover:text-text'
                  }`}
                >
                  {lang === 'hinglish' ? 'Hinglish' : lang === 'hindi' ? 'हिंदी' : 'EN'}
                </button>
              ))}
            </div>

            {/* Dark Mode Toggle */}
            <button
              type="button"
              onClick={onToggleDarkMode}
              className="w-8.5 h-8.5 rounded-xl bg-surface-card border border-border text-text-muted hover:text-text flex items-center justify-center transition-colors shadow-2xs"
              title="Toggle Theme"
            >
              {isDarkMode ? <Sun className="w-4 h-4 text-warning" /> : <Moon className="w-4 h-4 text-text-muted" />}
            </button>

            {/* Log In Button */}
            <button
              type="button"
              onClick={onLogin}
              className="px-3.5 py-1.5 rounded-xl text-xs font-bold border border-border text-text hover:bg-surface-muted transition-all cursor-pointer"
            >
              Log In
            </button>

            {/* Launch App Button */}
            <Button
              variant="primary"
              size="sm"
              onClick={onGetStarted}
              className="hidden sm:inline-flex items-center gap-1.5 font-bold shadow-fintech-sm"
            >
              <span>Get Started</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-12 pb-20 md:pt-16 md:pb-28 overflow-hidden">
        {/* Glow Background blobs */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-blue-500/15 to-purple-500/15 blur-3xl rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300 text-xs font-semibold mb-6 shadow-2xs animate-fade-in">
            <Sparkles className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
            <span>भारत के 60M+ खुदरा व्यापारियों के लिए AI ऑपरेटिंग सिस्टम</span>
            {backendWarmedUp && (
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.2 rounded-full border border-emerald-500/30">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Live Cloud Ready
              </span>
            )}
          </div>

          {/* Main Headline */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-text tracking-tight max-w-4xl mx-auto leading-tight sm:leading-tight">
            दुकान चलाएं स्मार्ट AI से—
            <br />
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
              तेज़ बिलिंग, डिजिटल खाता और सटीक मुनाफा
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mt-5 text-base sm:text-lg text-text-muted max-w-2xl mx-auto leading-relaxed">
            VyaparMitra transforms traditional kirana &amp; retail stores with 3-second POS billing, voice-enabled UPI soundbox alerts, automated customer Khata (उधार), and predictive stock reorders.
          </p>

          {/* Action CTAs */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3.5">
            <Button
              variant="primary"
              size="lg"
              onClick={onGetStarted}
              className="w-full sm:w-auto px-7 py-3 text-sm font-bold shadow-fintech-md flex items-center justify-center gap-2 group"
            >
              <span>Get Started Free &bull; बिना क्रेडिट कार्ड</span>
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Button>
            <button
              type="button"
              onClick={onLogin}
              className="w-full sm:w-auto px-6 py-3 rounded-xl border border-border bg-surface-card hover:bg-surface-muted text-sm font-bold text-text transition-colors flex items-center justify-center gap-2 shadow-2xs"
            >
              <Store className="w-4 h-4 text-blue-600" />
              <span>Log In to Store Dashboard</span>
            </button>
          </div>

          {/* Social Proof Strip */}
          <div className="mt-12 pt-8 border-t border-border/80 max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-blue-600 dark:text-blue-400">3 Seconds</div>
              <div className="text-xs text-text-subtle font-medium mt-0.5">Average POS Checkout</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">100%</div>
              <div className="text-xs text-text-subtle font-medium mt-0.5">Zero-Hallucination AI</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-purple-600 dark:text-purple-400">₹0 Fee</div>
              <div className="text-xs text-text-subtle font-medium mt-0.5">Free Starter Tier</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-amber-500">256-Bit</div>
              <div className="text-xs text-text-subtle font-medium mt-0.5">Bank-Grade Cloud Security</div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section id="features" className="py-16 md:py-24 bg-surface-muted/50 border-y border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <h2 className="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-2">
              Everything Your Kirana Needs
            </h2>
            <h3 className="text-2xl sm:text-4xl font-extrabold text-text tracking-tight">
              हर खुदरा व्यापारी की ज़रूरतों के लिए संपूर्ण समाधान
            </h3>
            <p className="mt-3 text-sm text-text-muted">
              Built ground-up for Indian retail workflows—from quick barcode billing to credit collection and predictive procurement.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Feature 1: POS & Thermal Billing */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-blue-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-4">
                <ShoppingCart className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">High-Speed POS &amp; Thermal Billing</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                Instant counter billing with product search, barcode reader, split payments (UPI, Cash, Credit), and 80mm thermal receipt printing with GST breakup.
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-blue-600 dark:text-blue-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>GST Breakup &bull; Double-Submit Safe</span>
              </div>
            </div>

            {/* Feature 2: Smart Soundbox & UPI */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-emerald-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-4">
                <Volume2 className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">Smart Soundbox Voice Alerts</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                Never miss a payment during morning rush hours. Audio confirmation in Hindi, Hinglish, and English for every UPI and digital transaction.
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Paytm-Style Audio &bull; 4G Cloud Sync</span>
              </div>
            </div>

            {/* Feature 3: Digital Khata & Udhaar */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-purple-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-4">
                <Users className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">Digital Customer Khata &amp; Udhaar</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                Track customer debit balances, enforce credit limits, send automatic WhatsApp reminders, and eliminate ledger calculation errors.
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-purple-600 dark:text-purple-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Credit Limit Guard &bull; WhatsApp Slips</span>
              </div>
            </div>

            {/* Feature 4: Two-Step Procurement */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-amber-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-500 flex items-center justify-center mb-4">
                <Truck className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">2-Step Procurement &amp; Goods Receipt</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                Strict accounting discipline: Owner approvals issue formal Purchase Orders (PO), and inventory stock is increased only upon physical Goods Receipt.
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-amber-600 dark:text-amber-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>PO Generation &bull; Goods Receipt (GRN)</span>
              </div>
            </div>

            {/* Feature 5: Multilingual AI Copilot */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-indigo-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4">
                <Bot className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">Multilingual AI Copilot (Hindi/Hinglish)</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                Ask queries naturally like <em>"Kal kitna profit hua?"</em> or <em>"Atta kab reorder karein?"</em>. Zero hallucinations, grounded 100% in your store's live ledger.
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-indigo-600 dark:text-indigo-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Voice STT/TTS &bull; Daily Morning Brief</span>
              </div>
            </div>

            {/* Feature 6: Demand Forecasts & Benchmarks */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-cyan-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-cyan-50 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400 flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">7-Day Demand ML &amp; Peer Benchmarks</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                Compare your store's performance with city peers. Automated machine learning models forecast 7-day sales and flag seasonal stockout risks.
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-cyan-600 dark:text-cyan-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Local Kirana Ranks &bull; Stockout Protection</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-2">
              Transparent Pricing
            </h2>
            <h3 className="text-2xl sm:text-4xl font-extrabold text-text tracking-tight">
              सरल और पारदर्शी योजनाएं—कोई छुपा शुल्क नहीं
            </h3>
            <p className="mt-3 text-sm text-text-muted">
              Choose the right tier for your single store or multi-branch retail network.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Starter Plan */}
            <div className="p-6 rounded-3xl bg-surface-card border border-border shadow-fintech-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-bold text-text">Kirana Starter</span>
                  <Badge variant="neutral">Free Forever</Badge>
                </div>
                <div className="text-3xl font-black text-text mb-2">₹0 <span className="text-xs font-normal text-text-muted">/ month</span></div>
                <p className="text-xs text-text-muted mb-6">Perfect for small neighborhood kirana stores getting started with digital billing.</p>
                <ul className="space-y-2.5 text-xs text-text">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Unlimited POS Counter Sales</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Customer Khata (up to 100 customers)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Thermal Receipt Printing</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>1 Store Branch &amp; 2 Users</span>
                  </li>
                </ul>
              </div>
              <Button
                variant="outline"
                className="w-full mt-8 font-bold"
                onClick={onGetStarted}
              >
                Start Free
              </Button>
            </div>

            {/* Retail Pro Plan (Highlighted) */}
            <div className="p-6 rounded-3xl bg-surface-card border-2 border-blue-600 shadow-fintech-lg relative flex flex-col justify-between">
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-blue-600 text-white text-[10px] font-extrabold uppercase tracking-wider shadow-xs">
                Most Popular
              </div>
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-bold text-text">Retail Pro</span>
                  <Badge variant="brand">Full AI Suite</Badge>
                </div>
                <div className="text-3xl font-black text-text mb-2">₹399 <span className="text-xs font-normal text-text-muted">/ month</span></div>
                <p className="text-xs text-text-muted mb-6">For established retailers wanting AI forecasts, audio soundbox alerts, and auto-procurement.</p>
                <ul className="space-y-2.5 text-xs text-text">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>Everything in Starter + Unlimited Customers</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>Smart Soundbox Audio Alert Engine</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>7-Day ML Demand Projections</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>Multilingual Voice AI Copilot</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>Two-Step PO Approval &amp; Goods Receipt</span>
                  </li>
                </ul>
              </div>
              <Button
                variant="primary"
                className="w-full mt-8 font-bold shadow-fintech-md"
                onClick={onGetStarted}
              >
                Launch Retail Pro
              </Button>
            </div>

            {/* Enterprise Chain */}
            <div className="p-6 rounded-3xl bg-surface-card border border-border shadow-fintech-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-bold text-text">Enterprise Chain</span>
                  <Badge variant="neutral">Multi-Store</Badge>
                </div>
                <div className="text-3xl font-black text-text mb-2">₹999 <span className="text-xs font-normal text-text-muted">/ month</span></div>
                <p className="text-xs text-text-muted mb-6">For multi-outlet kirana chains and wholesale supermarket operations.</p>
                <ul className="space-y-2.5 text-xs text-text">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-purple-600 shrink-0" />
                    <span>Unlimited Branches &amp; Cashier Counters</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-purple-600 shrink-0" />
                    <span>Inter-Store Stock Transfers</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-purple-600 shrink-0" />
                    <span>Granular RBAC (Owner, Manager, Staff)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-purple-600 shrink-0" />
                    <span>Dedicated SLA &bull; WhatsApp Support</span>
                  </li>
                </ul>
              </div>
              <Button
                variant="outline"
                className="w-full mt-8 font-bold"
                onClick={onGetStarted}
              >
                Contact Sales
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-16 md:py-20 bg-surface-muted/30 border-t border-border">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-2xl sm:text-3xl font-extrabold text-text">
              Frequently Asked Questions (FAQ)
            </h3>
            <p className="text-xs text-text-muted mt-2">
              Common questions from Indian retail store owners.
            </p>
          </div>

          <div className="space-y-3">
            {[
              {
                q: 'क्या मुझे विशेष कंप्यूटर या हार्डवेयर खरीदना होगा?',
                a: 'बिलकुल नहीं। VyaparMitra किसी भी साधारण स्मार्टफोन, टैबलेट, या लैपटॉप पर तुरंत चलता है। आप अपने मौजूदा ब्लूटूथ या USB थर्मल प्रिंटर को भी सीधे जोड़ सकते हैं।',
              },
              {
                q: 'क्या मेरा दुकान का डेटा सुरक्षित है?',
                a: 'हाँ। VyaparMitra 256-बिट बैंक-ग्रेड एन्क्रिप्शन का उपयोग करता है। आपका डेटा केवल आपकी दुकान के लिए सुरक्षित रूप से संग्रहीत होता है।',
              },
              {
                q: 'क्या AI कॉपायलट हिंदी में काम करता है?',
                a: 'हाँ। हमारा AI कॉपायलट हिंदी, हिंग्लिश और अंग्रेजी तीनों भाषाओं में बात कर सकता है। आप बोलकर भी सवाल पूछ सकते हैं।',
              },
              {
                q: 'क्या मैं अपने पुराने ग्राहकों और सामान की लिस्ट CSV से ला सकता हूँ?',
                a: 'हाँ। Products और Customers पेज पर बल्क CSV अपलोड की सुविधा है, जिससे आप 1 मिनट में 5,000+ आइटम इम्पोर्ट कर सकते हैं।',
              },
            ].map((faq, i) => (
              <div
                key={i}
                className="rounded-2xl bg-surface-card border border-border/80 overflow-hidden shadow-2xs transition-colors"
              >
                <button
                  type="button"
                  onClick={() => toggleFaq(i)}
                  className="w-full p-4 text-left flex items-center justify-between text-xs sm:text-sm font-bold text-text hover:text-blue-600 transition-colors"
                >
                  <span>{faq.q}</span>
                  <span className="text-lg text-text-subtle font-normal">
                    {activeFaq === i ? '−' : '+'}
                  </span>
                </button>
                {activeFaq === i && (
                  <div className="px-4 pb-4 text-xs text-text-muted leading-relaxed border-t border-border/40 pt-3">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 bg-surface border-t border-border text-center text-xs text-text-subtle">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Store className="w-4 h-4 text-blue-600" />
            <span className="font-bold text-text">VyaparMitra AI</span>
            <span>&bull; Intelligence-Led Retail OS</span>
          </div>
          <div>
            Built with ❤️ for Indian Retail Merchants &bull; ISO 27001 Security Standard
          </div>
          <div className="flex items-center gap-4 text-text-muted">
            <button type="button" onClick={onLogin} className="hover:text-text cursor-pointer">
              Login
            </button>
            <button type="button" onClick={onGetStarted} className="hover:text-text cursor-pointer">
              Register
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};
