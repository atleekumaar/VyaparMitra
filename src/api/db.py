"""
Database access and initialization for VyaparMitra Backend Architecture.
Provides SQLite connection management, table schemas, and automatic seeding.
"""

from __future__ import annotations

import hashlib
import logging
import secrets
import sqlite3
from datetime import datetime, timezone
from typing import Generator
import pandas as pd
from src.api.config import get_api_config

logger = logging.getLogger("vyaparmitra.api.db")


def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a unique salt."""
    salt = secrets.token_hex(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2:sha256:{iterations}${salt}${derived.hex()}"


def get_db_connection() -> sqlite3.Connection:
    """Creates a raw SQLite connection with Row factory and multi-thread safety."""
    config = get_api_config()
    conn = sqlite3.connect(str(config.db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency for obtaining a DB connection with transaction commit and auto-close."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_table_df(table_name: str) -> pd.DataFrame:
    """Utility function to load a table into a pandas DataFrame."""
    conn = get_db_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


def save_table_df(table_name: str, df: pd.DataFrame) -> None:
    """Utility function to save a pandas DataFrame into SQLite table."""
    conn = get_db_connection()
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    except Exception:
        pass
    finally:
        conn.close()


def init_db() -> None:
    """
    Initializes core operational tables for VyaparMitra backend architecture:
    - businesses & branches (multi-branch tenant isolation)
    - users (RBAC: Owner, Manager, Staff)
    - inventory (stock tracking, low stock thresholds)
    - sales & sale_items (POS transactions & stock deductions)
    - customers & customer_ledgers (Khata / Udhaar tracking)
    - suppliers & supplier_invoices (vendor management)
    - expenses (financial accounting)
    - audit_logs (security & change tracking)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Businesses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            business_type TEXT DEFAULT 'Retail',
            gstin TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # 2. Branches
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS branches (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            name TEXT NOT NULL,
            code TEXT,
            city TEXT,
            state TEXT,
            address TEXT,
            phone TEXT,
            is_main INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE
        )
    """)

    # 3. Users (Owner, Admin, Manager, Staff)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            branch_id TEXT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            phone TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE,
            FOREIGN KEY(branch_id) REFERENCES branches(id) ON DELETE SET NULL
        )
    """)

    # 4. Inventory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            branch_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            current_stock INTEGER NOT NULL DEFAULT 0,
            min_stock_threshold INTEGER NOT NULL DEFAULT 10,
            unit_cost REAL NOT NULL DEFAULT 0.0,
            selling_price REAL NOT NULL DEFAULT 0.0,
            barcode TEXT,
            unit TEXT DEFAULT 'pcs',
            updated_at TEXT NOT NULL,
            UNIQUE(business_id, branch_id, product_id),
            FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE,
            FOREIGN KEY(branch_id) REFERENCES branches(id) ON DELETE CASCADE
        )
    """)

    # 5. Sales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id TEXT PRIMARY KEY,
            invoice_number TEXT UNIQUE NOT NULL,
            business_id TEXT NOT NULL,
            branch_id TEXT NOT NULL,
            customer_id TEXT,
            customer_name TEXT,
            subtotal REAL NOT NULL,
            discount REAL NOT NULL DEFAULT 0.0,
            tax REAL NOT NULL DEFAULT 0.0,
            total_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'COMPLETED',
            created_by TEXT NOT NULL,
            created_by_name TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE,
            FOREIGN KEY(branch_id) REFERENCES branches(id) ON DELETE CASCADE
        )
    """)

    # 6. Sale Items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id TEXT PRIMARY KEY,
            sale_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            unit_cost REAL NOT NULL DEFAULT 0.0,
            discount REAL NOT NULL DEFAULT 0.0,
            total_price REAL NOT NULL,
            FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE
        )
    """)

    # 7. Customers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            city TEXT,
            credit_limit REAL NOT NULL DEFAULT 5000.0,
            current_balance REAL NOT NULL DEFAULT 0.0,
            loyalty_points INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL,
            FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE
        )
    """)

    # 8. Customer Ledgers (Khata / Udhaar)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_ledgers (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            entry_type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_after REAL NOT NULL,
            reference_id TEXT,
            notes TEXT,
            created_by TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE,
            FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
    """)

    # 9. Suppliers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            gstin TEXT,
            current_payable REAL NOT NULL DEFAULT 0.0,
            payment_terms TEXT DEFAULT 'Net 30',
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL,
            FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE
        )
    """)

    # 10. Supplier Invoices (Purchases)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS supplier_invoices (
            id TEXT PRIMARY KEY,
            invoice_number TEXT NOT NULL,
            business_id TEXT NOT NULL,
            branch_id TEXT NOT NULL,
            supplier_id TEXT NOT NULL,
            total_amount REAL NOT NULL,
            paid_amount REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'UNPAID',
            items_json TEXT,
            notes TEXT,
            created_by TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE,
            FOREIGN KEY(branch_id) REFERENCES branches(id) ON DELETE CASCADE,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
        )
    """)

    # 11. Expenses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            branch_id TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            description TEXT,
            receipt_url TEXT,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE,
            FOREIGN KEY(branch_id) REFERENCES branches(id) ON DELETE CASCADE
        )
    """)

    # 12. Audit Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            branch_id TEXT,
            user_id TEXT NOT NULL,
            user_name TEXT NOT NULL,
            user_role TEXT NOT NULL,
            action TEXT NOT NULL,
            resource TEXT NOT NULL,
            resource_id TEXT,
            details TEXT,
            ip_address TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE
        )
    """)

    # Create indices for high-frequency queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_business ON users(business_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_lookup ON inventory(business_id, branch_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_lookup ON sales(business_id, branch_id, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_business ON customers(business_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_ledgers ON customer_ledgers(business_id, customer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_lookup ON expenses(business_id, branch_id, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_lookup ON audit_logs(business_id, timestamp)")

    conn.commit()
    conn.close()

    seed_default_data()


def seed_default_data() -> None:
    """Seeds baseline data for demo business M015 and default roles if absent."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    # Check if business M015 exists
    biz = cursor.execute("SELECT id FROM businesses WHERE id = 'M015'").fetchone()
    if not biz:
        cursor.execute("""
            INSERT INTO businesses (id, name, business_type, gstin, phone, email, address, city, state, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "M015",
            "Merchant_015 Bakery & Retail",
            "Bakery",
            "07AAAAA0000A1Z5",
            "+919876543210",
            "contact@merchant015.com",
            "Shop 12, Sector 18 Market",
            "Noida",
            "Uttar Pradesh",
            now_str,
        ))

    # Seed main branch and secondary branch
    branches = [
        ("BR_M015_MAIN", "M015", "Main Branch - Sector 18", "SEC18", "Noida", "Uttar Pradesh", "Shop 12, Sector 18 Market", "+919876543210", 1),
        ("BR_M015_SEC62", "M015", "Sector 62 Outlet", "SEC62", "Noida", "Uttar Pradesh", "Plot 45, Sector 62", "+919876543211", 0),
    ]
    for b_id, biz_id, name, code, city, state, addr, phone, is_main in branches:
        exists = cursor.execute("SELECT id FROM branches WHERE id = ?", (b_id,)).fetchone()
        if not exists:
            cursor.execute("""
                INSERT INTO branches (id, business_id, name, code, city, state, address, phone, is_main, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (b_id, biz_id, name, code, city, state, addr, phone, is_main, now_str))

    # Seed 3 User Roles: Owner/Admin, Manager, Staff
    default_users = [
        (
            "USR_OWNER_01",
            "M015",
            "BR_M015_MAIN",
            "owner_m015",
            "owner@vyaparmitra.com",
            "Atul Kumar (Owner)",
            hash_password("OwnerPassword123!"),
            "owner",
            "+919876543210",
        ),
        (
            "USR_MGR_01",
            "M015",
            "BR_M015_MAIN",
            "manager_m015",
            "manager@vyaparmitra.com",
            "Vikram Singh (Manager)",
            hash_password("ManagerPassword123!"),
            "manager",
            "+919876543212",
        ),
        (
            "USR_STAFF_01",
            "M015",
            "BR_M015_MAIN",
            "staff_m015",
            "staff@vyaparmitra.com",
            "Rohan Sharma (POS Staff)",
            hash_password("StaffPassword123!"),
            "staff",
            "+919876543213",
        ),
    ]
    for u_id, b_id, br_id, uname, email, fname, pwd_hash, role, phone in default_users:
        exists = cursor.execute("SELECT id FROM users WHERE username = ?", (uname,)).fetchone()
        if not exists:
            cursor.execute("""
                INSERT INTO users (id, business_id, branch_id, username, email, full_name, password_hash, role, phone, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (u_id, b_id, br_id, uname, email, fname, pwd_hash, role, phone, now_str))

    # Seed Inventory from clean_products table if inventory empty for M015
    inv_count = cursor.execute("SELECT COUNT(*) FROM inventory WHERE business_id = 'M015'").fetchone()[0]
    if inv_count == 0:
        try:
            prod_rows = cursor.execute("SELECT product_id, product_name, product_category, unit_cost, selling_price FROM clean_products").fetchall()
            for row in prod_rows:
                p_id, p_name, p_cat, u_cost, s_price = row
                for br_id in ["BR_M015_MAIN", "BR_M015_SEC62"]:
                    inv_id = f"INV_{br_id}_{p_id}"
                    cursor.execute("""
                        INSERT OR IGNORE INTO inventory (
                            id, business_id, branch_id, product_id, product_name, category,
                            current_stock, min_stock_threshold, unit_cost, selling_price, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        inv_id, "M015", br_id, p_id, p_name, p_cat,
                        75, 15, float(u_cost), float(s_price), now_str
                    ))
        except Exception as e:
            logger.warning(f"Could not populate inventory from clean_products: {e}")

    # Seed Customers from clean_customers if customers table empty for M015
    cust_count = cursor.execute("SELECT COUNT(*) FROM customers WHERE business_id = 'M015'").fetchone()[0]
    if cust_count == 0:
        try:
            c_rows = cursor.execute("SELECT customer_id, customer_name, city, signup_date FROM clean_customers LIMIT 25").fetchall()
            for r in c_rows:
                c_id, c_name, c_city, s_date = r
                cursor.execute("""
                    INSERT OR IGNORE INTO customers (
                        id, business_id, name, phone, email, address, city, credit_limit, current_balance, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    c_id, "M015", c_name, "+919811223344", f"{c_id.lower()}@example.com",
                    f"Sector 15, {c_city}", c_city, 10000.0, 0.0, s_date or now_str
                ))
        except Exception as e:
            logger.warning(f"Could not populate customers: {e}")

    # Seed Suppliers if empty
    sup_count = cursor.execute("SELECT COUNT(*) FROM suppliers WHERE business_id = 'M015'").fetchone()[0]
    if sup_count == 0:
        suppliers = [
            ("SUP_M015_01", "M015", "Delhi Flour & Dairy Wholesalers", "Rajesh Gupta", "+919820011223", "orders@delhiflour.in", "Okhla Phase 2, New Delhi", "07AABCS1429B1Z1", 12500.0),
            ("SUP_M015_02", "M015", "Evergreen Packaging Supplies", "Sunita Verma", "+919830022334", "sales@evergreenpack.com", "Sector 8, Noida", "09AABCE9988D1Z8", 4800.0),
            ("SUP_M015_03", "M015", "Shree Ganesh Spices & Essentials", "Ganesh Agarwal", "+919840033445", "ganesh@spices.co.in", "Khari Baoli, Old Delhi", "07AAACG5544K1ZR", 0.0),
        ]
        for s_id, b_id, s_name, contact, phone, email, addr, gstin, payable in suppliers:
            cursor.execute("""
                INSERT OR IGNORE INTO suppliers (
                    id, business_id, name, contact_person, phone, email, address, gstin, current_payable, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (s_id, b_id, s_name, contact, phone, email, addr, gstin, payable, now_str))

    # Seed Sample Expenses if empty
    exp_count = cursor.execute("SELECT COUNT(*) FROM expenses WHERE business_id = 'M015'").fetchone()[0]
    if exp_count == 0:
        sample_expenses = [
            ("EXP_001", "M015", "BR_M015_MAIN", "RENT", 25000.0, "BANK_TRANSFER", "Monthly Shop Rent for Main Store", "USR_OWNER_01"),
            ("EXP_002", "M015", "BR_M015_MAIN", "UTILITY", 4200.0, "UPI", "Commercial Electricity Bill (PVVNL)", "USR_MGR_01"),
            ("EXP_003", "M015", "BR_M015_MAIN", "SALARY", 30000.0, "BANK_TRANSFER", "Staff Monthly Salaries", "USR_OWNER_01"),
        ]
        for e_id, b_id, br_id, cat, amt, p_method, desc, created_by in sample_expenses:
            cursor.execute("""
                INSERT OR IGNORE INTO expenses (
                    id, business_id, branch_id, category, amount, payment_method, description, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (e_id, b_id, br_id, cat, amt, p_method, desc, created_by, now_str))

    conn.commit()
    conn.close()
