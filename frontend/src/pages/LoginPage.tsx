import React, { useState, useEffect } from 'react';
import {
  Store,
  ArrowRight,
  Sun,
  Moon,
  Sparkles,
  Mail,
  User,
  Smartphone,
  CheckCircle2,
  AlertCircle,
  Volume2,
  Lock,
  ArrowLeft,
} from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import { UserCategory, UserProfile } from '../types';
import { api } from '../api/client';
import { LoginBrandPanel } from '../components/auth/LoginBrandPanel';
import { OtpInput } from '../components/auth/OtpInput';
import { DemoProfilesModal, DemoPersona } from '../components/auth/DemoProfilesModal';
import { Button } from '../components/Button';
import { Badge } from '../components/Badge';

interface LoginPageProps {
  onLogin: (profile: UserProfile) => void;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({
  onLogin,
  isDarkMode,
  onToggleDarkMode,
}) => {
  const { t, language, setLanguage } = useLanguage();

  // Input states - BLANK BY DEFAULT as requested
  const [fullName, setFullName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [mobileNumber, setMobileNumber] = useState<string>('');
  const [storeId, setStoreId] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<UserCategory>('small_merchant');
  const [selectedDemoPersona, setSelectedDemoPersona] = useState<DemoPersona | null>(null);

  // Flow & State
  const [otpSent, setOtpSent] = useState<boolean>(false);
  const [otpCode, setOtpCode] = useState<string[]>(['', '', '', '', '', '']);
  const [countdown, setCountdown] = useState<number>(30);
  const [isSendingOtp, setIsSendingOtp] = useState<boolean>(false);
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [notificationMsg, setNotificationMsg] = useState<string | null>(null);
  const [demoModalOpen, setDemoModalOpen] = useState<boolean>(false);

  // Soundbox Welcome audio toggle
  const [soundboxWelcome, setSoundboxWelcome] = useState<boolean>(true);
  const [soundboxSimPlaying, setSoundboxSimPlaying] = useState<boolean>(false);

  // Resend Countdown Timer
  useEffect(() => {
    if (otpSent && countdown > 0) {
      const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [otpSent, countdown]);

  // Request OTP from Brevo SMTP / backend relay
  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setNotificationMsg(null);

    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      setAuthError('Please enter a valid email address to receive your verification code.');
      return;
    }

    setIsSendingOtp(true);

    try {
      const res = await api.requestOtp({
        email: cleanEmail,
        phone: mobileNumber.trim() || undefined,
        name: fullName.trim() || undefined,
      });

      setIsSendingOtp(false);
      setOtpSent(true);
      setCountdown(res.expires_in_seconds ? Math.min(res.expires_in_seconds, 60) : 60);
      setOtpCode(['', '', '', '', '', '']);
      setNotificationMsg(res.message || `Verification code sent to ${cleanEmail}`);

      // Auto-fill demo OTP only in DEV environment
      const isDev = Boolean((import.meta as any).env?.DEV);
      if (isDev && res.demo_otp && res.demo_otp.length === 6) {
        setOtpCode(res.demo_otp.split(''));
      }
    } catch (err: any) {
      setIsSendingOtp(false);
      setAuthError(err?.message || 'Failed to send OTP code. Please try again.');
    }
  };

  // Verify OTP and complete sign-in
  const handleVerifyOtp = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setAuthError(null);

    const fullCode = otpCode.join('').trim();
    if (fullCode.length !== 6) {
      setAuthError('Please enter all 6 digits of the verification code.');
      return;
    }

    setIsVerifying(true);

    try {
      const res = await api.verifyOtp({
        email: email.trim().toLowerCase(),
        otp: fullCode,
        phone: mobileNumber.trim() || undefined,
        name: fullName.trim() || undefined,
        store_id: storeId.trim() || undefined,
      });

      setIsVerifying(false);

      // Persist access token
      if (res.access_token) {
        localStorage.setItem('vyaparmitra_token', res.access_token);
      }

      // Play Soundbox welcome greeting if enabled
      if (soundboxWelcome) {
        try {
          const utterance = new SpeechSynthesisUtterance();
          if (language === 'hindi') {
            utterance.text = 'व्यापार मित्र में आपका स्वागत है!';
            utterance.lang = 'hi-IN';
          } else {
            utterance.text = 'VyaparMitra me aapka swagat hai!';
            utterance.lang = 'hi-IN';
          }
          utterance.rate = 1.0;
          window.speechSynthesis.speak(utterance);
        } catch {
          // Ignore audio errors
        }
      }

      // Build UserProfile
      const initials = (res.user.full_name || fullName || 'VM')
        .split(' ')
        .map((w) => w[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);

      const profile: UserProfile = {
        id: res.user.business_id,
        business_id: res.user.business_id,
        merchant_id: res.user.business_id,
        name: res.user.full_name || fullName || 'Merchant Partner',
        email: res.user.email,
        storeName:
          selectedDemoPersona?.storeName ||
          (fullName ? `${fullName}'s Store` : 'My Retail Store'),
        category: selectedCategory,
        categoryLabel:
          selectedCategory === 'wholesaler'
            ? 'Wholesaler & Distributor'
            : selectedCategory === 'billing_staff'
            ? 'Billing Counter Staff'
            : selectedCategory === 'enterprise'
            ? 'Enterprise Retail Chain'
            : 'Kirana & Retail Store',
        phone: res.user.phone || mobileNumber || '+919876543210',
        city: selectedDemoPersona?.city || 'India',
        role: res.user.role || 'owner',
        avatarInitials: initials,
        token: res.access_token,
        is_demo: Boolean(selectedDemoPersona),
      };

      onLogin(profile);
    } catch (err: any) {
      setIsVerifying(false);
      setAuthError(err?.message || 'Invalid or expired OTP. Please try again.');
    }
  };

  // When user selects a demo persona
  const handleSelectDemoPersona = (p: DemoPersona) => {
    setSelectedDemoPersona(p);
    setSelectedCategory(p.category);
    setFullName(p.name);
    setEmail(p.email);
    setMobileNumber(p.phone);
    setStoreId(p.id);
    setOtpSent(false);
    setOtpCode(['', '', '', '', '', '']);
    setAuthError(null);
    setNotificationMsg(`Demo persona loaded: ${p.name} (${p.id})`);
  };

  return (
    <div className="min-h-screen bg-surface flex flex-col justify-between transition-colors">
      {/* Top microbar */}
      <header className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-brand text-white flex items-center justify-center font-black text-xs select-none">
            VM
          </div>
          <span className="font-extrabold text-sm text-text tracking-tight">
            Vyapar<span className="text-brand">Mitra</span>
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Language Selector */}
          <div className="flex items-center bg-surface-muted border border-border rounded-xl p-0.5 text-xs font-semibold">
            {(['hinglish', 'hindi', 'english'] as const).map((lang) => (
              <button
                key={lang}
                type="button"
                onClick={() => setLanguage(lang)}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  language === lang
                    ? 'bg-surface-card text-text shadow-2xs font-bold'
                    : 'text-text-muted hover:text-text'
                }`}
              >
                {lang === 'hinglish' ? 'Hinglish' : lang === 'hindi' ? 'हिंदी' : 'EN'}
              </button>
            ))}
          </div>

          {/* Theme Toggle */}
          <button
            type="button"
            onClick={onToggleDarkMode}
            className="w-8.5 h-8.5 rounded-xl bg-surface-card border border-border text-text-muted hover:text-text flex items-center justify-center transition-colors"
            title="Toggle Theme"
          >
            {isDarkMode ? <Sun className="w-4 h-4 text-warning" /> : <Moon className="w-4 h-4 text-text-muted" />}
          </button>
        </div>
      </header>

      {/* Main Split Grid */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-2 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 items-center gap-8">
        {/* Left: Brand showcase panel */}
        <LoginBrandPanel />

        {/* Right: Auth Card */}
        <div className="w-full max-w-md mx-auto">
          <div className="bg-surface-card rounded-3xl border border-border p-6 sm:p-8 shadow-fintech-lg transition-all space-y-6">
            {/* Header */}
            <div>
              <div className="flex items-center justify-between">
                <h2 className="text-xl sm:text-2xl font-black text-text tracking-tight">
                  {otpSent ? 'Enter Verification Code' : 'Sign in to VyaparMitra'}
                </h2>
                {selectedDemoPersona && (
                  <Badge variant="demo" dot>
                    Demo: {selectedDemoPersona.id}
                  </Badge>
                )}
              </div>
              <p className="text-xs text-text-muted mt-1 leading-relaxed">
                {otpSent
                  ? `Enter the 6-digit OTP code sent to ${email}.`
                  : 'Enter your business credentials to access your merchant dashboard.'}
              </p>
            </div>

            {/* Error banner */}
            {authError && (
              <div className="p-3 rounded-xl bg-danger-soft border border-danger/30 text-danger text-xs flex items-start gap-2 animate-in fade-in-50">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span className="leading-normal font-medium">{authError}</span>
              </div>
            )}

            {/* Success notification */}
            {notificationMsg && (
              <div className="p-3 rounded-xl bg-success-soft border border-success/30 text-success text-xs flex items-start gap-2 animate-in fade-in-50">
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                <span className="leading-normal font-medium">{notificationMsg}</span>
              </div>
            )}

            {!otpSent ? (
              // Step 1: Input Details (Blank by default!)
              <form onSubmit={handleRequestOtp} className="space-y-4">
                {/* Full Name */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text flex items-center justify-between">
                    <span>Full Name</span>
                    <span className="text-[11px] text-text-subtle font-normal">Optional</span>
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-text-subtle absolute left-3.5 top-3.5" />
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Your full name"
                      className="w-full pl-10 pr-3.5 py-2.5 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text placeholder-text-subtle focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand"
                    />
                  </div>
                </div>

                {/* Email Address */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text flex items-center justify-between">
                    <span>Email Address</span>
                    <span className="text-[11px] text-brand font-medium">OTP delivery</span>
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-text-subtle absolute left-3.5 top-3.5" />
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                      className="w-full pl-10 pr-3.5 py-2.5 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text placeholder-text-subtle focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand"
                    />
                  </div>
                </div>

                {/* Mobile Number */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text flex items-center justify-between">
                    <span>Mobile Number</span>
                    <span className="text-[11px] text-text-subtle font-normal">SMS / WhatsApp</span>
                  </label>
                  <div className="relative">
                    <Smartphone className="w-4 h-4 text-text-subtle absolute left-3.5 top-3.5" />
                    <input
                      type="tel"
                      value={mobileNumber}
                      onChange={(e) => setMobileNumber(e.target.value)}
                      placeholder="10-digit mobile"
                      className="w-full pl-10 pr-3.5 py-2.5 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text placeholder-text-subtle focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand tabular-nums"
                    />
                  </div>
                </div>

                {/* Soundbox toggle */}
                <div className="pt-1 flex items-center justify-between">
                  <label className="text-xs font-medium text-text-muted flex items-center gap-2 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={soundboxWelcome}
                      onChange={(e) => setSoundboxWelcome(e.target.checked)}
                      className="rounded text-brand focus:ring-brand"
                    />
                    <span>Play Audio Soundbox welcome</span>
                  </label>
                  <Volume2 className="w-4 h-4 text-brand" />
                </div>

                {/* Submit button */}
                <Button
                  type="submit"
                  variant="primary"
                  className="w-full py-3 justify-center text-sm font-bold shadow-fintech"
                  disabled={isSendingOtp}
                >
                  {isSendingOtp ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Sending OTP...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      Get Verification Code
                      <ArrowRight className="w-4 h-4" />
                    </span>
                  )}
                </Button>
              </form>
            ) : (
              // Step 2: 6-Box OTP Verification
              <form onSubmit={handleVerifyOtp} className="space-y-5">
                <OtpInput
                  value={otpCode}
                  onChange={setOtpCode}
                  disabled={isVerifying}
                />

                <div className="flex items-center justify-between text-xs pt-1">
                  <button
                    type="button"
                    onClick={() => {
                      setOtpSent(false);
                      setAuthError(null);
                    }}
                    className="inline-flex items-center gap-1 font-semibold text-text-muted hover:text-text"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" />
                    Change Email
                  </button>

                  {countdown > 0 ? (
                    <span className="text-text-muted tabular-nums font-medium">
                      Resend in {countdown}s
                    </span>
                  ) : (
                    <button
                      type="button"
                      onClick={handleRequestOtp}
                      disabled={isSendingOtp}
                      className="font-bold text-brand hover:underline"
                    >
                      Resend Code
                    </button>
                  )}
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  className="w-full py-3 justify-center text-sm font-bold shadow-fintech"
                  disabled={isVerifying || otpCode.join('').length !== 6}
                >
                  {isVerifying ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Verifying &amp; Logging in...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      Verify &amp; Launch Dashboard
                      <ArrowRight className="w-4 h-4" />
                    </span>
                  )}
                </Button>
              </form>
            )}

            {/* Try demo account link */}
            <div className="pt-4 border-t border-border/80 text-center">
              <button
                type="button"
                onClick={() => setDemoModalOpen(true)}
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand hover:underline"
              >
                <Sparkles className="w-3.5 h-3.5 text-brand" />
                <span>Try demo account (Pre-loaded personas)</span>
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 py-4 text-center text-xs text-text-subtle">
        VyaparMitra AI Merchant OS &bull; ISO Bank Grade Security &bull; Powered by DeepMind Agentic AI
      </footer>

      {/* Demo Profiles Modal */}
      <DemoProfilesModal
        isOpen={demoModalOpen}
        onClose={() => setDemoModalOpen(false)}
        onSelect={handleSelectDemoPersona}
      />
    </div>
  );
};
