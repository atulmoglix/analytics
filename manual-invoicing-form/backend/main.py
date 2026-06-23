import os
import sqlite3
from datetime import date
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List

from .models import DocumentType, InvoiceModel, CreditNoteModel, DebitNoteModel, DocumentResponse
from .database import get_db_connection, init_db
from .pdf_generator import generate_pdf

# Initialize DB on startup
init_db()

app = FastAPI(title="Manual Invoicing Form API", version="1.0.0")

# CORS middleware to allow local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def serialize_row(row):
    d = dict(row)
    # Parse dates if present
    if d.get("invoice_date"):
        d["invoice_date"] = date.fromisoformat(d["invoice_date"])
    if d.get("return_date"):
        d["return_date"] = date.fromisoformat(d["return_date"])
    return d

@app.post("/api/documents/invoice", response_model=DocumentResponse, status_code=201)
def create_invoice(invoice: InvoiceModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO documents (
            doc_type, sale_type, invoice_number, invoice_date, id_company, plant_id, plant_name,
            value_sp, qty, sales_wo_tax, sales_with_tax, tax, gmv, cogs, eff_cogs, msn, supplier_id, supplier_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            DocumentType.INVOICE.value,
            invoice.sale_type.value,
            invoice.invoice_number,
            invoice.invoice_date.isoformat(),
            invoice.id_company,
            invoice.plant_id,
            invoice.plant_name,
            invoice.value_sp,
            invoice.qty,
            invoice.sales_wo_tax,
            invoice.sales_with_tax,
            invoice.tax,
            invoice.gmv,
            invoice.cogs,
            invoice.eff_cogs,
            invoice.msn,
            invoice.supplier_id,
            invoice.supplier_name
        ))
        conn.commit()
        doc_id = cursor.lastrowid
        
        # Retrieve the newly created document
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        return serialize_row(row)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/documents/credit-note", response_model=DocumentResponse, status_code=201)
def create_credit_note(cn: CreditNoteModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO documents (
            doc_type, sale_type, invoice_number, note_no, return_date, id_company, plant_id, plant_name,
            return_remark, return_sales, return_cogs, return_tax, msn, supplier_id, supplier_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            DocumentType.CREDIT_NOTE.value,
            cn.sale_type.value,
            cn.invoice_number,
            cn.note_no,
            cn.return_date.isoformat(),
            cn.id_company,
            cn.plant_id,
            cn.plant_name,
            cn.return_remark,
            cn.return_sales,
            cn.return_cogs,
            cn.return_tax,
            cn.msn,
            cn.supplier_id,
            cn.supplier_name
        ))
        conn.commit()
        doc_id = cursor.lastrowid
        
        # Retrieve the newly created document
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        return serialize_row(row)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/documents/debit-note", response_model=DocumentResponse, status_code=201)
def create_debit_note(dn: DebitNoteModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO documents (
            doc_type, sale_type, invoice_number, invoice_date, id_company, plant_id, plant_name,
            value_sp, qty, sales_wo_tax, sales_with_tax, tax, gmv, cogs, eff_cogs, msn, supplier_id, supplier_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            DocumentType.DEBIT_NOTE.value,
            dn.sale_type.value,
            dn.invoice_number,
            dn.invoice_date.isoformat(),
            dn.id_company,
            dn.plant_id,
            dn.plant_name,
            dn.value_sp,
            dn.qty,
            dn.sales_wo_tax,
            dn.sales_with_tax,
            dn.tax,
            dn.gmv,
            dn.cogs,
            dn.eff_cogs,
            dn.msn,
            dn.supplier_id,
            dn.supplier_name
        ))
        conn.commit()
        doc_id = cursor.lastrowid
        
        # Retrieve the newly created document
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        return serialize_row(row)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/documents", response_model=List[DocumentResponse])
def get_documents(doc_type: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if doc_type:
            cursor.execute("SELECT * FROM documents WHERE doc_type = ? ORDER BY id DESC", (doc_type,))
        else:
            cursor.execute("SELECT * FROM documents ORDER BY id DESC")
        rows = cursor.fetchall()
        return [serialize_row(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/documents/{id}", response_model=DocumentResponse)
def get_document(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM documents WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")
        return serialize_row(row)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/documents/{id}/pdf")
def get_document_pdf(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM documents WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = serialize_row(row)
        
        # Create a temp file path for pdf
        pdf_dir = os.path.join(os.path.dirname(__file__), "temp_pdfs")
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"doc_{id}.pdf")
        
        generate_pdf(doc_data, pdf_path)
        
        # Get custom name for download
        doc_type_str = doc_data["doc_type"].upper().replace("_", "")
        doc_no = doc_data.get("note_no") if doc_data["doc_type"] == "credit_note" else doc_data.get("invoice_number")
        filename = f"{doc_type_str}_{doc_no}.pdf"
        
        return FileResponse(pdf_path, media_type="application/pdf", filename=filename)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Serves static frontend client files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
