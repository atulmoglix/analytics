from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum

class DocumentType(str, Enum):
    INVOICE = "invoice"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"

class SaleTypeInvoice(str, Enum):
    MANUAL = "Manual"
    INTEREST = "Interest"

class SaleTypeCN(str, Enum):
    MANUAL = "Manual"
    INTEREST = "Interest"

class SaleTypeDN(str, Enum):
    MANUAL_DN_PRICE = "Manual DN Price"

# Invoice model
class InvoiceModel(BaseModel):
    sale_type: SaleTypeInvoice
    invoice_number: str = Field(..., min_length=1)
    invoice_date: date
    id_company: str = Field(..., min_length=1)
    plant_id: str = Field(..., min_length=1)
    plant_name: str = Field(..., min_length=1)
    value_sp: float
    sales_wo_tax: float
    qty: Optional[float] = None
    sales_with_tax: Optional[float] = None
    tax: Optional[float] = None
    gmv: Optional[float] = None
    cogs: Optional[float] = None
    eff_cogs: Optional[float] = None
    msn: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None

# Credit Note model
class CreditNoteModel(BaseModel):
    sale_type: SaleTypeCN
    invoice_number: str = Field(..., min_length=1)
    return_date: date
    note_no: str = Field(..., min_length=1)
    id_company: str = Field(..., min_length=1)
    plant_id: str = Field(..., min_length=1)
    plant_name: str = Field(..., min_length=1)
    return_remark: str = Field(..., min_length=1)
    return_sales: Optional[float] = None
    return_cogs: Optional[float] = None
    return_tax: Optional[float] = None
    msn: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None

# Debit Note model
class DebitNoteModel(BaseModel):
    sale_type: SaleTypeDN
    invoice_number: str = Field(..., min_length=1)
    invoice_date: date
    id_company: str = Field(..., min_length=1)
    plant_id: str = Field(..., min_length=1)
    plant_name: str = Field(..., min_length=1)
    value_sp: float
    sales_wo_tax: float
    qty: Optional[float] = None
    sales_with_tax: Optional[float] = None
    tax: Optional[float] = None
    gmv: Optional[float] = None
    cogs: Optional[float] = None
    eff_cogs: Optional[float] = None
    msn: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None

# Unified model for API response / generic read
class DocumentResponse(BaseModel):
    id: int
    doc_type: DocumentType
    sale_type: str
    invoice_number: str
    invoice_date: Optional[date] = None
    note_no: Optional[str] = None
    return_date: Optional[date] = None
    id_company: str
    plant_id: str
    plant_name: str
    return_remark: Optional[str] = None
    value_sp: Optional[float] = None
    qty: Optional[float] = None
    sales_wo_tax: Optional[float] = None
    sales_with_tax: Optional[float] = None
    tax: Optional[float] = None
    gmv: Optional[float] = None
    cogs: Optional[float] = None
    eff_cogs: Optional[float] = None
    msn: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None
    return_sales: Optional[float] = None
    return_cogs: Optional[float] = None
    return_tax: Optional[float] = None
    created_at: str
