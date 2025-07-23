import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Eastern Union Optimizer", layout="wide")

st.title("🚚 Eastern Union Logistics Optimizer")
st.write("خوارزمية التفعيل الشرطي والتقييم الديناميكي لإدارة الطلبات اللوجستية المعقدة")

# ================================
# تكيف الأوزان حسب المركبة
VEHICLE_WEIGHTS = {
    "Motorbike": {"Wz": 0.8, "Wd": 1.0, "Ws": 1.5, "Wb": 1.2, "Wu": 1.0},
    "Van": {"Wz": 1.2, "Wd": 1.0, "Ws": 0.8, "Wb": 0.6, "Wu": 1.0},
    "Truck": {"Wz": 1.5, "Wd": 1.5, "Ws": 0.2, "Wb": 0.0, "Wu": 0.5}
}

# ================================
def calculate_score(zone, distance, size, bulk, urgency, order_type, weights):
    Wz, Wd, Ws, Wb, Wu = weights["Wz"], weights["Wd"], weights["Ws"], weights["Wb"], weights["Wu"]
    base_score = (zone * Wz) + (distance * Wd) + (size * Ws) + ((5 - bulk) * Wb) + ((10 - urgency) * Wu)
    if order_type == "Pickup":
        base_score += 5  # Pickup له أولوية لأنه بيفتح Linked
    return round(base_score, 2)

# ================================
st.sidebar.header("⚙️ إعدادات الخطة")

vehicle_type = st.sidebar.selectbox("نوع المركبة", ["Motorbike", "Van", "Truck"])
weights = VEHICLE_WEIGHTS[vehicle_type]

start_lat = st.sidebar.number_input("نقطة البداية - Latitude", value=30.0444)
start_lon = st.sidebar.number_input("نقطة البداية - Longitude", value=31.2357)

if "orders" not in st.session_state:
    st.session_state.orders = []

# ================================
st.sidebar.subheader("➕ إضافة طلب")
order_type = st.sidebar.selectbox("نوع الطلب", ["Delivery", "Pickup", "Linked Delivery"])
zone = st.sidebar.slider("صعوبة المنطقة Z", 1, 3, 2)
distance = st.sidebar.slider("المسافة (كم)", 1, 50, 10)
size = st.sidebar.slider("حجم/وزن الطرد", 1, 20, 5)
bulk = st.sidebar.slider("عدد الطرود لنفس العميل", 1, 5, 1)
urgency = st.sidebar.slider("درجة الاستعجال", 1, 10, 5)
latitude = st.sidebar.number_input("Latitude للطلب", value=start_lat)
longitude = st.sidebar.number_input("Longitude للطلب", value=start_lon)

if st.sidebar.button("✅ إضافة الطلب"):
    score = calculate_score(zone, distance, size, bulk, urgency, order_type, weights)
    st.session_state.orders.append({
        "type": order_type,
        "zone": zone,
        "distance": distance,
        "size": size,
        "bulk": bulk,
        "urgency": urgency,
        "score": score,
        "lat": latitude,
        "lon": longitude
    })
    st.sidebar.success("تم إضافة الطلب ✅")

# ================================
st.subheader("📋 خطة الطلبات")
if st.session_state.orders:
    sorted_orders = sorted(st.session_state.orders, key=lambda x: x["score"], reverse=True)
    st.write("ترتيب الطلبات حسب الأولوية:")
    st.table(sorted_orders)

    # ================================
    # عرض الخريطة
    st.subheader("🗺️ الخريطة - الطلبات مرتبة")
    m = folium.Map(location=[start_lat, start_lon], zoom_start=11)
    folium.Marker([start_lat, start_lon], popup="Start Point", icon=folium.Icon(color="green")).add_to(m)

    for idx, order in enumerate(sorted_orders, start=1):
        folium.Marker(
            [order["lat"], order["lon"]],
            popup=f"{idx}. {order['type']} | Score {order['score']}",
            icon=folium.Icon(color="blue" if order["type"] == "Delivery" else "red")
        ).add_to(m)

    st_folium(m, width=900, height=500)

else:
    st.warning("⚠️ لم يتم إضافة أي طلبات بعد")

