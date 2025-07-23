import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Eastern Union Route Planner", layout="wide")

st.title("🚚 Eastern Union Route Planner")

# تخزين النقاط
if "locations" not in st.session_state:
    st.session_state.locations = []

st.sidebar.header("➕ أضف نقطة توصيل")

# إدخال البيانات بنفس الشكل القديم
lat = st.sidebar.text_input("Latitude (مثال: 30.018745)")
lon = st.sidebar.text_input("Longitude (مثال: 31.230984)")
weight = st.sidebar.number_input("وزن الطرود (كجم)", min_value=0.1, step=0.1)
num_packages = st.sidebar.number_input("عدد الطرود", min_value=1, step=1)
zone = st.sidebar.selectbox("كلاس الحي", ["A", "B", "C"])
order_type = st.sidebar.selectbox("نوع الطلب", ["Delivery", "Pickup", "Linked Delivery"])

if st.sidebar.button("✅ أضف النقطة"):
    try:
        # حفظ القيم بدقة كاملة
        lat_f = float(lat)
        lon_f = float(lon)
        st.session_state.locations.append({
            "lat": lat_f,
            "lon": lon_f,
            "weight": weight,
            "num_packages": num_packages,
            "zone": zone,
            "type": order_type
        })
        st.sidebar.success("✅ تم إضافة النقطة!")
    except ValueError:
        st.sidebar.error("❌ تأكد من إدخال الإحداثيات بشكل صحيح")

# عرض النقاط بنفس الستايل القديم
if st.session_state.locations:
    st.subheader("📍 النقاط المدخلة")
    for i, loc in enumerate(st.session_state.locations, 1):
        st.write(
            f"**{i}. ({loc['lat']:.6f}, {loc['lon']:.6f})** | وزن: {loc['weight']} كجم | طرود: {loc['num_packages']} | حي: {loc['zone']} | نوع: {loc['type']}"
        )

    # خريطة بسيطة زي النسخة القديمة
    avg_lat = sum([l["lat"] for l in st.session_state.locations]) / len(st.session_state.locations)
    avg_lon = sum([l["lon"] for l in st.session_state.locations]) / len(st.session_state.locations)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

    for i, loc in enumerate(st.session_state.locations, 1):
        folium.Marker(
            [loc["lat"], loc["lon"]],
            popup=f"نقطة {i}\nوزن: {loc['weight']} كجم | طرود: {loc['num_packages']} | حي: {loc['zone']} | نوع: {loc['type']}",
            tooltip=f"نقطة {i}"
        ).add_to(m)

    st_folium(m, width=900, height=500)

else:
    st.info("ℹ️ لم يتم إضافة أي نقاط بعد.")

