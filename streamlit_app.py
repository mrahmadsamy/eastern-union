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
    zone_map = {"A": 1.0, "B": 1.5, "C": 2.0}   # كلاس الحي
    Z = zone_map.get(zone_class.upper(), 1.5)

    type_map = {"Delivery": 1.0, "Pickup": 1.2, "Linked": 0.8}  # نوع الطلب
    T = type_map.get(order_type, 1.0)

    # المعادلة
    score = (distance * 1.0 + weight * 0.5 + parcels * 0.3) * Z * T
    return score

# ========================
# واجهة التطبيق الرسمية
# ========================
st.set_page_config(page_title="Eastern Union Route Planner", layout="wide")

# خلفية رسمية بدون إيموجي
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #9fd3f4, #0b1d3a);
        color: #e0e6ed;
    }
    .stButton>button {
        background: linear-gradient(90deg, #1f6fb2, #0b2d55);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-weight: bold;
    }
    .stNumberInput label, .stSelectbox label {
        font-weight: 500;
        color: #cdd9e5;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Eastern Union • Dynamic Route Planner")

# نقطة البداية
st.subheader("نقطة البداية")
start_lat = st.number_input("Latitude", value=30.0444, format="%.6f")
start_lon = st.number_input("Longitude", value=31.235700, format="%.6f")

# إدخال الطلبات
st.subheader("إدخال بيانات الطلبات")
num_orders = st.number_input("كم طلب تريد إضافته؟", min_value=1, max_value=50, value=3)

orders = []
for i in range(num_orders):
    st.markdown(f"#### الطلب رقم {i+1}")
    lat = st.number_input(f"Latitude الطلب {i+1}", value=30.050000 + i*0.010000, format="%.6f")
    lon = st.number_input(f"Longitude الطلب {i+1}", value=31.230000 + i*0.010000, format="%.6f")
    weight = st.number_input(f"الوزن (كجم) للطلب {i+1}", value=5.0)
    parcels = st.number_input(f"عدد الطرود للطلب {i+1}", value=2)
    zone_class = st.selectbox(f"كلاس الحي للطلب {i+1}", ["A", "B", "C"], key=f"zone_{i}")
    order_type = st.selectbox(f"نوع الطلب {i+1}", ["Delivery", "Pickup", "Linked"], key=f"type_{i}")

    orders.append({
        "lat": lat,
        "lon": lon,
        "weight": weight,
        "parcels": parcels,
        "zone": zone_class,
        "type": order_type
    })

if st.button("احسب المسار الأمثل"):
    # احسب المسافات والـ Score
    for order in orders:
        dist = haversine(start_lat, start_lon, order["lat"], order["lon"])
        order["distance"] = dist
        order["score"] = calculate_score(dist, order["weight"], order["parcels"], order["zone"], order["type"])

    # رتب الطلبات حسب الـ Score
    sorted_orders = sorted(orders, key=lambda x: x["score"])

    st.subheader("الترتيب المقترح")
    for i, order in enumerate(sorted_orders, start=1):
        st.write(
            f"{i}. ({order['lat']:.6f}, {order['lon']:.6f}) | المسافة: {order['distance']:.2f} كم | Score: {order['score']:.2f}"
        )

    # رسم الخريطة
    m = folium.Map(location=[start_lat, start_lon], zoom_start=12)
    folium.Marker([start_lat, start_lon], popup="Start", icon=folium.Icon(color="green")).add_to(m)

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

    st.subheader("المسار على الخريطة")
    st.components.v1.html(m._repr_html_(), height=500)
