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
    zone_map = {"A": 1.0, "B": 1.5, "C": 2.0}
    Z = zone_map.get(zone_class.upper(), 1.5)
    type_map = {"Delivery": 1.0, "Pickup": 1.2, "Linked": 0.8}
    T = type_map.get(order_type, 1.0)
    score = (distance * 1.0 + weight * 0.5 + parcels * 0.3) * Z * T
    return score

# ========================
# واجهة التطبيق
# ========================
st.set_page_config(page_title="Eastern Union Route Planner", layout="wide")
st.title("🚚 Dynamic Route Planner with Custom Scoring")

# نقطة البداية
st.subheader("📍 نقطة البداية")
start_lat = st.number_input("Latitude (مثال: 30.044400)", value=30.044400, format="%.6f")
start_lon = st.number_input("Longitude (مثال: 31.235700)", value=31.235700, format="%.6f")

# اختيار طريقة إدخال الطلبات
st.subheader("📦 أدخل بيانات الطلبات")
mode = st.radio("كيف تريد إدخال الإحداثيات؟", ["يدوي", "Paste للإحداثيات دفعة واحدة"])

orders = []

if mode == "يدوي":
    num_orders = st.number_input("كم طلب تريد إضافته؟", min_value=1, max_value=50, value=3)

    for i in range(num_orders):
        st.markdown(f"### الطلب رقم {i+1}")
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

else:
    st.info("📋 الصق هنا الإحداثيات بالصيغة: `lat,lon,weight,parcels,zone,type` لكل سطر")
    coords_text = st.text_area("الصق هنا الإحداثيات")

    if coords_text.strip():
        for line in coords_text.strip().split("\n"):
            parts = line.split(",")
            if len(parts) == 6:
                lat, lon, weight, parcels, zone_class, order_type = parts
                orders.append({
                    "lat": float(lat.strip()),
                    "lon": float(lon.strip()),
                    "weight": float(weight.strip()),
                    "parcels": int(parcels.strip()),
                    "zone": zone_class.strip(),
                    "type": order_type.strip()
                })

if st.button("🚀 احسب المسار الأمثل") and orders:
    # احسب المسافات والـ Score
    for order in orders:
        dist = haversine(start_lat, start_lon, order["lat"], order["lon"])
        order["distance"] = dist
        order["score"] = calculate_score(dist, order["weight"], order["parcels"], order["zone"], order["type"])
    
    # رتب الطلبات حسب Score
    sorted_orders = sorted(orders, key=lambda x: x["score"])

    # عرض النتائج
    st.subheader("✅ الترتيب المقترح")
    for i, order in enumerate(sorted_orders, start=1):
        st.write(f"{i}. ({order['lat']:.6f}, {order['lon']:.6f}) | المسافة: {order['distance']:.2f} كم | Score: {order['score']:.2f}")

    # رسم الخريطة
    m = folium.Map(location=[start_lat, start_lon], zoom_start=12)
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
            tooltip=f"طلب #{i}",
            icon=folium.Icon(color="blue" if order["type"]=="Delivery" else "red")
        ).add_to(marker_cluster)

    route_coords = [(start_lat, start_lon)] + [(o["lat"], o["lon"]) for o in sorted_orders]
    folium.PolyLine(route_coords, color="orange", weight=3).add_to(m)

    st.subheader("🗺️ المسار على الخريطة")
    st.components.v1.html(m._repr_html_(), height=500)
