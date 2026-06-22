// API URL Base (Assuming frontend is served by FastAPI or runs on localhost:8000)
const API_BASE = window.location.origin;

// Detect Environment (GitHub Pages or opening index.html directly)
const isGitHubPages = window.location.hostname.includes('github.io') || window.location.protocol === 'file:';

// State Management
let documents = [];

// DOM Elements
const pages = {
    'dashboard': document.getElementById('tab-dashboard'),
    'create-invoice': document.getElementById('tab-create-invoice'),
    'create-cn': document.getElementById('tab-create-cn'),
    'create-dn': document.getElementById('tab-create-dn')
};

const navButtons = document.querySelectorAll('.nav-btn');
const pageTitle = document.getElementById('page-title');
const themeToggleBtn = document.getElementById('theme-toggle');
const filterDocType = document.getElementById('filter-doc-type');
const documentsTbody = document.getElementById('documents-tbody');

// Stat Display Elements
const statInvoiceCount = document.getElementById('stat-invoice-count');
const statCnCount = document.getElementById('stat-cn-count');
const statDnCount = document.getElementById('stat-dn-count');

// Modals
const detailsModal = document.getElementById('details-modal');
const modalDocTitle = document.getElementById('modal-doc-title');
const modalDetailsBody = document.getElementById('modal-details-body');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnModalClose = document.getElementById('btn-modal-close');
const btnModalDownload = document.getElementById('btn-modal-download');
let activeModalDocId = null;

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    setupTheme();
    setupNavigation();
    setupForms();
    setupFilters();
    setupModal();
    loadDocuments();
});

// Theme Management
function setupTheme() {
    // Check localStorage or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        showToast(`Theme switched to ${newTheme} mode`, 'success');
    });
}

// Navigation Tabs Management
function setupNavigation() {
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            // Toggle nav button active state
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Toggle view pane visibility
            Object.keys(pages).forEach(key => {
                if (key === targetTab) {
                    pages[key].classList.add('active');
                } else {
                    pages[key].classList.remove('active');
                }
            });
            
            // Update Header Title
            const titleMap = {
                'dashboard': 'Dashboard',
                'create-invoice': 'Create Manual Invoice',
                'create-cn': 'Create Manual Credit Note (CN)',
                'create-dn': 'Create Manual Debit Note (DN)'
            };
            pageTitle.textContent = titleMap[targetTab];
            
            // Custom Actions on Tab Switch
            if (targetTab === 'dashboard') {
                loadDocuments();
            }
        });
    });
}

// Form Handlers & Calculators
function setupForms() {
    // 1. Math triggers for Manual Invoice
    const invValueSpInput = document.getElementById('inv-value-sp');
    const invSalesWoTaxInput = document.getElementById('inv-sales-wo-tax');
    const invTaxInput = document.getElementById('inv-tax');
    const invSalesWithTaxInput = document.getElementById('inv-sales-with-tax');
    const invGmvInput = document.getElementById('inv-gmv');
    const btnCalcTaxInv = document.getElementById('btn-calc-tax-inv');

    // Trigger defaults on input change
    invValueSpInput.addEventListener('input', () => {
        if (!invGmvInput.value) {
            invGmvInput.value = invValueSpInput.value;
        }
    });

    btnCalcTaxInv.addEventListener('click', () => {
        const salesWoTax = parseFloat(invSalesWoTaxInput.value);
        if (!isNaN(salesWoTax)) {
            const tax = Math.round(salesWoTax * 0.18 * 100) / 100;
            const salesWithTax = Math.round((salesWoTax + tax) * 100) / 100;
            invTaxInput.value = tax.toFixed(2);
            invSalesWithTaxInput.value = salesWithTax.toFixed(2);
            showToast('Calculated 18% GST and Sales With Tax', 'info');
        } else {
            showToast('Please enter a valid "Sales Without Tax" amount first.', 'error');
        }
    });

    // 2. Math triggers for Manual DN
    const dnValueSpInput = document.getElementById('dn-value-sp');
    const dnSalesWoTaxInput = document.getElementById('dn-sales-wo-tax');
    const dnTaxInput = document.getElementById('dn-tax');
    const dnSalesWithTaxInput = document.getElementById('dn-sales-with-tax');
    const dnGmvInput = document.getElementById('dn-gmv');
    const btnCalcTaxDn = document.getElementById('btn-calc-tax-dn');

    dnValueSpInput.addEventListener('input', () => {
        if (!dnGmvInput.value) {
            dnGmvInput.value = dnValueSpInput.value;
        }
    });

    btnCalcTaxDn.addEventListener('click', () => {
        const salesWoTax = parseFloat(dnSalesWoTaxInput.value);
        if (!isNaN(salesWoTax)) {
            const tax = Math.round(salesWoTax * 0.18 * 100) / 100;
            const salesWithTax = Math.round((salesWoTax + tax) * 100) / 100;
            dnTaxInput.value = tax.toFixed(2);
            dnSalesWithTaxInput.value = salesWithTax.toFixed(2);
            showToast('Calculated 18% GST and Sales With Tax for DN', 'info');
        } else {
            showToast('Please enter a valid "Sales Without Tax" amount first.', 'error');
        }
    });

    // 3. Form Submit Handlers
    document.getElementById('form-invoice').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const payload = {
            doc_type: 'invoice',
            sale_type: document.getElementById('inv-sale-type').value,
            invoice_number: document.getElementById('inv-invoice-number').value,
            invoice_date: document.getElementById('inv-invoice-date').value,
            id_company: document.getElementById('inv-id-company').value,
            plant_id: document.getElementById('inv-plant-id').value,
            plant_name: document.getElementById('inv-plant-name').value,
            value_sp: parseFloat(invValueSpInput.value),
            sales_wo_tax: parseFloat(invSalesWoTaxInput.value),
            qty: parseOptionalFloat(document.getElementById('inv-qty').value),
            sales_with_tax: parseOptionalFloat(invSalesWithTaxInput.value),
            tax: parseOptionalFloat(invTaxInput.value),
            gmv: parseOptionalFloat(invGmvInput.value),
            cogs: parseOptionalFloat(document.getElementById('inv-cogs').value),
            eff_cogs: parseOptionalFloat(document.getElementById('inv-eff-cogs').value),
            msn: document.getElementById('inv-msn').value || null,
            supplier_id: document.getElementById('inv-supplier-id').value || null,
            supplier_name: document.getElementById('inv-supplier-name').value || null
        };

        if (isGitHubPages) {
            saveDocumentLocal(payload);
            showToast('Manual Invoice created (Local Storage mode)!', 'success');
            document.getElementById('form-invoice').reset();
            document.getElementById('btn-tab-dashboard').click();
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/api/documents/invoice`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error(await res.text());
            
            showToast('Manual Invoice created successfully!', 'success');
            document.getElementById('form-invoice').reset();
            document.getElementById('btn-tab-dashboard').click();
        } catch (err) {
            console.error(err);
            showToast(`Submission failed: ${err.message}`, 'error');
        }
    });

    document.getElementById('form-cn').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const payload = {
            doc_type: 'credit_note',
            sale_type: document.getElementById('cn-sale-type').value,
            invoice_number: document.getElementById('cn-invoice-number').value,
            note_no: document.getElementById('cn-note-no').value,
            return_date: document.getElementById('cn-return-date').value,
            id_company: document.getElementById('cn-id-company').value,
            plant_id: document.getElementById('cn-plant-id').value,
            plant_name: document.getElementById('cn-plant-name').value,
            return_remark: document.getElementById('cn-return-remark').value,
            return_sales: parseOptionalFloat(document.getElementById('cn-return-sales').value),
            return_cogs: parseOptionalFloat(document.getElementById('cn-return-cogs').value),
            return_tax: parseOptionalFloat(document.getElementById('cn-return-tax').value),
            msn: document.getElementById('cn-msn').value || null,
            supplier_id: document.getElementById('cn-supplier-id').value || null,
            supplier_name: document.getElementById('cn-supplier-name').value || null
        };

        if (isGitHubPages) {
            saveDocumentLocal(payload);
            showToast('Credit Note created (Local Storage mode)!', 'success');
            document.getElementById('form-cn').reset();
            document.getElementById('btn-tab-dashboard').click();
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/api/documents/credit-note`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error(await res.text());
            
            showToast('Credit Note created successfully!', 'success');
            document.getElementById('form-cn').reset();
            document.getElementById('btn-tab-dashboard').click();
        } catch (err) {
            console.error(err);
            showToast(`Submission failed: ${err.message}`, 'error');
        }
    });

    document.getElementById('form-dn').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const payload = {
            doc_type: 'debit_note',
            sale_type: document.getElementById('dn-sale-type').value,
            invoice_number: document.getElementById('dn-invoice-number').value,
            invoice_date: document.getElementById('dn-invoice-date').value,
            id_company: document.getElementById('dn-id-company').value,
            plant_id: document.getElementById('dn-plant-id').value,
            plant_name: document.getElementById('dn-plant-name').value,
            value_sp: parseFloat(dnValueSpInput.value),
            sales_wo_tax: parseFloat(dnSalesWoTaxInput.value),
            qty: parseOptionalFloat(document.getElementById('dn-qty').value),
            sales_with_tax: parseOptionalFloat(dnSalesWithTaxInput.value),
            tax: parseOptionalFloat(dnTaxInput.value),
            gmv: parseOptionalFloat(dnGmvInput.value),
            cogs: parseOptionalFloat(document.getElementById('dn-cogs').value),
            eff_cogs: parseOptionalFloat(document.getElementById('dn-eff-cogs').value),
            msn: document.getElementById('dn-msn').value || null,
            supplier_id: document.getElementById('dn-supplier-id').value || null,
            supplier_name: document.getElementById('dn-supplier-name').value || null
        };

        if (isGitHubPages) {
            saveDocumentLocal(payload);
            showToast('Debit Note created (Local Storage mode)!', 'success');
            document.getElementById('form-dn').reset();
            document.getElementById('btn-tab-dashboard').click();
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/api/documents/debit-note`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error(await res.text());
            
            showToast('Debit Note created successfully!', 'success');
            document.getElementById('form-dn').reset();
            document.getElementById('btn-tab-dashboard').click();
        } catch (err) {
            console.error(err);
            showToast(`Submission failed: ${err.message}`, 'error');
        }
    });
}

function parseOptionalFloat(val) {
    if (val === "" || val === undefined || val === null) return null;
    const num = parseFloat(val);
    return isNaN(num) ? null : num;
}

// Local Storage Helpers for GitHub Pages Mode
function loadDocumentsLocal() {
    let stored = localStorage.getItem('moglix_documents');
    if (!stored) {
        // Pre-seed sample records to match SQLite DB experience
        documents = [
            {
                id: 1,
                doc_type: "invoice",
                sale_type: "Manual",
                invoice_number: "INV-2026-001",
                invoice_date: "2026-06-20",
                id_company: "MOGLIX-IND",
                plant_id: "PL001",
                plant_name: "Delhi Warehouse",
                value_sp: 150000.0,
                qty: 150.0,
                sales_wo_tax: 127118.64,
                sales_with_tax: 150000.0,
                tax: 22881.36,
                gmv: 150000.0,
                cogs: 100000.0,
                eff_cogs: 98000.0,
                msn: "MSN-99881",
                supplier_id: "SUP-552",
                supplier_name: "Acme Industrial Corp",
                created_at: new Date().toISOString()
            },
            {
                id: 2,
                doc_type: "credit_note",
                sale_type: "Manual",
                invoice_number: "INV-2026-001",
                note_no: "CN-2026-001",
                return_date: "2026-06-21",
                id_company: "MOGLIX-IND",
                plant_id: "PL001",
                plant_name: "Delhi Warehouse",
                return_remark: "Defective items returned",
                return_sales: 20000.0,
                return_cogs: 15000.0,
                return_tax: 3600.0,
                msn: "MSN-99881",
                supplier_id: "SUP-552",
                supplier_name: "Acme Industrial Corp",
                created_at: new Date().toISOString()
            },
            {
                id: 3,
                doc_type: "debit_note",
                sale_type: "Manual DN Price",
                invoice_number: "INV-2026-001",
                invoice_date: "2026-06-22",
                id_company: "MOGLIX-IND",
                plant_id: "PL001",
                plant_name: "Delhi Warehouse",
                value_sp: 12000.0,
                qty: 10.0,
                sales_wo_tax: 10169.49,
                sales_with_tax: 12000.0,
                tax: 1830.51,
                gmv: 12000.0,
                cogs: 8000.0,
                eff_cogs: 7800.0,
                msn: "MSN-99881",
                supplier_id: "SUP-552",
                supplier_name: "Acme Industrial Corp",
                created_at: new Date().toISOString()
            }
        ];
        localStorage.setItem('moglix_documents', JSON.stringify(documents));
    } else {
        documents = JSON.parse(stored);
    }
    renderDocuments();
    updateDashboardStats();
}

function saveDocumentLocal(doc) {
    doc.id = documents.length > 0 ? Math.max(...documents.map(d => d.id)) + 1 : 1;
    doc.created_at = new Date().toISOString();
    documents.push(doc);
    localStorage.setItem('moglix_documents', JSON.stringify(documents));
    loadDocumentsLocal();
}

// Loading & Rendering Documents
async function loadDocuments() {
    if (isGitHubPages) {
        loadDocumentsLocal();
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/api/documents`);
        if (!res.ok) throw new Error('Failed to load documents');
        
        documents = await res.json();
        renderDocuments();
        updateDashboardStats();
    } catch (err) {
        console.error(err);
        showToast('Connection to backend failed. Switching to Local Storage mode.', 'info');
        loadDocumentsLocal();
    }
}

function renderDocuments() {
    const selectedFilter = filterDocType.value;
    
    // Clear list
    documentsTbody.innerHTML = '';
    
    const filteredDocs = selectedFilter 
        ? documents.filter(doc => doc.doc_type === selectedFilter)
        : documents;
        
    if (filteredDocs.length === 0) {
        documentsTbody.innerHTML = `<tr><td colspan="7" style="text-align: center;" class="text-muted">No documents found.</td></tr>`;
        return;
    }
    
    filteredDocs.forEach(doc => {
        const tr = document.createElement('tr');
        
        // Doc Type Badge
        const badgeMap = {
            invoice: 'badge-invoice',
            credit_note: 'badge-credit_note',
            debit_note: 'badge-debit_note'
        };
        const labelMap = {
            invoice: 'Invoice',
            credit_note: 'Credit Note',
            debit_note: 'Debit Note'
        };
        const badgeClass = badgeMap[doc.doc_type] || '';
        const badgeLabel = labelMap[doc.doc_type] || doc.doc_type;
        
        // Date details
        const dateVal = doc.doc_type === 'credit_note' ? doc.return_date : doc.invoice_date;
        const noVal = doc.doc_type === 'credit_note' ? doc.note_no : doc.invoice_number;
        const valueVal = doc.doc_type === 'credit_note' ? doc.return_sales : doc.value_sp;
        const displayValue = valueVal !== null ? `₹${valueVal.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : '—';
        
        tr.innerHTML = `
            <td><span class="badge ${badgeClass}">${badgeLabel}</span></td>
            <td>${doc.invoice_number}</td>
            <td>${dateVal || '—'}</td>
            <td><strong>${noVal || '—'}</strong></td>
            <td>
                <div>${doc.id_company}</div>
                <div class="text-muted">${doc.plant_name} (${doc.plant_id})</div>
            </td>
            <td class="amount-text">${displayValue}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn-action-view" onclick="openDetailsModal(${doc.id})" title="View Details">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    </button>
                    <button class="btn-action-pdf" onclick="downloadPdf(${doc.id})" title="Download PDF">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                    </button>
                </div>
            </td>
        `;
        documentsTbody.appendChild(tr);
    });
}

function updateDashboardStats() {
    const invCount = documents.filter(doc => doc.doc_type === 'invoice').length;
    const cnCount = documents.filter(doc => doc.doc_type === 'credit_note').length;
    const dnCount = documents.filter(doc => doc.doc_type === 'debit_note').length;
    
    statInvoiceCount.textContent = invCount;
    statCnCount.textContent = cnCount;
    statDnCount.textContent = dnCount;
}

function setupFilters() {
    filterDocType.addEventListener('change', renderDocuments);
}

// Modal View details popup
function setupModal() {
    btnCloseModal.addEventListener('click', closeModal);
    btnModalClose.addEventListener('click', closeModal);
    
    // Close on overlay click
    window.addEventListener('click', (e) => {
        if (e.target === detailsModal) closeModal();
    });
    
    btnModalDownload.addEventListener('click', () => {
        if (activeModalDocId) downloadPdf(activeModalDocId);
    });
}

window.openDetailsModal = function(id) {
    const doc = documents.find(d => d.id === id);
    if (!doc) return;
    
    activeModalDocId = id;
    
    const labelMap = {
        invoice: 'Manual Invoice',
        credit_note: 'Credit Note (CN)',
        debit_note: 'Debit Note (DN)'
    };
    
    modalDocTitle.textContent = `${labelMap[doc.doc_type]} Details`;
    
    let htmlContent = '';
    
    if (doc.doc_type === 'credit_note') {
        htmlContent = `
            <div class="details-grid">
                <div class="detail-item">
                    <span class="detail-label">Sale Type</span>
                    <span class="detail-val">${doc.sale_type}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Original Invoice No</span>
                    <span class="detail-val">${doc.invoice_number}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">CN Note Number</span>
                    <span class="detail-val">${doc.note_no || '—'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Return Date</span>
                    <span class="detail-val">${doc.return_date || '—'}</span>
                </div>
                
                <div class="details-divider"></div>
                
                <div class="detail-item">
                    <span class="detail-label">Company ID</span>
                    <span class="detail-val">${doc.id_company}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Plant ID / Name</span>
                    <span class="detail-val">${doc.plant_name} (${doc.plant_id})</span>
                </div>
                <div class="detail-item" style="grid-column: span 2;">
                    <span class="detail-label">Return Remark</span>
                    <span class="detail-val">${doc.return_remark || '—'}</span>
                </div>
                
                <div class="details-divider"></div>
                
                <div class="detail-item">
                    <span class="detail-label">Return Sales</span>
                    <span class="detail-val amount-text">${formatINR(doc.return_sales)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Return Tax</span>
                    <span class="detail-val amount-text">${formatINR(doc.return_tax)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Return COGS</span>
                    <span class="detail-val amount-text">${formatINR(doc.return_cogs)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">MSN Code</span>
                    <span class="detail-val">${doc.msn || '—'}</span>
                </div>
                
                <div class="details-divider"></div>
                
                <div class="detail-item">
                    <span class="detail-label">Supplier ID</span>
                    <span class="detail-val">${doc.supplier_id || '—'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Supplier Name</span>
                    <span class="detail-val">${doc.supplier_name || '—'}</span>
                </div>
            </div>
        `;
    } else {
        // Invoice or DN
        htmlContent = `
            <div class="details-grid">
                <div class="detail-item">
                    <span class="detail-label">Sale Type</span>
                    <span class="detail-val">${doc.sale_type}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Invoice Number</span>
                    <span class="detail-val">${doc.invoice_number}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Invoice Date</span>
                    <span class="detail-val">${doc.invoice_date || '—'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Company ID</span>
                    <span class="detail-val">${doc.id_company}</span>
                </div>
                
                <div class="details-divider"></div>
                
                <div class="detail-item">
                    <span class="detail-label">Plant ID / Name</span>
                    <span class="detail-val">${doc.plant_name} (${doc.plant_id})</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">MSN Code</span>
                    <span class="detail-val">${doc.msn || '—'}</span>
                </div>
                
                <div class="details-divider"></div>
                
                <div class="detail-item">
                    <span class="detail-label">Value SP</span>
                    <span class="detail-val amount-text">${formatINR(doc.value_sp)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Sales Without Tax</span>
                    <span class="detail-val amount-text">${formatINR(doc.sales_wo_tax)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Quantity</span>
                    <span class="detail-val">${doc.qty || '—'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Tax Amount</span>
                    <span class="detail-val amount-text">${formatINR(doc.tax)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Sales With Tax</span>
                    <span class="detail-val amount-text">${formatINR(doc.sales_with_tax)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">GMV</span>
                    <span class="detail-val amount-text">${formatINR(doc.gmv)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">COGS</span>
                    <span class="detail-val amount-text">${formatINR(doc.cogs)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Effective COGS</span>
                    <span class="detail-val amount-text">${formatINR(doc.eff_cogs)}</span>
                </div>
                
                <div class="details-divider"></div>
                
                <div class="detail-item">
                    <span class="detail-label">Supplier ID</span>
                    <span class="detail-val">${doc.supplier_id || '—'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Supplier Name</span>
                    <span class="detail-val">${doc.supplier_name || '—'}</span>
                </div>
            </div>
        `;
    }
    
    modalDetailsBody.innerHTML = htmlContent;
    detailsModal.classList.add('active');
};

function closeModal() {
    detailsModal.classList.remove('active');
    activeModalDocId = null;
}

window.downloadPdf = function(id) {
    const doc = documents.find(d => d.id === id);
    if (!doc) return;

    if (isGitHubPages) {
        printDocumentClientSide(doc);
        return;
    }

    window.open(`${API_BASE}/api/documents/${id}/pdf`, '_blank');
    showToast('Downloading PDF invoice...', 'info');
};

function printDocumentClientSide(doc) {
    const printWindow = window.open('', '_blank');
    const docTypeStr = doc.doc_type.toUpperCase().replace('_', ' ');
    
    let leftMeta = `
        <p><strong>Company ID:</strong> ${doc.id_company}</p>
        <p><strong>Plant ID:</strong> ${doc.plant_id}</p>
        <p><strong>Plant Name:</strong> ${doc.plant_name}</p>
    `;
    let rightMeta = '';
    let measuresRows = '';
    let primaryColor = '#de1c24'; // Invoice red
    
    if (doc.doc_type === 'credit_note') {
        primaryColor = '#0d9488'; // Teal
        rightMeta = `
            <p><strong>CN Note No:</strong> ${doc.note_no || 'N/A'}</p>
            <p><strong>Return Date:</strong> ${doc.return_date || 'N/A'}</p>
            <p><strong>Ref Invoice No:</strong> ${doc.invoice_number}</p>
        `;
        
        measuresRows = `
            <tr><td>Return Sales</td><td>₹${doc.return_sales?.toLocaleString('en-IN', {minimumFractionDigits:2}) || '0.00'}</td></tr>
            <tr><td>Return Tax</td><td>₹${doc.return_tax?.toLocaleString('en-IN', {minimumFractionDigits:2}) || '0.00'}</td></tr>
            <tr><td>Return COGS</td><td>₹${doc.return_cogs?.toLocaleString('en-IN', {minimumFractionDigits:2}) || '0.00'}</td></tr>
        `;
    } else {
        if (doc.doc_type === 'debit_note') {
            primaryColor = '#d97706'; // Amber
        }
        rightMeta = `
            <p><strong>Invoice No:</strong> ${doc.invoice_number}</p>
            <p><strong>Invoice Date:</strong> ${doc.invoice_date || 'N/A'}</p>
            <p><strong>Sale Type:</strong> ${doc.sale_type}</p>
        `;
        
        measuresRows = `
            <tr><td>Value SP (Selling Price)</td><td>₹${doc.value_sp?.toLocaleString('en-IN', {minimumFractionDigits:2}) || '0.00'}</td></tr>
            <tr><td>Quantity</td><td>${doc.qty || '0'}</td></tr>
            <tr><td>Sales Without Tax</td><td>₹${doc.sales_wo_tax?.toLocaleString('en-IN', {minimumFractionDigits:2}) || '0.00'}</td></tr>
            <tr><td>Tax Amount</td><td>₹${doc.tax?.toLocaleString('en-IN', {minimumFractionDigits:2}) || '0.00'}</td></tr>
            <tr><td>Sales With Tax</td><td>₹${doc.sales_with_tax?.toLocaleString('en-IN', {minimumFractionDigits:2}) || '0.00'}</td></tr>
            <tr><td>GMV</td><td>₹${doc.gmv?.toLocaleString('en-IN', {minimumFractionDigits:2}) || '0.00'}</td></tr>
            <tr><td>COGS</td><td>₹${doc.cogs?.toLocaleString('en-IN', {minimumFractionDigits:2}) || '0.00'}</td></tr>
            <tr><td>Effective COGS</td><td>₹${doc.eff_cogs?.toLocaleString('en-IN', {minimumFractionDigits:2}) || '0.00'}</td></tr>
        `;
    }

    if (doc.supplier_id || doc.supplier_name) {
        leftMeta += `
            <p><strong>Supplier ID:</strong> ${doc.supplier_id || 'N/A'}</p>
            <p><strong>Supplier Name:</strong> ${doc.supplier_name || 'N/A'}</p>
        `;
    }
    if (doc.msn) {
        rightMeta += `<p><strong>MSN Code:</strong> ${doc.msn}</p>`;
    }
    
    let remarkSection = '';
    if (doc.doc_type === 'credit_note' && doc.return_remark) {
        remarkSection = `<div class="remark"><strong>Return Remark:</strong> ${doc.return_remark}</div>`;
    }

    printWindow.document.write(`
        <html>
        <head>
            <title>${docTypeStr} - ${doc.invoice_number || doc.note_no}</title>
            <style>
                body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; margin: 40px; }
                .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid ${primaryColor}; padding-bottom: 10px; margin-bottom: 30px; }
                .title { font-size: 24px; font-weight: bold; color: ${primaryColor}; }
                .brand { text-align: right; }
                .brand-name { font-size: 18px; font-weight: bold; color: ${primaryColor}; }
                .brand-sub { font-size: 10px; color: #666; }
                .meta-container { display: flex; justify-content: space-between; margin-bottom: 30px; }
                .meta-col { width: 45%; font-size: 12px; line-height: 1.6; }
                .meta-col p { margin: 4px 0; }
                .remark { background-color: #f8fafc; border-left: 3px solid ${primaryColor}; padding: 12px; margin-bottom: 30px; font-size: 12px; }
                .table-title { font-size: 14px; font-weight: bold; margin-bottom: 10px; color: #475569; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 50px; font-size: 12px; }
                th, td { padding: 10px; text-align: left; border: 1px solid #cbd5e1; }
                th { background-color: ${primaryColor}; color: white; font-weight: bold; }
                tr:nth-child(even) { background-color: #f8fafc; }
                .footer { display: flex; justify-content: space-between; align-items: flex-end; font-size: 10px; color: #666; margin-top: 50px; }
                .terms { width: 60%; }
                .sig { text-align: right; width: 30%; }
                @media print {
                    body { margin: 20px; }
                    button { display: none; }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">${docTypeStr}</div>
                <div class="brand">
                    <div class="brand-name">MOGLIX</div>
                    <div class="brand-sub">Mogli Labs (India) Pvt. Ltd.</div>
                </div>
            </div>
            <div class="meta-container">
                <div class="meta-col">${leftMeta}</div>
                <div class="meta-col">${rightMeta}</div>
            </div>
            ${remarkSection}
            <div class="table-title">Financial Summary</div>
            <table>
                <thead>
                    <tr><th>Measure Field</th><th>Value (INR)</th></tr>
                </thead>
                <tbody>
                    ${measuresRows}
                </tbody>
            </table>
            <div class="footer">
                <div class="terms">
                    <strong>Terms & Conditions:</strong>
                    <p>1. This is a computer generated document.</p>
                    <p>2. Discrepancies if any should be reported immediately.</p>
                    <p>3. Subject to jurisdiction of local courts.</p>
                </div>
                <div class="sig">
                    <br/><br/>
                    <p>___________________________</p>
                    <strong>Authorized Signatory</strong>
                </div>
            </div>
            <script>
                window.onload = function() {
                    window.print();
                }
            </script>
        </body>
        </html>
    `);
    printWindow.document.close();
    showToast('Triggered client-side print layout...', 'info');
}

function formatINR(val) {
    if (val === null || val === undefined) return '—';
    return `₹${val.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
}

// Toast Notifications System
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    // Auto-remove after animation finishes (5 seconds total)
    setTimeout(() => {
        toast.remove();
    }, 5000);
}
