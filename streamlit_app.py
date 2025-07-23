import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Eastern Union Route Planner", layout="wide")

st.title("🚚 Eastern Union Dynamic Route Planner")

# تخزين البيانات
if "points" not in st.session_state:
    st.session_state.points = []

st.sidebar.header("➕ إضافة نقطة جديدة")

# إدخال الإحداثيات بدقة كاملة
lat = st.sidebar.text_input("Latitude (مثال: 30.018745)")
lon = st.sidebar.text_input("Longitude (مثال: 31.230984)")
weight = st.sidebar.number_input("وزن الطرود (كجم)", min_value=0.1, step=0.1)
num_packages = st.sidebar.number_input("عدد الطرود", min_value=1, step=1)
zone_class = st.sidebar.selectbox("كلاس الحي", ["A", "B", "C"])
order_type = st.sidebar.selectbox("نوع الطلب", ["Delivery", "Pickup", "Linked Delivery"])

if st.sidebar.button("✅ أضف النقطة"):
    try:
        lat_f = float(lat)
        lon_f = float(lon)
        # نضيف النقطة بدون أي تقريب
        st.session_state.points.append({
            "lat": lat_f,
            "lon": lon_f,
            "weight": weight,
            "num_packages": num_packages,
            "zone": zone_class,
            "type": order_type
        })
        st.sidebar.success("✅ تم إضافة النقطة بدقة كاملة!")
    except ValueError:
        st.sidebar.error("❌ تأكد من كتابة الإحداثيات بشكل صحيح")

# عرض النقاط المدخلة بدقتها الكاملة
if st.session_state.points:
    st.subheader("📍 النقاط المدخلة (بدقة كاملة)")
    for i, p in enumerate(st.session_state.points, start=1):
        st.write(
            f"**{i}. ({p['lat']:.6f}, {p['lon']:.6f})** | وزن: {p['weight']} كجم | طرود: {p['num_packages']} | حي: {p['zone']} | نوع: {p['type']}"
        )

    # نرسم الخريطة بالإحداثيات الحقيقية
    avg_lat = sum([p["lat"] for p in st.session_state.points]) / len(st.session_state.points)
    avg_lon = sum([p["lon"] for p in st.session_state.points]) / len(st.session_state.points)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

    # إضافة النقاط بدقة كاملة
    for i, p in enumerate(st.session_state.points, start=1):
        folium.Marker(
            [p["lat"], p["lon"]],
            popup=f"نقطة {i}\nوزن: {p['weight']} كجم | طرود: {p['num_packages']} | حي: {p['zone']} | نوع: {p['type']}",
            tooltip=f"نقطة {i} ({p['lat']:.6f}, {p['lon']:.6f})"
        ).add_to(m)

    st_folium(m, width=900, height=500)

else:
    st.info("ℹ️ لم يتم إضافة أي نقاط بعد.")

