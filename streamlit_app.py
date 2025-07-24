import streamlit as st
import folium
from folium.plugins import MarkerCluster
from math import radians, cos, sin, asin, sqrt

# استدعاء بيانات الأحياء
from cairo_zones import get_zone_class

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
    zone_factor = {"A": 1.0, "B": 1.5, "C": 2.0}
    Z = zone_factor.get(zone_class.upper(), 1.5)

    # نوع الطلب
    type_map = {"Delivery": 1.0, "Pickup": 1.2, "Linked": 0.8}
    T = type_map.get(order_type, 1.0)

    # المعادلة
    score = (distance * 1.0 + weight * 0.5 + parcels * 0.3) * Z * T
    return score

# ========================
# ديزاين التطبيق
# ========================
st.set_page_config(page_title="Eastern Union – Advanced Route Planner", layout="wide")

# خلفية داكنة
st.markdown("""
    <style>
    body {
        background-color: #000000;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# لوجو في النص
st.image("https://github.com/mrahmadsamy/eastern-union/blob/main/eastren_union_favicon-removebg-preview.png?raw=true", width=120)
st.markdown("<h1 style='text-align:center; color:white;'>Eastern Union – Advanced Route Planner</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:gray;'>الكفاءة... منهج وليست صدفة</h4>", unsafe_allow_html=True)
st.markdown("---")

# نقطة البداية
st.subheader("📍 نقطة البداية")
col1, col2 = st.columns(2)
with col1:
    start_lat = st.number_input("Latitude", value=30.0444, format="%.6f")
with col2:
    start_lon = st.number_input("Longitude", value=31.2357, format="%.6f")

# إدخال الطلبات
st.subheader("📦 الطلبات")
num_orders = st.number_input("كم طلب تريد إضافته؟", min_value=1, max_value=20, value=2)

orders = []
for i in range(num_orders):
    st.markdown(f"### 🏷️ الطلب رقم {i+1}")
    
    # اسم المنطقة
    area_name = st.text_input(f"📝 اسم المنطقة للطلب {i+1}", "الزمالك")
    zone_class = get_zone_class(area_name)
    st.write(f"📌 {area_name} → **Class {zone_class}**")

    # باقي البيانات
    lat = st.number_input(f"Latitude الطلب {i+1}", value=30.050000 + i*0.01, format="%.6f")
    lon = st.number_input(f"Longitude الطلب {i+1}", value=31.230000 + i*0.01, format="%.6f")
    weight = st.number_input(f"وزن الطرود (كجم) للطلب {i+1}", value=5.0)
    parcels = st.number_input(f"عدد الطرود للطلب {i+1}", value=2)
    order_type = st.selectbox(f"نوع الطلب {i+1}", ["Delivery", "Pickup", "Linked"], key=f"type_{i}")

    orders.append({
        "area": area_name,
        "lat": lat,
        "lon": lon,
        "weight": weight,
        "parcels": parcels,
        "zone": zone_class,
        "type": order_type
    })

# زر حساب المسار
if st.button("🚀 احسب المسار الأمثل"):
    for order in orders:
        dist = haversine(start_lat, start_lon, order["lat"], order["lon"])
        order["distance"] = dist
        order["score"] = calculate_score(dist, order["weight"], order["parcels"], order["zone"], order["type"])

    sorted_orders = sorted(orders, key=lambda x: x["score"])

    st.subheader("✅ الترتيب المقترح")
    for i, order in enumerate(sorted_orders, start=1):
        st.write(f"{i}. {order['area']} ({order['lat']:.6f}, {order['lon']:.6f}) | المسافة: {order['distance']:.2f} كم | Score: {order['score']:.2f} | Class {order['zone']}")

    # خريطة داكنة
    m = folium.Map(location=[start_lat, start_lon], zoom_start=12, tiles="CartoDB dark_matter")
    folium.Marker(
        [start_lat, start_lon],
        popup="🚩 Start",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)
    for i, order in enumerate(sorted_orders, start=1):
        folium.Marker(
            [order["lat"], order["lon"]],
            popup=f"#{i} - {order['type']} | Score: {order['score']:.2f}",
            tooltip=f"طلب #{i} ({order['zone']})",
            icon=folium.Icon(color="blue" if order["type"]=="Delivery" else "red")
        ).add_to(marker_cluster)

    route_coords = [(start_lat, start_lon)] + [(o["lat"], o["lon"]) for o in sorted_orders]
    folium.PolyLine(route_coords, color="orange", weight=3).add_to(m)

    st.subheader("🗺️ المسار على الخريطة")
    st.components.v1.html(m._repr_html_(), height=500)

    st.subheader("🗺️ المسار على الخريطة")
    st.components.v1.html(m._repr_html_(), height=500)
