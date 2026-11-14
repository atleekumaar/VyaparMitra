"""
Generates standard PostgreSQL SQL script (supabase_schema.sql) from vyaparmitra.db.
Outputs clean DDL and essential seed data for Supabase SQL Editor execution.
"""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "vyaparmitra.db"
OUTPUT_SQL = PROJECT_ROOT / "scripts" / "supabase_schema.sql"

def get_pg_type(sqlite_type: str) -> str:
    t = sqlite_type.upper().strip()
    if "INT" in t:
        return "BIGINT" if "64" in t else "INTEGER"
    if "REAL" in t or "FLOA" in t or "DOUB" in t or "NUM" in t:
        return "DOUBLE PRECISION"
    if "BLOB" in t:
        return "BYTEA"
    return "TEXT"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql_lines = [
        "-- ====================================================================",
        "-- VyaparMitra Complete Supabase PostgreSQL Schema & Multi-Tenant Setup",
        "-- Generated for Supabase Project: pthcubbwukibmmmsmjpm",
        "-- Run directly in Supabase Dashboard -> SQL Editor -> New Query",
        "-- ====================================================================",
        "",
        "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
        "",
    ]

    # Tables to extract DDL
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()]

    # Core operational tables order
    core_priority = [
        "businesses",
        "branches",
        "users",
        "inventory",
        "sales",
        "sale_items",
        "customers",
        "customer_ledgers",
        "suppliers",
        "supplier_invoices",
        "expenses",
        "audit_logs",
        "agent_approvals",
        "otps",
    ]

    ordered_tables = [t for t in core_priority if t in tables] + [t for t in tables if t not in core_priority]

    sql_lines.append("-- --------------------------------------------------------------------")
    sql_lines.append("-- 1. DDL: Table Definitions")
    sql_lines.append("-- --------------------------------------------------------------------")

    for table in ordered_tables:
        cursor.execute(f"PRAGMA table_info('{table}')")
        columns = cursor.fetchall()
        if not columns:
            continue

        col_defs = []
        pk_cols = []
        for cid, name, col_type, notnull, dflt_value, pk in columns:
            pg_t = get_pg_type(col_type)
            constraints = []
            if notnull:
                constraints.append("NOT NULL")
            if dflt_value is not None:
                constraints.append(f"DEFAULT {dflt_value}")
            if pk == 1 and len([c for c in columns if c[5] == 1]) == 1:
                constraints.append("PRIMARY KEY")
            elif pk > 0:
                pk_cols.append(f'"{name}"')

            col_defs.append(f'    "{name}" {pg_t} {" ".join(constraints)}'.rstrip())

        if pk_cols:
            col_defs.append(f"    PRIMARY KEY ({', '.join(pk_cols)})")

        create_stmt = f'CREATE TABLE IF NOT EXISTS public."{table}" (\n' + ",\n".join(col_defs) + "\n);"
        sql_lines.append(create_stmt)
        sql_lines.append("")

    sql_lines.append("-- --------------------------------------------------------------------")
    sql_lines.append("-- 2. Performance & Multi-Tenant Indexes")
    sql_lines.append("-- --------------------------------------------------------------------")
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_users_business ON public."users"("business_id");',
        'CREATE INDEX IF NOT EXISTS idx_users_username ON public."users"("username");',
        'CREATE INDEX IF NOT EXISTS idx_users_email ON public."users"("email");',
        'CREATE INDEX IF NOT EXISTS idx_inventory_lookup ON public."inventory"("business_id", "branch_id");',
        'CREATE INDEX IF NOT EXISTS idx_sales_lookup ON public."sales"("business_id", "branch_id", "created_at");',
        'CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON public."sale_items"("sale_id");',
        'CREATE INDEX IF NOT EXISTS idx_customers_business ON public."customers"("business_id");',
        'CREATE INDEX IF NOT EXISTS idx_customer_ledgers ON public."customer_ledgers"("business_id", "customer_id");',
        'CREATE INDEX IF NOT EXISTS idx_expenses_lookup ON public."expenses"("business_id", "branch_id", "created_at");',
        'CREATE INDEX IF NOT EXISTS idx_audit_logs_lookup ON public."audit_logs"("business_id", "timestamp");',
        'CREATE INDEX IF NOT EXISTS idx_agent_approvals_lookup ON public."agent_approvals"("business_id", "status");',
        'CREATE INDEX IF NOT EXISTS idx_otps_lookup ON public."otps"("identifier", "is_used", "expires_at");',
    ]
    sql_lines.extend(indexes)
    sql_lines.append("")

    sql_lines.append("-- --------------------------------------------------------------------")
    sql_lines.append("-- 3. Core Baseline Seed Data (Businesses, Branches, Users, Inventory)")
    sql_lines.append("-- --------------------------------------------------------------------")

    seed_tables = [
        "businesses",
        "branches",
        "users",
        "inventory",
        "clean_products",
        "clean_merchants",
        "sales_forecast_7d",
        "business_trend_predictions",
        "all_recommendations",
        "pricing_recommendations",
        "inventory_recommendations",
    ]

    for table in seed_tables:
        if table not in tables:
            continue
        cursor.execute(f"SELECT * FROM {table} LIMIT 100")
        rows = cursor.fetchall()
        if not rows:
            continue

        col_names = [f'"{d[0]}"' for d in cursor.description]
        col_str = ", ".join(col_names)

        value_clauses = []
        for row in rows:
            formatted_vals = []
            for v in row:
                if v is None:
                    formatted_vals.append("NULL")
                elif isinstance(v, (int, float)):
                    formatted_vals.append(str(v))
                else:
                    # Escape single quotes
                    escaped = str(v).replace("'", "''")
                    formatted_vals.append(f"'{escaped}'")
            value_clauses.append(f"({', '.join(formatted_vals)})")

        if value_clauses:
            insert_stmt = f'INSERT INTO public."{table}" ({col_str})\nVALUES\n  ' + ",\n  ".join(value_clauses) + "\nON CONFLICT DO NOTHING;"
            sql_lines.append(insert_stmt)
            sql_lines.append("")

    conn.close()

    OUTPUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_lines))

    print(f"Successfully generated {OUTPUT_SQL} ({len(sql_lines)} lines)")

if __name__ == "__main__":
    main()
