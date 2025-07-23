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

st.title("🚚 Dynamic Route Planner with Bulk Coordinates Input")

# نقطة البداية
st.subheader("📍 نقطة البداية")
start_lat = st.number_input("Latitude (مثال: 30.0444)", value=30.0444)
start_lon = st.number_input("Longitude (مثال: 31.2357)", value=31.2357)

# إدخال الإحداثيات كوبي/بيست
st.subheader("📋 الصق الإحداثيات هنا (كل نقطة في سطر)")
coords_text = st.text_area("مثال:\n30.018745,31.230984\n30.056912,31.291231\n30.002381,31.195678")

bulk_coords = []
if coords_text.strip():
    for line in coords_text.strip().split("\n"):
        try:
            lat_str, lon_str = line.strip().split(",")
            lat, lon = float(lat_str), float(lon_str)
            bulk_coords.append((lat, lon))
        except:
            st.error(f"❌ خطأ في الصيغة: {line}")

# إدخال الطلبات
orders = []
if bulk_coords:
    st.success(f"✅ تم قراءة {len(bulk_coords)} نقطة بنجاح")
    for i, (lat, lon) in enumerate(bulk_coords):
        st.markdown(f"### الطلب رقم {i+1} ({lat}, {lon})")
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

if st.button("🚀 احسب المسار الأمثل") and orders:
    # احسب المسافات و الـ Score
    for order in orders:
        dist = haversine(start_lat, start_lon, order["lat"], order["lon"])
        order["distance"] = dist
        order["score"] = calculate_score(dist, order["weight"], order["parcels"], order["zone"], order["type"])
    
    # رتب الطلبات حسب الـ Score
    sorted_orders = sorted(orders, key=lambda x: x["score"])

    # اعرض الترتيب
    st.subheader("✅ الترتيب المقترح")
    for i, order in enumerate(sorted_orders, start=1):
        st.write(f"{i}. ({order['lat']}, {order['lon']}) | المسافة: {order['distance']:.2f} كم | Score: {order['score']:.2f}")

    # ارسم الخريطة
    m = folium.Map(location=[start_lat, start_lon], zoom_start=12)
    folium.Marker([start_lat, start_lon], popup="🚩 Start", icon=folium.Icon(color="green")).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)
    for i, order in enumerate(sorted_orders, start=1):
        folium.Marker(
            [order["lat"], order["lon"]],
            popup=f"#{i} - {order['type']} | {order['score']:.2f}",
            icon=folium.Icon(color="blue" if order["type"]=="Delivery" else "red")
        ).add_to(marker_cluster)

    # وصل النقاط بخط
    route_coords = [(start_lat, start_lon)] + [(o["lat"], o["lon"]) for o in sorted_orders]
    folium.PolyLine(route_coords, color="orange", weight=3).add_to(m)

    st.subheader("🗺️ المسار على الخريطة")
    st.components.v1.html(m._repr_html_(), height=500)
