"""
AgriTrust AI Farming Assistant Service
Comprehensive agronomy and marketplace knowledge assistant with clear transparency.
"""

import os
import re

CHAT_KNOWLEDGE_BASE = [
    {
        'keywords': ['soil', 'prepare', 'preparation', 'land', 'plow', 'ph'],
        'topic': 'Soil Preparation',
        'response': """**Soil Preparation Guidelines:**
1. **Soil Testing:** Test pH (ideal is 6.0 - 7.5 for most vegetables) and available N-P-K plus organic carbon.
2. **Deep Tillage:** Perform 1-2 deep plowings to break hardpan layers and expose soil-borne grubs/pathogens to sunlight.
3. **Organic Matter:** Incorporate 5–8 tons of well-decomposed Farm Yard Manure (FYM) or 2.5 tons of vermicompost per acre 2-3 weeks before transplanting.
4. **Bed Formation:** Make raised beds (15–20 cm high, 90–120 cm wide) to prevent waterlogging and facilitate furrow or drip irrigation."""
    },
    {
        'keywords': ['water', 'irrigation', 'drip', 'sprinkler', 'watering'],
        'topic': 'Irrigation Management',
        'response': """**Efficient Irrigation Best Practices:**
- **Drip Irrigation:** Saves 40–60% water compared to flood irrigation, reduces weed growth, and keeps plant canopies dry to prevent fungal outbreaks.
- **Critical Watering Stages:**
  - *Tomato & Vegetables:* Flowering and fruit enlargement.
  - *Rice:* Tillering and panicle development (maintain 2-3 cm water).
  - *Banana:* Shooting and bunch maturation.
- **Water Timing:** Always irrigate in the early morning or late afternoon to minimize evaporation losses."""
    },
    {
        'keywords': ['fertilizer', 'npk', 'urea', 'manure', 'compost', 'nutrient', 'feed'],
        'topic': 'Fertilizer & Plant Nutrition',
        'response': """**Nutrient Management Strategy:**
- **Basal Dose:** Apply full Phosphorus (P) and 30-50% Nitrogen (N) & Potassium (K) during final land preparation.
- **Top Dressing / Fertigation:** Split remaining Nitrogen and Potassium during vegetative surge and flowering to avoid leaching.
- **Micronutrients:** Foliar spray of Zinc Sulphate (0.5%) and Borax (0.2%) during flower budding prevents blossom drop and improves fruit set.
- **Organic Bio-fertilizers:** Seed treatment with Azotobacter/Rhizobium and Phosphate Solubilizing Bacteria (PSB) enhances natural nutrient uptake."""
    },
    {
        'keywords': ['pest', 'insect', 'worm', 'borer', 'aphid', 'whitefly', 'neem'],
        'topic': 'Integrated Pest Management (IPM)',
        'response': """**Integrated Pest Management (IPM):**
1. **Physical & Cultural:** Use yellow and blue sticky traps (15–20 traps/acre) to monitor and trap sucking pests (aphids, thrips, whiteflies).
2. **Bio-pesticides:** Spray Neem Seed Kernel Extract (NSKE 5%) or 10,000 ppm cold-pressed Neem Oil (3 ml/liter) at the first sighting of pests.
3. **Biological Control:** Release Trichogramma egg parasitoids against bollworms and fruit borers.
4. **Synthetic Chemicals:** Use targeted systemic insecticides only as a last resort when pest population crosses economic threshold levels (ETL)."""
    },
    {
        'keywords': ['disease', 'blight', 'wilt', 'mildew', 'fungus', 'rot', 'yellow leaf', 'spot'],
        'topic': 'Disease Symptoms & Control',
        'response': """**Disease Identification & Prevention:**
- **Early Blight:** Concentric target-like rings on lower leaves. Treat with copper oxychloride or Mancozeb.
- **Powdery Mildew:** White floury dusting on leaves. Treat with wettable sulfur (2g/L) or neem extract.
- **Bacterial Wilt:** Sudden drooping without leaf yellowing. Remove affected plants immediately and drench surrounding soil with bleaching powder solution.
- *Notice:* You can upload a photo of your leaf to our **Crop Health Scanner** for OpenCV-validated diagnostic assistance."""
    },
    {
        'keywords': ['harvest', 'harvesting', 'mature', 'picking', 'yield'],
        'topic': 'Harvesting Timing & Techniques',
        'response': """**Harvesting Recommendations:**
- **Tomatoes:** Harvest at 'breaker' or 'pink' stage for distant transit; harvest at full-red ripe for direct local delivery.
- **Cucumber:** Pick when fruits are firm, crisp, and dark green before yellowing begins.
- **Rice:** Harvest when 85–90% of panicle grains turn golden straw color and grain moisture is approximately 20-22%.
- **Handling:** Harvest in the cool morning hours, avoid throwing produce into crates, and move immediately to shaded cooling areas."""
    },
    {
        'keywords': ['price', 'fair price', 'mandi', 'rate', 'cost', 'advisor'],
        'topic': 'Price Intelligence & Fair Pricing',
        'response': """**Fair Price Intelligence on AgriTrust:**
- Our **Fair Price Advisor** displays benchmark wholesale reference bands, historical averages, and active buyer procurement bids.
- As a farmer, you retain 100% autonomy to set your farm-gate asking price based on your input costs, organic certification, and grading.
- Cutting out intermediary commissions typically yields farmers 15%–30% higher margins while keeping prices fair for bulk buyers."""
    },
    {
        'keywords': ['market', 'marketplace', 'sell', 'list', 'product', 'buyer'],
        'topic': 'Direct Marketplace Guidelines',
        'response': """**How to Sell Directly on AgriTrust:**
1. Navigate to **Direct Marketplace** and click **+ List Produce**.
2. Add product details: crop variety, harvest date, quantity available, grade, and farm location.
3. Upload clear photos of your harvested produce.
4. Verified buyers can view your listing and place purchase orders directly. You receive real-time notifications for incoming orders!"""
    },
    {
        'keywords': ['reserve', 'reservation', 'contract', 'advance', 'future harvest'],
        'topic': 'Harvest Reservations',
        'response': """**How Harvest Reservations Work:**
- Farmers can list expected upcoming harvests weeks before harvest date.
- Commercial buyers and cooperatives lock in advance reservations at an agreed price per kg.
- This secures guaranteed market demand before crops are cut, virtually eliminating distress sales and post-harvest spoilage."""
    },
    {
        'keywords': ['traceability', 'batch', 'qr', 'verify', 'trust'],
        'topic': 'Traceability & Trust',
        'response': """**Farm-to-Table Traceability:**
- Every harvest lot can be registered with a unique **Batch ID**.
- AgriTrust tracks the product journey: Farm → Harvest → Quality Inspection → Packaging → In Transit → Buyer Delivery.
- Each verified batch generates an auditable record and QR code that buyers can scan to confirm authenticity and harvest freshness."""
    }
]

DEFAULT_RESPONSE = """Hello! I am **AgriTrust AI**, your agricultural decision support assistant.
I can assist you with:
- **Crop Planning & Soil Prep:** Choosing optimal crops and preparing beds.
- **Irrigation & Nutrition:** Drip scheduling, N-P-K balances, and organic composts.
- **Pest & Disease Control:** Identifying symptoms and organic or chemical solutions.
- **Direct Marketplace:** Listing produce, understanding fair prices, and harvest reservations.

*Transparency notice:* I operate using AgriTrust's built-in agronomy knowledge base and standard advisory guidelines. How may I assist your farm today?"""

SUGGESTED_PROMPTS = [
    "What is the best fertilizer schedule for tomatoes?",
    "How do I prevent powdery mildew in cucumbers?",
    "How does harvest reservation work?",
    "What soil preparation is needed for basmati rice?",
    "How do I list my produce directly for buyers?"
]

def get_chatbot_response(user_query):
    query = user_query.strip().lower()
    
    # Check for greeting
    if any(g in query for g in ['hi', 'hello', 'hey', 'namaste']):
        return {
            'reply': DEFAULT_RESPONSE,
            'topic': 'General Assistant',
            'suggested_questions': SUGGESTED_PROMPTS,
            'is_rule_based': True
        }

    # Match best knowledge base topic
    best_match = None
    max_hits = 0

    for item in CHAT_KNOWLEDGE_BASE:
        hits = sum(1 for kw in item['keywords'] if re.search(r'\b' + re.escape(kw) + r'\b', query))
        if hits > max_hits:
            max_hits = hits
            best_match = item

    if best_match and max_hits > 0:
        return {
            'reply': best_match['response'],
            'topic': best_match['topic'],
            'suggested_questions': SUGGESTED_PROMPTS[:3],
            'is_rule_based': True
        }

    return {
        'reply': f"I received your question about: *'{user_query}'*.\n\nWhile this specific query isn't fully matched in the offline agronomic rules, our recommendations cover soil prep, drip irrigation, pest scouting, harvest reservation, and direct marketplace sales.\n\nCould you try one of the suggestions below, or rephrase with key terms like *fertilizer*, *pest*, *tomato*, *irrigation*, or *reservation*?",
        'topic': 'Agricultural Help',
        'suggested_questions': SUGGESTED_PROMPTS,
        'is_rule_based': True
    }
