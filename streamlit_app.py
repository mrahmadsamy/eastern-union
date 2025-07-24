import streamlit as st
import folium
from folium.plugins import MarkerCluster
from math import radians, cos, sin, asin, sqrt

# ========================
# إعداد الصفحة
# ========================
st.set_page_config(page_title="Eastern Union – Advanced Route Planner", layout="centered")

# ========================
# تنسيق CSS أبيض × أسود
# ========================
st.markdown("""
    <style>
    body {
        background-color: #000000;
        color: #FFFFFF;
        font-family: 'Consolas', monospace;
    }
    .main {
        background-color: #000000;
    }
    .stNumberInput > div > div > input {
        background-color: #111;
        color: #fff;
        border: 1px solid #444;
    }
    .stSelectbox > div > div {
        background-color: #111 !important;
        color: #fff !important;
    }
    .stButton>button {
        background-color: #fff;
        color: #000;
        border-radius: 4px;
        font-weight: bold;
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

    return (distance * 1.0 + weight * 0.5 + parcels * 0.3) * Z * T

# ========================
# الواجهة الرئيسية
# ========================
st.markdown("<h1 style='text-align:center;'>Eastern Union – Advanced Route Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:14px;'>الكفاءة... منهج وليست صدفة</p>", unsafe_allow_html=True)
st.divider()

# ========================
# نقطة البداية
# ========================
st.subheader("📍 نقطة البداية")
col1, col2 = st.columns(2)
with col1:
    start_lat = st.number_input("Latitude", value=30.044400, format="%.6f")
with col2:
    start_lon = st.number_input("Longitude", value=31.235700, format="%.6f")

st.divider()

# ========================
# الطلبات
# ========================
st.subheader("📦 الطلبات")
num_orders = st.number_input("كم طلب تريد إضافته؟", min_value=1, max_value=20, value=3)

orders = []
for i in range(int(num_orders)):
    st.markdown(f"<h4>📌 الطلب رقم {i+1}</h4>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        lat = st.number_input(f"Latitude الطلب {i+1}", value=30.05 + i*0.01, format="%.6f", key=f"lat_{i}")
        weight = st.number_input("وزن الطرود (كجم)", value=5.0, key=f"weight_{i}")
        parcels = st.number_input("عدد الطرود", value=2, key=f"parcels_{i}")
    with c2:
        lon = st.number_input(f"Longitude الطلب {i+1}", value=31.23 + i*0.01, format="%.6f", key=f"lon_{i}")
        zone_class = st.selectbox("كلاس الحي", ["A", "B", "C"], key=f"zone_{i}")
        order_type = st.selectbox("نوع الطلب", ["Delivery", "Pickup", "Linked"], key=f"type_{i}")

    orders.append({
        "lat": lat,
        "lon": lon,
        "weight": weight,
        "parcels": parcels,
        "zone": zone_class,
        "type": order_type
    })

st.divider()

# ========================
# زر الحساب
# ========================
if st.button("🚀 حساب المسار الأمثل"):
    # حساب المسافة والسكور
    for order in orders:
        dist = haversine(start_lat, start_lon, order["lat"], order["lon"])
        order["distance"] = dist
        order["score"] = calculate_score(dist, order["weight"], order["parcels"], order["zone"], order["type"])
    
    # ترتيب الطلبات حسب السكور
    sorted_orders = sorted(orders, key=lambda x: x["score"])

    st.subheader("✅ الترتيب المقترح")
    for idx, order in enumerate(sorted_orders, start=1):
        st.write(f"{idx}. ({order['lat']:.6f}, {order['lon']:.6f}) | المسافة: {order['distance']:.2f} كم | Score: {order['score']:.2f}")

    # رسم الخريطة
    m = folium.Map(location=[start_lat, start_lon], zoom_start=12, tiles="CartoDB dark_matter")
    folium.Marker([start_lat, start_lon], popup="🚩 Start", icon=folium.Icon(color="green", icon="play")).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)
    for idx, order in enumerate(sorted_orders, start=1):
        folium.Marker(
            [order["lat"], order["lon"]],
            popup=f"#{idx} - {order['type']} | Score: {order['score']:.2f}",
            tooltip=f"طلب #{idx}",
            icon=folium.Icon(color="blue" if order["type"]=="Delivery" else "red")
        ).add_to(marker_cluster)

    # خط المسار
    route_coords = [(start_lat, start_lon)] + [(o["lat"], o["lon"]) for o in sorted_orders]
    folium.PolyLine(route_coords, color="orange", weight=3).add_to(m)

    st.subheader("🗺️ المسار على الخريطة")
    st.components.v1.html(m._repr_html_(), height=500)
