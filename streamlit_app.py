import streamlit as st
import folium
from folium.plugins import MarkerCluster
from math import radians, cos, sin, asin, sqrt

# ========================
# نفس ألوان وخلفية صفحة اللوجين
# ========================
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0A192F, #050B14);
        color: #E0E6ED;
        font-family: 'Consolas', monospace;
    }
    .stApp {
        background: linear-gradient(135deg, #0A192F, #050B14);
        color: #A8F2D1;
    }
    h1, h2, h3, h4 {
        color: #A8F2D1 !important;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .stButton>button {
        background: #3AB0A2;
        color: #0A192F;
        font-weight: bold;
        border: none;
        border-radius: 4px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background: #2C9085;
    }
    .stNumberInput input {
        background: #0F2238 !important;
        color: #E0E6ED !important;
        border: 1px solid #2C3E5A !important;
    }
    .stSelectbox div {
        background: #0F2238 !important;
        color: #A8F2D1 !important;
    }
    .stSelectbox>div>div {
        background-color: #0F2238 !important;
        color: #A8F2D1 !important;
    }
    .stMarkdown, .stText {
        color: #A8F2D1 !important;
    }
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ========================
# دالة حساب المسافة
# ========================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
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
# واجهة البرنامج – نفس الطابع الأمني
# ========================
st.set_page_config(page_title="Eastern Union Secure Routing", layout="wide")

st.markdown("<h1 style='text-align:center;'>EASTERN UNION SECURE ROUTE SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#5C6C8A;'>CLASSIFIED ACCESS ONLY - MISSION PLANNING INTERFACE</p>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #3AB0A2;'>", unsafe_allow_html=True)

# نقطة البداية
st.subheader("Origin Coordinates")
start_lat = st.number_input("Latitude", value=30.0444, format="%.6f")
start_lon = st.number_input("Longitude", value=31.235700, format="%.6f")

# إدخال الطلبات
st.subheader("Mission Points")

num_orders = st.number_input("How many mission points?", min_value=1, max_value=50, value=3)

orders = []
for i in range(num_orders):
    st.markdown(f"### Mission #{i+1}")
    lat = st.number_input(f"Latitude for point {i+1}", value=30.050000 + i*0.010000, format="%.6f")
    lon = st.number_input(f"Longitude for point {i+1}", value=31.230000 + i*0.010000, format="%.6f")
    weight = st.number_input(f"Cargo weight (kg) for point {i+1}", value=5.0)
    parcels = st.number_input(f"Parcels count for point {i+1}", value=2)
    zone_class = st.selectbox(f"Zone class for point {i+1}", ["A", "B", "C"], key=f"zone_{i}")
    order_type = st.selectbox(f"Mission type for point {i+1}", ["Delivery", "Pickup", "Linked"], key=f"type_{i}")
    
    orders.append({
        "lat": lat,
        "lon": lon,
        "weight": weight,
        "parcels": parcels,
        "zone": zone_class,
        "type": order_type
    })

# زر الحساب
if st.button("Execute Route Calculation"):
    for order in orders:
        dist = haversine(start_lat, start_lon, order["lat"], order["lon"])
        order["distance"] = dist
        order["score"] = calculate_score(dist, order["weight"], order["parcels"], order["zone"], order["type"])
    
    sorted_orders = sorted(orders, key=lambda x: x["score"])

    st.subheader("Mission Execution Order")
    for i, order in enumerate(sorted_orders, start=1):
        st.write(
            f"▣ {i}. ({order['lat']:.6f}, {order['lon']:.6f}) | Distance: {order['distance']:.2f} km | Priority Score: {order['score']:.2f}"
        )

    m = folium.Map(location=[start_lat, start_lon], zoom_start=12, tiles="CartoDB dark_matter")
    folium.Marker(
        [start_lat, start_lon],
        popup="HQ - START",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)
    for i, order in enumerate(sorted_orders, start=1):
        folium.Marker(
            [order["lat"], order["lon"]],
            popup=f"Mission #{i} | Score: {order['score']:.2f}",
            tooltip=f"Mission #{i}",
            icon=folium.Icon(color="blue" if order["type"]=="Delivery" else "red")
        ).add_to(marker_cluster)

    route_coords = [(start_lat, start_lon)] + [(o["lat"], o["lon"]) for o in sorted_orders]
    folium.PolyLine(route_coords, color="#3AB0A2", weight=3).add_to(m)

    st.subheader("Satellite Map View")
    st.components.v1.html(m._repr_html_(), height=500)

    st.markdown("<hr style='border:1px solid #3AB0A2;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#5C6C8A;'>Mission plan generated - Eastern Union Secure Network</p>", unsafe_allow_html=True)
