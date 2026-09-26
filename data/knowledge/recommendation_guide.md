# VyaparMitra Recommendation Guide (सुझाव मार्गदर्शिका)

How merchants should interpret and act upon VyaparMitra recommendations.

## Recommendation Types and Merchant Actions

### 1. RESTOCK (माल दोबारा मंगाना)
- **When Triggered**: Forward 7-day predicted demand exceeds estimated supplier lead-time coverage and safety buffer.
- **Recommended Action**: Review suggested reorder batch and contact supplier before inventory runs dry.
- **Guardrail Note**: Operates in `inventory_estimation_mode = True` because live store shelf telemetry is not tracked. Guidance is based on forecast demand velocity.

### 2. RETENTION (ग्राहक को जोड़े रखना)
- **When Triggered**: High-value customer (top 25% lifetime spend) has exceeded their usual purchase interval and has high churn risk ($\ge 60\%$).
- **Recommended Action**: Proactive personal phone call, WhatsApp greeting, or special loyalty courtesy.
- **Guardrail Note**: Decision support recommendation; VyaparMitra does not promise that a discount guarantees retention.

### 3. FOCUS (मुख्य उत्पाद पर ध्यान)
- **When Triggered**: Star product with high historical revenue and high forward forecast.
- **Recommended Action**: Ensure front-row shelf placement, zero stockouts, and prime catalog visibility.

### 4. PROMOTE (प्रचार और छूट)
- **When Triggered**: High-margin product with low/moderate recent sales velocity.
- **Recommended Action**: Feature in digital storefront or introduce a modest promotional introductory offer.

### 5. CROSS_SELL (साथ में बिकाऊ जोड़ा)
- **When Triggered**: Strong statistical affinity (Lift $> 1.15$, Confidence $> 8\%$) between two products.
- **Recommended Action**: Display the secondary product near the primary product or suggest it at checkout.

### 6. MAINTAIN_PRICE (कीमत सुरक्षित रखें)
- **When Triggered**: High demand + high margin product.
- **Recommended Action**: Avoid unnecessary discounting; customers value the product at its current price.

### 7. REVIEW_MARGIN (लागत और मुनाफे की समीक्षा)
- **When Triggered**: High volume demand but very slim margin ($< 15\%$).
- **Recommended Action**: Request wholesale bulk discounts from distributor or consider a minor price adjustment.
