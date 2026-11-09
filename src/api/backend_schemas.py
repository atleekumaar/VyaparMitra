"""
Pydantic Schemas for VyaparMitra Backend Core Architecture:
Authentication, RBAC, Multi-Branch, Sales, Inventory, Customers/Khata, Suppliers, Finance, and Audit Logs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# 1. AUTHENTICATION & USER MANAGEMENT SCHEMAS
# ============================================================================

class RegisterBusinessRequest(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=120)
    business_type: str = Field(default="Retail", max_length=60)
    gstin: Optional[str] = Field(None, max_length=15)
    city: str = Field(..., min_length=2, max_length=60)
    state: str = Field(..., min_length=2, max_length=60)
    address: Optional[str] = None
    phone: str = Field(..., min_length=10, max_length=15)
    owner_username: str = Field(..., min_length=3, max_length=50)
    owner_email: str = Field(..., min_length=5, max_length=100)
    owner_full_name: str = Field(..., min_length=2, max_length=100)
    owner_password: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    username_or_email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=4)


class UserResponse(BaseModel):
    id: str
    business_id: str
    branch_id: Optional[str] = None
    username: str
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    is_active: bool
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    permissions: List[str]


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(..., description="owner, manager, staff")
    branch_id: Optional[str] = None
    phone: Optional[str] = None


class RoleInfoItem(BaseModel):
    role: str
    title: str
    description: str
    permissions: List[str]


class RolesListResponse(BaseModel):
    roles: List[RoleInfoItem]


# ============================================================================
# 2. MULTI-BRANCH SCHEMAS
# ============================================================================

class BranchCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    city: str = Field(..., min_length=2, max_length=60)
    state: str = Field(..., min_length=2, max_length=60)
    address: Optional[str] = None
    phone: Optional[str] = None
    is_main: bool = False


class BranchResponse(BaseModel):
    id: str
    business_id: str
    name: str
    code: Optional[str] = None
    city: str
    state: str
    address: Optional[str] = None
    phone: Optional[str] = None
    is_main: bool
    created_at: str


class BranchListResponse(BaseModel):
    total: int
    branches: List[BranchResponse]


# ============================================================================
# 3. SALES & POS SCHEMAS
# ============================================================================

class SaleItemInput(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)
    unit_price: Optional[float] = Field(None, ge=0.0)
    discount: float = Field(default=0.0, ge=0.0)


class CreateSaleRequest(BaseModel):
    branch_id: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = "Walk-in Customer"
    items: List[SaleItemInput] = Field(..., min_length=1)
    payment_method: str = Field(default="CASH", description="CASH, UPI, CARD, CREDIT")
    discount: float = Field(default=0.0, ge=0.0)
    tax: float = Field(default=0.0, ge=0.0)
    notes: Optional[str] = None


class SaleItemOutput(BaseModel):
    id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    unit_cost: float
    discount: float
    total_price: float


class SaleResponse(BaseModel):
    id: str
    invoice_number: str
    business_id: str
    branch_id: str
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    subtotal: float
    discount: float
    tax: float
    total_amount: float
    payment_method: str
    status: str
    created_by: str
    created_by_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    items: List[SaleItemOutput] = Field(default_factory=list)
    low_stock_warnings: List[str] = Field(default_factory=list)


class SaleListResponse(BaseModel):
    total_count: int
    total_revenue: float
    sales: List[SaleResponse]


class RefundSaleResponse(BaseModel):
    sale_id: str
    invoice_number: str
    status: str
    restored_items_count: int
    message: str


# ============================================================================
# 4. INVENTORY MANAGEMENT SCHEMAS
# ============================================================================

class InventoryItemOutput(BaseModel):
    id: str
    business_id: str
    branch_id: str
    product_id: str
    product_name: str
    category: str
    current_stock: int
    min_stock_threshold: int
    unit_cost: float
    selling_price: float
    barcode: Optional[str] = None
    unit: str
    stock_value_cost: float
    stock_value_retail: float
    is_low_stock: bool
    updated_at: str


class InventoryListResponse(BaseModel):
    total_count: int
    total_stock_units: int
    total_valuation_cost: float
    items: List[InventoryItemOutput]


class StockAdjustmentRequest(BaseModel):
    inventory_id: str
    adjustment_type: str = Field(..., description="INCREASE, DECREASE, SET")
    quantity: int = Field(..., ge=0)
    reason: str = Field(..., description="DAMAGE, EXPIRED, RESTOCK, PHYSICAL_AUDIT, CORRECTION")
    notes: Optional[str] = None


class InventoryCreateRequest(BaseModel):
    branch_id: Optional[str] = None
    product_id: str
    product_name: str
    category: str
    current_stock: int = Field(default=0, ge=0)
    min_stock_threshold: int = Field(default=10, ge=0)
    unit_cost: float = Field(..., ge=0.0)
    selling_price: float = Field(..., ge=0.0)
    barcode: Optional[str] = None
    unit: str = "pcs"


class InventoryUpdateRequest(BaseModel):
    product_name: Optional[str] = None
    category: Optional[str] = None
    min_stock_threshold: Optional[int] = Field(None, ge=0)
    unit_cost: Optional[float] = Field(None, ge=0.0)
    selling_price: Optional[float] = Field(None, ge=0.0)
    barcode: Optional[str] = None


class LowStockItemOutput(BaseModel):
    inventory_id: str
    branch_id: str
    product_id: str
    product_name: str
    category: str
    current_stock: int
    min_stock_threshold: int
    suggested_reorder_qty: int
    unit_cost: float
    estimated_reorder_cost: float


class LowStockListResponse(BaseModel):
    total_low_stock_items: int
    items: List[LowStockItemOutput]


# ============================================================================
# 5. CUSTOMERS & KHATA (CREDIT) SCHEMAS
# ============================================================================

class CustomerCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    credit_limit: float = Field(default=5000.0, ge=0.0)


class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    credit_limit: Optional[float] = Field(None, ge=0.0)
    status: Optional[str] = None


class CustomerManageOutput(BaseModel):
    id: str
    business_id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    credit_limit: float
    current_balance: float  # Udhaar owed to merchant
    loyalty_points: int
    status: str
    created_at: str


class CustomerManageListResponse(BaseModel):
    total_customers: int
    total_outstanding_credit: float
    customers: List[CustomerManageOutput]


class CustomerKhataPaymentRequest(BaseModel):
    amount: float = Field(..., gt=0.0)
    payment_method: str = Field(default="CASH", description="CASH, UPI, BANK_TRANSFER, CHEQUE")
    notes: Optional[str] = None


class LedgerEntryOutput(BaseModel):
    id: str
    business_id: str
    customer_id: str
    entry_type: str  # DEBIT (credit sale), CREDIT (payment received)
    amount: float
    balance_after: float
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None
    created_at: str


class CustomerLedgerResponse(BaseModel):
    customer_id: str
    customer_name: str
    credit_limit: float
    current_balance: float
    total_entries: int
    entries: List[LedgerEntryOutput]


# ============================================================================
# 6. SUPPLIER & PURCHASE SCHEMAS
# ============================================================================

class SupplierCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gstin: Optional[str] = None
    payment_terms: str = "Net 30"


class SupplierUpdateRequest(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gstin: Optional[str] = None
    payment_terms: Optional[str] = None
    status: Optional[str] = None


class SupplierOutput(BaseModel):
    id: str
    business_id: str
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gstin: Optional[str] = None
    current_payable: float
    payment_terms: str
    status: str
    created_at: str


class SupplierListResponse(BaseModel):
    total_suppliers: int
    total_payables: float
    suppliers: List[SupplierOutput]


class SupplierInvoiceItem(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)
    unit_cost: float = Field(..., ge=0.0)


class SupplierInvoiceRequest(BaseModel):
    branch_id: Optional[str] = None
    invoice_number: str = Field(..., min_length=2)
    total_amount: float = Field(..., gt=0.0)
    paid_amount: float = Field(default=0.0, ge=0.0)
    items: List[SupplierInvoiceItem] = Field(default_factory=list)
    auto_update_inventory: bool = True
    notes: Optional[str] = None


class SupplierPaymentRequest(BaseModel):
    amount: float = Field(..., gt=0.0)
    payment_method: str = Field(default="BANK_TRANSFER", description="BANK_TRANSFER, UPI, CASH, CHEQUE")
    notes: Optional[str] = None


class SupplierInvoiceResponse(BaseModel):
    invoice_id: str
    invoice_number: str
    supplier_name: str
    total_amount: float
    paid_amount: float
    unpaid_amount: float
    status: str
    inventory_items_inwarded: int
    created_at: str


class SupplierPaymentResponse(BaseModel):
    supplier_id: str
    supplier_name: str
    amount_paid: float
    previous_payable: float
    remaining_payable: float
    expense_id: str
    paid_at: str


# ============================================================================
# 7. FINANCE & EXPENSES SCHEMAS
# ============================================================================

class ExpenseCreateRequest(BaseModel):
    branch_id: Optional[str] = None
    category: str = Field(..., description="RENT, SALARY, UTILITY, PURCHASE, LOGISTICS, MAINTENANCE, MARKETING, OTHER")
    amount: float = Field(..., gt=0.0)
    payment_method: str = Field(default="UPI", description="CASH, UPI, BANK_TRANSFER, CHEQUE")
    description: Optional[str] = None
    receipt_url: Optional[str] = None


class ExpenseOutput(BaseModel):
    id: str
    business_id: str
    branch_id: str
    category: str
    amount: float
    payment_method: str
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    created_by: str
    created_at: str


class ExpenseListResponse(BaseModel):
    total_count: int
    total_expenses: float
    expenses: List[ExpenseOutput]


class FinanceSummaryResponse(BaseModel):
    business_id: str
    branch_id: Optional[str] = None
    total_sales_revenue: float
    cost_of_goods_sold: float
    gross_profit: float
    gross_profit_margin_pct: float
    total_operational_expenses: float
    net_profit: float
    net_profit_margin_pct: float
    total_receivables_khata: float
    total_payables_suppliers: float
    cash_inflow: float
    cash_outflow: float


class CashflowDailyPoint(BaseModel):
    date: str
    inflow: float
    outflow: float
    net: float


class CashflowSummaryResponse(BaseModel):
    total_inflow: float
    total_outflow: float
    net_cashflow: float
    daily_breakdown: List[CashflowDailyPoint]


# ============================================================================
# 8. AUDIT LOG SCHEMAS
# ============================================================================

class AuditLogOutput(BaseModel):
    id: str
    business_id: str
    branch_id: Optional[str] = None
    user_id: str
    user_name: str
    user_role: str
    action: str
    resource: str
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: str


class AuditLogListResponse(BaseModel):
    total_logs: int
    logs: List[AuditLogOutput]
