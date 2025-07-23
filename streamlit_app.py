import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests

st.set_page_config(page_title="Eastern Union Auto Optimizer", layout="wide")

st.title("🚚 Eastern Union Smart Route Optimizer")
st.write("أدخل العناوين فقط، والنظام هيحسب المسافات ويرتب الطلبات تلقائيًا")

# ========= إعداد Geocoder =========
geolocator = Nominatim(user_agent="eastern_union_optimizer")

# ========= نقطة البداية =========
st.sidebar.header("🏢 نقطة البداية (المخزن)")
start_address = st.sidebar.text_input("عنوان نقطة البداية", "ميدان التحرير، القاهرة")

def get_coords(address):
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

start_coords = get_coords(start_address)

# ========= إعداد الطلبات =========
if "orders" not in st.session_state:
    st.session_state.orders = []

st.sidebar.subheader("➕ إضافة طلب جديد")
order_type = st.sidebar.selectbox("نوع الطلب", ["Delivery", "Pickup", "Linked Delivery"])
address = st.sidebar.text_input("📍 عنوان الطلب")

if st.sidebar.button("✅ إضافة الطلب"):
    coords = get_coords(address)
    if coords:
        st.session_state.orders.append({
            "type": order_type,
            "address": address,
            "lat": coords[0],
            "lon": coords[1],
        })
        st.sidebar.success(f"تم إضافة الطلب: {address}")
    else:
        st.sidebar.error("❌ العنوان غير صحيح أو غير مفهوم")

# ========= حساب المسافات من نقطة البداية =========
def get_distance_km(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    r = requests.get(url)
    data = r.json()
    if "routes" in data:
        return round(data["routes"][0]["distance"] / 1000, 2)
    return 9999  # لو فشل الحساب

def calculate_score(distance, order_type):
    base = distance
    if order_type == "Pickup":
        base -= 2  # نعطيه أولوية أعلى
    return round(base, 2)

# ========= عند الضغط على زر التخطيط =========
if st.button("🚀 خطط المسار"):
    if start_coords and st.session_state.orders:
        optimized_orders = []
        for o in st.session_state.orders:
            dist = get_distance_km(start_coords[0], start_coords[1], o["lat"], o["lon"])
            score = calculate_score(dist, o["type"])
            o["distance_km"] = dist
            o["score"] = score
            optimized_orders.append(o)
        
        # ترتيب حسب الأولوية
        sorted_orders = sorted(optimized_orders, key=lambda x: x["score"])
        st.subheader("📋 الطلبات مرتبة حسب الأولوية:")
        st.table(sorted_orders)
        
        # رسم الخريطة
        st.subheader("🗺️ خريطة المسار")
        m = folium.Map(location=start_coords, zoom_start=12)
        folium.Marker(start_coords, popup="🏢 نقطة البداية", icon=folium.Icon(color="green")).add_to(m)
        for idx, order in enumerate(sorted_orders, start=1):
            folium.Marker(
                [order["lat"], order["lon"]],
                popup=f"{idx}. {order['type']} | {order['address']} | {order['distance_km']} km",
                icon=folium.Icon(color="blue" if order["type"] == "Delivery" else "red")
            ).add_to(m)
        
        st_folium(m, width=900, height=500)
    else:
        st.warning("⚠️ تأكد إنك أضفت نقطة البداية والطلبات")
else:
    st.info("📌 أدخل الطلبات واضغط على 🚀 خطط المسار")
