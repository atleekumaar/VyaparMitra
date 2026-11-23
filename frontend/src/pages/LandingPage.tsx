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

const LANDING_COPY = {
  english: {
    nav_features: 'Features',
    nav_solutions: 'Kirana Solutions',
    nav_pricing: 'Pricing',
    nav_faq: 'FAQ',
    nav_login: 'Log In',
    nav_get_started: 'Get Started',
    hero_badge: "AI Operating System for India's 60M+ Retail Merchants",
    hero_title_1: 'Run Your Retail Store with Smart AI—',
    hero_title_2: 'Lightning-Fast POS, Digital Khata & Precise Profits',
    hero_subtitle:
      'VyaparMitra transforms traditional kirana & retail stores with 3-second POS billing, voice-enabled UPI soundbox alerts, automated customer Khata (credit ledger), and predictive stock reorders.',
    hero_cta_free: 'Get Started Free • No Credit Card Required',
    hero_cta_login: 'Log In to Store Dashboard',
    stat_1_val: '3 Seconds',
    stat_1_lbl: 'Average POS Checkout',
    stat_2_val: '100%',
    stat_2_lbl: 'Zero-Hallucination AI',
    stat_3_val: '₹0 Fee',
    stat_3_lbl: 'Free Starter Tier',
    stat_4_val: '256-Bit',
    stat_4_lbl: 'Bank-Grade Cloud Security',
    features_badge: 'Everything Your Store Needs',
    features_title: 'Complete Operating Suite for Modern Retail Merchants',
    features_subtitle:
      'Built ground-up for Indian retail workflows—from quick barcode billing to credit collection and predictive procurement.',
    feat_1_title: 'High-Speed POS & Thermal Billing',
    feat_1_desc:
      'Instant counter billing with product search, barcode reader, split payments (UPI, Cash, Credit), and 80mm thermal receipt printing with GST breakup.',
    feat_1_tag: 'GST Breakup • Double-Submit Safe',
    feat_2_title: 'Smart Soundbox Voice Alerts',
    feat_2_desc:
      'Never miss a payment during morning rush hours. Audio confirmation in Hindi, Hinglish, and English for every UPI and digital transaction.',
    feat_2_tag: 'Paytm-Style Audio • 4G Cloud Sync',
    feat_3_title: 'Digital Customer Khata & Credit Ledger',
    feat_3_desc:
      'Track customer debit balances, enforce credit limits, send automatic WhatsApp reminders, and eliminate ledger calculation errors.',
    feat_3_tag: 'Credit Limit Guard • WhatsApp Slips',
    feat_4_title: '2-Step Procurement & Goods Receipt',
    feat_4_desc:
      'Strict accounting discipline: Owner approvals issue formal Purchase Orders (PO), and inventory stock is increased only upon physical Goods Receipt.',
    feat_4_tag: 'PO Generation • Goods Receipt (GRN)',
    feat_5_title: 'Multilingual AI Copilot (English & Regional)',
    feat_5_desc:
      'Ask queries naturally like "What was yesterday\'s profit?" or "When should we reorder flour?". Zero hallucinations, grounded 100% in your store\'s live ledger.',
    feat_5_tag: 'Voice STT/TTS • Daily Morning Brief',
    feat_6_title: '7-Day Demand ML & Peer Benchmarks',
    feat_6_desc:
      'Compare your store\'s performance with city peers. Automated machine learning models forecast 7-day sales and flag seasonal stockout risks.',
    feat_6_tag: 'Local Retail Ranks • Stockout Protection',
    pricing_badge: 'Transparent Pricing',
    pricing_title: 'Simple, Transparent Plans — No Hidden Fees',
    pricing_subtitle: 'Choose the right tier for your single store or multi-branch retail network.',
    plan_starter_name: 'Kirana Starter',
    plan_starter_badge: 'Free Forever',
    plan_starter_price: '₹0',
    plan_starter_period: '/ month',
    plan_starter_desc: 'Perfect for small neighborhood retail stores getting started with digital billing.',
    plan_starter_f1: 'Unlimited POS Counter Sales',
    plan_starter_f2: 'Customer Khata (up to 100 customers)',
    plan_starter_f3: 'Thermal Receipt Printing',
    plan_starter_f4: '1 Store Branch & 2 Users',
    plan_starter_cta: 'Start Free',
    plan_pro_name: 'Retail Pro',
    plan_pro_badge: 'Full AI Suite',
    plan_pro_price: '₹399',
    plan_pro_period: '/ month',
    plan_pro_desc: 'For established retailers wanting AI forecasts, audio soundbox alerts, and auto-procurement.',
    plan_pro_f1: 'Everything in Starter + Unlimited Customers',
    plan_pro_f2: 'Smart Soundbox Audio Alert Engine',
    plan_pro_f3: '7-Day ML Demand Projections',
    plan_pro_f4: 'Multilingual Voice AI Copilot',
    plan_pro_f5: 'Two-Step PO Approval & Goods Receipt',
    plan_pro_cta: 'Launch Retail Pro',
    plan_ent_name: 'Enterprise Chain',
    plan_ent_badge: 'Multi-Store',
    plan_ent_price: '₹999',
    plan_ent_period: '/ month',
    plan_ent_desc: 'For multi-outlet retail chains and wholesale supermarket operations.',
    plan_ent_f1: 'Unlimited Branches & Cashier Counters',
    plan_ent_f2: 'Inter-Store Stock Transfers',
    plan_ent_f3: 'Granular RBAC (Owner, Manager, Staff)',
    plan_ent_f4: 'Dedicated SLA • Priority Support',
    plan_ent_cta: 'Contact Sales',
    faq_title: 'Frequently Asked Questions (FAQ)',
    faq_subtitle: 'Common questions from Indian retail store owners.',
    faqs: [
      {
        q: 'Do I need special hardware or computers to run VyaparMitra?',
        a: 'Not at all. VyaparMitra runs smoothly in any web browser on smartphones, tablets, laptops, or desktop PCs. You can also connect your existing USB or Bluetooth 80mm thermal receipt printer directly.',
      },
      {
        q: 'Is my store financial and customer data secure?',
        a: 'Yes. VyaparMitra uses 256-bit bank-grade encryption with multi-tenant database isolation. Your store records, khata balances, and sales data are private and accessible strictly by you.',
      },
      {
        q: 'Does the AI Copilot understand conversational queries?',
        a: 'Yes. Our AI Copilot understands plain English, Hinglish, and Hindi queries. You can type or speak questions regarding daily profits, customer receivables, or restocking schedules.',
      },
      {
        q: 'Can I import my existing product list and customer khata balances?',
        a: 'Yes. The Products and Customers pages feature fast CSV bulk import tools with automatic column mapping and validation, allowing you to import thousands of records in seconds.',
      },
    ],
    footer_text: 'Built with ❤️ for Indian Retail Merchants • ISO 27001 Security Standard',
  },
  hinglish: {
    nav_features: 'Features',
    nav_solutions: 'Kirana Solutions',
    nav_pricing: 'Keemat (Pricing)',
    nav_faq: 'Sawaal-Jawaab (FAQ)',
    nav_login: 'Log In',
    nav_get_started: 'Shuru Karein',
    hero_badge: 'Bharat ke 60M+ Retail Vyapariyon ke liye AI Operating System',
    hero_title_1: 'Dukaan chalayein Smart AI se—',
    hero_title_2: 'Tez Billing, Digital Khaata aur Sateek Munafa',
    hero_subtitle:
      'VyaparMitra traditional kirana aur retail dukano ko deta hai 3-second POS billing, bolne wala UPI soundbox, automatic customer Khaata (udhaar), aur stock reorder alerts.',
    hero_cta_free: 'Muft Shuru Karein • Bina Credit Card',
    hero_cta_login: 'Dukaan Dashboard me Login Karein',
    stat_1_val: '3 Seconds',
    stat_1_lbl: 'Average POS Checkout Samay',
    stat_2_val: '100%',
    stat_2_lbl: 'Zero Hallucination Sateek AI',
    stat_3_val: '₹0 Fee',
    stat_3_lbl: 'Muft Starter Tier',
    stat_4_val: '256-Bit',
    stat_4_lbl: 'Bank-Grade Suraksha',
    features_badge: 'Aapki Dukaan ki Har Zaroorat',
    features_title: 'Modern Retail Vyapariyon ke liye Complete Operating Suite',
    features_subtitle:
      'Khaas taur par Indian retail dukano ke liye banaya gaya—fast barcode billing se lekar udhaar collection aur stock reorder tak.',
    feat_1_title: 'Superfast POS aur Thermal Billing',
    feat_1_desc:
      'Counter par turant billing: item search, barcode reader, split payments (UPI, Cash, Udhaar) aur GST invoice receipt print.',
    feat_1_tag: 'GST Breakup • Double-Submit Suraksha',
    feat_2_title: 'Smart Soundbox Voice Alerts',
    feat_2_desc:
      'Bheed-bhaad ke samay koi payment miss na ho. Har digital aur UPI transaction par Hindi, Hinglish aur English me bolkar batata hai.',
    feat_2_tag: 'Paytm-Style Audio • Cloud Sync',
    feat_3_title: 'Digital Customer Khaata aur Udhaar Ledger',
    feat_3_desc:
      'Har graahak ka baaki hisab rakhein, credit limit set karein, automated WhatsApp payment reminder bhejein aur hisab me galti khatam karein.',
    feat_3_tag: 'Credit Limit Alert • WhatsApp Parchi',
    feat_4_title: '2-Step Procurement aur Goods Receipt',
    feat_4_desc:
      'Hisaab-kitaab me full discipline: Mal order karne ke liye Purchase Order (PO) bane aur godown me delivery aane par hi stock bade.',
    feat_4_tag: 'PO Generation • Goods Receipt (GRN)',
    feat_5_title: 'Apni Bhasha me AI Vyapar Copilot',
    feat_5_desc:
      'Seedhe bolkar ya type karke poochein: "Kal kitna munafa hua?" ya "Aata kab reorder karna hai?". Live ledger se 100% sateek jawaab.',
    feat_5_tag: 'Voice Awaaz Se Kaam • Rozana Morning Report',
    feat_6_title: '7-Din ki Demand Prediction aur Peer Comparison',
    feat_6_desc:
      'Apne shehar ki doosri dukano se tulna karein. Smart AI aage ke 7 dino ki bikri predict karta hai taaki zaroori samaan out-of-stock na ho.',
    feat_6_tag: 'Local Retail Ranking • Stockout Suraksha',
    pricing_badge: 'Saaf aur Seedhi Keemat',
    pricing_title: 'Simple Plans — Koi Hidden Charges Nahi',
    pricing_subtitle: 'Apni single dukaan ya multi-branch supermarket ke hisab se sahi plan chunein.',
    plan_starter_name: 'Kirana Starter',
    plan_starter_badge: 'Hamesha Muft',
    plan_starter_price: '₹0',
    plan_starter_period: '/ mahina',
    plan_starter_desc: 'Chhoti kirana dukano ke liye jo digital billing shuru karna chahti hain.',
    plan_starter_f1: 'Unlimited POS Counter Sales',
    plan_starter_f2: 'Customer Khaata (100 graahak tak)',
    plan_starter_f3: 'Thermal Receipt Printing',
    plan_starter_f4: '1 Dukaan Branch aur 2 Staff',
    plan_starter_cta: 'Muft Shuru Karein',
    plan_pro_name: 'Retail Pro',
    plan_pro_badge: 'Full AI Suite',
    plan_pro_price: '₹399',
    plan_pro_period: '/ mahina',
    plan_pro_desc: 'Badhti dukano ke liye jinhe AI predictions, soundbox alerts aur smart khareed chahiye.',
    plan_pro_f1: 'Starter ke sabhi features + Unlimited Graahak',
    plan_pro_f2: 'Smart Soundbox Audio Alert Engine',
    plan_pro_f3: '7-Din ki AI Bikri Forecast',
    plan_pro_f4: 'Voice AI Copilot Apni Bhasha Me',
    plan_pro_f5: 'Purchase Order Approval aur Goods Receipt',
    plan_pro_cta: 'Retail Pro Shuru Karein',
    plan_ent_name: 'Enterprise Chain',
    plan_ent_badge: 'Multi-Store',
    plan_ent_price: '₹999',
    plan_ent_period: '/ mahina',
    plan_ent_desc: 'Kayi branches, wholesale aur supermarket chain chalaane ke liye.',
    plan_ent_f1: 'Unlimited Branches aur Billing Counters',
    plan_ent_f2: 'Ek branch se doosri branch stock transfer',
    plan_ent_f3: 'Staff Permissions (Malik, Manager, Cashier)',
    plan_ent_f4: 'Dedicated Account Manager • 24x7 Support',
    plan_ent_cta: 'Sampark Karein',
    faq_title: 'Aksar Pooche Jaane Wale Sawaal (FAQ)',
    faq_subtitle: 'Indian retail vyapariyon ke aam sawaal aur jawaab.',
    faqs: [
      {
        q: 'Kya VyaparMitra chalane ke liye mehenga computer ya hardware chahiye?',
        a: 'Bilkul nahi! VyaparMitra kisi bhi mobile, tablet, laptop ya desktop browser par asani se chalta hai. Aap apna koi bhi USB ya Bluetooth receipt printer bhi jod sakte hain.',
      },
      {
        q: 'Kya meri dukaan aur graahako ka data surakshit hai?',
        a: 'Haan, 100% surakshit hai. VyaparMitra 256-bit bank-grade encryption aur isolated cloud database use karta hai. Aapka data sirf aap dekh sakte hain.',
      },
      {
        q: 'Kya AI Copilot meri aam bolchal ki bhasha samajhta hai?',
        a: 'Haan! Copilot Hindi, Hinglish aur English poori tarah samajhta hai. Aap type karke ya aawaz se poochein aur turant sateek hisab paayein.',
      },
      {
        q: 'Kya main apne purane product aur customer udhaar import kar sakta hoon?',
        a: 'Haan, Products aur Customers page par fast CSV bulk import hai jisse hazaron items aur hisab kuch seconds me load ho jaate hain.',
      },
    ],
    footer_text: 'Bharat ke Retail Vyapariyon ke liye banaya gaya ❤️ • ISO 27001 Suraksha Standard',
  },
  hindi: {
    nav_features: 'सुविधाएं (Features)',
    nav_solutions: 'किराना समाधान',
    nav_pricing: 'मूल्य (Pricing)',
    nav_faq: 'प्रश्नोत्तरी (FAQ)',
    nav_login: 'लॉग इन करें',
    nav_get_started: 'शुरू करें',
    hero_badge: 'भारत के 60M+ खुदरा व्यापारियों के लिए AI ऑपरेटिंग सिस्टम',
    hero_title_1: 'दुकान चलाएं स्मार्ट AI से—',
    hero_title_2: 'तेज़ बिलिंग, डिजिटल खाता और सटीक मुनाफा',
    hero_subtitle:
      'व्यापार मित्र पारंपरिक किराना और रिटेल दुकानों को देता है 3-सेकंड POS बिलिंग, बोलने वाला UPI साउंडबॉक्स, ऑटोमैटिक ग्राहक खाता (उधार) और सटीक स्टॉक सुझाव।',
    hero_cta_free: 'मुफ्त शुरू करें • बिना क्रेडिट कार्ड',
    hero_cta_login: 'दुकान डैशबोर्ड में लॉगिन करें',
    stat_1_val: '3 सेकंड',
    stat_1_lbl: 'औसत POS चेकआउट समय',
    stat_2_val: '100%',
    stat_2_lbl: 'सटीक शून्य-भ्रम AI',
    stat_3_val: '₹0 शुल्क',
    stat_3_lbl: 'मुफ्त शुरुआत टियर',
    stat_4_val: '256-बिट',
    stat_4_lbl: 'बैंक-स्तरीय क्लाउड सुरक्षा',
    features_badge: 'आपकी दुकान की हर ज़रूरत',
    features_title: 'आधुनिक रिटेल व्यापारियों के लिए संपूर्ण ऑपरेटिंग सिस्टम',
    features_subtitle:
      'भारतीय रिटेल दुकानों के लिए विशेष रूप से निर्मित—तेज़ बारकोड बिलिंग से लेकर उधार वसूली और सटीक माल खरीद तक।',
    feat_1_title: 'सुपरफ़ास्ट POS एवं थर्मल बिलिंग',
    feat_1_desc:
      'काउंटर पर तुरंत बिलिंग: उत्पाद खोज, बारकोड स्कैनर, स्प्लिट भुगतान (UPI, नकद, उधार) और GST बिल रसीद प्रिंट।',
    feat_1_tag: 'GST विवरण • सुरक्षित बिलिंग',
    feat_2_title: 'स्मार्ट साउंडबॉक्स वॉइस अलर्ट',
    feat_2_desc:
      'दुकान की भीड़ में कोई पेमेंट छूटेगी नहीं। हर डिजिटल और UPI भुगतान पर हिंदी, हिंग्लिश व अंग्रेज़ी में बोलकर सूचना।',
    feat_2_tag: 'पेटीएम-स्टाइल साउंडबॉक्स • क्लाउड सिंक',
    feat_3_title: 'डिजिटल ग्राहक खाता व उधार बही',
    feat_3_desc:
      'प्रत्येक ग्राहक का बकाया ट्रैक करें, क्रेडिट सीमा निर्धारित करें, स्वचालित WhatsApp रिमाइंडर भेजें और बहीखाता की गलतियां मिटाएं।',
    feat_3_tag: 'उधार सीमा चेतावनी • WhatsApp पर्ची',
    feat_4_title: '2-चरणीय खरीद एवं माल प्राप्ति',
    feat_4_desc:
      'सख्त लेखा अनुशासन: मालिक की स्वीकृति पर औपचारिक परचेज ऑर्डर (PO) बने और दुकान में माल आने पर ही स्टॉक बढ़े।',
    feat_4_tag: 'PO निर्माण • माल प्राप्ति रसीद (GRN)',
    feat_5_title: 'बहुभाषी AI व्यापार मित्र (Copilot)',
    feat_5_desc:
      'स्वाभाविक रूप से पूछें: "कल कितना मुनाफा हुआ?" या "आटा कब मंगवाना है?". दुकान के लाइव बहीखाते से 100% सटीक उत्तर।',
    feat_5_tag: 'आवाज़ से निर्देश • दैनिक प्रातः रिपोर्ट',
    feat_6_title: '7-दिवसीय मांग पूर्वानुमान एवं तुलना',
    feat_6_desc:
      'अपने शहर की अन्य दुकानों से प्रदर्शन की तुलना करें। मशीन लर्निंग मॉडल अगले 7 दिनों की बिक्री का सटीक अनुमान लगाते हैं।',
    feat_6_tag: 'स्थानीय रिटेल रैंकिंग • स्टॉकआउट सुरक्षा',
    pricing_badge: 'स्पष्ट मूल्य निर्धारण',
    pricing_title: 'सरल और पारदर्शी प्लान — कोई छुपा हुआ शुल्क नहीं',
    pricing_subtitle: 'अपनी एकल दुकान या बहु-शाखा सुपरमार्केट के अनुसार सही प्लान चुनें।',
    plan_starter_name: 'किराना स्टार्टर',
    plan_starter_badge: 'हमेशा मुफ्त',
    plan_starter_price: '₹0',
    plan_starter_period: '/ माह',
    plan_starter_desc: 'छोटी रिटेल दुकानों के लिए जो डिजिटल बिलिंग शुरू करना चाहती हैं।',
    plan_starter_f1: 'असीमित POS काउंटर बिक्री',
    plan_starter_f2: 'ग्राहक खाता (100 ग्राहकों तक)',
    plan_starter_f3: 'थर्मल रसीद प्रिंटिंग',
    plan_starter_f4: '1 स्टोर शाखा व 2 स्टाफ सदस्य',
    plan_starter_cta: 'मुफ्त शुरू करें',
    plan_pro_name: 'रिटेल प्रो',
    plan_pro_badge: 'संपूर्ण AI सूट',
    plan_pro_price: '₹399',
    plan_pro_period: '/ माह',
    plan_pro_desc: 'सक्रिय व्यापारियों के लिए जिन्हें AI पूर्वानुमान, साउंडबॉक्स अलर्ट और ऑटो-खरीद चाहिए।',
    plan_pro_f1: 'स्टार्टर के सभी फीचर्स + असीमित ग्राहक',
    plan_pro_f2: 'स्मार्ट साउंडबॉक्स वॉइस अलर्ट इंजन',
    plan_pro_f3: '7-दिवसीय AI बिक्री पूर्वानुमान',
    plan_pro_f4: 'बहुभाषी वॉइस AI व्यापार मित्र',
    plan_pro_f5: 'PO स्वीकृति एवं माल प्राप्ति रसीद',
    plan_pro_cta: 'रिटेल प्रो शुरू करें',
    plan_ent_name: 'एंटरप्राइज चेन',
    plan_ent_badge: 'मल्टी-स्टोर',
    plan_ent_price: '₹999',
    plan_ent_period: '/ माह',
    plan_ent_desc: 'कई शाखाओं, थोक और सुपरमार्केट चेन के संचालन के लिए।',
    plan_ent_f1: 'असीमित शाखाएं व बिलिंग काउंटर',
    plan_ent_f2: 'शाखाओं के बीच सीधा स्टॉक ट्रांसफर',
    plan_ent_f3: 'कर्मचारी अनुमतियां (मालिक, मैनेजर, कैशियर)',
    plan_ent_f4: 'समर्पित अकाउंट मैनेजर • 24x7 सहायता',
    plan_ent_cta: 'संपर्क करें',
    faq_title: 'अक्सर पूछे जाने वाले सवाल (FAQ)',
    faq_subtitle: 'भारतीय रिटेल दुकानदारों के प्रमुख सवाल और उनके जवाब।',
    faqs: [
      {
        q: 'क्या व्यापार मित्र चलाने के लिए विशेष कंप्यूटर या हार्डवेयर चाहिए?',
        a: 'बिल्कुल नहीं! व्यापार मित्र किसी भी स्मार्टफोन, टैबलेट, लैपटॉप या कंप्यूटर के ब्राउज़र पर आसानी से चलता है। आप अपना मौजूदा 80mm थर्मल रसीद प्रिंटर भी सीधे जोड़ सकते हैं।',
      },
      {
        q: 'क्या मेरी दुकान और ग्राहकों का वित्तीय डेटा सुरक्षित है?',
        a: 'हाँ, 100% सुरक्षित है। व्यापार मित्र 256-बिट बैंक-स्तरीय एन्क्रिप्शन का उपयोग करता है। आपका खाता और बिक्री डेटा पूर्णतः गोपनीय और केवल आपके लिए सुलभ है।',
      },
      {
        q: 'क्या AI व्यापार मित्र आम बातचीत की भाषा समझता है?',
        a: 'हाँ! हमारा AI हिंदी, हिंग्लिश और अंग्रेज़ी में पूछे गए सवाल समझता है। आप बोलकर या टाइप करके दैनिक मुनाफे या स्टॉक के बारे में पूछ सकते हैं।',
      },
      {
        q: 'क्या मैं अपने पुराने उत्पाद और ग्राहकों का बकाया खाता आयात कर सकता हूँ?',
        a: 'हाँ, प्रोडक्ट्स और ग्राहक पृष्ठ पर तेज़ CSV बल्क आयात की सुविधा है, जिससे हज़ारों रिकॉर्ड्स कुछ ही सेकंड में आयात हो जाते हैं।',
      },
    ],
    footer_text: 'भारतीय खुदरा व्यापारियों के लिए समर्पित ❤️ • ISO 27001 सुरक्षा मानक',
  },
};

export const LandingPage: React.FC<LandingPageProps> = ({
  onGetStarted,
  onLogin,
  isDarkMode,
  onToggleDarkMode,
}) => {
  const { language, setLanguage } = useLanguage();
  const [activeFaq, setActiveFaq] = useState<number | null>(null);
  const [backendWarmedUp, setBackendWarmedUp] = useState<boolean>(false);

  const t = LANDING_COPY[language] || LANDING_COPY.english;

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
              {t.nav_features}
            </a>
            <a href="#solutions" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              {t.nav_solutions}
            </a>
            <a href="#pricing" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              {t.nav_pricing}
            </a>
            <a href="#faq" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              {t.nav_faq}
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
                  className={`px-2 sm:px-2.5 py-1 rounded-lg transition-all text-[11px] sm:text-xs cursor-pointer ${
                    language === lang
                      ? 'bg-surface-card text-text shadow-2xs font-bold ring-1 ring-border'
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
              className="w-8.5 h-8.5 rounded-xl bg-surface-card border border-border text-text-muted hover:text-text flex items-center justify-center transition-colors shadow-2xs cursor-pointer"
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
              {t.nav_login}
            </button>

            {/* Launch App Button */}
            <Button
              variant="primary"
              size="sm"
              onClick={onGetStarted}
              className="hidden sm:inline-flex items-center gap-1.5 font-bold shadow-fintech-sm"
            >
              <span>{t.nav_get_started}</span>
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
            <span>{t.hero_badge}</span>
            {backendWarmedUp && (
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.2 rounded-full border border-emerald-500/30">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Live Cloud Ready
              </span>
            )}
          </div>

          {/* Main Headline */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-text tracking-tight max-w-4xl mx-auto leading-tight sm:leading-tight">
            {t.hero_title_1}
            <br />
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
              {t.hero_title_2}
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mt-5 text-base sm:text-lg text-text-muted max-w-2xl mx-auto leading-relaxed">
            {t.hero_subtitle}
          </p>

          {/* Action CTAs */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3.5">
            <Button
              variant="primary"
              size="lg"
              onClick={onGetStarted}
              className="w-full sm:w-auto px-7 py-3 text-sm font-bold shadow-fintech-md flex items-center justify-center gap-2 group"
            >
              <span>{t.hero_cta_free}</span>
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Button>
            <button
              type="button"
              onClick={onLogin}
              className="w-full sm:w-auto px-6 py-3 rounded-xl border border-border bg-surface-card hover:bg-surface-muted text-sm font-bold text-text transition-colors flex items-center justify-center gap-2 shadow-2xs cursor-pointer"
            >
              <Store className="w-4 h-4 text-blue-600" />
              <span>{t.hero_cta_login}</span>
            </button>
          </div>

          {/* Social Proof Strip */}
          <div className="mt-12 pt-8 border-t border-border/80 max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-blue-600 dark:text-blue-400">{t.stat_1_val}</div>
              <div className="text-xs text-text-subtle font-medium mt-0.5">{t.stat_1_lbl}</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">{t.stat_2_val}</div>
              <div className="text-xs text-text-subtle font-medium mt-0.5">{t.stat_2_lbl}</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-purple-600 dark:text-purple-400">{t.stat_3_val}</div>
              <div className="text-xs text-text-subtle font-medium mt-0.5">{t.stat_3_lbl}</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-amber-500">{t.stat_4_val}</div>
              <div className="text-xs text-text-subtle font-medium mt-0.5">{t.stat_4_lbl}</div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section id="features" className="py-16 md:py-24 bg-surface-muted/50 border-y border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <h2 className="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-2">
              {t.features_badge}
            </h2>
            <h3 className="text-2xl sm:text-4xl font-extrabold text-text tracking-tight">
              {t.features_title}
            </h3>
            <p className="mt-3 text-sm text-text-muted">
              {t.features_subtitle}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Feature 1: POS & Thermal Billing */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-blue-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-4">
                <ShoppingCart className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">{t.feat_1_title}</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                {t.feat_1_desc}
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-blue-600 dark:text-blue-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{t.feat_1_tag}</span>
              </div>
            </div>

            {/* Feature 2: Smart Soundbox & UPI */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-emerald-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-4">
                <Volume2 className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">{t.feat_2_title}</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                {t.feat_2_desc}
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{t.feat_2_tag}</span>
              </div>
            </div>

            {/* Feature 3: Digital Khata & Udhaar */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-purple-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-4">
                <Users className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">{t.feat_3_title}</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                {t.feat_3_desc}
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-purple-600 dark:text-purple-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{t.feat_3_tag}</span>
              </div>
            </div>

            {/* Feature 4: Two-Step Procurement */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-amber-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-500 flex items-center justify-center mb-4">
                <Truck className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">{t.feat_4_title}</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                {t.feat_4_desc}
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-amber-600 dark:text-amber-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{t.feat_4_tag}</span>
              </div>
            </div>

            {/* Feature 5: Multilingual AI Copilot */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-indigo-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4">
                <Bot className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">{t.feat_5_title}</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                {t.feat_5_desc}
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-indigo-600 dark:text-indigo-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{t.feat_5_tag}</span>
              </div>
            </div>

            {/* Feature 6: Demand Forecasts & Benchmarks */}
            <div className="p-6 rounded-2xl bg-surface-card border border-border shadow-fintech-sm hover:border-cyan-500/40 transition-all">
              <div className="w-12 h-12 rounded-xl bg-cyan-50 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400 flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-text mb-2">{t.feat_6_title}</h4>
              <p className="text-xs text-text-muted leading-relaxed mb-4">
                {t.feat_6_desc}
              </p>
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-cyan-600 dark:text-cyan-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{t.feat_6_tag}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Solutions Anchor Section */}
      <section id="solutions" className="py-12 bg-surface text-center">
        <div className="max-w-4xl mx-auto px-4">
          <Badge variant="brand" className="mb-3">{t.nav_solutions}</Badge>
          <h3 className="text-xl sm:text-2xl font-bold text-text">
            {language === 'hindi'
              ? 'किराना, जनरल स्टोर एवं थोक व्यापारियों के लिए विशेष समाधान'
              : language === 'hinglish'
              ? 'Kirana, General Store aur Wholesalers ke liye tailored solutions'
              : 'Tailored Solutions for Kirana, General Stores & Wholesalers'}
          </h3>
          <p className="text-xs text-text-muted mt-2 max-w-xl mx-auto">
            {language === 'hindi'
              ? 'हर प्रकार के खुदरा व्यापार के लिए उपयुक्त — चाहे वह एकल काउंटर किराना हो या बहु-शाखा सुपरमार्केट।'
              : language === 'hinglish'
              ? 'Single counter kirana ho ya multi-branch supermarket, har retail vyapar ke liye seamless setup.'
              : 'Designed for single counter kiranas up to multi-outlet supermarket networks.'}
          </p>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-16 md:py-24 bg-surface-muted/30 border-t border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-2">
              {t.pricing_badge}
            </h2>
            <h3 className="text-2xl sm:text-4xl font-extrabold text-text tracking-tight">
              {t.pricing_title}
            </h3>
            <p className="mt-3 text-sm text-text-muted">
              {t.pricing_subtitle}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Starter Plan */}
            <div className="p-6 rounded-3xl bg-surface-card border border-border shadow-fintech-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-bold text-text">{t.plan_starter_name}</span>
                  <Badge variant="neutral">{t.plan_starter_badge}</Badge>
                </div>
                <div className="text-3xl font-black text-text mb-2">
                  {t.plan_starter_price} <span className="text-xs font-normal text-text-muted">{t.plan_starter_period}</span>
                </div>
                <p className="text-xs text-text-muted mb-6">{t.plan_starter_desc}</p>
                <ul className="space-y-2.5 text-xs text-text">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>{t.plan_starter_f1}</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>{t.plan_starter_f2}</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>{t.plan_starter_f3}</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>{t.plan_starter_f4}</span>
                  </li>
                </ul>
              </div>
              <Button
                variant="outline"
                className="w-full mt-8 font-bold"
                onClick={onGetStarted}
              >
                {t.plan_starter_cta}
              </Button>
            </div>

            {/* Retail Pro Plan (Highlighted) */}
            <div className="p-6 rounded-3xl bg-surface-card border-2 border-blue-600 shadow-fintech-lg relative flex flex-col justify-between">
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-blue-600 text-white text-[10px] font-extrabold uppercase tracking-wider shadow-xs">
                {language === 'hindi' ? 'सबसे लोकप्रिय' : language === 'hinglish' ? 'Sabse Popular' : 'Most Popular'}
              </div>
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-bold text-text">{t.plan_pro_name}</span>
                  <Badge variant="brand">{t.plan_pro_badge}</Badge>
                </div>
                <div className="text-3xl font-black text-text mb-2">
                  {t.plan_pro_price} <span className="text-xs font-normal text-text-muted">{t.plan_pro_period}</span>
                </div>
                <p className="text-xs text-text-muted mb-6">{t.plan_pro_desc}</p>
                <ul className="space-y-2.5 text-xs text-text">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>{t.plan_pro_f1}</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>{t.plan_pro_f2}</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>{t.plan_pro_f3}</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>{t.plan_pro_f4}</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>{t.plan_pro_f5}</span>
                  </li>
                </ul>
              </div>
              <Button
                variant="primary"
                className="w-full mt-8 font-bold shadow-fintech-md"
                onClick={onGetStarted}
              >
                {t.plan_pro_cta}
              </Button>
            </div>

            {/* Enterprise Chain */}
            <div className="p-6 rounded-3xl bg-surface-card border border-border shadow-fintech-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-bold text-text">{t.plan_ent_name}</span>
                  <Badge variant="neutral">{t.plan_ent_badge}</Badge>
                </div>
                <div className="text-3xl font-black text-text mb-2">
                  {t.plan_ent_price} <span className="text-xs font-normal text-text-muted">{t.plan_ent_period}</span>
                </div>
                <p className="text-xs text-text-muted mb-6">{t.plan_ent_desc}</p>
                <ul className="space-y-2.5 text-xs text-text">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-purple-600 shrink-0" />
                    <span>{t.plan_ent_f1}</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-purple-600 shrink-0" />
                    <span>{t.plan_ent_f2}</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-purple-600 shrink-0" />
                    <span>{t.plan_ent_f3}</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-purple-600 shrink-0" />
                    <span>{t.plan_ent_f4}</span>
                  </li>
                </ul>
              </div>
              <Button
                variant="outline"
                className="w-full mt-8 font-bold"
                onClick={onGetStarted}
              >
                {t.plan_ent_cta}
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-16 md:py-20 bg-surface border-t border-border">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-2xl sm:text-3xl font-extrabold text-text">
              {t.faq_title}
            </h3>
            <p className="text-xs text-text-muted mt-2">
              {t.faq_subtitle}
            </p>
          </div>

          <div className="space-y-3">
            {t.faqs.map((faq, i) => (
              <div
                key={i}
                className="rounded-2xl bg-surface-card border border-border/80 overflow-hidden shadow-2xs transition-colors"
              >
                <button
                  type="button"
                  onClick={() => toggleFaq(i)}
                  className="w-full p-4 text-left flex items-center justify-between text-xs sm:text-sm font-bold text-text hover:text-blue-600 transition-colors cursor-pointer"
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
            {t.footer_text}
          </div>
          <div className="flex items-center gap-4 text-text-muted">
            <button type="button" onClick={onLogin} className="hover:text-text cursor-pointer">
              {t.nav_login}
            </button>
            <button type="button" onClick={onGetStarted} className="hover:text-text cursor-pointer">
              {t.nav_get_started}
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};
