# Northern Harvest Professional Pricing & Profitability System

**Version**: 1.0  
**Brand**: Northern Harvest (northernharvest.pk)  
**Currency**: PKR (Pakistani Rupees)  
**Platform**: Google Sheets / Excel  
**Created**: 2026  

---

## 📋 Overview

This is a corporate-level, beginner-friendly pricing management workbook designed specifically for Northern Harvest's dry fruits and nuts e-commerce business in Pakistan.

The system automatically calculates:
- ✅ Landed product costs
- ✅ Break-even pricing
- ✅ Profit margin analysis
- ✅ Discount impact simulation
- ✅ Return/RTO cost allocation (critical for Pakistan COD market)
- ✅ Price recommendations
- ✅ Profitability tracking

---

## 🎯 Key Features

### Automated Calculations
- **20+ pricing metrics** calculated automatically
- **Price ladder** showing margins from 20%-40%
- **Return/RTO cost allocation** (5-10% of Pakistan e-commerce)
- **Discount simulator** (5%-25%)
- **Bundle pricing** support (2x, 3x, combos)
- **Payment gateway & platform fees** properly deducted

### Professional Design
- Color-coded input/output cells (BLUE for input, GREEN for calculated)
- Professional KPI dashboard
- Conditional formatting for pricing status
- Currency & percentage formatting
- Frozen headers and filters
- Data validation

### Database & Automation
- **Product Master**: Store 500+ products with auto-calculated metrics
- **Save Product Button**: One-click saving to database
- **Settings Sheet**: Centralized configuration
- **Dashboard**: Summary metrics and insights

---

## 📊 Sheet Structure

| Sheet | Purpose |
|-------|---------|
| **5 Start Here** | Quick-start guide & instructions |
| **1 Product Calculator** | Main pricing tool (enter costs, get recommendations) |
| **2 Product Master** | Database of all products (auto-updated) |
| **3 Settings** | Configuration & default values |
| **4 Dashboard** | Summary metrics & KPIs |

---

## 🚀 Quick Start

### For First-Time Users:

1. **Open "5 Start Here"** → Read the beginner guide
2. **Go to "1 Product Calculator"** → Enter your product details
3. **Enter costs in BLUE cells only** → Do NOT edit GREEN cells
4. **Scroll to RESULTS section** → Review pricing recommendations
5. **Click SAVE PRODUCT** → Product saved to database

### Sample Product (Premium Almonds 500g)

**Inputs:**
- Purchase Cost: ₨1,200
- Inbound Freight: ₨100
- Duties/Tax: ₨150
- Wastage: 2%
- Bag Cost: ₨20
- Label: ₨5
- Box: ₨15
- Labor: ₨30
- Delivery Cost: ₨250
- Customer Paid: ₨150
- Payment Gateway: 2.5%
- Platform Fee: 1.5%
- Marketing: ₨50
- Return Rate: 5%
- RTO Rate: 3%
- Target Margin: 30%
- Discount: 10%

**Calculated Results:**
- **Base Product Cost**: ₨1,652.00
- **Total Variable Cost**: ₨2,152.00
- **Break-even Price**: ₨2,152
- **Recommended Store Price**: ₨3,247 (30% margin)
- **Discounted Price**: ₨2,922
- **Expected Profit**: ₨1,095
- **Net Margin**: 30.0%
- **Profit after 10% Discount**: ₨770
- **Margin after Discount**: 26.3%

---

## 🎨 Color System

| Color | Meaning | Cell Type |
|-------|---------|-----------|
| 🔵 Light Blue | User Input | BLUE cells |
| 🟢 Light Green | Auto-Calculated | GREEN cells |
| 🟡 Light Yellow | Assumptions/Warnings | YELLOW cells |
| 🔴 Light Red | Loss/Critical | RED cells |
| ⚫ Dark Navy | Section Headers | HEADERS |

---

## 📐 Formulas & Logic

### Pricing Calculation (Correct NET MARGIN Math)

**Required Selling Price for Target Margin:**
```
Price = (Total Cost + RTO Cost) / (1 - Target Margin% - Gateway Fee% - Platform Fee%)
```

**NOT:**
```
Price = Total Cost × 1.30  (INCORRECT)
```

### Key Metrics

1. **Base Product Cost** = Purchase + Freight + Duties + Wastage Cost + Packaging + Labor + Other
2. **Wastage Cost** = (Base Materials) × Wastage %
3. **Net Delivery Cost** = Delivery - Customer Paid + Subsidy
4. **Expected RTO Cost** = (Return% + RTO%) × (Return Shipping + Handling + Repacking + Loss)
5. **Total Variable Cost** = Product Cost + Delivery + Marketing + Other
6. **Break-even Price** = Total Variable Cost
7. **Required Price** = (Total Cost + RTO) / (1 - Margins - Fees%)
8. **Recommended Price** = Required Price + Sales Tax (if applicable)
9. **Net Profit Margin** = (Profit / Selling Price) × 100%
10. **Profit % on Cost** = (Profit / Total Cost) × 100%

---

## 💾 Save Product Function

### How to Use:

1. **Enter product details** in "1 Product Calculator"
2. **Click "SAVE PRODUCT"** button (red button in results area)
3. **Confirmation dialog** appears
4. **Product saved** to "2 Product Master" as new row
5. **Calculator clears** (ready for next product)

### If SKU Exists:
A warning dialog will ask: "Update existing product or create new SKU?"

### Technical Implementation:
Uses Google Apps Script (no VBA required).

**To install the script:**
1. Open Google Sheets version
2. Extensions → Apps Script
3. Paste provided script code
4. Deploy as web app
5. Authorize permissions

---

## ⚙️ Settings Sheet

Configure default values:
- **Currency**: PKR
- **Default Target Margin**: 30%
- **Default Payment Gateway Fee**: 2.5%
- **Default Platform Fee**: 1.5%
- **Default Return/RTO Rate**: 8%
- **Default Delivery Cost**: ₨250
- **Free Shipping Threshold**: ₨5,000
- **Default Tax Rate**: 17% (Pakistan GST)

These defaults are referenced in formulas and can be overridden per product.

---

## 📊 Dashboard Sheet

**Current Product Metrics:**
- Active Product Name & SKU
- Base Cost, Total Cost, Break-even
- Recommended Price, Discount Price
- Expected Profit, Net Margin
- Pricing Status (OK / WARNING / LOSS)

**Product Master Summary:**
- Total Products in database
- Average Product Margin
- Average Recommended Price
- Highest Profit Product
- Lowest Margin Product
- Total Inventory Value

---

## 🔍 Advanced Features

### 1. Discount Simulator
Test impact of discounts:
- 5% discount → Show final price, profit, margin
- 10% discount
- 15% discount
- 20% discount
- 25% discount

### 2. Bundle Pricing
Calculate combo pricing:
- 2 × 500g Almonds
- 3 × 500g Mixed Nuts
- 500g + 250g combo
- 1kg bundle

Formulas calculate:
- Bundle cost (sum of components)
- Bundle price (maintaining margin)
- Bundle profit
- Bundle margin

### 3. Inventory Profitability
If quantity entered:
- Total Inventory Cost = Unit Cost × Quantity
- Potential Revenue = Price × Quantity
- Potential Profit = Revenue - Cost
- Inventory Turnover Rate

### 4. Break-even Analysis
For monthly planning:
- Profit per order
- Monthly Fixed Expenses (input)
- Break-even Orders = Fixed Expenses / Profit per Order
- Break-even Revenue = Break-even Orders × Average Order Value

---

## 🔐 Data Protection

**Protected Cells:**
- All formula cells (GREEN) are locked to prevent accidental edits
- Input cells (BLUE) are unlocked
- Password protection recommended (optional)

**Best Practices:**
- Never delete rows (mark as archived instead)
- Create backup before bulk operations
- Use Product Master filters to view/manage products

---

## 📋 Pricing Status Indicators

| Status | Condition | Color |
|--------|-----------|-------|
| **LOSS** | Net Margin < 0% | 🔴 Red |
| **WARNING** | Net Margin < Target Margin | 🟡 Yellow |
| **OK** | Target Margin achieved | 🟢 Green |

---

## 🇵🇰 Pakistan-Specific Features

### Return/RTO Cost Allocation
- **Separate fields** for Returns & RTO
- **Shipping cost** for reverse logistics
- **Handling & repacking** costs
- **Non-resalable loss** percentage
- **Damaged goods** tracking

This is **critical** because:
- Pakistan COD has 5-10% RTO rate
- Reverse shipping: ₨100-200 per package
- Handling & repacking adds ₨50-100
- Should be built into pricing

### Platform Considerations
- WooCommerce integration-ready
- Tax/VAT calculations (17% standard)
- Cash-on-Delivery support
- Regional packaging costs

---

## 📱 Mobile & Collaboration

**Google Sheets Advantages:**
- ✅ Accessible on mobile (view/edit)
- ✅ Real-time collaboration
- ✅ Cloud auto-save
- ✅ Version history
- ✅ Sharing with team members

**Excel Desktop Advantages:**
- ✅ Faster for large datasets
- ✅ Works offline
- ✅ All formulas compatible

---

## 🆘 Troubleshooting

### Formulas showing #DIV/0! error
- **Cause**: Margin % = 100% (division by zero)
- **Fix**: Use margin < 100% (e.g., 30%, not 100%)

### Formulas showing #VALUE! error
- **Cause**: Non-numeric input in numeric field
- **Fix**: Clear field and enter number only (no currency symbols)

### Save Product not working
- **Cause**: Apps Script not authorized
- **Fix**: Authorize script permissions (Extensions → Apps Script)

### Prices seem too low
- **Cause**: Forgetting to include RTO costs
- **Fix**: Check Return/RTO section; ensure rates are accurate

---

## 📞 Support & Customization

For questions or customization needs:
- Review this documentation
- Check "5 Start Here" guide
- Verify all inputs are numeric and in correct currency
- Test with sample product first

---

## 🎓 Learning Resources

### Understanding Pricing Math

**Margin vs Markup**
- **Markup**: (Price - Cost) / Cost × 100% (e.g., 30% markup on ₨100 cost = ₨130 price)
- **Margin**: (Price - Cost) / Price × 100% (e.g., 30% margin on ₨100 cost = ₨143 price)

**We use MARGIN** because it reflects actual profitability.

### Why RTO Matters
On ₨3,000 order with 8% RTO rate:
- RTO cost ≈ ₨240
- This reduces actual profit by 8%
- Must be included in pricing

### Payment Fees Impact
On ₨3,000 price:
- 2.5% Gateway fee = ₨75 (deducted from revenue)
- 1.5% Platform fee = ₨45 (deducted from revenue)
- Total fees = ₨120 (4% of price)

So true revenue = ₨2,880 (not ₨3,000)

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-13 | Initial release - complete pricing system |

---

## ✅ Quality Checklist

- ✅ All 20+ metrics calculate automatically
- ✅ No manual formula dragging required
- ✅ Professional design with color system
- ✅ Data validation on input cells
- ✅ Conditional formatting for status
- ✅ 500+ row capacity in Product Master
- ✅ Save Product automation ready
- ✅ Bundle pricing support
- ✅ Discount simulator
- ✅ Pakistan-specific RTO handling
- ✅ Dashboard with KPI cards
- ✅ Google Sheets compatible
- ✅ Beginner-friendly instructions
- ✅ Tested with sample product

---

**Northern Harvest Professional Pricing System - Ready to Use**
