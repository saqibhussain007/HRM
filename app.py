"""
Northern Harvest Professional Pricing System
Complete Production-Ready Application
Author: Copilot
Date: 2026-08-14
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import hashlib
import json
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import os

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Northern Harvest - Pricing System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Northern Harvest Professional Pricing & Profitability System v1.0"
    }
)

# ============================================================================
# CSS STYLING
# ============================================================================
st.markdown("""
    <style>
    :root {
        --primary-color: #1F3A5F;
        --secondary-color: #2E5090;
        --success-color: #27AE60;
        --warning-color: #F39C12;
        --danger-color: #E74C3C;
        --light-color: #ECF0F1;
        --dark-color: #2C3E50;
    }
    
    * {
        margin: 0;
        padding: 0;
    }
    
    .main-header {
        color: var(--primary-color);
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        color: var(--secondary-color);
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 0.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 0.5rem;
    }
    
    .status-ok {
        color: #27AE60;
        font-weight: bold;
    }
    
    .status-warning {
        color: #F39C12;
        font-weight: bold;
    }
    
    .status-loss {
        color: #E74C3C;
        font-weight: bold;
    }
    
    .input-section {
        background-color: #D9E1F2;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .result-section {
        background-color: #C6EFCE;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .warning-section {
        background-color: #FFFFCC;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #F39C12;
    }
    
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE SETUP
# ============================================================================
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, 
                  email TEXT UNIQUE, 
                  password TEXT, 
                  name TEXT,
                  role TEXT,
                  created_at TIMESTAMP,
                  is_active INTEGER)''')
    
    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY,
                  sku TEXT UNIQUE,
                  product_name TEXT,
                  pack_size REAL,
                  units_per_order INTEGER,
                  purchase_cost REAL,
                  inbound_freight REAL,
                  customs_duties REAL,
                  wastage_pct REAL,
                  bag_cost REAL,
                  label_cost REAL,
                  box_cost REAL,
                  labor_cost REAL,
                  other_product_cost REAL,
                  delivery_cost REAL,
                  customer_delivery REAL,
                  gateway_fee_pct REAL,
                  gateway_fixed REAL,
                  platform_fee_pct REAL,
                  marketing_cost REAL,
                  return_rate_pct REAL,
                  rto_rate_pct REAL,
                  return_shipping REAL,
                  return_handling REAL,
                  target_margin_pct REAL,
                  discount_pct REAL,
                  created_by TEXT,
                  created_at TIMESTAMP,
                  updated_at TIMESTAMP,
                  is_active INTEGER)''')
    
    # Settings table
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (id INTEGER PRIMARY KEY,
                  setting_key TEXT UNIQUE,
                  setting_value TEXT,
                  user_email TEXT,
                  created_at TIMESTAMP,
                  updated_at TIMESTAMP)''')
    
    # Audit log table
    c.execute('''CREATE TABLE IF NOT EXISTS audit_log
                 (id INTEGER PRIMARY KEY,
                  user_email TEXT,
                  action TEXT,
                  product_sku TEXT,
                  details TEXT,
                  timestamp TIMESTAMP)''')
    
    conn.commit()
    conn.close()

# ============================================================================
# AUTHENTICATION
# ============================================================================
def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_default_users():
    """Create default admin and users"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    
    users = [
        ('saqibhussain505@gmail.com', '@Hussain007', 'Saqib Hussain', 'admin'),
        ('achill0076@gmail.com', 'password123', 'Ali', 'user'),
    ]
    
    for email, password, name, role in users:
        try:
            c.execute('''INSERT INTO users (email, password, name, role, created_at, is_active)
                         VALUES (?, ?, ?, ?, ?, 1)''',
                     (email, hash_password(password), name, role, datetime.now()))
        except sqlite3.IntegrityError:
            pass  # User already exists
    
    conn.commit()
    conn.close()

def login_user(email, password):
    """Authenticate user"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ? AND password = ? AND is_active = 1',
              (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def set_default_settings():
    """Set default settings"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    
    default_settings = [
        ('target_margin', '30'),
        ('gateway_fee', '2.5'),
        ('platform_fee', '1.5'),
        ('delivery_cost', '250'),
        ('return_rate', '5'),
        ('rto_rate', '3'),
        ('currency', 'PKR'),
        ('timezone', 'UTC+5'),
    ]
    
    for key, value in default_settings:
        try:
            c.execute('''INSERT INTO settings (setting_key, setting_value, created_at, updated_at)
                         VALUES (?, ?, ?, ?)''',
                     (key, value, datetime.now(), datetime.now()))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

# ============================================================================
# PRICING CALCULATIONS
# ============================================================================
def calculate_pricing(data):
    """Calculate all pricing metrics"""
    
    # Base Product Cost
    purchase = float(data.get('purchase_cost', 0))
    wastage_pct = float(data.get('wastage_pct', 0))
    wastage_cost = purchase * (wastage_pct / 100)
    
    base_cost = (
        purchase +
        float(data.get('inbound_freight', 0)) +
        float(data.get('customs_duties', 0)) +
        wastage_cost +
        float(data.get('bag_cost', 0)) +
        float(data.get('label_cost', 0)) +
        float(data.get('box_cost', 0)) +
        float(data.get('labor_cost', 0)) +
        float(data.get('other_product_cost', 0))
    )
    
    # Net Delivery Cost
    net_delivery = (
        float(data.get('delivery_cost', 0)) -
        float(data.get('customer_delivery', 0))
    )
    
    # Expected RTO Cost
    return_rto_rate = (
        float(data.get('return_rate_pct', 0)) +
        float(data.get('rto_rate_pct', 0))
    ) / 100
    
    expected_rto = return_rto_rate * (
        float(data.get('return_shipping', 0)) +
        float(data.get('return_handling', 0))
    )
    
    # Total Variable Cost
    total_cost = (
        base_cost +
        net_delivery +
        float(data.get('marketing_cost', 0))
    )
    
    # Break-even Price
    breakeven = total_cost
    
    # Target Margin & Fees
    target_margin = float(data.get('target_margin_pct', 30)) / 100
    gateway_fee = float(data.get('gateway_fee_pct', 2.5)) / 100
    platform_fee = float(data.get('platform_fee_pct', 1.5)) / 100
    
    # Required Price
    if (1 - target_margin - gateway_fee - platform_fee) <= 0:
        required_price = total_cost
    else:
        required_price = (total_cost + expected_rto) / (1 - target_margin - gateway_fee - platform_fee)
    
    recommended_price = round(required_price, 0)
    
    # Discount Price
    discount_pct = float(data.get('discount_pct', 10)) / 100
    discount_price = round(recommended_price * (1 - discount_pct), 0)
    
    # Profits
    gateway_cost = recommended_price * gateway_fee
    platform_cost = recommended_price * platform_fee
    
    profit = recommended_price - total_cost - expected_rto - gateway_cost - platform_cost
    
    discount_gateway_cost = discount_price * gateway_fee
    discount_platform_cost = discount_price * platform_fee
    discount_profit = discount_price - total_cost - expected_rto - discount_gateway_cost - discount_platform_cost
    
    # Margins
    margin = (profit / recommended_price * 100) if recommended_price > 0 else 0
    discount_margin = (discount_profit / discount_price * 100) if discount_price > 0 else 0
    
    # Markup
    markup = (profit / total_cost * 100) if total_cost > 0 else 0
    
    # Status
    if margin < 0:
        status = "🔴 LOSS - PRICE TOO LOW"
    elif margin < target_margin * 100:
        status = "🟡 WARNING - BELOW TARGET"
    else:
        status = "🟢 OK - TARGET ACHIEVED"
    
    return {
        'base_cost': base_cost,
        'net_delivery': net_delivery,
        'expected_rto': expected_rto,
        'total_cost': total_cost,
        'breakeven': breakeven,
        'required_price': required_price,
        'recommended_price': recommended_price,
        'discount_price': discount_price,
        'profit': profit,
        'discount_profit': discount_profit,
        'margin': margin,
        'discount_margin': discount_margin,
        'markup': markup,
        'status': status,
    }

def generate_price_ladder(data):
    """Generate pricing for different margins"""
    ladder = []
    target_margin_pct = float(data.get('target_margin_pct', 30))
    gateway_fee = float(data.get('gateway_fee_pct', 2.5)) / 100
    platform_fee = float(data.get('platform_fee_pct', 1.5)) / 100
    
    base_pricing = calculate_pricing(data)
    
    for margin in [20, 25, 30, 35, 40]:
        m = margin / 100
        if (1 - m - gateway_fee - platform_fee) <= 0:
            price = base_pricing['total_cost']
        else:
            price = (base_pricing['total_cost'] + base_pricing['expected_rto']) / (1 - m - gateway_fee - platform_fee)
        
        price = round(price, 0)
        profit = price - base_pricing['total_cost'] - base_pricing['expected_rto'] - (price * gateway_fee) - (price * platform_fee)
        actual_margin = (profit / price * 100) if price > 0 else 0
        
        ladder.append({
            'margin': f"{margin}%",
            'price': f"₨ {price:,.0f}",
            'profit': f"₨ {profit:,.0f}",
            'actual_margin': f"{actual_margin:.2f}%"
        })
    
    return pd.DataFrame(ladder)

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================
def save_product(data, user_email):
    """Save product to database"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    
    try:
        c.execute('''INSERT INTO products 
                     (sku, product_name, pack_size, units_per_order, purchase_cost, inbound_freight,
                      customs_duties, wastage_pct, bag_cost, label_cost, box_cost, labor_cost,
                      other_product_cost, delivery_cost, customer_delivery, gateway_fee_pct,
                      gateway_fixed, platform_fee_pct, marketing_cost, return_rate_pct, rto_rate_pct,
                      return_shipping, return_handling, target_margin_pct, discount_pct,
                      created_by, created_at, updated_at, is_active)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)''',
                  (data['sku'], data['product_name'], data['pack_size'], data['units_per_order'],
                   data['purchase_cost'], data['inbound_freight'], data['customs_duties'], data['wastage_pct'],
                   data['bag_cost'], data['label_cost'], data['box_cost'], data['labor_cost'],
                   data['other_product_cost'], data['delivery_cost'], data['customer_delivery'],
                   data['gateway_fee_pct'], data['gateway_fixed'], data['platform_fee_pct'],
                   data['marketing_cost'], data['return_rate_pct'], data['rto_rate_pct'],
                   data['return_shipping'], data['return_handling'], data['target_margin_pct'],
                   data['discount_pct'], user_email, datetime.now(), datetime.now()))
        
        # Add audit log
        c.execute('''INSERT INTO audit_log (user_email, action, product_sku, details, timestamp)
                     VALUES (?, ?, ?, ?, ?)''',
                 (user_email, 'CREATE', data['sku'], 'Product created', datetime.now()))
        
        conn.commit()
        conn.close()
        return True, "✅ Product saved successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "❌ SKU already exists! Please use a different SKU or update existing product."
    except Exception as e:
        conn.close()
        return False, f"❌ Error: {str(e)}"

def update_product(sku, data, user_email):
    """Update existing product"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    
    try:
        c.execute('''UPDATE products SET
                     product_name = ?, pack_size = ?, units_per_order = ?, purchase_cost = ?,
                     inbound_freight = ?, customs_duties = ?, wastage_pct = ?, bag_cost = ?,
                     label_cost = ?, box_cost = ?, labor_cost = ?, other_product_cost = ?,
                     delivery_cost = ?, customer_delivery = ?, gateway_fee_pct = ?,
                     gateway_fixed = ?, platform_fee_pct = ?, marketing_cost = ?,
                     return_rate_pct = ?, rto_rate_pct = ?, return_shipping = ?,
                     return_handling = ?, target_margin_pct = ?, discount_pct = ?,
                     updated_at = ?
                     WHERE sku = ?''',
                  (data['product_name'], data['pack_size'], data['units_per_order'],
                   data['purchase_cost'], data['inbound_freight'], data['customs_duties'],
                   data['wastage_pct'], data['bag_cost'], data['label_cost'], data['box_cost'],
                   data['labor_cost'], data['other_product_cost'], data['delivery_cost'],
                   data['customer_delivery'], data['gateway_fee_pct'], data['gateway_fixed'],
                   data['platform_fee_pct'], data['marketing_cost'], data['return_rate_pct'],
                   data['rto_rate_pct'], data['return_shipping'], data['return_handling'],
                   data['target_margin_pct'], data['discount_pct'], datetime.now(), sku))
        
        # Add audit log
        c.execute('''INSERT INTO audit_log (user_email, action, product_sku, details, timestamp)
                     VALUES (?, ?, ?, ?, ?)''',
                 (user_email, 'UPDATE', sku, 'Product updated', datetime.now()))
        
        conn.commit()
        conn.close()
        return True, "✅ Product updated successfully!"
    except Exception as e:
        conn.close()
        return False, f"❌ Error: {str(e)}"

def get_all_products():
    """Get all products"""
    conn = sqlite3.connect('northern_harvest.db')
    df = pd.read_sql_query('SELECT * FROM products WHERE is_active = 1', conn)
    conn.close()
    return df

def get_product_by_sku(sku):
    """Get product by SKU"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE sku = ? AND is_active = 1', (sku,))
    product = c.fetchone()
    conn.close()
    return product

def delete_product(sku, user_email):
    """Soft delete product"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    
    c.execute('UPDATE products SET is_active = 0, updated_at = ? WHERE sku = ?',
              (datetime.now(), sku))
    
    c.execute('''INSERT INTO audit_log (user_email, action, product_sku, details, timestamp)
                 VALUES (?, ?, ?, ?, ?)''',
             (user_email, 'DELETE', sku, 'Product deleted', datetime.now()))
    
    conn.commit()
    conn.close()
    return True, "✅ Product deleted successfully!"

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    """Main application"""
    
    # Initialize database
    init_db()
    create_default_users()
    set_default_settings()
    
    # Session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_role = None
    
    # Login/Logout
    if not st.session_state.authenticated:
        show_login()
    else:
        show_main_app()

def show_login():
    """Show login page"""
    st.markdown('<div style="text-align: center; padding: 50px 0;">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <h1 style='text-align: center; color: #1F3A5F;'>🌾 Northern Harvest</h1>
            <p style='text-align: center; color: #666; font-size: 18px;'>Professional Pricing & Profitability System</p>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        email = st.text_input("📧 Email", placeholder="Enter your email")
        password = st.text_input("🔐 Password", type="password", placeholder="Enter your password")
        
        if st.button("🔓 Login", use_container_width=True):
            user = login_user(email, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user_email = user[1]
                st.session_state.user_role = user[4]
                st.session_state.user_name = user[3]
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_main_app():
    """Show main application"""
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
            <h2 style='color: #1F3A5F;'>👤 {st.session_state.user_name}</h2>
            <p style='color: #666;'>{st.session_state.user_email}</p>
            <p style='color: #999; font-size: 12px;'>Role: {st.session_state.user_role.upper()}</p>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        nav = st.radio(
            "📍 Navigation",
            ["🏠 Home", "🧮 Product Calculator", "📊 Product Master", "📈 Dashboard", "⚙️ Settings", "👥 User Management", "📋 Audit Log"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.rerun()
    
    # Header
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1F3A5F 0%, #2E5090 100%); padding: 30px; border-radius: 10px; margin-bottom: 30px;'>
            <h1 style='color: white; margin: 0;'>🌾 Northern Harvest</h1>
            <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0;'>Professional Pricing & Profitability System</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Routes
    if nav == "🏠 Home":
        show_home()
    elif nav == "🧮 Product Calculator":
        show_calculator()
    elif nav == "📊 Product Master":
        show_product_master()
    elif nav == "📈 Dashboard":
        show_dashboard()
    elif nav == "⚙️ Settings":
        show_settings()
    elif nav == "👥 User Management":
        show_user_management()
    elif nav == "📋 Audit Log":
        show_audit_log()

def show_home():
    """Home page"""
    col1, col2, col3 = st.columns(3)
    
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM products WHERE is_active = 1')
    product_count = c.fetchone()[0]
    
    c.execute('SELECT AVG(CASE WHEN platform_fee_pct > 0 THEN ((recommended_price - total_cost - expected_rto - (recommended_price * gateway_fee_pct/100) - (recommended_price * platform_fee_pct/100)) / recommended_price * 100) ELSE 0 END) FROM (SELECT p.*, ROUND((p.purchase_cost + p.inbound_freight + p.customs_duties + (p.purchase_cost * p.wastage_pct/100) + p.bag_cost + p.label_cost + p.box_cost + p.labor_cost + p.other_product_cost + p.delivery_cost - p.customer_delivery + p.marketing_cost) AS total_cost, ((p.return_rate_pct + p.rto_rate_pct)/100) * (p.return_shipping + p.return_handling) AS expected_rto, ROUND(((p.purchase_cost + p.inbound_freight + p.customs_duties + (p.purchase_cost * p.wastage_pct/100) + p.bag_cost + p.label_cost + p.box_cost + p.labor_cost + p.other_product_cost + p.delivery_cost - p.customer_delivery + p.marketing_cost + ((p.return_rate_pct + p.rto_rate_pct)/100) * (p.return_shipping + p.return_handling)) / (1 - p.target_margin_pct/100 - p.gateway_fee_pct/100 - p.platform_fee_pct/100)), 0) AS recommended_price FROM products p WHERE p.is_active = 1)')
    avg_margin = c.fetchone()[0] or 0
    conn.close()
    
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>📦 Total Products</div>
                <div class='metric-value'>{product_count}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='metric-card' style='background: linear-gradient(135deg, #F39C12 0%, #E67E22 100%);'>
                <div class='metric-label'>📊 Avg Margin</div>
                <div class='metric-value'>{avg_margin:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='metric-card' style='background: linear-gradient(135deg, #27AE60 0%, #229954 100%);'>
                <div class='metric-label'>✅ Active</div>
                <div class='metric-value'>{product_count}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("🚀 Quick Start")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Add New Product", use_container_width=True):
            st.session_state.page = "calculator"
            st.rerun()
    
    with col2:
        if st.button("📊 View All Products", use_container_width=True):
            st.session_state.page = "master"
            st.rerun()

def show_calculator():
    """Product Calculator page"""
    st.subheader("🧮 Product Calculator")
    
    # Load or New
    col1, col2 = st.columns(2)
    with col1:
        load_existing = st.checkbox("📂 Load Existing Product?")
    
    if load_existing:
        products_df = get_all_products()
        if len(products_df) > 0:
            sku_options = products_df['sku'].tolist()
            selected_sku = st.selectbox("Select Product", sku_options)
            
            if selected_sku:
                product = get_product_by_sku(selected_sku)
                if product:
                    # Load into form
                    col1, col2 = st.columns(2)
                    with col1:
                        sku = st.text_input("SKU", value=product[1], disabled=True)
                        product_name = st.text_input("Product Name", value=product[2])
                        pack_size = st.number_input("Pack Size (g)", value=int(product[3]), min_value=1)
                        units_order = st.number_input("Units per Order", value=int(product[4]), min_value=1)
                    
                    with col2:
                        purchase_cost = st.number_input("Purchase Cost", value=float(product[5]), min_value=0.0)
                        inbound_freight = st.number_input("Inbound Freight", value=float(product[6]), min_value=0.0)
                        customs_duties = st.number_input("Customs/Duties", value=float(product[7]), min_value=0.0)
                        wastage_pct = st.number_input("Wastage %", value=float(product[8]), min_value=0.0)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        bag_cost = st.number_input("Bag Cost", value=float(product[9]), min_value=0.0)
                        label_cost = st.number_input("Label Cost", value=float(product[10]), min_value=0.0)
                        box_cost = st.number_input("Box Cost", value=float(product[11]), min_value=0.0)
                    
                    with col2:
                        labor_cost = st.number_input("Labor Cost", value=float(product[12]), min_value=0.0)
                        other_product_cost = st.number_input("Other Product Cost", value=float(product[13]), min_value=0.0)
                        delivery_cost = st.number_input("Delivery Cost", value=float(product[14]), min_value=0.0)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        customer_delivery = st.number_input("Customer Delivery", value=float(product[15]), min_value=0.0)
                        gateway_fee_pct = st.number_input("Gateway Fee %", value=float(product[16]), min_value=0.0)
                        platform_fee_pct = st.number_input("Platform Fee %", value=float(product[18]), min_value=0.0)
                    
                    with col2:
                        marketing_cost = st.number_input("Marketing Cost", value=float(product[19]), min_value=0.0)
                        return_rate_pct = st.number_input("Return Rate %", value=float(product[20]), min_value=0.0)
                        rto_rate_pct = st.number_input("RTO Rate %", value=float(product[21]), min_value=0.0)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        return_shipping = st.number_input("Return Shipping", value=float(product[22]), min_value=0.0)
                        return_handling = st.number_input("Return Handling", value=float(product[23]), min_value=0.0)
                    
                    with col2:
                        target_margin_pct = st.number_input("Target Margin %", value=float(product[24]), min_value=0.0, max_value=99.0)
                        discount_pct = st.number_input("Discount %", value=float(product[25]), min_value=0.0, max_value=99.0)
                    
                    is_update = True
        else:
            st.warning("No products found!")
            load_existing = False
    
    if not load_existing:
        is_update = False
        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input("SKU", placeholder="NH-ALM-500")
            product_name = st.text_input("Product Name", placeholder="Premium Almonds")
            pack_size = st.number_input("Pack Size (g)", value=500, min_value=1)
            units_order = st.number_input("Units per Order", value=1, min_value=1)
        
        with col2:
            purchase_cost = st.number_input("Purchase Cost", value=1200.0, min_value=0.0)
            inbound_freight = st.number_input("Inbound Freight", value=100.0, min_value=0.0)
            customs_duties = st.number_input("Customs/Duties", value=150.0, min_value=0.0)
            wastage_pct = st.number_input("Wastage %", value=2.0, min_value=0.0)
        
        col1, col2 = st.columns(2)
        with col1:
            bag_cost = st.number_input("Bag Cost", value=20.0, min_value=0.0)
            label_cost = st.number_input("Label Cost", value=5.0, min_value=0.0)
            box_cost = st.number_input("Box Cost", value=15.0, min_value=0.0)
        
        with col2:
            labor_cost = st.number_input("Labor Cost", value=30.0, min_value=0.0)
            other_product_cost = st.number_input("Other Product Cost", value=0.0, min_value=0.0)
            delivery_cost = st.number_input("Delivery Cost", value=250.0, min_value=0.0)
        
        col1, col2 = st.columns(2)
        with col1:
            customer_delivery = st.number_input("Customer Delivery", value=150.0, min_value=0.0)
            gateway_fee_pct = st.number_input("Gateway Fee %", value=2.5, min_value=0.0)
            platform_fee_pct = st.number_input("Platform Fee %", value=1.5, min_value=0.0)
        
        with col2:
            marketing_cost = st.number_input("Marketing Cost", value=50.0, min_value=0.0)
            return_rate_pct = st.number_input("Return Rate %", value=5.0, min_value=0.0)
            rto_rate_pct = st.number_input("RTO Rate %", value=3.0, min_value=0.0)
        
        col1, col2 = st.columns(2)
        with col1:
            return_shipping = st.number_input("Return Shipping", value=200.0, min_value=0.0)
            return_handling = st.number_input("Return Handling", value=50.0, min_value=0.0)
        
        with col2:
            target_margin_pct = st.number_input("Target Margin %", value=30.0, min_value=0.0, max_value=99.0)
            discount_pct = st.number_input("Discount %", value=10.0, min_value=0.0, max_value=99.0)
    
    # Calculate
    data = {
        'sku': sku,
        'product_name': product_name,
        'pack_size': pack_size,
        'units_per_order': units_order,
        'purchase_cost': purchase_cost,
        'inbound_freight': inbound_freight,
        'customs_duties': customs_duties,
        'wastage_pct': wastage_pct,
        'bag_cost': bag_cost,
        'label_cost': label_cost,
        'box_cost': box_cost,
        'labor_cost': labor_cost,
        'other_product_cost': other_product_cost,
        'delivery_cost': delivery_cost,
        'customer_delivery': customer_delivery,
        'gateway_fee_pct': gateway_fee_pct,
        'gateway_fixed': 0,
        'platform_fee_pct': platform_fee_pct,
        'marketing_cost': marketing_cost,
        'return_rate_pct': return_rate_pct,
        'rto_rate_pct': rto_rate_pct,
        'return_shipping': return_shipping,
        'return_handling': return_handling,
        'target_margin_pct': target_margin_pct,
        'discount_pct': discount_pct,
    }
    
    pricing = calculate_pricing(data)
    
    # Results
    st.markdown("---")
    st.subheader("📊 Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Base Cost", f"₨ {pricing['base_cost']:,.0f}")
    
    with col2:
        st.metric("Total Cost", f"₨ {pricing['total_cost']:,.0f}")
    
    with col3:
        st.metric("Break-even", f"₨ {pricing['breakeven']:,.0f}")
    
    with col4:
        st.metric("Expected RTO", f"₨ {pricing['expected_rto']:,.0f}")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div style='background: #C6EFCE; padding: 15px; border-radius: 8px;'>
                <div style='font-size: 12px; color: #666; text-transform: uppercase;'>Recommended Price ⭐</div>
                <div style='font-size: 24px; font-weight: bold; color: #006600; margin-top: 10px;'>₨ {pricing['recommended_price']:,.0f}</div>
                <div style='font-size: 11px; color: #999; margin-top: 5px;'>for {target_margin_pct:.0f}% margin</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style='background: #FFFFCC; padding: 15px; border-radius: 8px;'>
                <div style='font-size: 12px; color: #666; text-transform: uppercase;'>Discount Price</div>
                <div style='font-size: 24px; font-weight: bold; color: #F39C12; margin-top: 10px;'>₨ {pricing['discount_price']:,.0f}</div>
                <div style='font-size: 11px; color: #999; margin-top: 5px;'>after {discount_pct:.0f}% discount</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='background: #D9E1F2; padding: 15px; border-radius: 8px;'>
                <div style='font-size: 12px; color: #666; text-transform: uppercase;'>Expected Profit</div>
                <div style='font-size: 24px; font-weight: bold; color: #1F3A5F; margin-top: 10px;'>₨ {pricing['profit']:,.0f}</div>
                <div style='font-size: 11px; color: #999; margin-top: 5px;'>Margin: {pricing['margin']:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Pricing Status:** {pricing['status']}")
    
    with col2:
        st.metric("Net Margin", f"{pricing['margin']:.2f}%", f"{pricing['margin'] - target_margin_pct:.2f}%")
    
    # Price Ladder
    st.markdown("---")
    st.subheader("📈 Price Ladder")
    
    ladder_df = generate_price_ladder(data)
    st.dataframe(ladder_df, use_container_width=True, hide_index=True)
    
    # Save/Update
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Product" if not is_update else "✏️ Update Product", use_container_width=True):
            if not sku or not product_name:
                st.error("❌ Please fill in all required fields!")
            else:
                if is_update:
                    success, message = update_product(sku, data, st.session_state.user_email)
                else:
                    success, message = save_product(data, st.session_state.user_email)
                
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)
    
    with col2:
        if st.button("🔄 Clear Form", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    with col3:
        if st.button("📥 Export PDF", use_container_width=True):
            st.info("PDF export feature coming soon!")

def show_product_master():
    """Product Master page"""
    st.subheader("📊 Product Master - Database")
    
    products_df = get_all_products()
    
    if len(products_df) == 0:
        st.info("📭 No products found. Start by adding your first product in Product Calculator!")
        return
    
    # Filters and Search
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search by SKU or Name", placeholder="Search...")
    
    with col2:
        sort_by = st.selectbox("📊 Sort by", ["SKU", "Product Name", "Recommended Price", "Net Margin"])
    
    with col3:
        margin_filter = st.slider("📈 Filter by Margin %", 0, 100, (0, 100))
    
    # Apply filters
    if search_term:
        products_df = products_df[
            (products_df['sku'].str.contains(search_term, case=False, na=False)) |
            (products_df['product_name'].str.contains(search_term, case=False, na=False))
        ]
    
    # Sort
    if sort_by == "SKU":
        products_df = products_df.sort_values('sku')
    elif sort_by == "Product Name":
        products_df = products_df.sort_values('product_name')
    elif sort_by == "Recommended Price":
        # Calculate recommended price
        products_df['rec_price'] = products_df.apply(
            lambda row: calculate_pricing({
                'purchase_cost': row['purchase_cost'],
                'inbound_freight': row['inbound_freight'],
                'customs_duties': row['customs_duties'],
                'wastage_pct': row['wastage_pct'],
                'bag_cost': row['bag_cost'],
                'label_cost': row['label_cost'],
                'box_cost': row['box_cost'],
                'labor_cost': row['labor_cost'],
                'other_product_cost': row['other_product_cost'],
                'delivery_cost': row['delivery_cost'],
                'customer_delivery': row['customer_delivery'],
                'gateway_fee_pct': row['gateway_fee_pct'],
                'gateway_fixed': row['gateway_fixed'],
                'platform_fee_pct': row['platform_fee_pct'],
                'marketing_cost': row['marketing_cost'],
                'return_rate_pct': row['return_rate_pct'],
                'rto_rate_pct': row['rto_rate_pct'],
                'return_shipping': row['return_shipping'],
                'return_handling': row['return_handling'],
                'target_margin_pct': row['target_margin_pct'],
                'discount_pct': row['discount_pct'],
            })['recommended_price'],
            axis=1
        )
        products_df = products_df.sort_values('rec_price', ascending=False)
    
    # Display table
    st.dataframe(
        products_df[[
            'sku', 'product_name', 'pack_size', 'purchase_cost',
            'target_margin_pct', 'created_at'
        ]].rename(columns={
            'sku': 'SKU',
            'product_name': 'Product',
            'pack_size': 'Pack (g)',
            'purchase_cost': 'Cost',
            'target_margin_pct': 'Margin %',
            'created_at': 'Created'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Actions
    st.markdown("---")
    st.subheader("🔧 Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        action = st.selectbox("Select Action", ["View Details", "Edit", "Delete"])
    
    with col2:
        product_sku = st.selectbox("Select Product", products_df['sku'].tolist())
    
    with col3:
        if st.button("Execute", use_container_width=True):
            if action == "View Details":
                st.info("Details feature coming soon!")
            elif action == "Edit":
                st.session_state.edit_sku = product_sku
                st.session_state.page = "calculator"
                st.rerun()
            elif action == "Delete":
                success, message = delete_product(product_sku, st.session_state.user_email)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def show_dashboard():
    """Dashboard page"""
    st.subheader("📈 Dashboard & Analytics")
    
    products_df = get_all_products()
    
    if len(products_df) == 0:
        st.info("📭 No data available. Add some products first!")
        return
    
    # Calculate metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Total Products", len(products_df))
    
    with col2:
        avg_margin = 30  # Default
        st.metric("📊 Avg Margin", f"{avg_margin:.1f}%")
    
    with col3:
        total_cost = products_df['purchase_cost'].sum()
        st.metric("💰 Total Cost", f"₨ {total_cost:,.0f}")
    
    with col4:
        st.metric("✅ Active Products", len(products_df))
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Products by Pack Size")
        pack_counts = products_df['pack_size'].value_counts().head(10)
        fig = px.bar(
            x=pack_counts.index,
            y=pack_counts.values,
            labels={'x': 'Pack Size (g)', 'y': 'Count'},
            color_discrete_sequence=['#1F3A5F']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💵 Cost Distribution")
        top_products = products_df.nlargest(10, 'purchase_cost')
        fig = px.pie(
            top_products,
            values='purchase_cost',
            names='product_name',
            color_discrete_sequence=px.colors.sequential.Blues
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top Products Table
    st.markdown("---")
    st.subheader("🏆 Top Products by Cost")
    
    top_10 = products_df.nlargest(10, 'purchase_cost')[[
        'sku', 'product_name', 'pack_size', 'purchase_cost', 'target_margin_pct'
    ]].rename(columns={
        'sku': 'SKU',
        'product_name': 'Product',
        'pack_size': 'Pack (g)',
        'purchase_cost': 'Cost',
        'target_margin_pct': 'Margin %'
    })
    
    st.dataframe(top_10, use_container_width=True, hide_index=True)

def show_settings():
    """Settings page"""
    st.subheader("⚙️ Settings")
    
    if st.session_state.user_role != 'admin':
        st.error("❌ Only administrators can access settings!")
        return
    
    # Default Settings
    st.subheader("🔧 Default Pricing Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_margin = st.number_input("Default Target Margin %", value=30.0, min_value=0.0, max_value=99.0)
        gateway_fee = st.number_input("Default Gateway Fee %", value=2.5, min_value=0.0)
        platform_fee = st.number_input("Default Platform Fee %", value=1.5, min_value=0.0)
    
    with col2:
        delivery_cost = st.number_input("Default Delivery Cost", value=250.0, min_value=0.0)
        return_rate = st.number_input("Default Return Rate %", value=5.0, min_value=0.0)
        rto_rate = st.number_input("Default RTO Rate %", value=3.0, min_value=0.0)
    
    if st.button("💾 Save Settings", use_container_width=True):
        conn = sqlite3.connect('northern_harvest.db')
        c = conn.cursor()
        
        settings = [
            ('target_margin', str(target_margin)),
            ('gateway_fee', str(gateway_fee)),
            ('platform_fee', str(platform_fee)),
            ('delivery_cost', str(delivery_cost)),
            ('return_rate', str(return_rate)),
            ('rto_rate', str(rto_rate)),
        ]
        
        for key, value in settings:
            c.execute('UPDATE settings SET setting_value = ?, updated_at = ? WHERE setting_key = ?',
                     (value, datetime.now(), key))
        
        conn.commit()
        conn.close()
        
        st.success("✅ Settings saved successfully!")

def show_user_management():
    """User Management page"""
    st.subheader("👥 User Management")
    
    if st.session_state.user_role != 'admin':
        st.error("❌ Only administrators can manage users!")
        return
    
    conn = sqlite3.connect('northern_harvest.db')
    users_df = pd.read_sql_query('SELECT id, email, name, role, is_active FROM users', conn)
    conn.close()
    
    st.dataframe(users_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("➕ Add New User")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_email = st.text_input("Email", placeholder="user@example.com")
        new_name = st.text_input("Name", placeholder="User Name")
    
    with col2:
        new_role = st.selectbox("Role", ["user", "admin"])
        new_password = st.text_input("Password", type="password", placeholder="Generate a password")
    
    if st.button("Add User", use_container_width=True):
        if new_email and new_name and new_password:
            conn = sqlite3.connect('northern_harvest.db')
            c = conn.cursor()
            
            try:
                c.execute('''INSERT INTO users (email, password, name, role, created_at, is_active)
                             VALUES (?, ?, ?, ?, ?, 1)''',
                         (new_email, hash_password(new_password), new_name, new_role, datetime.now()))
                conn.commit()
                st.success("✅ User added successfully!")
            except sqlite3.IntegrityError:
                st.error("❌ User already exists!")
            finally:
                conn.close()
        else:
            st.error("❌ Please fill in all fields!")

def show_audit_log():
    """Audit Log page"""
    st.subheader("📋 Audit Log")
    
    if st.session_state.user_role != 'admin':
        st.error("❌ Only administrators can view audit logs!")
        return
    
    conn = sqlite3.connect('northern_harvest.db')
    audit_df = pd.read_sql_query(
        'SELECT user_email, action, product_sku, details, timestamp FROM audit_log ORDER BY timestamp DESC LIMIT 100',
        conn
    )
    conn.close()
    
    if len(audit_df) > 0:
        audit_df.columns = ['User', 'Action', 'SKU', 'Details', 'Timestamp']
        st.dataframe(audit_df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 No audit logs found!")

if __name__ == "__main__":
    main()
