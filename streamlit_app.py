import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Eastern Union Demo", layout="wide")

st.title("Eastern Union Logistics - Demo")
st.write("نسخة تجريبية لعرض الخوارزمية والخريطة")

# ================================
# خوارزمية حساب Score
def calculate_score(zone, distance, size, bulk, urgency, order_type):
    # معاملات افتراضية
    Wz, Wd, Ws, Wb, Wu = 1.2, 1.0, 1.5, 0.8, 2.0
    
    base_score = (zone * Wz) + (distance * Wd) + (size * Ws) + ((5 - bulk) * Wb) + ((10 - urgency) * Wu)
    if order_type == "Pickup":
        base_score += 5  # أولوية أعلى لأنه بيفتح طلبات تانية
    return round(base_score, 2)

# ================================
# واجهة إدخال الطلبات
st.sidebar.header("أضف طلب جديد")

order_type = st.sidebar.selectbox("نوع الطلب", ["Delivery", "Pickup", "Linked Delivery"])
zone = st.sidebar.slider("صعوبة المنطقة Z", 1, 3, 2)
distance = st.sidebar.slider("المسافة (كم)", 1, 50, 10)
size = st.sidebar.slider("حجم/وزن الطرد", 1, 20, 5)
bulk = st.sidebar.slider("عدد الطرود لنفس العميل", 1, 5, 1)
urgency = st.sidebar.slider("درجة الاستعجال", 1, 10, 5)

if "orders" not in st.session_state:
    st.session_state.orders = []

if st.sidebar.button("➕ إضافة الطلب"):
    score = calculate_score(zone, distance, size, bulk, urgency, order_type)
    st.session_state.orders.append({
        "type": order_type,
        "zone": zone,
        "distance": distance,
        "size": size,
        "bulk": bulk,
        "urgency": urgency,
        "score": score
    })
    st.sidebar.success("تم إضافة الطلب ✅")

# ================================
# عرض قائمة الطلبات مرتبة بالأولوية
if st.session_state.orders:
    st.subheader("📋 قائمة الطلبات")
    sorted_orders = sorted(st.session_state.orders, key=lambda x: x["score"], reverse=True)
    st.table(sorted_orders)
else:
    st.info("لم يتم إضافة أي طلبات بعد")

# ================================
# خريطة بسيطة (ثابتة تجريبية)
st.subheader("🗺️ الخريطة")
m = folium.Map(location=[30.0444, 31.2357], zoom_start=11)  # القاهرة

# إضافة نقاط تجريبية
folium.Marker(location=[30.05, 31.25], popup="Pickup P1").add_to(m)
folium.Marker(location=[30.06, 31.23], popup="Delivery D1").add_to(m)

st_folium(m, width=800, height=500)
