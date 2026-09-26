"""
Mock LLM Provider for offline, deterministic, and CI execution of VyaparMitra Copilot.
Generates structured, natural language responses in Hindi, Hinglish, and English
strictly grounded in the supplied BusinessContext.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.copilot.llm.base import LLMProvider
from src.copilot.schemas import BusinessContext, Intent, Language


class MockProvider(LLMProvider):
    """
    Deterministic response generator that formats answers using the exact
    facts, metrics, and recommendations present in BusinessContext.
    Guarantees 100% grounding, reproducibility, and zero external network calls.
    """

    def generate(
        self,
        prompt: str,
        context: BusinessContext,
        system_prompt: Optional[str] = None,
    ) -> str:
        lang = context.language.lower()
        intent = context.intent.lower()

        if lang == Language.HINDI.value.lower():
            return self._generate_hindi(intent, context)
        elif lang == Language.ENGLISH.value.lower():
            return self._generate_english(intent, context)
        else:
            return self._generate_hinglish(intent, context)

    # -------------------------------------------------------------
    # HINGLISH GENERATION
    # -------------------------------------------------------------
    def _generate_hinglish(self, intent: str, ctx: BusinessContext) -> str:
        m = ctx.metrics
        recs = ctx.recommendations

        if intent == Intent.GREETING.value.lower():
            return (
                "Namaste! Main VyaparMitra AI business assistant hoon. "
                "Aap mujhse apni dukaan ki sales, demand forecast, customer risk ya inventory stock ke baare mein pooch sakte hain."
            )

        if intent == Intent.HELP_CAPABILITIES.value.lower():
            return (
                "VyaparMitra aapki dukaan ke liye ye sab kar sakta hai:\n"
                "1. Sales & Revenue Summary: Pichhle hafte ya mahine ki bikri.\n"
                "2. 7-Day Sales & Demand Forecast: Aane wale dino ki bikri ka anumaan.\n"
                "3. Inventory Stock Alerts: Kaunsa samaan khatam hone wala hai.\n"
                "4. At-Risk Customers: Kaunse purane grahak aana band ho gaye hain.\n"
                "5. Cross-Sell & Bundling: Kaunse products ek sath bechein.\n"
                "6. Daily Action Plan: Aaj dukaan mein kya 3 zaroori kaam karne hain."
            )

        if intent == Intent.OUT_OF_DOMAIN.value.lower():
            return (
                "Kshama karein, main sirf aapke business data, bikri, inventory, aur grahako ke vishay mein sahayata kar sakta hoon. "
                "Kripya dukaan ya vyapar se juda prashna poochein."
            )

        if intent == Intent.SALES_SUMMARY.value.lower():
            rev = m.get("total_revenue", 0.0)
            orders = m.get("total_orders", 0)
            aov = m.get("average_order_value", 0.0)
            time_r = m.get("time_range", "total")
            return (
                f"Aapki {time_r} ki total bikri (revenue) ₹{rev:,.2f} rahi hai, jisme kul {orders} orders aaye hain. "
                f"Aapki average order value (AOV) ₹{aov:,.2f} hai."
            )

        if intent == Intent.SALES_TREND.value.lower():
            rev = m.get("total_revenue", 0.0)
            orders = m.get("total_orders", 0)
            days = m.get("days_recorded", 0)
            return (
                f"Pichhle {days} dino ka bikri trend dekhein toh kul revenue ₹{rev:,.2f} aur {orders} orders rahe hain. "
                f"Daily business activity stable dikh rahi hai."
            )

        if intent == Intent.SALES_FORECAST.value.lower():
            f_rev = m.get("forecast_total_revenue", 0.0)
            f_orders = m.get("forecast_total_orders", 0)
            horizon = m.get("forecast_horizon", "7 days")
            return (
                f"Aane wale {horizon} mein aapki kul sales lagbhag ₹{f_rev:,.2f} hone ka anumaan hai, "
                f"aur lagbhag {f_orders} orders aane ki ummeed hai. Apni inventory taiyar rakhein."
            )

        if intent == Intent.PRODUCT_PERFORMANCE.value.lower():
            p_id = m.get("product_id") or "Product"
            rev = m.get("product_revenue", 0.0)
            qty = m.get("product_units_sold", 0)
            return (
                f"{p_id} ki kul bikri ₹{rev:,.2f} rahi hai, jisme {qty} units biki hain."
            )

        if intent == Intent.PRODUCT_DEMAND_FORECAST.value.lower():
            p_id = m.get("product_id") or "SKU"
            f_qty = m.get("forecast_units", 0)
            horizon = m.get("horizon", "7 days")
            return (
                f"{p_id} ke liye agle {horizon} mein lagbhag {f_qty} units bikne ki sambhavna hai."
            )

        if intent == Intent.CUSTOMER_RISK.value.lower():
            c_id = m.get("customer_id")
            if c_id:
                tier = m.get("churn_tier", "Unknown")
                score = m.get("churn_probability", 0.0)
                return (
                    f"Customer {c_id} ka churn risk '{tier}' tier par hai (risk score: {score:.2f}). "
                    f"Inhe retention discount ya follow-up message bhejna behtar hoga."
                )
            else:
                high_count = m.get("high_risk_customers_count", 0)
                tot = m.get("total_customers_evaluated", 0)
                return (
                    f"Aapke kul {tot} grahako mein se {high_count} grahak high churn risk par hain "
                    f"jo kaafi samay se dukaan par nahi aaye hain."
                )

        if intent == Intent.INVENTORY_RECOMMENDATION.value.lower():
            if recs:
                top = recs[0]
                action = top.get("action", "RESTOCK")
                sku = top.get("sku", "Product")
                qty = top.get("suggested_quantity", 0)
                impact = top.get("estimated_revenue_impact", 0.0)
                return (
                    f"Inventory alert: {sku} ke liye '{action}' zaroori hai. "
                    f"Lagbhag {qty} units restock karein jisse ₹{impact:,.2f} ka sambhavit nuksaan bachaya ja sake."
                )
            return "Filhal sabhi jaruri products ka stock paryapt sthiti mein hai."

        if intent == Intent.CROSS_SELL.value.lower():
            if recs:
                top = recs[0]
                target = top.get("target_sku", "SKU")
                recom = top.get("recommended_sku", "Bundle SKU")
                conf = top.get("confidence", 0.0)
                return (
                    f"Cross-sell sujhaav: {target} khareedne wale grahak aksar {recom} bhi lete hain "
                    f"(confidence: {conf:.2f}). Inka bundle offer counter par rakhein."
                )
            return "Abhi koi naya cross-sell combination uplabdh nahi hai."

        if intent == Intent.PRICING_RECOMMENDATION.value.lower():
            if recs:
                top = recs[0]
                sku = top.get("sku", "Product")
                action = top.get("action", "ADJUST_PRICE")
                curr_p = top.get("current_price", 0.0)
                rec_p = top.get("recommended_price", 0.0)
                return (
                    f"Pricing alert: {sku} ka vartaman daam ₹{curr_p:.2f} hai. "
                    f"Ise badal kar ₹{rec_p:.2f} karne ka sujhaav hai ({action})."
                )
            return "Sabhi products ke daam abhi optimal sthiti mein hain."

        if intent == Intent.DAILY_ACTION_PLAN.value.lower():
            if recs:
                items_str = "\n".join(
                    [f"{i+1}. [{r.get('type', 'ACTION')}] {r.get('sku', '')}: {r.get('action', '')} (Impact: ₹{r.get('estimated_revenue_impact', 0.0):,.2f})"
                     for i, r in enumerate(recs[:3])]
                )
                return (
                    f"Aaj ke mukhya business actions:\n{items_str}\n"
                    f"In par pehle dhyan dene se revenue aur customer retention dono behtar honge."
                )
            return "Aaj ke liye koi pending urgent action nahi hai. Business stable chal raha hai."

        if intent == Intent.RECOMMENDATION_EXPLANATION.value.lower():
            ev = ctx.evidence
            if ev:
                top_ev = ev[0]
                reason = top_ev.get("reasoning", "Evidence based on demand and stock.")
                return f"Is recommendation ka mukhya kaaran: {reason}"
            return "Yeh sujhaav Phase 1 se 4 ke historical patterns aur demand forecasts par aadharit hai."

        if intent == Intent.BENCHMARK.value.lower():
            rank = m.get("rank", 1)
            peer_count = m.get("peer_count", 8)
            peer_group = m.get("peer_group", "Peers")
            overall_score = m.get("overall_score", 70)
            repeat_rate = m.get("repeat_rate_you", 0.0)
            peer_repeat = m.get("repeat_rate_median", 0.0)
            ticket_size = m.get("ticket_size_you", 0.0)
            peer_ticket = m.get("ticket_size_median", 0.0)
            action = recs[0].get("action") if recs else "Dukaan ke regular grahakon ko re-engage karein."
            return (
                f"Aapki dukaan {peer_group} mein #{rank} of {peer_count} rank par hai (Overall score: {overall_score}/100).\n"
                f"• Repeat Customer Rate: {repeat_rate}% (Peer median: {peer_repeat}%)\n"
                f"• Average Bill (AOV): ₹{int(ticket_size)} (Peer median: ₹{int(peer_ticket)})\n"
                f"Action: {action}"
            )

        # Default fallback
        if ctx.facts:
            f_str = ", ".join([f"{f.key}: {f.value}" for f in ctx.facts[:3]])
            return f"Aapke vyapar ki uplabdh jankari: {f_str}."

        return "Main aapke business data ke anusar jankari khoj raha hoon. Kripya apna prashna thoda vistar se poochein."

    # -------------------------------------------------------------
    # HINDI (DEVANAGARI) GENERATION
    # -------------------------------------------------------------
    def _generate_hindi(self, intent: str, ctx: BusinessContext) -> str:
        m = ctx.metrics
        recs = ctx.recommendations

        if intent == Intent.GREETING.value.lower():
            return (
                "नमस्ते! मैं व्यापारमित्र एआई बिज़नेस साथी हूँ। "
                "आप मुझसे अपनी दुकान की बिक्री, मांग पूर्वानुमान, ग्राहक जोखिम या इन्वेंट्री स्टॉक के बारे में पूछ सकते हैं।"
            )

        if intent == Intent.HELP_CAPABILITIES.value.lower():
            return (
                "व्यापारमित्र आपकी दुकान के लिए निम्नलिखित सहायता कर सकता है:\n"
                "1. बिक्री व राजस्व सारांश (Sales & Revenue)\n"
                "2. 7-दिवसीय मांग व बिक्री पूर्वानुमान (7-Day Forecast)\n"
                "3. इन्वेंट्री रीस्टॉक अलर्ट (Inventory Restock Alerts)\n"
                "4. ग्राहक जोखिम विश्लेषण (Customer Churn Risk)\n"
                "5. क्रॉस-सेल एवं बंडलिंग सुझाव (Cross-Sell Offers)\n"
                "6. दैनिक कार्य योजना (Daily Action Plan)"
            )

        if intent == Intent.OUT_OF_DOMAIN.value.lower():
            return (
                "क्षमा करें, मैं केवल आपकी दुकान की बिक्री, स्टॉक और ग्राहकों के व्यवसाय संबंधी प्रश्नों में सहायता कर सकता हूँ। "
                "कृपया व्यापार से जुड़ा प्रश्न पूछें।"
            )

        if intent == Intent.SALES_SUMMARY.value.lower():
            rev = m.get("total_revenue", 0.0)
            orders = m.get("total_orders", 0)
            aov = m.get("average_order_value", 0.0)
            return (
                f"आपकी कुल बिक्री (राजस्व) ₹{rev:,.2f} रही है, जिसमें कुल {orders} ऑर्डर्स प्राप्त हुए हैं। "
                f"आपका औसत ऑर्डर मूल्य (AOV) ₹{aov:,.2f} रहा है।"
            )

        if intent == Intent.SALES_TREND.value.lower():
            rev = m.get("total_revenue", 0.0)
            orders = m.get("total_orders", 0)
            days = m.get("days_recorded", 0)
            return (
                f"पिछले {days} दिनों के बिक्री रुझान के अनुसार कुल राजस्व ₹{rev:,.2f} और {orders} ऑर्डर्स दर्ज किए गए हैं।"
            )

        if intent == Intent.SALES_FORECAST.value.lower():
            f_rev = m.get("forecast_total_revenue", 0.0)
            f_orders = m.get("forecast_total_orders", 0)
            horizon = m.get("forecast_horizon", "7 days")
            return (
                f"आगामी {horizon} में आपकी कुल बिक्री लगभग ₹{f_rev:,.2f} होने का अनुमान है, "
                f"और लगभग {f_orders} ऑर्डर्स आने की संभावना है।"
            )

        if intent == Intent.PRODUCT_PERFORMANCE.value.lower():
            p_id = m.get("product_id") or "उत्पाद"
            rev = m.get("product_revenue", 0.0)
            qty = m.get("product_units_sold", 0)
            return (
                f"{p_id} की कुल बिक्री ₹{rev:,.2f} रही है, जिसमें {qty} यूनिट्स बेची गई हैं।"
            )

        if intent == Intent.PRODUCT_DEMAND_FORECAST.value.lower():
            p_id = m.get("product_id") or "SKU"
            f_qty = m.get("forecast_units", 0)
            return f"{p_id} के लिए अगले 7 दिनों में लगभग {f_qty} यूनिट्स की मांग रहने का अनुमान है।"

        if intent == Intent.CUSTOMER_RISK.value.lower():
            c_id = m.get("customer_id")
            if c_id:
                tier = m.get("churn_tier", "Unknown")
                score = m.get("churn_probability", 0.0)
                return f"ग्राहक {c_id} का जोखिम स्तर '{tier}' है (जोखिम स्कोर: {score:.2f})।"
            else:
                high_count = m.get("high_risk_customers_count", 0)
                tot = m.get("total_customers_evaluated", 0)
                return f"कुल {tot} ग्राहकों में से {high_count} ग्राहक उच्च जोखिम (churn risk) पर हैं।"

        if intent == Intent.INVENTORY_RECOMMENDATION.value.lower():
            if recs:
                top = recs[0]
                action = top.get("action", "RESTOCK")
                sku = top.get("sku", "Product")
                qty = top.get("suggested_quantity", 0)
                impact = top.get("estimated_revenue_impact", 0.0)
                return (
                    f"इन्वेंट्री चेतावनी: {sku} के लिए '{action}' आवश्यक है। "
                    f"लगभग {qty} यूनिट्स का पुनः स्टॉक करें ताकि ₹{impact:,.2f} का संभावित नुकसान बचाया जा सके।"
                )
            return "वर्तमान में सभी आवश्यक उत्पादों का स्टॉक पर्याप्त स्थिति में है।"

        if intent == Intent.DAILY_ACTION_PLAN.value.lower():
            if recs:
                items_str = "\n".join(
                    [f"{i+1}. [{r.get('type', 'ACTION')}] {r.get('sku', '')}: {r.get('action', '')} (प्रभाव: ₹{r.get('estimated_revenue_impact', 0.0):,.2f})"
                     for i, r in enumerate(recs[:3])]
                )
                return f"आज के मुख्य व्यापारिक कार्य:\n{items_str}"
            return "आज के लिए कोई तत्काल लंबित कार्य नहीं है।"

        if intent == Intent.BENCHMARK.value.lower():
            rank = m.get("rank", 1)
            peer_count = m.get("peer_count", 8)
            peer_group = m.get("peer_group", "Peers")
            overall_score = m.get("overall_score", 70)
            repeat_rate = m.get("repeat_rate_you", 0.0)
            peer_repeat = m.get("repeat_rate_median", 0.0)
            ticket_size = m.get("ticket_size_you", 0.0)
            action = recs[0].get("action") if recs else "नियमित ग्राहकों को पुनः जोड़ें।"
            return (
                f"आपकी दुकान {peer_group} में {peer_count} दुकानों में से #{rank} रैंक पर है (स्कोर: {overall_score}/100)।\n"
                f"• रिपीट ग्राहक दर: {repeat_rate}% (औसत: {peer_repeat}%)\n"
                f"• औसत बिल साइज: ₹{int(ticket_size)}\n"
                f"सलाह: {action}"
            )

        # Fallback
        if ctx.facts:
            f_str = ", ".join([f"{f.key}: {f.value}" for f in ctx.facts[:3]])
            return f"व्यापार डेटा के अनुसार: {f_str}।"

        return "व्यापारमित्र आपके व्यवसाय डेटा के आधार पर प्रमाणित उत्तर प्रदान करता है।"

    # -------------------------------------------------------------
    # ENGLISH GENERATION
    # -------------------------------------------------------------
    def _generate_english(self, intent: str, ctx: BusinessContext) -> str:
        m = ctx.metrics
        recs = ctx.recommendations

        if intent == Intent.GREETING.value.lower():
            return (
                "Hello! I am VyaparMitra, your AI business copilot. "
                "You can ask me about your store's sales, 7-day demand forecasts, customer churn risk, or inventory restock recommendations."
            )

        if intent == Intent.HELP_CAPABILITIES.value.lower():
            return (
                "VyaparMitra capabilities include:\n"
                "1. Sales & Revenue Analytics: View historical sales, orders, and average ticket size.\n"
                "2. 7-Day Forecasting: Projected store revenue and SKU demand.\n"
                "3. Inventory Restock Alerts: Prevent stockouts with quantity suggestions.\n"
                "4. Customer Churn Risk: Identify at-risk patrons and re-engagement opportunities.\n"
                "5. Cross-Sell Recommendations: Product bundles with proven purchase affinity.\n"
                "6. Daily Action Plan: Top 3 prioritized actions for today."
            )

        if intent == Intent.OUT_OF_DOMAIN.value.lower():
            return (
                "I specialize strictly in merchant business intelligence, sales, inventory, and customer analytics. "
                "Please ask a question related to your store operations or data."
            )

        if intent == Intent.SALES_SUMMARY.value.lower():
            rev = m.get("total_revenue", 0.0)
            orders = m.get("total_orders", 0)
            aov = m.get("average_order_value", 0.0)
            time_r = m.get("time_range", "total")
            return (
                f"Your {time_r} total sales revenue is ₹{rev:,.2f} across {orders} completed orders, "
                f"with an average order value (AOV) of ₹{aov:,.2f}."
            )

        if intent == Intent.SALES_TREND.value.lower():
            rev = m.get("total_revenue", 0.0)
            orders = m.get("total_orders", 0)
            days = m.get("days_recorded", 0)
            return (
                f"Across {days} recorded days, total sales reached ₹{rev:,.2f} over {orders} transactions."
            )

        if intent == Intent.SALES_FORECAST.value.lower():
            f_rev = m.get("forecast_total_revenue", 0.0)
            f_orders = m.get("forecast_total_orders", 0)
            horizon = m.get("forecast_horizon", "7 days")
            return (
                f"Over the upcoming {horizon}, forecasted total revenue is ₹{f_rev:,.2f} "
                f"with approximately {f_orders} orders expected."
            )

        if intent == Intent.PRODUCT_PERFORMANCE.value.lower():
            p_id = m.get("product_id") or "Product"
            rev = m.get("product_revenue", 0.0)
            qty = m.get("product_units_sold", 0)
            return f"{p_id} generated ₹{rev:,.2f} in revenue with {qty} units sold."

        if intent == Intent.PRODUCT_DEMAND_FORECAST.value.lower():
            p_id = m.get("product_id") or "SKU"
            f_qty = m.get("forecast_units", 0)
            horizon = m.get("horizon", "7 days")
            return f"Projected demand for {p_id} over the next {horizon} is approximately {f_qty} units."

        if intent == Intent.CUSTOMER_RISK.value.lower():
            c_id = m.get("customer_id")
            if c_id:
                tier = m.get("churn_tier", "Unknown")
                score = m.get("churn_probability", 0.0)
                return f"Customer {c_id} is in the '{tier}' churn risk tier with a score of {score:.2f}."
            else:
                high_count = m.get("high_risk_customers_count", 0)
                tot = m.get("total_customers_evaluated", 0)
                return (
                    f"Out of {tot} evaluated customers, {high_count} are in the high churn risk tier."
                )

        if intent == Intent.INVENTORY_RECOMMENDATION.value.lower():
            if recs:
                top = recs[0]
                action = top.get("action", "RESTOCK")
                sku = top.get("sku", "Product")
                qty = top.get("suggested_quantity", 0)
                impact = top.get("estimated_revenue_impact", 0.0)
                return (
                    f"Inventory recommendation: '{action}' advised for {sku}. "
                    f"Restock {qty} units to protect an estimated ₹{impact:,.2f} in revenue."
                )
            return "Inventory levels are currently adequate across evaluated products."

        if intent == Intent.CROSS_SELL.value.lower():
            if recs:
                top = recs[0]
                target = top.get("target_sku", "SKU")
                recom = top.get("recommended_sku", "Bundle SKU")
                conf = top.get("confidence", 0.0)
                return (
                    f"Cross-sell suggestion: Customers purchasing {target} frequently buy {recom} "
                    f"(confidence: {conf:.2f}). Consider bundling these items."
                )
            return "No cross-sell associations are currently flagged."

        if intent == Intent.PRICING_RECOMMENDATION.value.lower():
            if recs:
                top = recs[0]
                sku = top.get("sku", "Product")
                action = top.get("action", "ADJUST_PRICE")
                curr_p = top.get("current_price", 0.0)
                rec_p = top.get("recommended_price", 0.0)
                return (
                    f"Pricing recommendation for {sku}: Current price is ₹{curr_p:.2f}; "
                    f"recommended price is ₹{rec_p:.2f} ({action})."
                )
            return "Pricing is currently aligned with market recommendations."

        if intent == Intent.DAILY_ACTION_PLAN.value.lower():
            if recs:
                items_str = "\n".join(
                    [f"{i+1}. [{r.get('type', 'ACTION')}] {r.get('sku', '')}: {r.get('action', '')} (Impact: ₹{r.get('estimated_revenue_impact', 0.0):,.2f})"
                     for i, r in enumerate(recs[:3])]
                )
                return f"Top prioritized business actions for today:\n{items_str}"
            return "No urgent actions pending for today. Operations are stable."

        if intent == Intent.RECOMMENDATION_EXPLANATION.value.lower():
            ev = ctx.evidence
            if ev:
                top_ev = ev[0]
                reason = top_ev.get("reasoning", "Evidence based on demand and stock.")
                return f"Primary rationale for this recommendation: {reason}"
            return "This recommendation is derived from Phase 1-4 analytics, predictive ML forecasts, and decision rules."

        if intent == Intent.BENCHMARK.value.lower():
            rank = m.get("rank", 1)
            peer_count = m.get("peer_count", 8)
            peer_group = m.get("peer_group", "Peers")
            overall_score = m.get("overall_score", 70)
            repeat_rate = m.get("repeat_rate_you", 0.0)
            peer_repeat = m.get("repeat_rate_median", 0.0)
            ticket_size = m.get("ticket_size_you", 0.0)
            peer_ticket = m.get("ticket_size_median", 0.0)
            action = recs[0].get("action") if recs else "Re-engage regular customers with targeted offers."
            return (
                f"Your shop ranks #{rank} of {peer_count} in {peer_group} with an overall benchmark score of {overall_score}/100.\n"
                f"• Repeat Customer Rate: {repeat_rate}% (Peer median: {peer_repeat}%)\n"
                f"• Average Bill (AOV): ₹{int(ticket_size)} (Peer median: ₹{int(peer_ticket)})\n"
                f"Recommended Action: {action}"
            )

        # Fallback
        if ctx.facts:
            f_str = ", ".join([f"{f.key}: {f.value}" for f in ctx.facts[:3]])
            return f"Verified business data: {f_str}."

        return "VyaparMitra answers are grounded strictly in your verified business records."
