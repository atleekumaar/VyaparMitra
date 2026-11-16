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
  Eye,
  EyeOff,
  KeyRound,
  ShieldCheck,
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

  // Auth Mode: 'login' (Email & Password), 'signup' (Create Account with Password), 'otp_login' (One-Time Password)
  const [authMode, setAuthMode] = useState<'login' | 'signup' | 'otp_login'>('login');

  // Input states - BLANK BY DEFAULT as requested
  const [fullName, setFullName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [mobileNumber, setMobileNumber] = useState<string>('');
  const [storeId, setStoreId] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<UserCategory>('small_merchant');
  const [selectedDemoPersona, setSelectedDemoPersona] = useState<DemoPersona | null>(null);

  // Flow & State
  const [otpSent, setOtpSent] = useState<boolean>(false);
  const [otpCode, setOtpCode] = useState<string[]>(['', '', '', '', '', '']);
  const [countdown, setCountdown] = useState<number>(30);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [notificationMsg, setNotificationMsg] = useState<string | null>(null);
  const [demoModalOpen, setDemoModalOpen] = useState<boolean>(false);

  // Soundbox Welcome audio toggle
  const [soundboxWelcome, setSoundboxWelcome] = useState<boolean>(true);

  // Resend Countdown Timer
  useEffect(() => {
    if (otpSent && countdown > 0) {
      const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [otpSent, countdown]);

  const playWelcomeAudio = () => {
    if (!soundboxWelcome) return;
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
      // Ignore audio failure
    }
  };

  // 1. Password Login Handler (Email + Password)
  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setNotificationMsg(null);

    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      setAuthError('Please enter a valid email address.');
      return;
    }
    if (!password || password.trim().length < 4) {
      setAuthError('Please enter your account password.');
      return;
    }

    setIsSubmitting(true);

    try {
      const res = await api.login({
        username_or_email: cleanEmail,
        password: password.trim(),
      });

      setIsSubmitting(false);

      if (res.access_token) {
        localStorage.setItem('vyaparmitra_token', res.access_token);
        localStorage.setItem('vyaparmitra_merchant_id', res.user.business_id);
      }

      playWelcomeAudio();

      const initials = (res.user.full_name || cleanEmail)
        .split(' ')
        .map((w) => w[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);

      const profile: UserProfile = {
        id: res.user.business_id,
        business_id: res.user.business_id,
        merchant_id: res.user.business_id,
        name: res.user.full_name || 'Merchant Partner',
        email: res.user.email,
        storeName: `${res.user.full_name || 'Merchant'}'s Store`,
        category: 'small_merchant',
        categoryLabel: 'Kirana & Retail Store',
        phone: res.user.phone || '+919876543210',
        city: 'India',
        role: res.user.role || 'owner',
        avatarInitials: initials,
        token: res.access_token,
        is_demo: false,
      };

      onLogin(profile);
    } catch (err: any) {
      setIsSubmitting(false);
      setAuthError(
        err?.message ||
          'Invalid credentials. Please check your email and password, or use OTP login below.'
      );
    }
  };

  // 2. Request OTP (Sign up with password or OTP Login)
  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setNotificationMsg(null);

    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      setAuthError('Please enter a valid email address to receive your verification code.');
      return;
    }

    if (authMode === 'signup') {
      if (!password || password.trim().length < 6) {
        setAuthError('Please create a secure password (minimum 6 characters) for your new account.');
        return;
      }
    }

    setIsSubmitting(true);

    try {
      const res = await api.requestOtp({
        email: cleanEmail,
        phone: mobileNumber.trim() || undefined,
        name: fullName.trim() || undefined,
      });

      setIsSubmitting(false);
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
      setIsSubmitting(false);
      setAuthError(err?.message || 'Failed to send verification code. Please try again.');
    }
  };

  // 3. Verify OTP (Commits created password & provisions account)
  const handleVerifyOtp = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setAuthError(null);

    const fullCode = otpCode.join('').trim();
    if (fullCode.length !== 6) {
      setAuthError('Please enter all 6 digits of the verification code.');
      return;
    }

    setIsSubmitting(true);

    try {
      const res = await api.verifyOtp({
        email: email.trim().toLowerCase(),
        otp: fullCode,
        phone: mobileNumber.trim() || undefined,
        name: fullName.trim() || undefined,
        store_id: storeId.trim() || undefined,
        password: password.trim() || undefined,
      });

      setIsSubmitting(false);

      if (res.access_token) {
        localStorage.setItem('vyaparmitra_token', res.access_token);
        localStorage.setItem('vyaparmitra_merchant_id', res.user.business_id);
      }

      playWelcomeAudio();

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
      setIsSubmitting(false);
      setAuthError(err?.message || 'Invalid or expired OTP. Please try again.');
    }
  };

  // When user selects a demo persona
  const handleSelectDemoPersona = (p: DemoPersona) => {
    setSelectedDemoPersona(p);
    setSelectedCategory(p.category);
    setFullName(p.name);
    setEmail(p.email);
    setPassword('DemoPassword123!');
    setMobileNumber(p.phone);
    setStoreId(p.id);
    setOtpSent(false);
    setOtpCode(['', '', '', '', '', '']);
    setAuthError(null);
    setNotificationMsg(`Demo persona loaded: ${p.name} (${p.id})`);
  };

  return (
    <div className="min-h-screen bg-surface bg-ambient-mesh flex flex-col justify-between transition-colors">
      {/* Top Navigation Bar */}
      <header className="px-6 py-4 flex items-center justify-between border-b border-border/40 bg-surface/80 backdrop-blur-sm sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <div className="w-8.5 h-8.5 rounded-xl bg-brand text-brand-contrast flex items-center justify-center shadow-xs select-none">
            <Store className="w-4 h-4 text-white" />
          </div>
          <span className="font-extrabold text-base text-text tracking-tight">
            Vyapar<span className="text-brand">Mitra</span>
          </span>
        </div>

        {/* Center Nav Links */}
        <nav className="hidden md:flex items-center gap-6 text-xs font-semibold text-text-muted">
          <span className="text-text hover:text-brand cursor-pointer transition-colors">Home</span>
          <span className="hover:text-brand cursor-pointer transition-colors">Features</span>
          <span className="hover:text-brand cursor-pointer transition-colors">For Merchants</span>
          <span className="hover:text-brand cursor-pointer transition-colors">Pricing</span>
        </nav>

        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Language Selector */}
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

          {/* Theme Toggle */}
          <button
            type="button"
            onClick={onToggleDarkMode}
            className="w-8.5 h-8.5 rounded-xl bg-surface-card border border-border text-text-muted hover:text-text flex items-center justify-center transition-colors"
            title="Toggle Theme"
          >
            {isDarkMode ? <Sun className="w-4 h-4 text-warning" /> : <Moon className="w-4 h-4 text-text-muted" />}
          </button>

          {/* Dedicated Log In Button */}
          <button
            type="button"
            onClick={() => {
              setAuthMode('login');
              setOtpSent(false);
              setAuthError(null);
              setNotificationMsg(null);
            }}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all border cursor-pointer ${
              authMode === 'login'
                ? 'bg-brand/10 border-brand text-brand font-extrabold shadow-2xs'
                : 'border-border text-text hover:bg-surface-muted'
            }`}
          >
            Log In
          </button>

          {/* Get Started (Sign Up) Button */}
          <button
            type="button"
            onClick={() => {
              setAuthMode('signup');
              setOtpSent(false);
              setAuthError(null);
              setNotificationMsg(null);
            }}
            className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all shadow-xs cursor-pointer ${
              authMode === 'signup'
                ? 'bg-brand text-white shadow-brand/20 ring-2 ring-brand/30'
                : 'bg-brand text-white hover:bg-brand-hover'
            }`}
          >
            <span>Get Started</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      {/* Main Split Grid */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-2 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 items-center gap-8">
        {/* Left: Brand showcase panel */}
        <LoginBrandPanel />

        {/* Right: Auth Card */}
        <div className="w-full max-w-md mx-auto">
          <div className="bg-surface-card rounded-3xl border border-border p-6 sm:p-8 shadow-fintech-lg transition-all space-y-5">
            
            {/* Top Auth Mode Tabs (Log In vs Create Account) */}
            <div className="grid grid-cols-2 p-1 bg-surface-muted border border-border rounded-2xl gap-1">
              <button
                type="button"
                onClick={() => {
                  setAuthMode('login');
                  setOtpSent(false);
                  setAuthError(null);
                  setNotificationMsg(null);
                }}
                className={`py-2 text-xs font-bold rounded-xl transition-all cursor-pointer ${
                  authMode === 'login'
                    ? 'bg-surface-card text-text shadow-xs border border-border/80'
                    : 'text-text-muted hover:text-text'
                }`}
              >
                Log In
              </button>
              <button
                type="button"
                onClick={() => {
                  setAuthMode('signup');
                  setOtpSent(false);
                  setAuthError(null);
                  setNotificationMsg(null);
                }}
                className={`py-2 text-xs font-bold rounded-xl transition-all cursor-pointer ${
                  authMode === 'signup'
                    ? 'bg-brand text-white shadow-xs'
                    : 'text-text-muted hover:text-text'
                }`}
              >
                Create Account
              </button>
            </div>

            {/* Card Header */}
            <div>
              <div className="flex items-center justify-between">
                <h2 className="text-xl sm:text-2xl font-black text-text tracking-tight">
                  {otpSent
                    ? 'Enter Verification Code'
                    : authMode === 'login'
                    ? 'Sign in with Password'
                    : authMode === 'signup'
                    ? 'Create Merchant Account'
                    : 'Sign in with OTP'}
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
                  : authMode === 'login'
                  ? 'Enter your registered email and password to access your dashboard.'
                  : authMode === 'signup'
                  ? 'Set up your store name, credentials, and password.'
                  : 'Enter your email to receive a secure 6-digit login code.'}
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

            {/* MODE 1: Email & Password Login */}
            {authMode === 'login' && !otpSent && (
              <form onSubmit={handlePasswordLogin} className="space-y-4">
                {/* Email Address */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text flex items-center justify-between">
                    <span>Email Address</span>
                    <span className="text-[11px] text-text-subtle font-normal">Registered email</span>
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

                {/* Password Input with Show/Hide Toggle */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text flex items-center justify-between">
                    <span>Password</span>
                    <button
                      type="button"
                      onClick={() => {
                        setAuthMode('otp_login');
                        setAuthError(null);
                      }}
                      className="text-[11px] font-semibold text-brand hover:underline"
                    >
                      Login via OTP instead?
                    </button>
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-text-subtle absolute left-3.5 top-3.5" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      className="w-full pl-10 pr-10 py-2.5 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text placeholder-text-subtle focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3.5 top-3.5 text-text-subtle hover:text-text cursor-pointer"
                      title={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Soundbox toggle */}
                <div className="pt-0.5 flex items-center justify-between">
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
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Logging in...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      Log In to Dashboard
                      <ArrowRight className="w-4 h-4" />
                    </span>
                  )}
                </Button>

                {/* Switch to Signup Link */}
                <div className="pt-2 text-center text-xs text-text-muted">
                  Don't have an account?{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('signup');
                      setAuthError(null);
                    }}
                    className="font-bold text-brand hover:underline"
                  >
                    Create Account
                  </button>
                </div>
              </form>
            )}

            {/* MODE 2: Sign Up (Create Account & Set Password) */}
            {authMode === 'signup' && !otpSent && (
              <form onSubmit={handleRequestOtp} className="space-y-3.5">
                {/* Full Name */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text flex items-center justify-between">
                    <span>Full Name</span>
                    <span className="text-[11px] text-text-subtle font-normal">Store Owner</span>
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
                    <span className="text-[11px] text-brand font-medium">OTP verification</span>
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

                {/* Create Password Input */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text flex items-center justify-between">
                    <span>Create Password</span>
                    <span className="text-[11px] text-brand font-medium">For future logins</span>
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-text-subtle absolute left-3.5 top-3.5" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Create a password (min 6 characters)"
                      className="w-full pl-10 pr-10 py-2.5 text-xs font-semibold rounded-xl border border-border bg-surface-muted text-text placeholder-text-subtle focus:bg-surface-card focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3.5 top-3.5 text-text-subtle hover:text-text cursor-pointer"
                      title={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Mobile Number */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-text flex items-center justify-between">
                    <span>Mobile Number</span>
                    <span className="text-[11px] text-text-subtle font-normal">Optional</span>
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
                <div className="pt-0.5 flex items-center justify-between">
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
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Sending OTP...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      Create Account &amp; Verify Code
                      <ArrowRight className="w-4 h-4" />
                    </span>
                  )}
                </Button>

                {/* Switch to Login Link */}
                <div className="pt-2 text-center text-xs text-text-muted">
                  Already have an account?{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('login');
                      setAuthError(null);
                    }}
                    className="font-bold text-brand hover:underline"
                  >
                    Log In
                  </button>
                </div>
              </form>
            )}

            {/* MODE 3: Sign In with OTP only */}
            {authMode === 'otp_login' && !otpSent && (
              <form onSubmit={handleRequestOtp} className="space-y-4">
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

                {/* Submit button */}
                <Button
                  type="submit"
                  variant="primary"
                  className="w-full py-3 justify-center text-sm font-bold shadow-fintech"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Sending OTP...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      Send Verification Code
                      <ArrowRight className="w-4 h-4" />
                    </span>
                  )}
                </Button>

                {/* Switch to Password Login */}
                <div className="pt-2 text-center text-xs text-text-muted">
                  Know your password?{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('login');
                      setAuthError(null);
                    }}
                    className="font-bold text-brand hover:underline"
                  >
                    Log In with Password
                  </button>
                </div>
              </form>
            )}

            {/* OTP Verification Step */}
            {otpSent && (
              <form onSubmit={handleVerifyOtp} className="space-y-5">
                <OtpInput
                  value={otpCode}
                  onChange={setOtpCode}
                  disabled={isSubmitting}
                />

                <div className="flex items-center justify-between text-xs pt-1">
                  <button
                    type="button"
                    onClick={() => {
                      setOtpSent(false);
                      setAuthError(null);
                    }}
                    className="inline-flex items-center gap-1 font-semibold text-text-muted hover:text-text cursor-pointer"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" />
                    Change Email / Password
                  </button>

                  {countdown > 0 ? (
                    <span className="text-text-muted tabular-nums font-medium">
                      Resend in {countdown}s
                    </span>
                  ) : (
                    <button
                      type="button"
                      onClick={handleRequestOtp}
                      disabled={isSubmitting}
                      className="font-bold text-brand hover:underline cursor-pointer"
                    >
                      Resend Code
                    </button>
                  )}
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  className="w-full py-3 justify-center text-sm font-bold shadow-fintech"
                  disabled={isSubmitting || otpCode.join('').length !== 6}
                >
                  {isSubmitting ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Verifying &amp; Creating Account...
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
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand hover:underline cursor-pointer"
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
