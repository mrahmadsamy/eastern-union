import streamlit as st
import folium
from folium.plugins import MarkerCluster
from math import radians, cos, sin, asin, sqrt

# ========================
# 🎨 إضافة ستايل شاشات المخابرات (CIA)
# ========================
st.markdown("""
    <style>
    body {
        background-color: #0a0a0a;
        color: #00ff9f;
        font-family: 'Courier New', monospace;
    }
    .stApp {
        background: linear-gradient(135deg, #000000 60%, #0d0d0d);
        color: #00ff9f;
    }
    h1, h2, h3, h4 {
        color: #00ffaa !important;
        text-shadow: 0 0 10px #00ffaa;
    }
    .stButton>button {
        background: #111;
        color: #00ff9f;
        border: 1px solid #00ff9f;
        font-weight: bold;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background: #00ff9f;
        color: black;
    }
    .css-1q8dd3e, .css-1d391kg, .css-ffhzg2 {
        color: #00ff9f !important;
    }
    .stNumberInput input {
        background: #111 !important;
        color: #00ff9f !important;
        border: 1px solid #00ff9f !important;
    }
    .stSelectbox div {
        background: #111 !important;
        color: #00ff9f !important;
    }
    .reportview-container .main footer {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# ========================
# دالة حساب المسافة بين نقطتين بالإحداثيات
# ========================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # نصف قطر الأرض بالكيلومتر
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# ========================
# دالة حساب الـ Score
# ========================
def calculate_score(distance, weight, parcels, zone_class, order_type):
    zone_map = {"A": 1.0, "B": 1.5, "C": 2.0}
    Z = zone_map.get(zone_class.upper(), 1.5)
    type_map = {"Delivery": 1.0, "Pickup": 1.2, "Linked": 0.8}
    T = type_map.get(order_type, 1.0)
    score = (distance * 1.0 + weight * 0.5 + parcels * 0.3) * Z * T
    return score

# ========================
# واجهة البرنامج
# ========================
st.set_page_config(page_title="EASTERN UNION SECURE ROUTE SYSTEM", layout="wide")

# شاشة تحذيرية في البداية
st.markdown("<h1 style='text-align:center;'>⚠️ CLASSIFIED ACCESS ⚠️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ff4444;'>UNAUTHORIZED ACCESS WILL BE TRACKED</p>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #00ffaa;'>", unsafe_allow_html=True)

st.title("🛰️ EASTERN UNION | Secure Route Planner")

# نقطة البداية
st.subheader("📍 نقطة البداية (ORIGIN)")
start_lat = st.number_input("Latitude (مثال: 30.0444)", value=30.0444, format="%.6f")
start_lon = st.number_input("Longitude (مثال: 31.2357)", value=31.235700, format="%.6f")

# إدخال الطلبات
st.subheader("📦 أدخل بيانات الطلبات (MISSION POINTS)")

num_orders = st.number_input("كم نقطة/طلب تريد إضافته؟", min_value=1, max_value=50, value=3)

orders = []
for i in range(num_orders):
    st.markdown(f"### 🗂️ MISSION #{i+1}")
    lat = st.number_input(f"Latitude للنقطة {i+1}", value=30.050000 + i*0.010000, format="%.6f")
    lon = st.number_input(f"Longitude للنقطة {i+1}", value=31.230000 + i*0.010000, format="%.6f")
    weight = st.number_input(f"الوزن (كجم) للنقطة {i+1}", value=5.0)
    parcels = st.number_input(f"عدد الطرود للنقطة {i+1}", value=2)
    zone_class = st.selectbox(f"كلاس الحي للنقطة {i+1}", ["A", "B", "C"], key=f"zone_{i}")
    order_type = st.selectbox(f"نوع العملية {i+1}", ["Delivery", "Pickup", "Linked"], key=f"type_{i}")
    
    orders.append({
        "lat": lat,
        "lon": lon,
        "weight": weight,
        "parcels": parcels,
        "zone": zone_class,
        "type": order_type
    })

# زر الحساب
if st.button("🚀 EXECUTE ROUTE CALCULATION"):
    # حساب المسافات و الـ Score
    for order in orders:
        dist = haversine(start_lat, start_lon, order["lat"], order["lon"])
        order["distance"] = dist
        order["score"] = calculate_score(dist, order["weight"], order["parcels"], order["zone"], order["type"])
    
    # ترتيب حسب الـ Score
    sorted_orders = sorted(orders, key=lambda x: x["score"])

    # عرض النتائج
    st.subheader("✅ MISSION ORDER SEQUENCE")
    for i, order in enumerate(sorted_orders, start=1):
        st.write(
            f"**{i}.** ({order['lat']:.6f}, {order['lon']:.6f}) | Distance: {order['distance']:.2f} km | Priority Score: {order['score']:.2f}"
        )

    # رسم الخريطة
    m = folium.Map(location=[start_lat, start_lon], zoom_start=12)
    folium.Marker(
        [start_lat, start_lon],
        popup="🚩 HQ - START",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)
    for i, order in enumerate(sorted_orders, start=1):
        folium.Marker(
            [order["lat"], order["lon"]],
            popup=f"#{i} - {order['type']} | Score: {order['score']:.2f}",
            tooltip=f"Mission #{i}",
            icon=folium.Icon(color="blue" if order["type"]=="Delivery" else "red")
        ).add_to(marker_cluster)

    route_coords = [(start_lat, start_lon)] + [(o["lat"], o["lon"]) for o in sorted_orders]
    folium.PolyLine(route_coords, color="orange", weight=3).add_to(m)

    st.subheader("🗺️ LIVE SATELLITE VIEW")
    st.components.v1.html(m._repr_html_(), height=500)

    st.markdown("<hr style='border:1px solid #ff4444;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#ff4444;'>END OF SECURE ROUTE CALCULATION</p>", unsafe_allow_html=True)
