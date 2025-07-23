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

# خلفية متدرجة ناعمة + مكان اللوجو
st.markdown("""
    <style>
    /* خلفية بتدرج هادي وحركة خفيفة */
    body {
        background: linear-gradient(120deg, #0b1d3a, #1f487c, #89c4f4);
        background-size: 400% 400%;
        animation: gradientMove 12s ease infinite;
        color: #e6edf5;
    }
    @keyframes gradientMove {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* اللوجو والعنوان */
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .logo-container img {
        width: 80px;
        filter: drop-shadow(0 0 8px rgba(173,216,230,0.4));
    }
    .logo-text {
        font-size: 20px;
        font-weight: 600;
        color: #d4ecff;
        letter-spacing: 1px;
        margin-top: 5px;
    }
    .tagline {
        font-size: 14px;
        color: #aacbe6;
        font-style: italic;
        margin-bottom: 20px;
    }

    /* تنسيقات الأزرار والنصوص */
    .stButton>button {
        background: linear-gradient(90deg, #2c78b5, #145083);
        color: #fff;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-weight: bold;
        transition: 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #3a8cd3, #1d5c99);
        transform: scale(1.03);
    }

    .stNumberInput label, .stSelectbox label {
        font-weight: 500;
        color: #e6edf5;
    }

    /* Fade-in للنتائج */
    .fade-in {
        animation: fadeIn 0.8s ease-in-out;
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(5px);}
        to {opacity: 1; transform: translateY(0);}
    }
    </style>
""", unsafe_allow_html=True)

# مكان اللوجو الرسمي
st.markdown("""
<div class="logo-container">
    <img src="eastren_union_favicon-removebg-preview.png" alt="Eastern Union Logo">
    <div class="logo-text">EASTERN UNION</div>
    <div class="tagline">الكفاءة... منهج وليست صدفة</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center;'>Dynamic Route Planner</h2>", unsafe_allow_html=True)

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

    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    st.subheader("الترتيب المقترح")
    for i, order in enumerate(sorted_orders, start=1):
        st.write(
            f"{i}. ({order['lat']:.6f}, {order['lon']:.6f}) | المسافة: {order['distance']:.2f} كم | Score: {order['score']:.2f}"
        )
    st.markdown("</div>", unsafe_allow_html=True)

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
