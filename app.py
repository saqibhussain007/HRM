import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib

# Configuration
st.set_page_config(page_title="Northern Harvest - Pricing System", page_icon="🌾", layout="wide", initial_sidebar_state="expanded")

# Professional Colors
PRIMARY = "#1f5e3b"
SECONDARY = "#c89b3c"
LIGHT_BG = "#f8f9fa"
WHITE = "#ffffff"
DANGER = "#dc3545"
SUCCESS = "#28a745"

# Custom CSS
st.markdown(f"""
<style>
    * {{
        margin: 0;
        padding: 0;
    }}
    
    .main-container {{
        background-color: {LIGHT_BG};
    }}
    
    .header {{
        background: linear-gradient(135deg, {PRIMARY} 0%, #2d7a52 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 30px;
        text-align: center;
    }}
    
    .header h1 {{
        font-size: 2.5rem;
        font-weight: bold;
        margin: 10px 0;
    }}
    
    .header p {{
        font-size: 1rem;
        opacity: 0.9;
    }}
    
    .metric-card {{
        background: white;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid {SECONDARY};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .price-card {{
        background: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .price-recommended {{
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border: 2px solid #4caf50;
    }}
    
    .price-discount {{
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border: 2px solid #ff9800;
    }}
    
    .price-profit {{
        background: linear-gradient(135deg, {PRIMARY}22 0%, {SECONDARY}22 100%);
        border: 2px solid {SECONDARY};
    }}
    
    .price-label {{
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 10px;
    }}
    
    .price-value {{
        font-size: 2rem;
        font-weight: bold;
        color: {PRIMARY};
        margin-bottom: 5px;
    }}
    
    .btn-primary {{
        background-color: {PRIMARY};
        color: white;
    }}
    
    .btn-secondary {{
        background-color: {SECONDARY};
        color: white;
    }}
    
    .section-title {{
        color: {PRIMARY};
        font-size: 1.8rem;
        font-weight: bold;
        border-bottom: 3px solid {SECONDARY};
        padding-bottom: 10px;
        margin-bottom: 20px;
    }}
    
    .table-header {{
        background-color: {PRIMARY};
        color: white;
        padding: 15px;
        border-radius: 5px;
        font-weight: bold;
    }}
    
    .action-btn {{
        margin: 5px;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.9rem;
        cursor: pointer;
    }}
    
    .btn-edit {{
        background-color: #007bff;
        color: white;
    }}
    
    .btn-delete {{
        background-color: {DANGER};
        color: white;
    }}
    
    .info-box {{
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
    }}
    
    .success-box {{
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
    }}
    
    .warning-box {{
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
    }}
    
    .danger-box {{
        background-color: #f8d7da;
        border-left: 4px solid {DANGER};
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
    }}
    
    .comp-card {{
        background: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
</style>
""", unsafe_allow_html=True)

# Database Functions
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
    
    c.execute('''CREATE TABLE IF NOT EXISTS monthly_business
                 (id INTEGER PRIMARY KEY, month TEXT UNIQUE, sales REAL, product_cost REAL, business_expenses REAL,
                  employee_pct REAL, owner_pct REAL, reinvestment_pct REAL, created_at TIMESTAMP, updated_at TIMESTAMP)''')
    
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
                ('delivery_cost', '250'), ('return_rate', '5'), ('rto_rate', '3'),
                ('employee_pct', '8'), ('owner_pct', '12'), ('reinvestment_pct', '6')]
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

def get_all_users():
    conn = sqlite3.connect('northern_harvest.db')
    df = pd.read_sql_query('SELECT id, email, name, role, created_at, is_active FROM users ORDER BY created_at DESC', conn)
    conn.close()
    return df

def add_user(email, password, name, role):
    """Add new user or reactivate deleted user"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    try:
        c.execute('SELECT id FROM users WHERE email = ?', (email,))
        existing = c.fetchone()
        
        if existing:
            c.execute('UPDATE users SET password = ?, name = ?, role = ?, is_active = 1, created_at = ? WHERE email = ?',
                     (hash_password(password), name, role, datetime.now(), email))
            action = 'USER_REACTIVATE'
            details = f'User reactivated: {name} ({role})'
        else:
            c.execute('INSERT INTO users (email, password, name, role, created_at, is_active) VALUES (?, ?, ?, ?, ?, 1)',
                     (email, hash_password(password), name, role, datetime.now()))
            action = 'USER_CREATE'
            details = f'User created: {name} ({role})'
        
        c.execute('INSERT INTO audit_log (user_email, action, product_sku, details, timestamp) VALUES (?, ?, ?, ?, ?)',
                 (st.session_state.user_email, action, email, details, datetime.now()))
        conn.commit()
        conn.close()
        return True, "✅ User created/reactivated successfully!"
    except Exception as e:
        conn.close()
        return False, f"❌ Error: {str(e)}"

def permanently_delete_user(user_id, user_email):
    """Permanently delete user (hard delete)"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    try:
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        c.execute('INSERT INTO audit_log (user_email, action, product_sku, details, timestamp) VALUES (?, ?, ?, ?, ?)',
                 (st.session_state.user_email, 'USER_HARD_DELETE', user_email, 'User permanently deleted', datetime.now()))
        conn.commit()
        conn.close()
        return True, "✅ User permanently deleted!"
    except:
        conn.close()
        return False, "❌ Error deleting user"

def soft_delete_user(user_id, user_email):
    """Soft delete user (set is_active = 0)"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    try:
        c.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
        c.execute('INSERT INTO audit_log (user_email, action, product_sku, details, timestamp) VALUES (?, ?, ?, ?, ?)',
                 (st.session_state.user_email, 'USER_DEACTIVATE', user_email, 'User deactivated', datetime.now()))
        conn.commit()
        conn.close()
        return True, "✅ User deactivated!"
    except:
        conn.close()
        return False, "❌ Error deactivating user"

def get_settings():
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    c.execute('SELECT setting_key, setting_value FROM settings')
    settings = dict(c.fetchall())
    conn.close()
    return settings

def update_settings(settings_dict):
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    for key, value in settings_dict.items():
        c.execute('UPDATE settings SET setting_value = ?, updated_at = ? WHERE setting_key = ?',
                 (str(value), datetime.now(), key))
    conn.commit()
    conn.close()

# Business & Compensation Functions
def calculate_compensation(sales, product_cost, business_expenses, employee_pct, owner_pct, reinvestment_pct):
    """Calculate monthly compensation"""
    actual_profit = sales - product_cost - business_expenses
    
    employee_comp = sales * (employee_pct / 100)
    owner_comp = sales * (owner_pct / 100)
    reinvestment = sales * (reinvestment_pct / 100)
    final_profit = actual_profit - employee_comp - owner_comp - reinvestment
    
    return {
        'actual_profit': actual_profit,
        'employee_comp': employee_comp,
        'owner_comp': owner_comp,
        'reinvestment': reinvestment,
        'final_profit': final_profit
    }

def save_monthly_business(month, sales, product_cost, business_expenses, employee_pct, owner_pct, reinvestment_pct):
    """Save monthly business record"""
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT OR REPLACE INTO monthly_business 
                     (month, sales, product_cost, business_expenses, employee_pct, owner_pct, reinvestment_pct, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (month, sales, product_cost, business_expenses, employee_pct, owner_pct, reinvestment_pct, datetime.now(), datetime.now()))
        conn.commit()
        conn.close()
        return True, "✅ Monthly record saved!"
    except Exception as e:
        conn.close()
        return False, f"❌ Error: {str(e)}"

def get_all_monthly_records():
    """Get all monthly business records"""
    conn = sqlite3.connect('northern_harvest.db')
    df = pd.read_sql_query('SELECT * FROM monthly_business ORDER BY month DESC', conn)
    conn.close()
    return df

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
        c.execute('INSERT INTO audit_log (user_email, action, product_sku, details, timestamp) VALUES (?, ?, ?, ?, ?)',
                 (user_email, 'PRODUCT_CREATE', data['sku'], 'Product created', datetime.now()))
        conn.commit()
        conn.close()
        return True, "✅ Product saved!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "❌ SKU already exists!"
    except Exception as e:
        conn.close()
        return False, f"❌ Error: {str(e)}"

def update_product(sku, data, user_email):
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    try:
        c.execute('''UPDATE products SET
                     product_name = ?, pack_size = ?, units_per_order = ?, purchase_cost = ?,
                     inbound_freight = ?, customs_duties = ?, wastage_pct = ?, bag_cost = ?,
                     label_cost = ?, box_cost = ?, labor_cost = ?, other_product_cost = ?,
                     delivery_cost = ?, customer_delivery = ?, gateway_fee_pct = ?,
                     platform_fee_pct = ?, marketing_cost = ?, return_rate_pct = ?, rto_rate_pct = ?,
                     return_shipping = ?, return_handling = ?, target_margin_pct = ?, discount_pct = ?,
                     updated_at = ? WHERE sku = ?''',
             (data['product_name'], data['pack_size'], data['units_per_order'], data['purchase_cost'],
              data['inbound_freight'], data['customs_duties'], data['wastage_pct'], data['bag_cost'],
              data['label_cost'], data['box_cost'], data['labor_cost'], data['other_product_cost'],
              data['delivery_cost'], data['customer_delivery'], data['gateway_fee_pct'],
              data['platform_fee_pct'], data['marketing_cost'], data['return_rate_pct'],
              data['rto_rate_pct'], data['return_shipping'], data['return_handling'],
              data['target_margin_pct'], data['discount_pct'], datetime.now(), sku))
        c.execute('INSERT INTO audit_log (user_email, action, product_sku, details, timestamp) VALUES (?, ?, ?, ?, ?)',
                 (user_email, 'PRODUCT_UPDATE', sku, 'Product updated', datetime.now()))
        conn.commit()
        conn.close()
        return True, "✅ Product updated!"
    except Exception as e:
        conn.close()
        return False, f"❌ Error: {str(e)}"

def delete_product(sku, user_email):
    conn = sqlite3.connect('northern_harvest.db')
    c = conn.cursor()
    try:
        c.execute('UPDATE products SET is_active = 0, updated_at = ? WHERE sku = ?', (datetime.now(), sku))
        c.execute('INSERT INTO audit_log (user_email, action, product_sku, details, timestamp) VALUES (?, ?, ?, ?, ?)',
                 (user_email, 'PRODUCT_DELETE', sku, 'Product deleted', datetime.now()))
        conn.commit()
        conn.close()
        return True, "✅ Product deleted!"
    except:
        conn.close()
        return False, "❌ Error deleting product"

def get_all_products():
    conn = sqlite3.connect('northern_harvest.db')
    df = pd.read_sql_query('SELECT * FROM products WHERE is_active = 1 ORDER BY created_at DESC', conn)
    conn.close()
    return df

def get_product_by_sku(sku):
    conn = sqlite3.connect('northern_harvest.db')
    df = pd.read_sql_query('SELECT * FROM products WHERE sku = ? AND is_active = 1', conn, params=(sku,))
    conn.close()
    return df.iloc[0].to_dict() if len(df) > 0 else None

# Initialize
init_db()
create_default_users()
set_default_settings()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_role = None
    st.session_state.user_name = None

# Login
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div class="header">
                <h1>🌾 Northern Harvest</h1>
                <p>Professional Pricing & Profitability System</p>
            </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("📧 Email")
        password = st.text_input("🔐 Password", type="password")
        
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
        
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
            <div style='background: {PRIMARY}; color: white; padding: 15px; border-radius: 8px;'>
                <h3>👤 {st.session_state.user_name}</h3>
                <p style='margin: 5px 0; font-size: 0.9rem;'>{st.session_state.user_email}</p>
                <p style='margin: 5px 0; font-size: 0.85rem; opacity: 0.8;'>Role: <strong>{st.session_state.user_role.upper()}</strong></p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        nav = st.radio("📍 Navigation", [
            "🏠 Home", 
            "🧮 Calculator", 
            "📊 Product Master",
            "💼 Business & Compensation",
            "⚙️ Settings",
            "👥 User Management",
            "📋 Audit Log"
        ])
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    # Header
    st.markdown(f"""
        <div class="header">
            <h1>🌾 Northern Harvest</h1>
            <p>Professional Pricing & Profitability System</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Home
    if nav == "🏠 Home":
        products_df = get_all_products()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div style='color: {SECONDARY}; font-size: 0.9rem; font-weight: 600;'>📦 Total Products</div>
                    <div style='font-size: 2rem; font-weight: bold; color: {PRIMARY};'>{len(products_df)}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div style='color: {SECONDARY}; font-size: 0.9rem; font-weight: 600;'>💰 Total Cost</div>
                    <div style='font-size: 1.5rem; font-weight: bold; color: {PRIMARY};'>₨ {products_df['purchase_cost'].sum():,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div style='color: {SECONDARY}; font-size: 0.9rem; font-weight: 600;'>📊 Avg Margin</div>
                    <div style='font-size: 1.5rem; font-weight: bold; color: {PRIMARY};'>{products_df['target_margin_pct'].mean():.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <div style='color: {SECONDARY}; font-size: 0.9rem; font-weight: 600;'>✅ Active</div>
                    <div style='font-size: 2rem; font-weight: bold; color: {PRIMARY};'>{len(products_df)}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Calculator
    elif nav == "🧮 Calculator":
        st.markdown(f"<div class='section-title'>🧮 Product Calculator</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            load_existing = st.checkbox("📂 Load Existing Product?")
        
        if load_existing:
            products_df = get_all_products()
            if len(products_df) > 0:
                selected_sku = st.selectbox("Select Product", products_df['sku'].tolist())
                product = get_product_by_sku(selected_sku)
                is_update = True
            else:
                st.warning("No products found!")
                is_update = False
        else:
            product = None
            is_update = False
        
        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input("SKU", value=product['sku'] if product else "NH-001")
            product_name = st.text_input("Product Name", value=product['product_name'] if product else "Product")
            pack_size = st.number_input("Pack Size (g)", value=int(product['pack_size']) if product else 500)
            units_per_order = st.number_input("Units per Order", value=int(product['units_per_order']) if product else 1)
        
        with col2:
            purchase_cost = st.number_input("Purchase Cost", value=float(product['purchase_cost']) if product else 1200.0)
            inbound_freight = st.number_input("Inbound Freight", value=float(product['inbound_freight']) if product else 100.0)
            customs_duties = st.number_input("Customs/Duties", value=float(product['customs_duties']) if product else 150.0)
            wastage_pct = st.number_input("Wastage %", value=float(product['wastage_pct']) if product else 2.0)
        
        col1, col2 = st.columns(2)
        with col1:
            bag_cost = st.number_input("Bag Cost", value=float(product['bag_cost']) if product else 20.0)
            label_cost = st.number_input("Label Cost", value=float(product['label_cost']) if product else 5.0)
            box_cost = st.number_input("Box Cost", value=float(product['box_cost']) if product else 15.0)
            labor_cost = st.number_input("Labor Cost", value=float(product['labor_cost']) if product else 30.0)
        
        with col2:
            other_product_cost = st.number_input("Other Cost", value=float(product['other_product_cost']) if product else 0.0)
            delivery_cost = st.number_input("Delivery Cost", value=float(product['delivery_cost']) if product else 250.0)
            customer_delivery = st.number_input("Customer Delivery", value=float(product['customer_delivery']) if product else 150.0)
            gateway_fee_pct = st.number_input("Gateway Fee %", value=float(product['gateway_fee_pct']) if product else 2.5)
        
        col1, col2 = st.columns(2)
        with col1:
            platform_fee_pct = st.number_input("Platform Fee %", value=float(product['platform_fee_pct']) if product else 1.5)
            marketing_cost = st.number_input("Marketing Cost", value=float(product['marketing_cost']) if product else 50.0)
            return_rate_pct = st.number_input("Return Rate %", value=float(product['return_rate_pct']) if product else 5.0)
            rto_rate_pct = st.number_input("RTO Rate %", value=float(product['rto_rate_pct']) if product else 3.0)
        
        with col2:
            return_shipping = st.number_input("Return Shipping", value=float(product['return_shipping']) if product else 200.0)
            return_handling = st.number_input("Return Handling", value=float(product['return_handling']) if product else 50.0)
            target_margin_pct = st.number_input("Target Margin %", value=float(product['target_margin_pct']) if product else 30.0)
            discount_pct = st.number_input("Discount %", value=float(product['discount_pct']) if product else 10.0)
        
        data = {
            'sku': sku, 'product_name': product_name, 'pack_size': pack_size, 'units_per_order': units_per_order,
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
        st.markdown(f"<div class='section-title'>📊 Pricing Results</div>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div style='color: {SECONDARY}; font-size: 0.9rem; font-weight: 600;'>Base Cost</div>
                    <div style='font-size: 1.3rem; font-weight: bold; color: {PRIMARY};'>₨ {pricing['base_cost']:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div style='color: {SECONDARY}; font-size: 0.9rem; font-weight: 600;'>Total Cost</div>
                    <div style='font-size: 1.3rem; font-weight: bold; color: {PRIMARY};'>₨ {pricing['total_cost']:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div style='color: {SECONDARY}; font-size: 0.9rem; font-weight: 600;'>Expected RTO</div>
                    <div style='font-size: 1.3rem; font-weight: bold; color: {PRIMARY};'>₨ {pricing['expected_rto']:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <div style='color: {SECONDARY}; font-size: 0.9rem; font-weight: 600;'>Status</div>
                    <div style='font-size: 1.3rem; font-weight: bold; color: {PRIMARY};'>{pricing['status']}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="price-card price-recommended">
                    <div class="price-label">⭐ Recommended Price</div>
                    <div class="price-value">₨ {pricing['recommended_price']:,.0f}</div>
                    <div style='font-size: 0.9rem; color: #666;'>for {target_margin_pct:.0f}% margin</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="price-card price-discount">
                    <div class="price-label">💰 Discount Price</div>
                    <div class="price-value">₨ {pricing['discount_price']:,.0f}</div>
                    <div style='font-size: 0.9rem; color: #666;'>after {discount_pct:.0f}% discount</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="price-card price-profit">
                    <div class="price-label">📈 Expected Profit</div>
                    <div class="price-value">₨ {pricing['profit']:,.0f}</div>
                    <div style='font-size: 0.9rem; color: #666;'>Margin: {pricing['margin']:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Save Product" if not is_update else "✏️ Update Product", use_container_width=True):
                if not sku or not product_name:
                    st.error("❌ Please fill in all required fields!")
                else:
                    if is_update:
                        success, msg = update_product(sku, data, st.session_state.user_email)
                    else:
                        success, msg = save_product(data, st.session_state.user_email)
                    
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
        
        with col2:
            if st.button("🔄 Clear", use_container_width=True):
                st.rerun()
    
    # Product Master
    elif nav == "📊 Product Master":
        st.markdown(f"<div class='section-title'>📊 Product Master Database</div>", unsafe_allow_html=True)
        
        products_df = get_all_products()
        
        if len(products_df) == 0:
            st.info("📭 No products found. Create your first product in Calculator!")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                search = st.text_input("🔍 Search SKU or Name")
            with col2:
                sort_by = st.selectbox("Sort by", ["SKU", "Product Name", "Cost", "Created"])
            
            if search:
                products_df = products_df[
                    (products_df['sku'].str.contains(search, case=False, na=False)) |
                    (products_df['product_name'].str.contains(search, case=False, na=False))
                ]
            
            if sort_by == "SKU":
                products_df = products_df.sort_values('sku')
            elif sort_by == "Product Name":
                products_df = products_df.sort_values('product_name')
            elif sort_by == "Cost":
                products_df = products_df.sort_values('purchase_cost', ascending=False)
            else:
                products_df = products_df.sort_values('created_at', ascending=False)
            
            # Display all columns
            display_df = products_df[[
                'sku', 'product_name', 'pack_size', 'purchase_cost', 'inbound_freight', 'customs_duties',
                'bag_cost', 'label_cost', 'box_cost', 'labor_cost', 'delivery_cost', 'gateway_fee_pct',
                'platform_fee_pct', 'marketing_cost', 'return_rate_pct', 'rto_rate_pct', 'target_margin_pct',
                'discount_pct', 'created_at'
            ]].copy()
            
            display_df.columns = ['SKU', 'Product', 'Pack (g)', 'Cost', 'Freight', 'Duties', 'Bag', 'Label', 'Box',
                                 'Labor', 'Delivery', 'Gateway %', 'Platform %', 'Marketing', 'Return %', 'RTO %',
                                 'Margin %', 'Discount %', 'Created']
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown(f"<div class='section-title'>🔧 Actions</div>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                action_sku = st.selectbox("Select Product", products_df['sku'].tolist())
            
            with col2:
                action = st.selectbox("Action", ["Edit", "Delete"])
            
            with col3:
                if st.button("Execute", use_container_width=True):
                    if action == "Edit":
                        st.session_state.edit_sku = action_sku
                        st.info(f"Go to Calculator and check 'Load Existing Product' to edit {action_sku}")
                    elif action == "Delete":
                        success, msg = delete_product(action_sku, st.session_state.user_email)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
    
    # Business & Compensation
    elif nav == "💼 Business & Compensation":
        st.markdown(f"<div class='section-title'>💼 Monthly Business & Compensation</div>", unsafe_allow_html=True)
        
        if st.session_state.user_role != 'admin':
            st.error("❌ Only administrators can manage business records!")
        else:
            tab1, tab2 = st.tabs(["📝 Add/Update Month", "📊 View Records"])
            
            with tab1:
                st.markdown("**Enter Monthly Business Data**")
                
                col1, col2 = st.columns(2)
                with col1:
                    month_year = st.text_input("Month & Year (e.g., January 2024)", "January 2024")
                    sales = st.number_input("💰 Total Sales", min_value=0.0, value=20000.0)
                    product_cost = st.number_input("📦 Product Cost", min_value=0.0, value=12000.0)
                
                with col2:
                    business_expenses = st.number_input("🏢 Business Expenses", min_value=0.0, value=3000.0)
                    st.markdown("---")
                    st.markdown("**Compensation %** (Recommended: Employee 8%, Owner 12%, Reinvestment 6%)")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    employee_pct = st.number_input("👨‍💼 Employee %", min_value=0.0, value=8.0)
                with col2:
                    owner_pct = st.number_input("👑 Owner %", min_value=0.0, value=12.0)
                with col3:
                    reinvestment_pct = st.number_input("🔄 Reinvestment %", min_value=0.0, value=6.0)
                
                st.markdown("---")
                
                # Calculate
                comp = calculate_compensation(sales, product_cost, business_expenses, employee_pct, owner_pct, reinvestment_pct)
                
                st.markdown(f"<div class='section-title'>📊 Calculation Results</div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                        <div class="comp-card">
                            <div class="price-label">Actual Profit</div>
                            <div class="price-value">₨ {comp['actual_profit']:,.0f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="comp-card" style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border: 2px solid #4caf50;">
                            <div class="price-label">✅ Final Profit</div>
                            <div class="price-value">₨ {comp['final_profit']:,.0f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                        <div class="comp-card">
                            <div class="price-label">👨‍💼 Employee Comp</div>
                            <div class="price-value">₨ {comp['employee_comp']:,.0f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="comp-card">
                            <div class="price-label">👑 Owner Comp</div>
                            <div class="price-value">₨ {comp['owner_comp']:,.0f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="comp-card">
                            <div class="price-label">🔄 Reinvestment</div>
                            <div class="price-value">₨ {comp['reinvestment']:,.0f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                if st.button("💾 Save Monthly Record", use_container_width=True):
                    success, msg = save_monthly_business(month_year, sales, product_cost, business_expenses, 
                                                        employee_pct, owner_pct, reinvestment_pct)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
            
            with tab2:
                st.markdown("**Monthly Records History**")
                records_df = get_all_monthly_records()
                
                if len(records_df) == 0:
                    st.info("📭 No records found. Create your first record in 'Add/Update Month' tab!")
                else:
                    # Prepare display dataframe
                    display_records = []
                    for _, row in records_df.iterrows():
                        comp = calculate_compensation(row['sales'], row['product_cost'], row['business_expenses'],
                                                     row['employee_pct'], row['owner_pct'], row['reinvestment_pct'])
                        display_records.append({
                            'Month': row['month'],
                            'Sales': f"₨ {row['sales']:,.0f}",
                            'Product Cost': f"₨ {row['product_cost']:,.0f}",
                            'Expenses': f"₨ {row['business_expenses']:,.0f}",
                            'Actual Profit': f"₨ {comp['actual_profit']:,.0f}",
                            'Employee': f"₨ {comp['employee_comp']:,.0f}",
                            'Owner': f"₨ {comp['owner_comp']:,.0f}",
                            'Reinvestment': f"₨ {comp['reinvestment']:,.0f}",
                            'Final Profit': f"₨ {comp['final_profit']:,.0f}"
                        })
                    
                    display_df = pd.DataFrame(display_records)
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Settings
    elif nav == "⚙️ Settings":
        st.markdown(f"<div class='section-title'>⚙️ Settings</div>", unsafe_allow_html=True)
        
        if st.session_state.user_role != 'admin':
            st.error("❌ Only administrators can access settings!")
        else:
            settings = get_settings()
            
            tab1, tab2 = st.tabs(["📊 Product Settings", "💼 Compensation Settings"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    target_margin = st.number_input("Default Target Margin %", value=float(settings.get('target_margin', 30)), min_value=0.0)
                    gateway_fee = st.number_input("Default Gateway Fee %", value=float(settings.get('gateway_fee', 2.5)), min_value=0.0)
                    platform_fee = st.number_input("Default Platform Fee %", value=float(settings.get('platform_fee', 1.5)), min_value=0.0)
                
                with col2:
                    delivery_cost = st.number_input("Default Delivery Cost", value=float(settings.get('delivery_cost', 250)), min_value=0.0)
                    return_rate = st.number_input("Default Return Rate %", value=float(settings.get('return_rate', 5)), min_value=0.0)
                    rto_rate = st.number_input("Default RTO Rate %", value=float(settings.get('rto_rate', 3)), min_value=0.0)
                
                if st.button("💾 Save Product Settings", use_container_width=True):
                    update_settings({
                        'target_margin': target_margin,
                        'gateway_fee': gateway_fee,
                        'platform_fee': platform_fee,
                        'delivery_cost': delivery_cost,
                        'return_rate': return_rate,
                        'rto_rate': rto_rate
                    })
                    st.success("✅ Settings updated!")
            
            with tab2:
                st.info("💡 Set default compensation percentages")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    employee_pct = st.number_input("Employee Compensation %", value=float(settings.get('employee_pct', 8)), min_value=0.0)
                
                with col2:
                    owner_pct = st.number_input("Owner Compensation %", value=float(settings.get('owner_pct', 12)), min_value=0.0)
                
                with col3:
                    reinvestment_pct = st.number_input("Reinvestment %", value=float(settings.get('reinvestment_pct', 6)), min_value=0.0)
                
                if st.button("💾 Save Compensation Settings", use_container_width=True):
                    update_settings({
                        'employee_pct': employee_pct,
                        'owner_pct': owner_pct,
                        'reinvestment_pct': reinvestment_pct
                    })
                    st.success("✅ Settings updated!")
    
    # User Management
    elif nav == "👥 User Management":
        st.markdown(f"<div class='section-title'>👥 User Management</div>", unsafe_allow_html=True)
        
        if st.session_state.user_role != 'admin':
            st.error("❌ Only administrators can manage users!")
        else:
            tab1, tab2 = st.tabs(["👤 All Users", "➕ Add New User"])
            
            with tab1:
                users_df = get_all_users()
                if len(users_df) > 0:
                    active_users_df = users_df[users_df['is_active'] == 1]
                    st.markdown("**Active Users:**")
                    st.dataframe(active_users_df[['id', 'email', 'name', 'role', 'created_at']], use_container_width=True, hide_index=True)
                    
                    inactive_users_df = users_df[users_df['is_active'] == 0]
                    if len(inactive_users_df) > 0:
                        st.markdown("---")
                        st.markdown("**Inactive Users (Deleted):**")
                        st.dataframe(inactive_users_df[['id', 'email', 'name', 'role', 'created_at']], use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    st.markdown(f"<div class='section-title'>🔧 Actions</div>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        action_type = st.selectbox("Action", ["Deactivate (Soft Delete)", "Permanently Delete"])
                    
                    with col2:
                        action_user_id = st.selectbox("Select User", users_df['id'].tolist(), format_func=lambda x: users_df[users_df['id']==x]['email'].values[0])
                    
                    with col3:
                        if st.button("Execute", use_container_width=True):
                            user_email = users_df[users_df['id']==action_user_id]['email'].values[0]
                            
                            if action_type == "Deactivate (Soft Delete)":
                                success, msg = soft_delete_user(action_user_id, user_email)
                            else:
                                success, msg = permanently_delete_user(action_user_id, user_email)
                            
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                else:
                    st.info("No users found!")
            
            with tab2:
                st.markdown("**Create New User or Reactivate Deleted User**")
                st.info("💡 Tip: If user was deleted, use same email and new password to reactivate!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_email = st.text_input("Email")
                    new_name = st.text_input("Full Name")
                
                with col2:
                    new_role = st.selectbox("Role", ["user", "admin"])
                    new_password = st.text_input("Password", type="password")
                
                if st.button("➕ Create/Reactivate User", use_container_width=True):
                    if new_email and new_name and new_password:
                        success, msg = add_user(new_email, new_password, new_name, new_role)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error("❌ Please fill in all fields!")
    
    # Audit Log
    elif nav == "📋 Audit Log":
        st.markdown(f"<div class='section-title'>📋 Audit Log</div>", unsafe_allow_html=True)
        
        if st.session_state.user_role != 'admin':
            st.error("❌ Only administrators can view audit logs!")
        else:
            conn = sqlite3.connect('northern_harvest.db')
            audit_df = pd.read_sql_query('SELECT user_email, action, product_sku, details, timestamp FROM audit_log ORDER BY timestamp DESC LIMIT 100', conn)
            conn.close()
            
            if len(audit_df) > 0:
                audit_df.columns = ['User', 'Action', 'SKU', 'Details', 'Timestamp']
                st.dataframe(audit_df, use_container_width=True, hide_index=True)
            else:
                st.info("📭 No audit logs found!")
