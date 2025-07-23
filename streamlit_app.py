import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests

st.set_page_config(page_title="Eastern Union Advanced Route Optimizer", layout="wide")

st.title("🚚 Eastern Union – Dynamic Smart Routing")
st.write("النظام يحسب أفضل ترتيب للطلبات بناءً على المسافة + الوزن + عدد الطرود + صعوبة المنطقة + نوع الطلب")

# ========= إعداد Geocoder =========
geolocator = Nominatim(user_agent="eastern_union_optimizer")

def get_coords(address):
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

# ========= نقطة البداية =========
st.sidebar.header("🏢 نقطة البداية")
start_address = st.sidebar.text_input("أدخل عنوان نقطة البداية", "ميدان التحرير، القاهرة")
start_coords = get_coords(start_address) if start_address else None

# ========= بيانات الطلبات =========
if "orders" not in st.session_state:
    st.session_state.orders = []

st.sidebar.subheader("➕ إضافة طلب جديد")
address = st.sidebar.text_input("📍 عنوان الطلب")
weight = st.sidebar.number_input("⚖️ الوزن الإجمالي (كجم)", min_value=0.1, step=0.5)
num_packages = st.sidebar.number_input("📦 عدد الطرود", min_value=1, step=1)
order_type = st.sidebar.selectbox("🛠 نوع الطلب", ["Delivery", "Pickup", "Linked Delivery"])
zone_class = st.sidebar.selectbox("🏙️ Class الحي", ["A", "B", "C"])

if st.sidebar.button("✅ إضافة الطلب"):
    coords = get_coords(address)
    if coords:
        st.session_state.orders.append({
            "address": address,
            "lat": coords[0],
            "lon": coords[1],
            "weight": weight,
            "num_packages": num_packages,
            "order_type": order_type,
            "zone_class": zone_class
        })
        st.sidebar.success(f"تم إضافة الطلب: {address}")
    else:
        st.sidebar.error("❌ العنوان غير صحيح")

# ========= دوال حساب المسافة و Score =========
def get_distance_km(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    r = requests.get(url)
    data = r.json()
    if "routes" in data:
        return round(data["routes"][0]["distance"] / 1000, 2)
    return 9999

def zone_impact(zone):
    return {"A": 1.0, "B": 1.5, "C": 2.0}[zone]

def order_type_impact(order_type):
    return {"Delivery": 1.0, "Pickup": 1.2, "Linked Delivery": 0.8}[order_type]

def calculate_score(distance, weight, num_packages, zone_class, order_type):
    base = (distance * 1.0) + (weight * 1.5) + (num_packages * 0.5)
    return round(base * zone_impact(zone_class) * order_type_impact(order_type), 2)

# ========= زر التخطيط =========
if st.button("🚀 خطط المسار"):
    if start_coords and st.session_state.orders:
        results = []
        for o in st.session_state.orders:
            dist = get_distance_km(start_coords[0], start_coords[1], o["lat"], o["lon"])
            score = calculate_score(dist, o["weight"], o["num_packages"], o["zone_class"], o["order_type"])
            o["distance_km"] = dist
            o["score"] = score
            results.append(o)
        
        # ترتيب الطلبات حسب Score
        sorted_orders = sorted(results, key=lambda x: x["score"])
        st.subheader("📋 الطلبات مرتبة حسب الأولوية")
        st.table(sorted_orders)

        # خريطة المسار
        st.subheader("🗺️ خريطة المسار")
        m = folium.Map(location=start_coords, zoom_start=12)
        folium.Marker(start_coords, popup="🏢 نقطة البداية", icon=folium.Icon(color="green")).add_to(m)

        for idx, order in enumerate(sorted_orders, start=1):
            folium.Marker(
                [order["lat"], order["lon"]],
                popup=f"{idx}. {order['order_type']} | {order['address']} | {order['distance_km']}km | {order['weight']}kg",
                icon=folium.Icon(color="blue" if order["order_type"] == "Delivery" else "red")
            ).add_to(m)

        st_folium(m, width=900, height=500)

    else:
        st.warning("⚠️ أدخل نقطة البداية وأضف الطلبات أولًا")
else:
    st.info("📌 أدخل الطلبات واضغط 🚀 خطط المسار")
