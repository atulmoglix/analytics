import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "manual_invoice.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create unified documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_type TEXT NOT NULL,          -- 'invoice', 'credit_note', 'debit_note'
        sale_type TEXT NOT NULL,
        invoice_number TEXT NOT NULL,
        invoice_date TEXT,               -- For Invoice / DN
        note_no TEXT,                    -- For CN
        return_date TEXT,                -- For CN
        id_company TEXT NOT NULL,
        plant_id TEXT NOT NULL,
        plant_name TEXT NOT NULL,
        return_remark TEXT,              -- For CN
        value_sp REAL,                   -- For Invoice / DN
        qty REAL,
        sales_wo_tax REAL,               -- For Invoice / DN
        sales_with_tax REAL,             -- For Invoice / DN
        tax REAL,                        -- For Invoice / DN
        gmv REAL,                        -- For Invoice / DN
        cogs REAL,                       -- For Invoice / DN
        eff_cogs REAL,                   -- For Invoice / DN
        msn TEXT,
        supplier_id TEXT,
        supplier_name TEXT,
        return_sales REAL,               -- For CN
        return_cogs REAL,                -- For CN
        return_tax REAL,                 -- For CN
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Check if table is empty, if so, seed sample data
    cursor.execute("SELECT COUNT(*) FROM documents")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # 1. Seed Sample Invoice
        cursor.execute("""
        INSERT INTO documents (
            doc_type, sale_type, invoice_number, invoice_date, id_company, plant_id, plant_name,
            value_sp, qty, sales_wo_tax, sales_with_tax, tax, gmv, cogs, eff_cogs, msn, supplier_id, supplier_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "invoice", "Manual", "INV-2026-001", "2026-06-20", "MOGLIX-IND", "PL001", "Delhi Warehouse",
            150000.0, 150.0, 127118.64, 150000.0, 22881.36, 150000.0, 100000.0, 98000.0, "MSN-99881", "SUP-552", "Acme Industrial Corp"
        ))
        
        # 2. Seed Sample Credit Note (CN)
        cursor.execute("""
        INSERT INTO documents (
            doc_type, sale_type, invoice_number, note_no, return_date, id_company, plant_id, plant_name,
            return_remark, return_sales, return_cogs, return_tax, msn, supplier_id, supplier_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "credit_note", "Manual", "INV-2026-001", "CN-2026-001", "2026-06-21", "MOGLIX-IND", "PL001", "Delhi Warehouse",
            "Defective items returned", 20000.0, 15000.0, 3600.0, "MSN-99881", "SUP-552", "Acme Industrial Corp"
        ))
        
        # 3. Seed Sample Debit Note (DN)
        cursor.execute("""
        INSERT INTO documents (
            doc_type, sale_type, invoice_number, invoice_date, id_company, plant_id, plant_name,
            value_sp, qty, sales_wo_tax, sales_with_tax, tax, gmv, cogs, eff_cogs, msn, supplier_id, supplier_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "debit_note", "Manual DN Price", "INV-2026-001", "2026-06-22", "MOGLIX-IND", "PL001", "Delhi Warehouse",
            12000.0, 10.0, 10169.49, 12000.0, 1830.51, 12000.0, 8000.0, 7800.0, "MSN-99881", "SUP-552", "Acme Industrial Corp"
        ))
        
        conn.commit()
        print("Database initialized and sample data seeded successfully.")
    else:
        print("Database already exists with data.")
        
    conn.close()

if __name__ == "__main__":
    init_db()
