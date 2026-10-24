import React, { useState, useEffect } from 'react';
import {
  Store,
  Boxes,
  CreditCard,
  Building2,
  ShieldCheck,
  Volume2,
  Lock,
  Smartphone,
  CheckCircle2,
  KeyRound,
  ArrowRight,
  Sun,
  Moon,
  Sparkles,
  TrendingUp,
  Award,
  Wifi,
  Play,
} from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import { UserCategory, UserProfile } from '../types';

interface LoginPageProps {
  onLogin: (profile: UserProfile) => void;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
}

interface PersonaConfig {
  category: UserCategory;
  id: string;
  name: string;
  storeName: string;
  role: string;
  phone: string;
  city: string;
  avatarInitials: string;
  titleKey: string;
  defaultTitle: string;
  subKey: string;
  defaultSub: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const LoginPage: React.FC<LoginPageProps> = ({
  onLogin,
  isDarkMode,
  onToggleDarkMode,
}) => {
  const { t, language, setLanguage } = useLanguage();

  const personas: PersonaConfig[] = [
    {
      category: 'small_merchant',
      id: 'M001',
      name: 'Rajesh Sharma',
      storeName: 'Shree Ganesh Kirana & General Store',
      role: 'Store Owner',
      phone: '98765 43210',
      city: 'Lucknow, UP',
      avatarInitials: 'RS',
      titleKey: 'category_kirana_title',
      defaultTitle: 'Kirana & Retail Store',
      subKey: 'category_kirana_sub',
      defaultSub: 'Small Merchant / Daily POS & Audio alerts',
      icon: Store,
    },
    {
      category: 'wholesaler',
      id: 'M015',
      name: 'Amit Agarwal',
      storeName: 'Agarwal Wholesale FMCG Distributors',
      role: 'Wholesale Partner',
      phone: '98123 45678',
      city: 'Kanpur, UP',
      avatarInitials: 'AA',
      titleKey: 'category_wholesaler_title',
      defaultTitle: 'Wholesale & Distributor',
      subKey: 'category_wholesaler_sub',
      defaultSub: 'Bulk Distribution, Invoicing & Supplier Khata',
      icon: Boxes,
    },
    {
      category: 'billing_staff',
      id: 'OP-04',
      name: 'Pooja Verma',
      storeName: 'Counter Terminal #01 (SuperStore)',
      role: 'Billing Operator',
      phone: '98345 67890',
      city: 'Lucknow, UP',
      avatarInitials: 'PV',
      titleKey: 'category_cashier_title',
      defaultTitle: 'Billing Operator / Staff',
      subKey: 'category_cashier_sub',
      defaultSub: 'Fast POS counter billing & daily shift tally',
      icon: CreditCard,
    },
    {
      category: 'enterprise',
      id: 'GRP-09',
      name: 'Vikram Malhotra',
      storeName: 'Malhotra Retail Chain (4 Outlets)',
      role: 'Managing Director',
      phone: '98999 11223',
      city: 'Uttar Pradesh Region',
      avatarInitials: 'VM',
      titleKey: 'category_enterprise_title',
      defaultTitle: 'Multi-Store Enterprise',
      subKey: 'category_enterprise_sub',
      defaultSub: 'Multi-outlet chain owner & central admin',
      icon: Building2,
    },
  ];

  const [selectedCategory, setSelectedCategory] = useState<UserCategory>('small_merchant');
  const [authMethod, setAuthMethod] = useState<'otp' | 'pin'>('otp');
  const [mobileNumber, setMobileNumber] = useState<string>('9876543210');
  const [otpCode, setOtpCode] = useState<string[]>(['4', '2', '5', '0', '2', '6']);
  const [storeId, setStoreId] = useState<string>('M001');
  const [pinCode, setPinCode] = useState<string>('4250');
  const [soundboxWelcome, setSoundboxWelcome] = useState<boolean>(true);
  const [isAuthenticating, setIsAuthenticating] = useState<boolean>(false);
  const [otpSent, setOtpSent] = useState<boolean>(true);
  const [countdown, setCountdown] = useState<number>(30);
  const [soundboxSimPlaying, setSoundboxSimPlaying] = useState<boolean>(false);

  // Current active persona details
  const activePersona = personas.find((p) => p.category === selectedCategory) || personas[0];

  // Update inputs whenever selected persona changes
  const handleSelectPersona = (p: PersonaConfig) => {
    setSelectedCategory(p.category);
    setMobileNumber(p.phone.replace(/\s+/g, ''));
    setStoreId(p.id);
  };

  // OTP Timer countdown
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  // Handle OTP digit changes
  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) {
      value = value.slice(-1);
    }
    const updated = [...otpCode];
    updated[index] = value;
    setOtpCode(updated);

    // Auto-advance
    if (value && index < 5) {
      const nextInput = document.getElementById(`otp-input-${index + 1}`);
      nextInput?.focus();
    }
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otpCode[index] && index > 0) {
      const prevInput = document.getElementById(`otp-input-${index - 1}`);
      prevInput?.focus();
    }
  };

  const handleAutoFillDemo = () => {
    setOtpCode(['4', '2', '5', '0', '2', '6']);
    setPinCode('4250');
  };

  // Preview Voice on the Soundbox
  const handlePlayVoicePreview = () => {
    setSoundboxSimPlaying(true);
    try {
      const utterance = new SpeechSynthesisUtterance();
      if (language === 'hindi') {
        utterance.text = 'व्यापारमित्र साउंडबॉक्स चालू है। चार हज़ार दो सौ पचास रुपये प्राप्त हुए!';
        utterance.lang = 'hi-IN';
      } else {
        utterance.text = 'VyaparMitra Soundbox live hai. 4250 rupees prapt hue!';
        utterance.lang = 'hi-IN';
      }
      window.speechSynthesis.speak(utterance);
    } catch {
      // Speech synthesis fallback
    }
    setTimeout(() => setSoundboxSimPlaying(false), 3500);
  };

  // Authenticate and Login
  const handleSubmitLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsAuthenticating(true);

    if (soundboxWelcome) {
      try {
        const welcomeUtterance = new SpeechSynthesisUtterance();
        if (language === 'hindi') {
          welcomeUtterance.text = `नमस्ते ${activePersona.name} जी, व्यापारमित्र में आपका स्वागत है!`;
          welcomeUtterance.lang = 'hi-IN';
        } else {
          welcomeUtterance.text = `Namaste ${activePersona.name} ji, VyaparMitra me aapka swagat hai!`;
          welcomeUtterance.lang = 'hi-IN';
        }
        window.speechSynthesis.speak(welcomeUtterance);
      } catch {
        // Speech synthesis fallback
      }
    }

    setTimeout(() => {
      setIsAuthenticating(false);
      onLogin({
        id: activePersona.id,
        name: activePersona.name,
        storeName: activePersona.storeName,
        category: activePersona.category,
        categoryLabel: t(activePersona.titleKey, activePersona.defaultTitle),
        phone: activePersona.phone,
        city: activePersona.city,
        role: activePersona.role,
        avatarInitials: activePersona.avatarInitials,
      });
    }, 700);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0B0F19] text-slate-900 dark:text-slate-100 flex flex-col justify-between transition-colors duration-200">
      {/* Top Floating App Bar */}
      <header className="px-4 sm:px-8 py-4 border-b border-slate-200/80 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          {/* Logo Branding */}
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-xs select-none">
              VM
            </div>
            <div>
              <span className="font-bold text-lg text-slate-900 dark:text-white tracking-tight leading-none block">
                Vyapar<span className="text-blue-600 dark:text-blue-400">Mitra</span>
              </span>
              <span className="text-[10px] font-medium text-slate-500 dark:text-slate-400 mt-0.5 block">
                Merchant Command Center
              </span>
            </div>
          </div>

          {/* Right Header Controls (Language & Theme) */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Theme Toggle */}
            <button
              onClick={onToggleDarkMode}
              className="w-8.5 h-8.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 text-slate-600 dark:text-amber-400 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center justify-center transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
              title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              aria-label="Toggle Dark/Light Mode"
            >
              {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
            </button>

            {/* Language Selector */}
            <div className="flex items-center bg-slate-100 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80 rounded-lg p-0.5 text-xs font-medium">
              <button
                onClick={() => setLanguage('hinglish')}
                className={`px-2.5 py-1 rounded-md transition-colors ${
                  language === 'hinglish'
                    ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Hinglish
              </button>
              <button
                onClick={() => setLanguage('hindi')}
                className={`px-2.5 py-1 rounded-md transition-colors ${
                  language === 'hindi'
                    ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                हिंदी
              </button>
              <button
                onClick={() => setLanguage('english')}
                className={`px-2.5 py-1 rounded-md transition-colors ${
                  language === 'english'
                    ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                English
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex items-center justify-center">
        <div className="w-full bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xl overflow-hidden grid grid-cols-1 lg:grid-cols-12 min-h-[640px]">
          {/* Left Panel: Visual Story & Live Soundbox Showcase (5 cols) */}
          <div className="lg:col-span-5 bg-gradient-to-br from-slate-900 via-slate-950 to-blue-950 text-white p-6 sm:p-8 lg:p-10 flex flex-col justify-between relative overflow-hidden">
            {/* Ambient Background Glows */}
            <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 rounded-full bg-blue-600/20 blur-3xl pointer-events-none" />
            <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-64 h-64 rounded-full bg-purple-600/20 blur-3xl pointer-events-none" />

            <div className="relative z-10 space-y-6">
              {/* Badge */}
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-300 border border-blue-500/20">
                <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                <span>Next-Gen Bharat Merchant Intelligence</span>
              </div>

              {/* Title & Tagline */}
              <div>
                <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white leading-tight">
                  Empowering Indian Retail with Voice POS & AI
                </h2>
                <p className="text-sm text-slate-300 mt-2 font-normal leading-relaxed">
                  Real-time UPI audio reconciliation, 7-day predictive stocking, and regional peer benchmarking in one platform.
                </p>
              </div>

              {/* Live Interactive Soundbox Simulator Widget */}
              <div className="rounded-xl p-4 bg-slate-900/90 border border-slate-700/80 shadow-lg text-slate-100 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-400 flex items-center justify-center">
                      <Volume2 className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="text-xs font-bold text-white block leading-tight">
                        Smart Soundbox Live
                      </span>
                      <span className="text-[11px] text-emerald-400 font-medium flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        Online &bull; 4G SIM Connected
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                    <Wifi className="w-3.5 h-3.5 text-blue-400" />
                    <span className="text-[11px]">Syncing</span>
                  </div>
                </div>

                {/* Animated Waveform & Audio Announcement */}
                <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-0.5 h-4">
                      <span className="w-1 bg-blue-400 h-2.5 rounded-full animate-soundbox-wave" />
                      <span className="w-1 bg-blue-400 h-4 rounded-full animate-soundbox-wave [animation-delay:0.2s]" />
                      <span className="w-1 bg-blue-400 h-3 rounded-full animate-soundbox-wave [animation-delay:0.4s]" />
                      <span className="w-1 bg-blue-400 h-1.5 rounded-full animate-soundbox-wave [animation-delay:0.1s]" />
                    </div>
                    <span className="text-xs font-semibold text-white tabular-nums">
                      &ldquo;₹4,250 prapt hue!&rdquo;
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={handlePlayVoicePreview}
                    className="px-2 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-medium flex items-center gap-1 transition-colors shadow-2xs"
                  >
                    <Play className="w-3 h-3 fill-white" />
                    <span>{soundboxSimPlaying ? 'Playing...' : 'Play Audio'}</span>
                  </button>
                </div>
              </div>

              {/* Feature Highlights */}
              <div className="space-y-3 pt-2">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <h3 className="text-xs font-semibold text-white">Instant UPI Settlement Alert</h3>
                    <p className="text-[11px] text-slate-400">100% verified voice announcements for every QR & cash payment.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded bg-blue-500/20 text-blue-400 flex items-center justify-center shrink-0 mt-0.5">
                    <TrendingUp className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <h3 className="text-xs font-semibold text-white">Machine Learning Inventory Run-Rate</h3>
                    <p className="text-[11px] text-slate-400">Know which items to restock before weekend surges.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded bg-purple-500/20 text-purple-400 flex items-center justify-center shrink-0 mt-0.5">
                    <Award className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <h3 className="text-xs font-semibold text-white">Hyper-Local Peer Benchmarks</h3>
                    <p className="text-[11px] text-slate-400">Compare bill size, margins, and repeat rates with nearby stores.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Security Trust Banner */}
            <div className="relative z-10 pt-6 mt-6 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Bank-Grade 256-Bit SSL</span>
              </div>
              <span>RBI Guidelines Compliant</span>
            </div>
          </div>

          {/* Right Panel: Interactive Multi-Persona Login (7 cols) */}
          <div className="lg:col-span-7 p-6 sm:p-8 lg:p-10 flex flex-col justify-between">
            <div>
              {/* Form Header */}
              <div className="pb-4">
                <h1 className="text-2xl sm:text-[26px] font-bold text-slate-900 dark:text-white tracking-tight">
                  {t('login_title', 'Sign In to VyaparMitra')}
                </h1>
                <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1 font-normal leading-normal">
                  {t('login_subtitle', 'Select your business category to access your financial dashboard')}
                </p>
              </div>

              {/* STEP 1: Select Category / Role (Interactive Cards) */}
              <div className="mt-4">
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-2.5">
                  {t('login_category_label', 'Who is Logging In?')}
                </label>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {personas.map((p) => {
                    const Icon = p.icon;
                    const isSelected = selectedCategory === p.category;
                    return (
                      <button
                        key={p.category}
                        type="button"
                        onClick={() => handleSelectPersona(p)}
                        className={`p-3 rounded-xl border text-left transition-all relative flex items-start gap-3 ${
                          isSelected
                            ? 'bg-blue-50/70 dark:bg-blue-950/40 border-blue-600 dark:border-blue-500 ring-2 ring-blue-500/20 shadow-xs'
                            : 'bg-white dark:bg-slate-850 border-slate-200/80 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                        }`}
                      >
                        <div
                          className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 border ${
                            isSelected
                              ? 'bg-blue-600 text-white border-blue-600'
                              : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200/60 dark:border-slate-700'
                          }`}
                        >
                          <Icon className="w-4 h-4" />
                        </div>

                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between gap-1">
                            <span className="text-xs font-semibold text-slate-900 dark:text-white truncate">
                              {t(p.titleKey, p.defaultTitle)}
                            </span>
                            {isSelected && (
                              <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400 shrink-0" />
                            )}
                          </div>
                          <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-1 mt-0.5">
                            {t(p.subKey, p.defaultSub)}
                          </p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Active Profile Context Banner */}
              <div className="mt-4 p-3 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200/70 dark:border-slate-800 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 font-bold text-xs flex items-center justify-center shrink-0">
                    {activePersona.avatarInitials}
                  </div>
                  <div className="min-w-0">
                    <span className="font-semibold text-slate-900 dark:text-white block truncate">
                      {activePersona.name} &bull; <span className="text-slate-500 font-normal">{activePersona.role}</span>
                    </span>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 block truncate">
                      {activePersona.storeName} ({activePersona.id})
                    </span>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 shrink-0">
                  Verified
                </span>
              </div>

              {/* STEP 2: Authentication Mode Tabs (OTP vs PIN) */}
              <div className="mt-5">
                <div className="flex items-center border-b border-slate-200/80 dark:border-slate-800 pb-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setAuthMethod('otp')}
                    className={`text-xs font-semibold pb-1.5 relative transition-colors ${
                      authMethod === 'otp'
                        ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                        : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
                    }`}
                  >
                    <span className="flex items-center gap-1.5">
                      <Smartphone className="w-3.5 h-3.5" />
                      {t('auth_tab_otp', 'Mobile OTP')}
                    </span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setAuthMethod('pin')}
                    className={`text-xs font-semibold pb-1.5 relative transition-colors ${
                      authMethod === 'pin'
                        ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                        : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
                    }`}
                  >
                    <span className="flex items-center gap-1.5">
                      <KeyRound className="w-3.5 h-3.5" />
                      {t('auth_tab_pin', 'Store ID & Quick PIN')}
                    </span>
                  </button>
                </div>

                {/* Form Fields */}
                <form onSubmit={handleSubmitLogin} className="mt-4 space-y-4">
                  {authMethod === 'otp' ? (
                    <>
                      {/* Mobile Number Field */}
                      <div>
                        <label className="text-xs font-medium text-slate-700 dark:text-slate-300 block mb-1">
                          {t('mobile_input_label', 'Registered Mobile Number')}
                        </label>
                        <div className="flex rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden bg-white dark:bg-slate-900 focus-within:ring-2 focus-within:ring-blue-600 focus-within:border-blue-600 transition-all">
                          <span className="inline-flex items-center px-3 text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-r border-slate-200 dark:border-slate-700 select-none">
                            +91 (IND)
                          </span>
                          <input
                            type="tel"
                            maxLength={10}
                            value={mobileNumber}
                            onChange={(e) => setMobileNumber(e.target.value.replace(/\D/g, ''))}
                            placeholder={t('mobile_input_placeholder', 'Enter 10-digit mobile number')}
                            className="flex-1 h-9 px-3 text-xs sm:text-sm bg-transparent text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none tabular-nums font-medium"
                          />
                        </div>
                      </div>

                      {/* 6-Digit OTP Field */}
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <label className="text-xs font-medium text-slate-700 dark:text-slate-300">
                            {t('otp_input_label', '6-Digit Verification Code (OTP)')}
                          </label>
                          <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                            {otpSent && `Code sent to +91 ${mobileNumber}`}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          {otpCode.map((digit, idx) => (
                            <input
                              key={idx}
                              id={`otp-input-${idx}`}
                              type="text"
                              maxLength={1}
                              value={digit}
                              onChange={(e) => handleOtpChange(idx, e.target.value)}
                              onKeyDown={(e) => handleOtpKeyDown(idx, e)}
                              className="w-10 h-10 sm:w-11 sm:h-11 text-center font-bold text-base sm:text-lg rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 tabular-nums transition-all"
                            />
                          ))}
                        </div>

                        <div className="mt-2 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                          <button
                            type="button"
                            onClick={handleAutoFillDemo}
                            className="text-blue-600 hover:text-blue-700 dark:text-blue-400 font-medium hover:underline inline-flex items-center gap-1"
                          >
                            <Sparkles className="w-3 h-3" />
                            {t('btn_autofill_demo', 'Auto-fill Demo OTP')}
                          </button>

                          <span>
                            {countdown > 0 ? (
                              <span>Resend in {countdown}s</span>
                            ) : (
                              <button
                                type="button"
                                onClick={() => setCountdown(30)}
                                className="text-blue-600 hover:text-blue-700 dark:text-blue-400 font-medium"
                              >
                                Resend OTP
                              </button>
                            )}
                          </span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      {/* Store ID & PIN Alternative */}
                      <div>
                        <label className="text-xs font-medium text-slate-700 dark:text-slate-300 block mb-1">
                          {t('store_id_label', 'Merchant Store ID')}
                        </label>
                        <input
                          type="text"
                          value={storeId}
                          onChange={(e) => setStoreId(e.target.value)}
                          placeholder="e.g. M001 or OP-04"
                          className="w-full h-9 px-3 text-xs sm:text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 font-medium transition-all"
                        />
                      </div>

                      <div>
                        <label className="text-xs font-medium text-slate-700 dark:text-slate-300 block mb-1">
                          {t('quick_pin_label', '4-Digit Security PIN')}
                        </label>
                        <input
                          type="password"
                          maxLength={4}
                          value={pinCode}
                          onChange={(e) => setPinCode(e.target.value.replace(/\D/g, ''))}
                          placeholder="••••"
                          className="w-full h-9 px-3 text-center text-lg tracking-widest rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 tabular-nums font-bold transition-all"
                        />
                      </div>
                    </>
                  )}

                  {/* Soundbox Voice Welcome Toggle */}
                  <div className="pt-1 flex items-center justify-between text-xs">
                    <label className="flex items-center gap-2 cursor-pointer text-slate-600 dark:text-slate-300">
                      <input
                        type="checkbox"
                        checked={soundboxWelcome}
                        onChange={(e) => setSoundboxWelcome(e.target.checked)}
                        className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4"
                      />
                      <span>{t('soundbox_announce_toggle', 'Play Soundbox audio welcome on login')}</span>
                    </label>
                  </div>

                  {/* Primary Verify & Submit Button */}
                  <button
                    type="submit"
                    disabled={isAuthenticating}
                    className="w-full h-10 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold text-xs sm:text-sm shadow-sm flex items-center justify-center gap-2 transition-all active:scale-[0.99] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                  >
                    {isAuthenticating ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>Verifying Merchant Credentials...</span>
                      </>
                    ) : (
                      <>
                        <span>{t('btn_verify_enter', 'Verify & Enter Dashboard')}</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>

            {/* Fast 1-Click Persona Switcher Footer */}
            <div className="mt-6 pt-4 border-t border-slate-200/80 dark:border-slate-800">
              <span className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider block mb-2">
                1-Click Quick Demo Profiles:
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {personas.map((p) => (
                  <button
                    key={p.category}
                    type="button"
                    onClick={() => {
                      handleSelectPersona(p);
                      onLogin({
                        id: p.id,
                        name: p.name,
                        storeName: p.storeName,
                        category: p.category,
                        categoryLabel: t(p.titleKey, p.defaultTitle),
                        phone: p.phone,
                        city: p.city,
                        role: p.role,
                        avatarInitials: p.avatarInitials,
                      });
                    }}
                    className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800 hover:bg-blue-50 dark:hover:bg-blue-950/40 border border-slate-200/80 dark:border-slate-700/80 text-left transition-colors text-xs group"
                  >
                    <span className="font-semibold text-slate-900 dark:text-white block truncate group-hover:text-blue-600 dark:group-hover:text-blue-400">
                      {p.name.split(' ')[0]}
                    </span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">
                      {p.role}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 text-center text-xs text-slate-500 dark:text-slate-400 border-t border-slate-200/60 dark:border-slate-800/60">
        VyaparMitra &copy; 2026 &bull; Certified by National Unified Payments Architecture &bull; Made with pride for Bharat 🇮🇳
      </footer>
    </div>
  );
};
