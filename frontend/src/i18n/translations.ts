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
    hinglish: 'Vyapar Kirana Store',
    hindi: 'व्यापार किराना स्टोर',
    english: 'Vyapar Kirana Store',
  },
  store_category: {
    hinglish: 'FMCG, Retail & Kirana • Lucknow',
    hindi: 'किराना व दैनिक सामग्री • लखनऊ',
    english: 'FMCG, Retail & Kirana • Lucknow',
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
    hinglish: 'Aapki dukaan ka commercial overview tayar hai. Sabhi metrics Feature Store aur ML models se verified hain.',
    hindi: 'आपकी दुकान का वाणिज्यिक ब्यौरा तैयार है। सभी आंकड़े फीचर स्टोर और एमएल मॉडल से सत्यापित हैं।',
    english: 'Here is your daily commercial overview. All metrics are verified against the Feature Store and ML models.',
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
    hinglish: 'Phase 3 Predictive AI • 7-Day Forecast',
    hindi: 'भविष्यवाणी • अगले 7 दिनों का अनुमानित राजस्व',
    english: 'Phase 3 Predictive AI • 7-Day Forecast',
  },
  forecast_7d_subtext: {
    hinglish: 'Autoregressive ML models ke anusaar agle 7 dino me anumanit store revenue.',
    hindi: 'मशीन लर्निंग मॉडल के अनुसार अगले 7 दिनों में अनुमानित दुकान की कुल बिक्री।',
    english: 'Expected store revenue over the upcoming 7 days based on ML demand patterns.',
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
  zero_hallucination: {
    hinglish: 'Zero Hallucination',
    hindi: '100% सत्यापित उत्तर',
    english: 'Zero Hallucination',
  },
  copilot_subtext: {
    hinglish: 'Grounded exclusively in Phase 1-4 Feature Store & Benchmark Data',
    hindi: 'आपकी दुकान के वास्तविक डेटा और फीचर स्टोर पर आधारित',
    english: 'Grounded exclusively in Phase 1-4 Feature Store & Benchmark Data',
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
};
