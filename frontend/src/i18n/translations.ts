export type Language = 'hinglish' | 'hindi' | 'english';

export const translations: Record<string, Record<Language, string>> = {
  // Navigation
  nav_dashboard: {
    hinglish: 'Dashboard',
    hindi: 'डैशबोर्ड',
    english: 'Dashboard',
  },
  nav_compare: {
    hinglish: 'Peers se Tulna',
    hindi: 'प्रतिस्पर्धा तुलना',
    english: 'Peer Benchmark',
  },
  nav_analytics: {
    hinglish: 'Analytics',
    hindi: 'व्यापार विश्लेषण',
    english: 'Analytics',
  },
  nav_products: {
    hinglish: 'Products & Stock',
    hindi: 'सामग्री व स्टॉक',
    english: 'Products & Stock',
  },
  nav_customers: {
    hinglish: 'Customers (Graahak)',
    hindi: 'ग्राहक सूची',
    english: 'Customers',
  },
  nav_forecasts: {
    hinglish: 'Sales Forecast',
    hindi: 'भविष्यवाणी (Forecast)',
    english: 'Sales Forecast',
  },
  nav_recommendations: {
    hinglish: 'Action Center',
    hindi: 'सुझाव व एक्शन',
    english: 'Action Center',
  },
  nav_copilot: {
    hinglish: 'AI Copilot',
    hindi: 'एआई व्यापार मित्र',
    english: 'AI Copilot',
  },
  nav_settings: {
    hinglish: 'Settings',
    hindi: 'सेटिंग्स',
    english: 'Settings',
  },

  // Navbar & Global
  store_name: {
    hinglish: 'Vyapar Store',
    hindi: 'व्यापार स्टोर',
    english: 'Vyapar Store',
  },
  store_category: {
    hinglish: 'FMCG & Retail • Lucknow',
    hindi: 'दैनिक सामग्री व रिटेल • लखनऊ',
    english: 'FMCG & Retail • Lucknow',
  },
  verified_merchant: {
    hinglish: 'Paytm Verified',
    hindi: 'पेटीएम सत्यापित',
    english: 'Paytm Verified',
  },
  soundbox_ready: {
    hinglish: 'Soundbox Ready:',
    hindi: 'साउंडबॉक्स चालू:',
    english: 'Soundbox Ready:',
  },
  soundbox_instant: {
    hinglish: '100% Instant Audio Alert',
    hindi: 'तत्काल ऑडियो अलर्ट',
    english: '100% Instant Audio Alert',
  },
  ask_copilot: {
    hinglish: 'Ask Copilot',
    hindi: 'मित्र से पूछें',
    english: 'Ask Copilot',
  },

  // Dashboard Page
  soundbox_banner_title: {
    hinglish: 'Paytm Soundbox 4.0 Live',
    hindi: 'पेटीएम साउंडबॉक्स 4.0 लाइव',
    english: 'Paytm Soundbox 4.0 Live',
  },
  soundbox_banner_text: {
    hinglish: '🔊 "Paytm par ₹4,250 prapt hue" • Aaj ka Total Collection: ₹45,280 (128 transactions)',
    hindi: '🔊 "पेटीएम पर ₹4,250 प्राप्त हुए" • आज का कुल कलेक्शन: ₹45,280 (128 लेनदेन)',
    english: '🔊 "Received ₹4,250 on Paytm" • Today\'s Total Collection: ₹45,280 (128 transactions)',
  },
  test_audio: {
    hinglish: 'Test Audio',
    hindi: 'ऑडियो चेक करें',
    english: 'Test Audio',
  },
  instant_settlement: {
    hinglish: '100% Instant Bank Settlement',
    hindi: 'बैंक खाते में तुरंत ट्रांसफर',
    english: '100% Instant Bank Settlement',
  },
  greeting: {
    hinglish: 'Shubh Prabhat, Merchant Ji 👋',
    hindi: 'शुभ प्रभात, व्यापारी जी 👋',
    english: 'Good Morning, Merchant 👋',
  },
  welcome_subtext: {
    hinglish: 'Aapki dukaan ka live business overview tayar hai. Sabhi metrics verified store records se update hain.',
    hindi: 'आपकी दुकान का लाइव व्यापार ब्यौरा तैयार है। सभी आंकड़े सत्यापित स्टोर रिकॉर्ड से अपडेट हैं।',
    english: 'Here is your daily business overview. All metrics are updated directly from verified store records.',
  },
  todays_brief: {
    hinglish: "Today's Brief",
    hindi: 'आज का सारांश',
    english: "Today's Brief",
  },
  priority_actions_btn: {
    hinglish: 'Priority Actions',
    hindi: 'प्राथमिक कार्य',
    english: 'Priority Actions',
  },
  daily_sales_trend: {
    hinglish: 'Daily Sales Trend (Bikri)',
    hindi: 'दैनिक बिक्री रुझान',
    english: 'Daily Sales Trend',
  },
  last_14_days: {
    hinglish: 'Last 14 recorded business days',
    hindi: 'पिछले 14 दिनों का रिकॉर्ड',
    english: 'Last 14 recorded business days',
  },
  peak_collection: {
    hinglish: 'Peak Day Collection:',
    hindi: 'सर्वाधिक बिक्री का दिन:',
    english: 'Peak Day Collection:',
  },
  deep_analytics: {
    hinglish: 'Deep Analytics',
    hindi: 'विस्तृत विश्लेषण',
    english: 'Deep Analytics',
  },
  forecast_7d_title: {
    hinglish: 'Sales Forecast • 7-Day Revenue Projection',
    hindi: 'बिक्री का अनुमान • अगले 7 दिनों का अनुमानित राजस्व',
    english: 'Sales Forecast • 7-Day Revenue Projection',
  },
  forecast_7d_subtext: {
    hinglish: 'Pichhli bikri aur demand patterns ke anusaar agle 7 dino me anumanit store revenue.',
    hindi: 'पिछली बिक्री और मांग के आधार पर अगले 7 दिनों में अनुमानित दुकान की कुल बिक्री।',
    english: 'Expected store revenue over the upcoming 7 days based on recent sales patterns.',
  },
  view_sku_forecasts: {
    hinglish: 'View SKU Forecasts',
    hindi: 'उत्पादवार अनुमान देखें',
    english: 'View SKU Forecasts',
  },
  peers_comparison: {
    hinglish: 'Peers se tulna',
    hindi: 'प्रतिस्पर्धी दुकानों से तुलना',
    english: 'Peer Benchmark Comparison',
  },
  recommended_action: {
    hinglish: 'Recommended Action:',
    hindi: 'सलाह व सुझाव:',
    english: 'Recommended Action:',
  },
  send_offer: {
    hinglish: 'Offer bhejein',
    hindi: 'ऑफर भेजें',
    english: 'Send Offer',
  },
  view_details: {
    hinglish: 'Details dekhein',
    hindi: 'विवरण देखें',
    english: 'View Details',
  },

  // Products Page
  products_title: {
    hinglish: 'Product Catalog & Demand Intelligence',
    hindi: 'उत्पाद सूची व मांग पूर्वानुमान (स्टॉक)',
    english: 'Product Catalog & Demand Intelligence',
  },
  products_subtitle: {
    hinglish: 'Monitor SKU margins, historical revenues, and 7-day predicted demand units.',
    hindi: 'प्रत्येक सामग्री का मुनाफा, पिछली बिक्री और अगले 7 दिनों की अनुमानित मांग देखें।',
    english: 'Monitor SKU margins, historical revenues, and 7-day predicted demand units.',
  },
  total_catalog: {
    hinglish: 'Total Catalog:',
    hindi: 'कुल उत्पाद:',
    english: 'Total Catalog:',
  },
  search_products_placeholder: {
    hinglish: 'Search by product name or SKU ID...',
    hindi: 'उत्पाद का नाम या SKU कोड खोजें...',
    english: 'Search by product name or SKU ID...',
  },
  all_categories: {
    hinglish: 'All Categories',
    hindi: 'सभी श्रेणियां',
    english: 'All Categories',
  },
  apply_filter: {
    hinglish: 'Apply',
    hindi: 'लागू करें',
    english: 'Apply',
  },
  col_product: {
    hinglish: 'Product / SKU',
    hindi: 'उत्पाद / सामग्री',
    english: 'Product / SKU',
  },
  col_category: {
    hinglish: 'Category',
    hindi: 'श्रेणी',
    english: 'Category',
  },
  col_unit_price: {
    hinglish: 'Price (MRP)',
    hindi: 'मूल्य (कीमत)',
    english: 'Price (MRP)',
  },
  col_margin: {
    hinglish: 'Profit Margin',
    hindi: 'मुनाफा मार्जिन',
    english: 'Profit Margin',
  },
  col_forecast_7d: {
    hinglish: '7D Demand',
    hindi: '7 दिन की मांग',
    english: '7D Demand',
  },
  col_stock_status: {
    hinglish: 'Stock Status',
    hindi: 'स्टॉक स्थिति',
    english: 'Stock Status',
  },
  col_action: {
    hinglish: 'Action',
    hindi: 'कार्रवाई',
    english: 'Action',
  },

  // Compare Tab
  compare_title: {
    hinglish: 'Peers se Tulna (Benchmark)',
    hindi: 'दुकान की प्रतिस्पर्धा से तुलना (Benchmark)',
    english: 'Peer Benchmark Comparison',
  },
  compare_subtitle: {
    hinglish: 'Compare your store against 6 core performance metrics of category peers',
    hindi: 'समान शहर व श्रेणी की अन्य दुकानों से 6 मुख्य संकेतकों पर तुलना',
    english: 'Compare your store against 6 core performance metrics of category peers',
  },
  select_shop: {
    hinglish: 'Select Shop:',
    hindi: 'दुकान चुनें:',
    english: 'Select Shop:',
  },
  whatsapp_digest: {
    hinglish: 'WhatsApp Digest',
    hindi: 'व्हाट्सएप रिपोर्ट',
    english: 'WhatsApp Digest',
  },
  overall_score: {
    hinglish: 'Overall Benchmark Score',
    hindi: 'कुल प्रदर्शन स्कोर',
    english: 'Overall Benchmark Score',
  },
  what_top_do: {
    hinglish: 'What Top 10% Performers Do',
    hindi: 'शीर्ष 10% सफल व्यापारी क्या करते हैं?',
    english: 'What Top 10% Performers Do',
  },
  top_practices_sub: {
    hinglish: 'Category leaders ke high-impact business practices aur strategies',
    hindi: 'प्रमुख सफल व्यापारियों द्वारा अपनाई गई लाभकारी रणनीतियां',
    english: 'Category leaders high-impact business practices and strategies',
  },

  // Copilot Page
  copilot_title: {
    hinglish: 'VyaparMitra Hindi AI Copilot',
    hindi: 'व्यापार मित्र एआई बिजनेस कोपायलट',
    english: 'VyaparMitra AI Business Copilot',
  },
  copilot_subtext: {
    hinglish: 'Grounded exclusively in Verified Store & Benchmark Data',
    hindi: 'आपकी दुकान के वास्तविक डेटा और फीचर स्टोर पर आधारित',
    english: 'Grounded exclusively in Verified Store & Benchmark Data',
  },
  copilot_placeholder: {
    hinglish: 'Poochiye apni dukaan ke baare mein koi bhi sawaal (e.g. Kal kitni bikri hui thi?)...',
    hindi: 'अपनी दुकान के बारे में कोई भी प्रश्न पूछें (उदा. कल कितनी बिक्री हुई थी?)...',
    english: 'Ask any question about your store (e.g. What were yesterday\'s sales?)...',
  },
  suggested: {
    hinglish: 'Suggested:',
    hindi: 'सुझाए गए प्रश्न:',
    english: 'Suggested:',
  },

  // KPI Metrics Labels
  kpi_revenue: {
    hinglish: 'Total Revenue',
    hindi: 'कुल राजस्व (बिक्री)',
    english: 'Total Revenue',
  },
  kpi_orders: {
    hinglish: 'Total Orders',
    hindi: 'कुल ऑर्डर्स',
    english: 'Total Orders',
  },
  kpi_aov: {
    hinglish: 'Average Order Value (AOV)',
    hindi: 'औसत बिल राशि (AOV)',
    english: 'Average Order Value',
  },
  kpi_units: {
    hinglish: 'Units Sold',
    hindi: 'बिके हुए सामान (Units)',
    english: 'Units Sold',
  },

  // Subtexts
  subtext_vs_prev_7d: {
    hinglish: 'vs pichhle 7 din',
    hindi: 'पिछले 7 दिनों के मुकाबले',
    english: 'vs previous 7-day period',
  },
  subtext_completed_orders: {
    hinglish: 'Total poore hue orders',
    hindi: 'कुल सफल ऑर्डर',
    english: 'Total completed orders',
  },
  subtext_avg_ticket: {
    hinglish: 'Average ticket size',
    hindi: 'प्रति ग्राहक औसत खरीदारी',
    english: 'Average ticket size',
  },
  subtext_items_moved: {
    hinglish: 'Total items moved',
    hindi: 'दुकान से बिका कुल माल',
    english: 'Total inventory items moved',
  },

  // Trends
  trend_decreasing: {
    hinglish: 'Trend: Giravat (DECREASING)',
    hindi: 'रुझान: गिरावट (कम हो रही है)',
    english: 'Trend: Decreasing',
  },
  trend_increasing: {
    hinglish: 'Trend: Badh rahi hai (INCREASING)',
    hindi: 'रुझान: वृद्धि (बढ़ रही है)',
    english: 'Trend: Increasing',
  },
  trend_stable: {
    hinglish: 'Trend: Sthir (STABLE)',
    hindi: 'रुझान: स्थिर',
    english: 'Trend: Stable',
  },

  // Benchmark metrics & badges
  repeat_customers: {
    hinglish: 'Repeat Graahak',
    hindi: 'दोहराने वाले ग्राहक',
    english: 'Repeat Customers',
  },
  avg_bill_size: {
    hinglish: 'Average Bill / Ticket Size',
    hindi: 'औसत बिल / टिकट आकार',
    english: 'Average Bill / Ticket Size',
  },
  payment_failure_rate: {
    hinglish: 'Payment Failure Rate',
    hindi: 'भुगतान विफलता दर',
    english: 'Payment Failure Rate',
  },
  status_good: {
    hinglish: 'Achha',
    hindi: 'अच्छा',
    english: 'Good',
  },
  status_fair: {
    hinglish: 'Thik',
    hindi: 'सामान्य',
    english: 'Fair',
  },
  status_attention: {
    hinglish: 'Dhyan Dein',
    hindi: 'सुधार चाहिए',
    english: 'Needs Attention',
  },

  // Priority Actions
  priority_actions_title: {
    hinglish: 'Priority Actions',
    hindi: 'सर्वोच्च प्राथमिकता वाले कार्य',
    english: 'Priority Actions',
  },
  critical_badge: {
    hinglish: 'Critical',
    hindi: 'अति-महत्वपूर्ण',
    english: 'Critical',
  },
  high_badge: {
    hinglish: 'High',
    hindi: 'उच्च',
    english: 'High',
  },
  medium_badge: {
    hinglish: 'Medium',
    hindi: 'मध्यम',
    english: 'Medium',
  },
  expected_impact_label: {
    hinglish: 'Impact:',
    hindi: 'संभावित लाभ:',
    english: 'Impact:',
  },
  review_btn: {
    hinglish: 'Review →',
    hindi: 'जांचें →',
    english: 'Review →',
  },
  open_action_center_btn: {
    hinglish: 'Open Action Center',
    hindi: 'ऐक्शन सेंटर खोलें',
    english: 'Open Action Center',
  },

  // Ask Copilot Box
  ask_copilot_box_title: {
    hinglish: 'Ask VyaparMitra Copilot',
    hindi: 'व्यापारमित्र एआई कोपायलट से पूछें',
    english: 'Ask VyaparMitra Copilot',
  },
  ask_copilot_box_sub: {
    hinglish: 'Sales, forecast, stockouts, ya Graahak ke baare mein Hindi/Hinglish me poochhein.',
    hindi: 'बिक्री, 7-दिवसीय अनुमान, स्टॉक या ग्राहकों के बारे में कुछ भी पूछें।',
    english: 'Ask anything about your sales, forecasts, stockouts, or customers.',
  },
  quick_ask_placeholder: {
    hinglish: 'e.g. Kal kitni bikri hui thi?',
    hindi: 'उदा. कल कितनी बिक्री हुई थी?',
    english: 'e.g. What were yesterday\'s sales?',
  },
  ask_btn: {
    hinglish: 'Ask Copilot',
    hindi: 'मित्र से पूछें',
    english: 'Ask Copilot',
  },

  // Analytics
  analytics_title: {
    hinglish: 'Business Intelligence & Analytics',
    hindi: 'व्यापार विश्लेषण और रिपोर्ट',
    english: 'Business Intelligence & Analytics',
  },
  analytics_sub: {
    hinglish: 'Empirical sales patterns, customer segments, category distributions, and payment methods.',
    hindi: 'बिक्री रुझान, ग्राहक वर्ग, उत्पाद श्रेणी विभाजन और भुगतान माध्यमों का संपूर्ण विवरण।',
    english: 'Empirical sales patterns, customer segments, category distributions, and payment methods.',
  },
};

/**
 * Universal text localizer for dynamic backend strings
 */
export function localizeDynamicText(text: string | null | undefined, language: Language): string {
  if (!text) return '';
  if (language === 'english') return text;

  const hindiMap: Record<string, string> = {
    // KPI labels
    'Total Revenue': 'कुल राजस्व (बिक्री)',
    'Total Orders': 'कुल ऑर्डर्स',
    'Average Order Value': 'औसत बिल राशि (AOV)',
    'Units Sold': 'कुल बिके सामान (Units)',
    'vs previous 7-day period': 'पिछले 7 दिनों के मुकाबले',
    'Total completed orders': 'कुल सफल ऑर्डर',
    'Average ticket size': 'प्रति ग्राहक औसत खरीदारी',
    'Total inventory items moved': 'दुकान से बिका कुल माल',

    // Benchmark Labels
    'Repeat Customers': 'दोहराने वाले ग्राहक',
    'Average Bill / Ticket Size': 'औसत बिल / टिकट आकार',
    'Payment Failure Rate': 'भुगतान विफलता दर',
    'Inventory Turnover': 'स्टॉक चक्र गति (Turnover)',
    'Gross Margin': 'सकल मुनाफा मार्जिन',
    'Customer Retention': 'ग्राहक जुड़ाव (Retention)',

    // Status Texts
    'Achha': 'अच्छा',
    'Thik': 'सामान्य',
    'Dhyan Dein': 'सुधार चाहिए',
    'Good': 'अच्छा',
    'Fair': 'सामान्य',
    'Needs Attention': 'सुधार चाहिए',

    // Priorities & Bands
    'CRITICAL': 'अति-गंभीर',
    'HIGH': 'उच्च',
    'MEDIUM': 'मध्यम',
    'LOW': 'कम',

    // Categories
    'Grocery, Uttar Pradesh': 'किराना व दैनिक सामग्री, उत्तर प्रदेश',
    'Grocery, Snacks & FMCG': 'किराना, स्नैक्स व दैनिक सामग्री',

    // Actions
    'Review quality and item packaging for frequently returned products': 'अक्सर वापस होने वाले सामान की गुणवत्ता और पैकेजिंग की समीक्षा करें।',
    'Introduce combo pack or loyalty incentive to lift basket size': 'औसत बिल बढ़ाने के लिए कॉम्बो पैक या लॉयल्टी छूट ऑफर शुरू करें।',
    'Encourage QR/UPI soundbox adoption to lower transaction drop-offs': 'ट्रांजेक्शन विफलता घटाने के लिए ग्राहकों को सीधे साउंडबॉक्स क्यूआर से भुगतान कराएं।',
  };

  const hinglishMap: Record<string, string> = {
    'Total Revenue': 'Total Revenue (Bikri)',
    'Total Orders': 'Total Orders',
    'Average Order Value': 'Average Order Value (AOV)',
    'Units Sold': 'Total Units Biki',
    'vs previous 7-day period': 'vs pichhle 7 din',
    'Total completed orders': 'Total poore hue orders',
    'Average ticket size': 'Average khareedari size',
    'Total inventory items moved': 'Total maal bika',
    'Repeat Customers': 'Repeat Graahak',
    'Average Bill / Ticket Size': 'Average Bill / Ticket Size',
    'Payment Failure Rate': 'Payment Failure Rate',
    'Achha': 'Achha',
    'Thik': 'Thik-thaak',
    'Dhyan Dein': 'Dhyan Dein',
  };

  if (language === 'hindi' && hindiMap[text]) {
    return hindiMap[text];
  }
  if (language === 'hinglish' && hinglishMap[text]) {
    return hinglishMap[text];
  }

  return text;
}
