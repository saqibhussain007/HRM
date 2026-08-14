import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib

st.set_page_config(page_title="Northern Harvest - Pricing System", page_icon="🌾", layout="wide")

st.markdown("""
<style>
.metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 10px; }
.metric-label { font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; }
.metric-value { font-size: 1.8rem; font-weight: bold; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, name TEXT, role TEXT, created_at TIMESTAMP, is_active INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, sku TEXT UNIQUE, product_name TEXT, pack_size REAL, units_per_order INTEGER,
                  purchase_cost REAL, inbound_freight REAL, customs_duties REAL, wastage_pct REAL, bag_cost REAL,
                  label_cost REAL, box_cost REAL, labor_cost REAL, other_product_cost REAL, delivery_cost REAL,
                  customer_delivery REAL, gateway_fee_pct REAL, gateway_fixed REAL, platform_fee_pct REAL, marketing_cost REAL,
                  return_rate_pct REAL, rto_rate_pct REAL, return_shipping REAL, return_handling REAL, target_margin_pct REAL,
                  discount_pct REAL, created_by TEXT, created_at TIMESTAMP, updated_at TIMESTAMP, is_active INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (id INTEGER PRIMARY KEY, setting_key TEXT UNIQUE, setting_value TEXT, created_at TIMESTAMP, updated_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS audit_log
                 (id INTEGER PRIMARY KEY, user_email TEXT, action TEXT, product_sku TEXT, details TEXT, timestamp TIMESTAMP)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_default_users():
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    users = [
        ('saqibhussain505@gmail.com', '@Hussain007', 'Saqib Hussain', 'admin'),
        ('achill0076@gmail.com', 'password123', 'Ali', 'user'),
    ]
    for email, password, name, role in users:
        try:
            c.execute('INSERT INTO users (email, password, name, role, created_at, is_active) VALUES (?, ?, ?, ?, ?, 1)',
                     (email, hash_password(password), name, role, datetime.now()))
        except:
            pass
    conn.commit()
    conn.close()

def set_default_settings():
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    settings = [('target_margin', '30'), ('gateway_fee', '2.5'), ('platform_fee', '1.5'), 
                ('delivery_cost', '250'), ('return_rate', '5'), ('rto_rate', '3')]
    for key, value in settings:
        try:
            c.execute('INSERT INTO settings (setting_key, setting_value, created_at, updated_at) VALUES (?, ?, ?, ?)',
                     (key, value, datetime.now(), datetime.now()))
        except:
            pass
    conn.commit()
    conn.close()

def login_user(email, password):
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ? AND password = ? AND is_active = 1',
              (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def calculate_pricing(data):
    purchase = float(data.get('purchase_cost', 0))
    wastage_pct = float(data.get('wastage_pct', 0))
    wastage_cost = purchase * (wastage_pct / 100)
    
    base_cost = (purchase + float(data.get('inbound_freight', 0)) + float(data.get('customs_duties', 0)) + 
                 wastage_cost + float(data.get('bag_cost', 0)) + float(data.get('label_cost', 0)) + 
                 float(data.get('box_cost', 0)) + float(data.get('labor_cost', 0)))
    
    net_delivery = float(data.get('delivery_cost', 0)) - float(data.get('customer_delivery', 0))
    
    return_rto_rate = (float(data.get('return_rate_pct', 0)) + float(data.get('rto_rate_pct', 0))) / 100
    expected_rto = return_rto_rate * (float(data.get('return_shipping', 0)) + float(data.get('return_handling', 0)))
    
    total_cost = base_cost + net_delivery + float(data.get('marketing_cost', 0))
    
    target_margin = float(data.get('target_margin_pct', 30)) / 100
    gateway_fee = float(data.get('gateway_fee_pct', 2.5)) / 100
    platform_fee = float(data.get('platform_fee_pct', 1.5)) / 100
    
    if (1 - target_margin - gateway_fee - platform_fee) <= 0:
        required_price = total_cost
    else:
        required_price = (total_cost + expected_rto) / (1 - target_margin - gateway_fee - platform_fee)
    
    recommended_price = round(required_price, 0)
    discount_pct = float(data.get('discount_pct', 10)) / 100
    discount_price = round(recommended_price * (1 - discount_pct), 0)
    
    gateway_cost = recommended_price * gateway_fee
    platform_cost = recommended_price * platform_fee
    profit = recommended_price - total_cost - expected_rto - gateway_cost - platform_cost
    margin = (profit / recommended_price * 100) if recommended_price > 0 else 0
    
    if margin < 0:
        status = "🔴 LOSS"
    elif margin < target_margin * 100:
        status = "🟡 WARNING"
    else:
        status = "🟢 OK"
    
    return {
        'base_cost': base_cost,
        'total_cost': total_cost,
        'expected_rto': expected_rto,
        'recommended_price': recommended_price,
        'discount_price': discount_price,
        'profit': profit,
        'margin': margin,
        'status': status,
    }

def save_product(data, user_email):
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO products (sku, product_name, pack_size, units_per_order, purchase_cost, inbound_freight,
                     customs_duties, wastage_pct, bag_cost, label_cost, box_cost, labor_cost, other_product_cost,
                     delivery_cost, customer_delivery, gateway_fee_pct, gateway_fixed, platform_fee_pct, marketing_cost,
                     return_rate_pct, rto_rate_pct, return_shipping, return_handling, target_margin_pct, discount_pct,
                     created_by, created_at, updated_at, is_active)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)''',
             (data['sku'], data['product_name'], data['pack_size'], data['units_per_order'], data['purchase_cost'],
              data['inbound_freight'], data['customs_duties'], data['wastage_pct'], data['bag_cost'], data['label_cost'],
              data['box_cost'], data['labor_cost'], data['other_product_cost'], data['delivery_cost'],
              data['customer_delivery'], data['gateway_fee_pct'], 0, data['platform_fee_pct'], data['marketing_cost'],
              data['return_rate_pct'], data['rto_rate_pct'], data['return_shipping'], data['return_handling'],
              data['target_margin_pct'], data['discount_pct'], user_email, datetime.now(), datetime.now()))
        conn.commit()
        conn.close()
        return True, "✅ Product saved!"
    except:
        conn.close()
        return False, "❌ Error saving product"

def get_all_products():
    conn = sqlite3.connect('northern_harvest.db')
    df = pd.read_sql_query('SELECT * FROM products WHERE is_active = 1', conn)
    conn.close()
    return df

init_db()
create_default_users()
set_default_settings()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_role = None
    st.session_state.user_name = None

if not st.session_state.authenticated:
    st.markdown('<div style="text-align: center; padding: 50px 0;">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #1F3A5F;'>🌾 Northern Harvest</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Professional Pricing System</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        email = st.text_input("📧 Email")
        password = st.text_input("🔐 Password", type="password")
        
        if st.button("🔓 Login"):
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
else:
    with st.sidebar:
        st.markdown(f"<h3>👤 {st.session_state.user_name}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p>{st.session_state.user_email}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        nav = st.radio("📍 Navigation", ["🏠 Home", "🧮 Calculator", "📊 Products", "📈 Dashboard", "⚙️ Settings"])
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("<div style='background: linear-gradient(135deg, #1F3A5F 0%, #2E5090 100%); padding: 30px; border-radius: 10px;'><h1 style='color: white;'>🌾 Northern Harvest</h1></div>", unsafe_allow_html=True)
    
    if nav == "🏠 Home":
        col1, col2, col3 = st.columns(3)
        products_df = get_all_products()
        
        with col1:
            st.metric("📦 Products", len(products_df))
        with col2:
            st.metric("📊 Margin", "30%")
        with col3:
            st.metric("✅ Active", len(products_df))
    
    elif nav == "🧮 Calculator":
        st.subheader("🧮 Product Calculator")
        
        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input("SKU", "NH-001")
            product_name = st.text_input("Product Name", "Product")
            pack_size = st.number_input("Pack Size (g)", 500)
        
        with col2:
            purchase_cost = st.number_input("Purchase Cost", 1200.0)
            inbound_freight = st.number_input("Inbound Freight", 100.0)
            customs_duties = st.number_input("Customs/Duties", 150.0)
        
        col1, col2 = st.columns(2)
        with col1:
            bag_cost = st.number_input("Bag Cost", 20.0)
            label_cost = st.number_input("Label Cost", 5.0)
            box_cost = st.number_input("Box Cost", 15.0)
        
        with col2:
            labor_cost = st.number_input("Labor Cost", 30.0)
            delivery_cost = st.number_input("Delivery Cost", 250.0)
            customer_delivery = st.number_input("Customer Delivery", 150.0)
        
        col1, col2 = st.columns(2)
        with col1:
            gateway_fee_pct = st.number_input("Gateway Fee %", 2.5)
            platform_fee_pct = st.number_input("Platform Fee %", 1.5)
            marketing_cost = st.number_input("Marketing Cost", 50.0)
        
        with col2:
            return_rate_pct = st.number_input("Return Rate %", 5.0)
            rto_rate_pct = st.number_input("RTO Rate %", 3.0)
            return_shipping = st.number_input("Return Shipping", 200.0)
        
        col1, col2 = st.columns(2)
        with col1:
            return_handling = st.number_input("Return Handling", 50.0)
            target_margin_pct = st.number_input("Target Margin %", 30.0)
        with col2:
            wastage_pct = st.number_input("Wastage %", 2.0)
            other_product_cost = st.number_input("Other Cost", 0.0)
            discount_pct = st.number_input("Discount %", 10.0)
        
        data = {
            'sku': sku, 'product_name': product_name, 'pack_size': pack_size, 'units_per_order': 1,
            'purchase_cost': purchase_cost, 'inbound_freight': inbound_freight, 'customs_duties': customs_duties,
            'wastage_pct': wastage_pct, 'bag_cost': bag_cost, 'label_cost': label_cost, 'box_cost': box_cost,
            'labor_cost': labor_cost, 'other_product_cost': other_product_cost, 'delivery_cost': delivery_cost,
            'customer_delivery': customer_delivery, 'gateway_fee_pct': gateway_fee_pct, 'platform_fee_pct': platform_fee_pct,
            'marketing_cost': marketing_cost, 'return_rate_pct': return_rate_pct, 'rto_rate_pct': rto_rate_pct,
            'return_shipping': return_shipping, 'return_handling': return_handling, 'target_margin_pct': target_margin_pct,
            'discount_pct': discount_pct
        }
        
        pricing = calculate_pricing(data)
        
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Base Cost", f"₨ {pricing['base_cost']:,.0f}")
        with col2:
            st.metric("Total Cost", f"₨ {pricing['total_cost']:,.0f}")
        with col3:
            st.metric("Expected RTO", f"₨ {pricing['expected_rto']:,.0f}")
        with col4:
            st.metric("Status", pricing['status'])
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"<div style='background: #C6EFCE; padding: 15px; border-radius: 8px;'><p>Recommended Price</p><h2>₨ {pricing['recommended_price']:,.0f}</h2></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"<div style='background: #FFFFCC; padding: 15px; border-radius: 8px;'><p>Discount Price</p><h2>₨ {pricing['discount_price']:,.0f}</h2></div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"<div style='background: #D9E1F2; padding: 15px; border-radius: 8px;'><p>Profit</p><h2>₨ {pricing['profit']:,.0f}</h2><p>Margin: {pricing['margin']:.2f}%</p></div>", unsafe_allow_html=True)
        
        if st.button("💾 Save Product"):
            success, msg = save_product(data, st.session_state.user_email)
            if success:
                st.success(msg)
            else:
                st.error(msg)
    
    elif nav == "📊 Products":
        st.subheader("📊 Product Master")
        products_df = get_all_products()
        if len(products_df) > 0:
            st.dataframe(products_df[['sku', 'product_name', 'pack_size', 'purchase_cost', 'target_margin_pct']], use_container_width=True)
        else:
            st.info("No products yet!")
    
    elif nav == "📈 Dashboard":
        st.subheader("📈 Dashboard")
        products_df = get_all_products()
        st.info(f"Total Products: {len(products_df)}")
    
    elif nav == "⚙️ Settings":
        st.subheader("⚙️ Settings")
        st.info("Settings page")
