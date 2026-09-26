"""
Synthetic dataset generator and enriched source normalizer for VyaparMitra Phase 1.

Generates realistic relational datasets:
- transactions.csv
- merchants.csv
- customers.csv
- products.csv
- festivals.csv
- weather.csv

Supports reproducible synthetic generation (seed=42) or normalizing from enriched CSV.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import yaml

logger = logging.getLogger(__name__)

# Realistic city geographic & administrative metadata
CITY_METADATA: Dict[str, Dict[str, Any]] = {
    "Noida": {"state": "Uttar Pradesh", "pincode": "201301", "latitude": 28.5355, "longitude": 77.3910},
    "Prayagraj": {"state": "Uttar Pradesh", "pincode": "211001", "latitude": 25.4358, "longitude": 81.8463},
    "Lucknow": {"state": "Uttar Pradesh", "pincode": "226001", "latitude": 26.8467, "longitude": 80.9462},
    "Patna": {"state": "Bihar", "pincode": "800001", "latitude": 25.5941, "longitude": 85.1376},
    "Kanpur": {"state": "Uttar Pradesh", "pincode": "208001", "latitude": 26.4499, "longitude": 80.3319},
    "Agra": {"state": "Uttar Pradesh", "pincode": "282001", "latitude": 27.1767, "longitude": 78.0081},
    "Jaipur": {"state": "Rajasthan", "pincode": "302001", "latitude": 26.9124, "longitude": 75.7873},
    "Varanasi": {"state": "Uttar Pradesh", "pincode": "221001", "latitude": 25.3176, "longitude": 82.9739},
    "Gorakhpur": {"state": "Uttar Pradesh", "pincode": "273001", "latitude": 26.7606, "longitude": 83.3732},
    "Delhi": {"state": "Delhi", "pincode": "110001", "latitude": 28.6139, "longitude": 77.2090},
}

# Catalog of 64 products across 32 categories (2 products per category)
PRODUCT_CATALOG: List[Dict[str, Any]] = [
    {"product_id": "PRD_ACC_01", "product_name": "Leather Wallet", "product_category": "Accessories", "unit_cost": 250.0, "selling_price": 499.0},
    {"product_id": "PRD_ACC_02", "product_name": "Fashion Sunglasses", "product_category": "Accessories", "unit_cost": 320.0, "selling_price": 699.0},
    {"product_id": "PRD_ART_01", "product_name": "Acrylic Color Set 12-Pack", "product_category": "Art Supplies", "unit_cost": 180.0, "selling_price": 320.0},
    {"product_id": "PRD_ART_02", "product_name": "Sketching Canvas Board 10x12", "product_category": "Art Supplies", "unit_cost": 95.0, "selling_price": 175.0},
    {"product_id": "PRD_BABY_01", "product_name": "Baby Diaper Mega Pack (M)", "product_category": "Baby Care", "unit_cost": 550.0, "selling_price": 799.0},
    {"product_id": "PRD_BABY_02", "product_name": "Gentle Baby Wet Wipes 72s", "product_category": "Baby Care", "unit_cost": 90.0, "selling_price": 160.0},
    {"product_id": "PRD_BEV_01", "product_name": "Fresh Mango Juice 1L", "product_category": "Beverages", "unit_cost": 65.0, "selling_price": 110.0},
    {"product_id": "PRD_BEV_02", "product_name": "Cold Pressed Orange Juice 500ml", "product_category": "Beverages", "unit_cost": 55.0, "selling_price": 95.0},
    {"product_id": "PRD_BRD_01", "product_name": "Brown Whole Wheat Bread 400g", "product_category": "Bread", "unit_cost": 28.0, "selling_price": 50.0},
    {"product_id": "PRD_BRD_02", "product_name": "Artisanal Sourdough Bread Loaf", "product_category": "Bread", "unit_cost": 75.0, "selling_price": 140.0},
    {"product_id": "PRD_CAB_01", "product_name": "Braided USB-C to USB-C Cable 1.5m", "product_category": "Cables", "unit_cost": 120.0, "selling_price": 299.0},
    {"product_id": "PRD_CAB_02", "product_name": "Lightning Charging Cable 1m", "product_category": "Cables", "unit_cost": 140.0, "selling_price": 349.0},
    {"product_id": "PRD_CAK_01", "product_name": "Dutch Chocolate Truffle Cake 500g", "product_category": "Cakes", "unit_cost": 280.0, "selling_price": 550.0},
    {"product_id": "PRD_CAK_02", "product_name": "Eggless Pineapple Cake 500g", "product_category": "Cakes", "unit_cost": 220.0, "selling_price": 450.0},
    {"product_id": "PRD_CAS_01", "product_name": "Shockproof Matte Phone Case", "product_category": "Cases", "unit_cost": 90.0, "selling_price": 249.0},
    {"product_id": "PRD_CAS_02", "product_name": "Premium Leather Back Case", "product_category": "Cases", "unit_cost": 180.0, "selling_price": 450.0},
    {"product_id": "PRD_CHG_01", "product_name": "Fast Charger 33W USB-C Adapter", "product_category": "Chargers", "unit_cost": 320.0, "selling_price": 699.0},
    {"product_id": "PRD_CHG_02", "product_name": "Wireless Charging Pad 15W", "product_category": "Chargers", "unit_cost": 450.0, "selling_price": 999.0},
    {"product_id": "PRD_COF_01", "product_name": "Arabica Roast Ground Coffee 250g", "product_category": "Coffee", "unit_cost": 210.0, "selling_price": 380.0},
    {"product_id": "PRD_COF_02", "product_name": "Instant Cold Brew Premix 200g", "product_category": "Coffee", "unit_cost": 150.0, "selling_price": 280.0},
    {"product_id": "PRD_ESS_01", "product_name": "Organic Hand Wash 500ml", "product_category": "Daily Essentials", "unit_cost": 75.0, "selling_price": 145.0},
    {"product_id": "PRD_ESS_02", "product_name": "Antibacterial Floor Cleaner 1L", "product_category": "Daily Essentials", "unit_cost": 85.0, "selling_price": 160.0},
    {"product_id": "PRD_DAI_01", "product_name": "Fresh Cow Milk Pouch 1L", "product_category": "Dairy", "unit_cost": 48.0, "selling_price": 66.0},
    {"product_id": "PRD_DAI_02", "product_name": "Fresh Malai Paneer 200g", "product_category": "Dairy", "unit_cost": 65.0, "selling_price": 95.0},
    {"product_id": "PRD_DES_01", "product_name": "Gulab Jamun Box 500g", "product_category": "Desserts", "unit_cost": 120.0, "selling_price": 220.0},
    {"product_id": "PRD_DES_02", "product_name": "Belgian Waffle with Syrup", "product_category": "Desserts", "unit_cost": 90.0, "selling_price": 180.0},
    {"product_id": "PRD_EAR_01", "product_name": "TWS True Wireless Earbuds", "product_category": "Earphones", "unit_cost": 650.0, "selling_price": 1299.0},
    {"product_id": "PRD_EAR_02", "product_name": "Deep Bass Wired Earphones 3.5mm", "product_category": "Earphones", "unit_cost": 140.0, "selling_price": 349.0},
    {"product_id": "PRD_ELE_01", "product_name": "Smart LED Desk Lamp 10W", "product_category": "Home Electronics", "unit_cost": 450.0, "selling_price": 899.0},
    {"product_id": "PRD_ELE_02", "product_name": "Electric Kettle 1.5L Stainless Steel", "product_category": "Home Electronics", "unit_cost": 550.0, "selling_price": 1099.0},
    {"product_id": "PRD_HOU_01", "product_name": "Microfiber Cleaning Cloth 4-Pack", "product_category": "Household", "unit_cost": 80.0, "selling_price": 180.0},
    {"product_id": "PRD_HOU_02", "product_name": "Aromatherapy Reed Diffuser 100ml", "product_category": "Household", "unit_cost": 160.0, "selling_price": 320.0},
    {"product_id": "PRD_KID_01", "product_name": "Kids Cotton Graphic T-Shirt", "product_category": "Kids", "unit_cost": 160.0, "selling_price": 349.0},
    {"product_id": "PRD_KID_02", "product_name": "Children Educational Puzzle Game", "product_category": "Kids", "unit_cost": 130.0, "selling_price": 275.0},
    {"product_id": "PRD_LAP_01", "product_name": "Laptop Stand Aluminum Ergonomic", "product_category": "Laptops", "unit_cost": 420.0, "selling_price": 899.0},
    {"product_id": "PRD_LAP_02", "product_name": "Wireless Optical Mouse 2.4GHz", "product_category": "Laptops", "unit_cost": 210.0, "selling_price": 499.0},
    {"product_id": "PRD_MEA_01", "product_name": "Special North Indian Thali Combo", "product_category": "Meals", "unit_cost": 110.0, "selling_price": 220.0},
    {"product_id": "PRD_MEA_02", "product_name": "Paneer Butter Masala Meal Box", "product_category": "Meals", "unit_cost": 125.0, "selling_price": 250.0},
    {"product_id": "PRD_MED_01", "product_name": "Paracetamol 650mg Strip of 15", "product_category": "Medicine", "unit_cost": 18.0, "selling_price": 35.0},
    {"product_id": "PRD_MED_02", "product_name": "Multivitamin & Minerals 30 Tablets", "product_category": "Medicine", "unit_cost": 120.0, "selling_price": 240.0},
    {"product_id": "PRD_MEN_01", "product_name": "Men Casual Slim-Fit Cotton Shirt", "product_category": "Men", "unit_cost": 380.0, "selling_price": 799.0},
    {"product_id": "PRD_MEN_02", "product_name": "Men Comfort Stretch Denim Jeans", "product_category": "Men", "unit_cost": 550.0, "selling_price": 1199.0},
    {"product_id": "PRD_MOB_01", "product_name": "Entry-level 4G Smartphone 32GB", "product_category": "Mobiles", "unit_cost": 4800.0, "selling_price": 6499.0},
    {"product_id": "PRD_MOB_02", "product_name": "Budget 5G Smartphone 128GB", "product_category": "Mobiles", "unit_cost": 8800.0, "selling_price": 11999.0},
    {"product_id": "PRD_NOT_01", "product_name": "Spiral Hardcover Journal 200 Pages", "product_category": "Notebooks", "unit_cost": 85.0, "selling_price": 160.0},
    {"product_id": "PRD_NOT_02", "product_name": "Executive PU Leather Diary", "product_category": "Notebooks", "unit_cost": 130.0, "selling_price": 260.0},
    {"product_id": "PRD_OFF_01", "product_name": "Heavy Duty Desktop Stapler Set", "product_category": "Office Supplies", "unit_cost": 90.0, "selling_price": 175.0},
    {"product_id": "PRD_OFF_02", "product_name": "A4 Copier Paper Ream 500 Sheets", "product_category": "Office Supplies", "unit_cost": 190.0, "selling_price": 310.0},
    {"product_id": "PRD_PAS_01", "product_name": "Red Velvet Pastry Slice", "product_category": "Pastries", "unit_cost": 45.0, "selling_price": 95.0},
    {"product_id": "PRD_PAS_02", "product_name": "Choco Lava Lava Cake Single", "product_category": "Pastries", "unit_cost": 50.0, "selling_price": 110.0},
    {"product_id": "PRD_PER_01", "product_name": "Herbal Aloe Vera Face Wash 150ml", "product_category": "Personal Care", "unit_cost": 80.0, "selling_price": 155.0},
    {"product_id": "PRD_PER_02", "product_name": "Moisturizing Shea Body Lotion 250ml", "product_category": "Personal Care", "unit_cost": 120.0, "selling_price": 235.0},
    {"product_id": "PRD_SNK_01", "product_name": "Spicy Masala Potato Chips 150g", "product_category": "Snacks", "unit_cost": 22.0, "selling_price": 45.0},
    {"product_id": "PRD_SNK_02", "product_name": "Roasted Salted Almonds 200g", "product_category": "Snacks", "unit_cost": 130.0, "selling_price": 225.0},
    {"product_id": "PRD_STA_01", "product_name": "Premium Basmati Rice 5kg", "product_category": "Staples", "unit_cost": 380.0, "selling_price": 540.0},
    {"product_id": "PRD_STA_02", "product_name": "Sharbati Whole Wheat Atta 5kg", "product_category": "Staples", "unit_cost": 160.0, "selling_price": 245.0},
    {"product_id": "PRD_TEA_01", "product_name": "Assam Masala CTC Chai 500g", "product_category": "Tea", "unit_cost": 130.0, "selling_price": 240.0},
    {"product_id": "PRD_TEA_02", "product_name": "Organic Darjeeling Green Tea 100g", "product_category": "Tea", "unit_cost": 110.0, "selling_price": 210.0},
    {"product_id": "PRD_WEL_01", "product_name": "Immunity Booster Chyawanprash 1kg", "product_category": "Wellness", "unit_cost": 220.0, "selling_price": 375.0},
    {"product_id": "PRD_WEL_02", "product_name": "Pure Apple Cider Vinegar 500ml", "product_category": "Wellness", "unit_cost": 140.0, "selling_price": 280.0},
    {"product_id": "PRD_WOM_01", "product_name": "Women Pure Cotton Printed Kurti", "product_category": "Women", "unit_cost": 310.0, "selling_price": 699.0},
    {"product_id": "PRD_WOM_02", "product_name": "Embroidered Rayon Anarkali Suit", "product_category": "Women", "unit_cost": 650.0, "selling_price": 1499.0},
    {"product_id": "PRD_WRI_01", "product_name": "Gel Roller Pen Blue Pack of 5", "product_category": "Writing", "unit_cost": 45.0, "selling_price": 90.0},
    {"product_id": "PRD_WRI_02", "product_name": "Permanent Whiteboard Marker Set 4s", "product_category": "Writing", "unit_cost": 55.0, "selling_price": 115.0},
]


def load_config(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_products_dataframe() -> pd.DataFrame:
    """Build standardized products dataframe with 64 products across 32 categories."""
    return pd.DataFrame(PRODUCT_CATALOG)


def build_merchants_from_enriched(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """Extract and augment merchants with geographic metadata."""
    merchants = (
        enriched_df[["merchant_id", "merchant_name", "business_category", "city"]]
        .drop_duplicates(subset=["merchant_id"])
        .reset_index(drop=True)
    )
    merchants.rename(columns={"business_category": "business_type"}, inplace=True)

    states = []
    pincodes = []
    latitudes = []
    longitudes = []

    for _, row in merchants.iterrows():
        city = row["city"]
        meta = CITY_METADATA.get(
            city,
            {"state": "Uttar Pradesh", "pincode": "201301", "latitude": 28.5355, "longitude": 77.3910},
        )
        states.append(meta["state"])
        pincodes.append(meta["pincode"])
        latitudes.append(meta["latitude"])
        longitudes.append(meta["longitude"])

    merchants["state"] = states
    merchants["pincode"] = pincodes
    merchants["latitude"] = latitudes
    merchants["longitude"] = longitudes

    return merchants[
        ["merchant_id", "merchant_name", "business_type", "city", "state", "pincode", "latitude", "longitude"]
    ]


def build_customers_from_enriched(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """Extract and standardize customer dimension table."""
    customers = (
        enriched_df[["customer_id", "customer_type", "city"]]
        .drop_duplicates(subset=["customer_id"])
        .reset_index(drop=True)
    )
    # Generate customer_name and realistic signup_date
    customers["customer_name"] = "Customer_" + customers["customer_id"].astype(str)
    # Minimum date in dataset is 2025-10-01; signup is simulated prior or equal
    customers["signup_date"] = "2025-01-15"
    return customers[["customer_id", "customer_name", "customer_type", "city", "signup_date"]]


def build_festivals_from_enriched(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract festival calendar data, supporting multi-festival dates.
    For example on 2026-04-14, Ambedkar Jayanti and Baisakhi are separate festival entries.
    """
    fest_rows = (
        enriched_df[["date_festival", "festival", "festival_group"]]
        .dropna(subset=["date_festival", "festival"])
        .drop_duplicates()
        .copy()
    )

    festival_list: List[Dict[str, Any]] = []
    for _, row in fest_rows.iterrows():
        dt = str(row["date_festival"]).strip()
        fest_name = str(row["festival"]).strip()
        fest_grp = str(row["festival_group"]).strip()

        # Handle compound festival entries like 'Ambedkar Jayanti / Baisakhi' by splitting into separate events
        if "/" in fest_name:
            names = [n.strip() for n in fest_name.split("/")]
            for idx, name in enumerate(names):
                intensity = 0.9 if idx == 0 else 0.85
                fest_type = "National" if "Ambedkar" in name else "Regional"
                festival_list.append({
                    "date": dt,
                    "festival_name": name,
                    "festival_type": fest_type,
                    "is_festival": 1,
                    "festival_intensity": intensity
                })
        else:
            # Assign intensity based on importance
            high_intensity_fests = {"Diwali", "Holi", "Eid al-Fitr", "Christmas", "Independence Day"}
            intensity = 1.0 if fest_name in high_intensity_fests else 0.8
            festival_list.append({
                "date": dt,
                "festival_name": fest_name,
                "festival_type": fest_grp if fest_grp else "Cultural",
                "is_festival": 1,
                "festival_intensity": intensity
            })

    fest_df = pd.DataFrame(festival_list).drop_duplicates()
    fest_df.sort_values(by="date", inplace=True)
    return fest_df.reset_index(drop=True)


def build_weather_from_enriched(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """Extract daily weather observations per city."""
    df_copy = enriched_df.copy()
    df_copy["date"] = df_copy["timestamp"].astype(str).str.slice(0, 10)
    weather_df = (
        df_copy[["date", "city", "temperature_c", "humidity_pct", "rainfall_mm", "weather_condition"]]
        .drop_duplicates(subset=["date", "city"])
        .reset_index(drop=True)
    )
    weather_df.rename(
        columns={
            "temperature_c": "temperature",
            "humidity_pct": "humidity",
            "rainfall_mm": "rainfall",
        },
        inplace=True,
    )
    weather_df.sort_values(by=["date", "city"], inplace=True)
    return weather_df[["date", "city", "temperature", "humidity", "rainfall", "weather_condition"]].reset_index(drop=True)


def build_transactions_from_enriched(
    enriched_df: pd.DataFrame,
    products_df: pd.DataFrame,
    random_seed: int = 42,
    inject_anomalies: bool = True,
) -> pd.DataFrame:
    """
    Transform enriched transaction records to raw schema:
    [transaction_id, merchant_id, customer_id, timestamp, product_id, product_category, quantity, unit_price, discount, payment_method]
    Maintains realistic pricing and discounts.
    Optionally injects controlled anomalies for validation testing.
    """
    rng = np.random.default_rng(random_seed)
    
    # Map category to products list
    cat_to_prods = products_df.groupby("product_category")["product_id"].apply(list).to_dict()
    prod_prices = products_df.set_index("product_id")["selling_price"].to_dict()

    n = len(enriched_df)
    assigned_prod_ids = []
    quantities = []
    unit_prices = []
    discounts = []
    payment_methods = []

    for i in range(n):
        row = enriched_df.iloc[i]
        cat = row["product_category"]
        amt = float(row["amount"])
        
        # Select product in category
        prods = cat_to_prods.get(cat, ["PRD_ESS_01"])
        prod_id = prods[i % len(prods)]
        catalog_price = prod_prices.get(prod_id, 100.0)

        # Realistic quantity: 1 to 5
        qty = int(rng.choice([1, 1, 1, 2, 2, 3, 4], p=[0.45, 0.25, 0.1, 0.1, 0.05, 0.03, 0.02]))
        
        # Calculate unit_price and discount to align with amount
        # total_amount = qty * unit_price
        # net_amount = total_amount - discount = amt
        # So unit_price = max(catalog_price, round(amt / qty, 2))
        unit_price = round(max(catalog_price, (amt / qty) * 1.05), 2)
        total_val = unit_price * qty
        discount = round(max(0.0, total_val - amt), 2)

        assigned_prod_ids.append(prod_id)
        quantities.append(qty)
        unit_prices.append(unit_price)
        discounts.append(discount)
        
        # Standardize payment method
        pmode = str(row["payment_mode"]).strip().upper()
        if pmode in ["UPI", "CASH", "CARD", "NETBANKING", "WALLET"]:
            payment_methods.append(pmode)
        else:
            payment_methods.append("UPI")

    tx_df = pd.DataFrame({
        "transaction_id": enriched_df["transaction_id"].astype(str),
        "merchant_id": enriched_df["merchant_id"].astype(str),
        "customer_id": enriched_df["customer_id"].astype(str),
        "timestamp": enriched_df["timestamp"].astype(str),
        "product_id": assigned_prod_ids,
        "product_category": enriched_df["product_category"].astype(str),
        "quantity": quantities,
        "unit_price": unit_prices,
        "discount": discounts,
        "payment_method": payment_methods,
    })

    if inject_anomalies:
        # Controlled anomalies to test validation and quarantine pipeline:
        # 1 & 2: Two duplicate transaction_ids
        tx_df.iloc[100, tx_df.columns.get_loc("transaction_id")] = tx_df.iloc[0]["transaction_id"]
        tx_df.iloc[200, tx_df.columns.get_loc("transaction_id")] = tx_df.iloc[1]["transaction_id"]
        # 3: Invalid quantity (quantity <= 0)
        tx_df.iloc[300, tx_df.columns.get_loc("quantity")] = 0
        # 4: Invalid price (unit_price < 0)
        tx_df.iloc[400, tx_df.columns.get_loc("unit_price")] = -50.0
        # 5: Invalid discount (discount > quantity * unit_price)
        total_p = tx_df.iloc[500]["quantity"] * tx_df.iloc[500]["unit_price"]
        tx_df.iloc[500, tx_df.columns.get_loc("discount")] = total_p + 500.0

    return tx_df


def generate_all_datasets(config_path: str = "configs/config.yaml") -> Dict[str, pd.DataFrame]:
    """
    Main data generation orchestrator.
    Generates and saves raw CSV files to data/raw.
    """
    config = load_config(config_path)
    raw_dir = Path(config["paths"]["raw"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    seed = config["dataset"].get("random_seed", 42)
    use_enriched = config["dataset"].get("use_enriched_source", True)
    enriched_path = config["dataset"].get("enriched_source_path", "data/raw/vyaparmitra_10000_transactions_enriched.csv")
    inject_anomalies = config["dataset"].get("inject_anomalies", True)

    logger.info("Initializing dataset generation (seed=%d)...", seed)

    # 1. Products catalog
    products_df = build_products_dataframe()
    products_path = raw_dir / "products.csv"
    products_df.to_csv(products_path, index=False)
    logger.info("Saved %d products to %s", len(products_df), products_path)

    if use_enriched and Path(enriched_path).exists():
        logger.info("Normalizing from enriched source: %s", enriched_path)
        enriched_df = pd.read_csv(enriched_path)

        # 2. Merchants
        merchants_df = build_merchants_from_enriched(enriched_df)
        merchants_path = raw_dir / "merchants.csv"
        merchants_df.to_csv(merchants_path, index=False)
        logger.info("Saved %d merchants to %s", len(merchants_df), merchants_path)

        # 3. Customers
        customers_df = build_customers_from_enriched(enriched_df)
        customers_path = raw_dir / "customers.csv"
        customers_df.to_csv(customers_path, index=False)
        logger.info("Saved %d customers to %s", len(customers_df), customers_path)

        # 4. Festivals
        festivals_df = build_festivals_from_enriched(enriched_df)
        festivals_path = raw_dir / "festivals.csv"
        festivals_df.to_csv(festivals_path, index=False)
        logger.info("Saved %d festival records to %s", len(festivals_df), festivals_path)

        # 5. Weather
        weather_df = build_weather_from_enriched(enriched_df)
        weather_path = raw_dir / "weather.csv"
        weather_df.to_csv(weather_path, index=False)
        logger.info("Saved %d daily weather records to %s", len(weather_df), weather_path)

        # 6. Transactions
        tx_df = build_transactions_from_enriched(
            enriched_df,
            products_df,
            random_seed=seed,
            inject_anomalies=inject_anomalies,
        )
        tx_path = raw_dir / "transactions.csv"
        tx_df.to_csv(tx_path, index=False)
        logger.info("Saved %d raw transactions to %s", len(tx_df), tx_path)

    else:
        logger.info("Generating purely synthetic transactions and entities from scratch...")
        # Pure synthetic generation fallback
        rng = np.random.default_rng(seed)
        num_merchants = config["dataset"].get("merchants", 10)
        num_customers = config["dataset"].get("customers", 100)
        num_transactions = config["dataset"].get("transactions", 10000)

        # Synthetic merchants
        merchant_ids = [f"M{i:03d}" for i in range(1, num_merchants + 1)]
        cities = list(CITY_METADATA.keys())
        b_types = ["Bakery", "Cafe", "Clothing", "Electronics", "General Store", "Grocery", "Pharmacy", "Restaurant", "Stationery"]
        merchants_list = []
        for i, mid in enumerate(merchant_ids):
            city = cities[i % len(cities)]
            meta = CITY_METADATA[city]
            merchants_list.append({
                "merchant_id": mid,
                "merchant_name": f"Merchant_{i+1:03d}",
                "business_type": b_types[i % len(b_types)],
                "city": city,
                "state": meta["state"],
                "pincode": meta["pincode"],
                "latitude": meta["latitude"],
                "longitude": meta["longitude"],
            })
        merchants_df = pd.DataFrame(merchants_list)
        merchants_df.to_csv(raw_dir / "merchants.csv", index=False)

        # Synthetic customers
        customer_ids = [f"C{i:05d}" for i in range(1, num_customers + 1)]
        customers_df = pd.DataFrame({
            "customer_id": customer_ids,
            "customer_name": [f"Customer_{cid}" for cid in customer_ids],
            "customer_type": rng.choice(["New", "Regular", "Repeat"], size=num_customers, p=[0.3, 0.4, 0.3]),
            "city": rng.choice(cities, size=num_customers),
            "signup_date": "2025-01-01",
        })
        customers_df.to_csv(raw_dir / "customers.csv", index=False)

        # Synthetic festivals
        festivals_df = pd.DataFrame([
            {"date": "2025-10-21", "festival_name": "Diwali", "festival_type": "Religious", "is_festival": 1, "festival_intensity": 1.0},
            {"date": "2025-12-25", "festival_name": "Christmas", "festival_type": "National", "is_festival": 1, "festival_intensity": 0.9},
            {"date": "2026-01-26", "festival_name": "Republic Day", "festival_type": "National", "is_festival": 1, "festival_intensity": 0.8},
            {"date": "2026-03-04", "festival_name": "Holi", "festival_type": "Religious", "is_festival": 1, "festival_intensity": 1.0},
            {"date": "2026-04-14", "festival_name": "Ambedkar Jayanti", "festival_type": "National", "is_festival": 1, "festival_intensity": 0.8},
            {"date": "2026-04-14", "festival_name": "Baisakhi", "festival_type": "Regional", "is_festival": 1, "festival_intensity": 0.85},
            {"date": "2026-08-15", "festival_name": "Independence Day", "festival_type": "National", "is_festival": 1, "festival_intensity": 0.9},
        ])
        festivals_df.to_csv(raw_dir / "festivals.csv", index=False)

        # Synthetic weather
        dates = pd.date_range("2025-10-01", "2026-09-30", freq="D").strftime("%Y-%m-%d")
        weather_rows = []
        for d in dates:
            for c in cities:
                weather_rows.append({
                    "date": d,
                    "city": c,
                    "temperature": round(float(rng.uniform(15.0, 38.0)), 1),
                    "humidity": round(float(rng.uniform(30.0, 85.0)), 1),
                    "rainfall": round(float(rng.exponential(0.5) if rng.random() > 0.8 else 0.0), 1),
                    "weather_condition": rng.choice(["Clear", "Partly Cloudy", "Rainy", "Hot", "Cool"], p=[0.6, 0.2, 0.1, 0.05, 0.05]),
                })
        weather_df = pd.DataFrame(weather_rows)
        weather_df.to_csv(raw_dir / "weather.csv", index=False)

        # Synthetic transactions
        tx_rows = []
        # Power-law distribution for customer loyalty
        cust_weights = 1.0 / np.arange(1, num_customers + 1) ** 0.8
        cust_weights /= cust_weights.sum()

        for i in range(num_transactions):
            tx_id = f"TXN{i+1:07d}"
            mid = str(rng.choice(merchant_ids))
            cid = str(rng.choice(customer_ids, p=cust_weights))
            p_record = products_df.iloc[rng.integers(0, len(products_df))]
            
            # Date simulation with weekend & evening weights
            d = str(rng.choice(dates))
            hour = int(rng.choice(range(8, 23), p=[0.02, 0.03, 0.05, 0.08, 0.10, 0.08, 0.06, 0.06, 0.08, 0.12, 0.14, 0.11, 0.05, 0.01, 0.01]))
            minute = rng.integers(0, 60)
            second = rng.integers(0, 60)
            ts = f"{d} {hour:02d}:{minute:02d}:{second:02d}"

            qty = int(rng.choice([1, 2, 3, 4], p=[0.65, 0.25, 0.07, 0.03]))
            u_price = float(p_record["selling_price"])
            disc = round(float(qty * u_price * rng.choice([0.0, 0.05, 0.10, 0.15], p=[0.6, 0.2, 0.15, 0.05])), 2)

            tx_rows.append({
                "transaction_id": tx_id,
                "merchant_id": mid,
                "customer_id": cid,
                "timestamp": ts,
                "product_id": str(p_record["product_id"]),
                "product_category": str(p_record["product_category"]),
                "quantity": qty,
                "unit_price": u_price,
                "discount": disc,
                "payment_method": rng.choice(["UPI", "Cash", "Card", "NetBanking"], p=[0.7, 0.15, 0.12, 0.03]),
            })

        tx_df = pd.DataFrame(tx_rows)
        tx_df.to_csv(raw_dir / "transactions.csv", index=False)

    return {
        "products": products_df,
        "merchants": merchants_df,
        "customers": customers_df,
        "festivals": festivals_df,
        "weather": weather_df,
        "transactions": tx_df,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    generate_all_datasets()
