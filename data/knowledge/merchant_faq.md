# VyaparMitra Merchant FAQ (अक्सर पूछे जाने वाले प्रश्न)

Frequently asked questions by shopkeepers and merchants about how VyaparMitra works.

## General Questions

### Q1: VyaparMitra meri dukan ka data kahan se leta hai?
**Answer**: VyaparMitra aapke pichhle bills aur transactions (Phase 1), sales analytics (Phase 2), AI forecasting models (Phase 3), aur rule-based decision engine (Phase 4) se data leta hai. Har number verified data par based hota hai.

### Q2: Kya VyaparMitra dukan mein rakha physical stock dekh sakta hai?
**Answer**: Nahi. Dukan mein physical shelf par exact kitna piece bacha hai, iski live telemetry system ke paas nahi hai. Isliye VyaparMitra `inventory_estimation_mode` mein kaam karta hai aur pichhli daily bikri aur aane wale 7-din ke forecast ke aadhar par restock ka sujhav deta hai.

### Q3: Forecast kitna vishwasniya (reliable) hai?
**Answer**: Phase 3 Sales Model ka Test WAPE lagbhag 27% hai, jiska matlab hai ki general sales trend aur weekly patterns me model baseline moving average se behtar perform karta hai. Lekin unannounced holidays ya mausam ke achanak badlav se thoda antar aa sakta hai.

### Q4: Cross-sell recommendation ka kya matlab hai?
**Answer**: Jab pichhle transactions me dekha gaya ki Product A lene wale grahak Product B bhi aksar khareedte hain (Lift $> 1.15$), to system sujhav deta hai ki counter par in dono ko sath me dikhayein.

### Q5: Kya VyaparMitra mere customer ko apne aap message bhej sakta hai?
**Answer**: Nahi. VyaparMitra kewal aapko decision support aur sujhav deta hai. Koi bhi message bhejna, order place karna ya price badalna poori tarah aapke haath mein hai.
