import streamlit as st
import folium
from folium.plugins import MarkerCluster
from math import radians, cos, sin, asin, sqrt

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
    # تحويل كلاس الحي إلى رقم
    zone_map = {"A": 1.0, "B": 1.5, "C": 2.0}
    Z = zone_map.get(zone_class.upper(), 1.5)
    
    # نوع الطلب
    type_map = {"Delivery": 1.0, "Pickup": 1.2, "Linked": 0.8}
    T = type_map.get(order_type, 1.0)

    # المعادلة
    score = (distance * 1.0 + weight * 0.5 + parcels * 0.3) * Z * T
    return score

# ========================
# واجهة Streamlit + تصميم Google X Style
# ========================
st.set_page_config(page_title="Eastern Union Advanced Route Planner", layout="centered")

# إضافة ستايل مخصص
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0A192F, #102840);
        color: #E0E6ED;
    }
    .main {
        background: transparent;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }
    .title-container {
        text-align: center;
        margin-bottom: 30px;
    }
    .title-container img {
        width: 90px;
        filter: drop-shadow(0px 0px 6px rgba(0, 255, 200, 0.2));
    }
    .title-container h1 {
        color: #A8F2D1;
        font-family: 'Consolas', monospace;
        letter-spacing: 2px;
        margin-top: 10px;
    }
    .stTextInput > div > div > input, .stNumberInput input, .stSelectbox div {
        background-color: #102840 !important;
        color: #E0E6ED !important;
        border: 1px solid #3AB0A2;
        border-radius: 6px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #3AB0A2, #298F8B);
        color: #0A192F;
        font-weight: bold;
        padding: 12px;
        border-radius: 6px;
        border: none;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #4DD4C2, #3AB0A2);
        box-shadow: 0px 0px 10px rgba(0,255,200,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ========================
# اللوجو والعنوان
# ========================
with st.container():
    st.markdown("""
    <div class="title-container">
        <img src="https://raw.githubusercontent.com/mrahmadsamy/eastern-union/refs/heads/main/eastren_union_favicon-removebg-preview.png" alt="Eastern Union Logo">
        <h1>Eastern Union – Advanced Route Planner</h1>
        <p style="color:#B0CDE5;font-size:14px;">الكفاءة... منهج وليست صدفة</p>
    </div>
    """, unsafe_allow_html=True)

# ========================
# نقطة البداية
# ========================
with st.container():
    st.subheader("📍 نقطة البداية")
    col1, col2 = st.columns(2)
    with col1:
        start_lat = st.number_input("Latitude", value=30.044400, format="%.6f")
    with col2:
        start_lon = st.number_input("Longitude", value=31.235700, format="%.6f")

# ========================
# إدخال الطلبات بشكل مريح
# ========================
st.subheader("📦 الطلبات")

num_orders = st.slider("كم طلب تريد إضافته؟", min_value=1, max_value=20, value=3)

orders = []
for i in range(num_orders):
    with st.expander(f"📌 الطلب رقم {i+1}", expanded=(i==0)):
        c1, c2 = st.columns(2)
        with c1:
            lat = st.number_input(f"Latitude الطلب {i+1}", value=30.050000 + i*0.010000, format="%.6f")
            weight = st.number_input(f"وزن الطرود (كجم)", value=5.0)
            parcels = st.number_input(f"عدد الطرود", value=2)
        with c2:
            lon = st.number_input(f"Longitude الطلب {i+1}", value=31.230000 + i*0.010000, format="%.6f")
            zone_class = st.selectbox(f"كلاس الحي", ["A", "B", "C"], key=f"zone_{i}")
            order_type = st.selectbox(f"نوع الطلب", ["Delivery", "Pickup", "Linked"], key=f"type_{i}")
        orders.append({
            "lat": lat,
            "lon": lon,
            "weight": weight,
            "parcels": parcels,
            "zone": zone_class,
            "type": order_type
        })

# ========================
# زر الحساب + عرض النتيجة
# ========================
if st.button("🚀 احسب المسار الأمثل"):
    # احسب المسافات و Score
    for order in orders:
        dist = haversine(start_lat, start_lon, order["lat"], order["lon"])
        order["distance"] = dist
        order["score"] = calculate_score(dist, order["weight"], order["parcels"], order["zone"], order["type"])
    
    # رتب الطلبات
    sorted_orders = sorted(orders, key=lambda x: x["score"])

    # اعرض الترتيب
    st.subheader("✅ الترتيب المقترح")
    for i, order in enumerate(sorted_orders, start=1):
        st.write(
            f"**{i}.** ({order['lat']:.6f}, {order['lon']:.6f}) | المسافة: {order['distance']:.2f} كم | Score: {order['score']:.2f}"
        )

    # الخريطة
    m = folium.Map(location=[start_lat, start_lon], zoom_start=12)
    folium.Marker([start_lat, start_lon], popup="🚩 Start", icon=folium.Icon(color="green", icon="play")).add_to(m)
    marker_cluster = MarkerCluster().add_to(m)

    for i, order in enumerate(sorted_orders, start=1):
        folium.Marker(
            [order["lat"], order["lon"]],
            popup=f"#{i} - {order['type']} | Score: {order['score']:.2f}",
            tooltip=f"طلب #{i}",
            icon=folium.Icon(color="blue" if order["type"]=="Delivery" else "red")
        ).add_to(marker_cluster)

    route_coords = [(start_lat, start_lon)] + [(o["lat"], o["lon"]) for o in sorted_orders]
    folium.PolyLine(route_coords, color="orange", weight=3).add_to(m)

    st.subheader("🗺️ المسار على الخريطة")
    st.components.v1.html(m._repr_html_(), height=500)
