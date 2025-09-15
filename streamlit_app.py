# streamlit_app.py
# --- Streamlit app: Map with callouts ("arrows" + small explanations)
# How it works
# - Left: interactive map (pydeck) with sites (Incheon islands, Busan lowlands)
# - We draw short arrow-like paths from each site to a nearby offset point
# - We place a text label near the arrow tip → callout effect inside the map
# - Right: small info cards that mirror the map points (image + short note)
# - You can toggle layers, region focus, and base map style in the sidebar

import math
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Sunny-day Flooding Callout Map", layout="wide")

# ------------------------------
# Utils
# ------------------------------

def offset_point(lat, lon, bearing_deg=45, distance_km=2.0):
    """Return lat,lon offset from a start point by a given bearing and distance.
    Uses a simple spherical earth approximation (good for short distances).
    """
    R = 6371.0
    bearing = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance_km / R)
        + math.cos(lat1) * math.sin(distance_km / R) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(distance_km / R) * math.cos(lat1),
        math.cos(distance_km / R) - math.sin(lat1) * math.sin(lat2),
    )
    return math.degrees(lat2), math.degrees(lon2)

# ------------------------------
# Demo data (you can replace with your CSV later)
# ------------------------------

data = [
    {
        "name": "대청도(옹진)",
        "city": "인천광역시 옹진군",
        "type": "만조 침수",
        "desc": "대조기 만조 시 도로·물양장 침수 반복 → 생활 불편 & 안전 위험",
        "lat": 37.828,
        "lon": 124.711,
        "bearing": 30,
        "distance_km": 3.0,
    },
    {
        "name": "연평도(옹진)",
        "city": "인천광역시 옹진군",
        "type": "만조 침수",
        "desc": "항만·주택 인근 침수 사례 보고, 썬니데이 침수 체감",
        "lat": 37.666,
        "lon": 125.701,
        "bearing": 345,
        "distance_km": 2.5,
    },
    {
        "name": "부산 해안 저지대",
        "city": "부산광역시",
        "type": "월파/침수",
        "desc": "태풍 + 고조 시 도로·상가 침수, 방재시설 확충 요구",
        "lat": 35.090,
        "lon": 129.045,
        "bearing": 75,
        "distance_km": 3.0,
    },
]

df = pd.DataFrame(data)

# Precompute arrow endpoints for callouts
callouts = []
for _, row in df.iterrows():
    tip_lat, tip_lon = offset_point(row.lat, row.lon, row.bearing, row.distance_km)
    callouts.append(
        {
            "name": row.name,
            "city": row.city,
            "type": row.type,
            "desc": row.desc,
            "lat": row.lat,
            "lon": row.lon,
            "tip_lat": tip_lat,
            "tip_lon": tip_lon,
        }
    )
callouts_df = pd.DataFrame(callouts)

# ------------------------------
# Sidebar controls
# ------------------------------
st.sidebar.title("레이어 & 보기 설정")
region = st.sidebar.selectbox(
    "초기 시야(Region)", ["대한민국", "인천(옹진)", "부산"], index=0
)
show_arrows = st.sidebar.checkbox("화살표(콜아웃) 보이기", value=True)
show_points = st.sidebar.checkbox("지점 마커 보이기", value=True)
show_labels = st.sidebar.checkbox("라벨 보이기", value=True)
map_style = st.sidebar.selectbox(
    "베이스맵 스타일",
    [
        "mapbox://styles/mapbox/light-v10",
        "mapbox://styles/mapbox/dark-v10",
        "mapbox://styles/mapbox/satellite-v9",
        "mapbox://styles/mapbox/streets-v11",
    ],
    index=0,
)

# Camera presets
views = {
    "대한민국": dict(latitude=36.4, longitude=127.9, zoom=5.3, pitch=0, bearing=0),
    "인천(옹진)": dict(latitude=37.7, longitude=125.2, zoom=7.0, pitch=0, bearing=0),
    "부산": dict(latitude=35.15, longitude=129.06, zoom=9.0, pitch=0, bearing=0),
}

# ------------------------------
# Layers
# ------------------------------

layers = []

if show_points:
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[lon, lat]",
            get_radius=6000,
            radius_min_pixels=3,
            radius_max_pixels=20,
            get_fill_color=[255, 99, 71],  # tomato
            pickable=True,
        )
    )

if show_arrows:
    # Path (from site → tip) to emulate an arrow shaft
    path_rows = []
    for _, r in callouts_df.iterrows():
        path_rows.append({
            "name": r["name"],
            "path": [ [r["lon"], r["lat"]], [r["tip_lon"], r["tip_lat"]] ]
        })
    path_df = pd.DataFrame(path_rows)

    layers.append(
        pdk.Layer(
            "PathLayer",
            data=path_df,
            get_path="path",
            get_width=4,
            width_min_pixels=2,
            get_color=[20, 80, 200, 200],
            pickable=False,
        )
    )

if show_labels:
    # Small text at the arrow tips → callout title
    label_df = callouts_df.copy()
    label_df["label"] = label_df["name"]
    layers.append(
        pdk.Layer(
            "TextLayer",
            data=label_df,
            get_position="[tip_lon, tip_lat]",
            get_text="label",
            get_color=[0, 0, 0, 220],
            get_size=16,
            size_units="pixels",
            get_alignment_baseline="bottom",
        )
    )

# Tooltip content for points
TOOLTIP = {
    "html": "<b>{name}</b><br/>{city}<br/>{type} · {desc}",
    "style": {"backgroundColor": "white", "color": "#333"},
}

r = pdk.Deck(
    map_style=map_style,
    initial_view_state=pdk.ViewState(**views[region]),
    layers=layers,
    tooltip=TOOLTIP,
)

# ------------------------------
# Layout: map (left) + callout cards (right)
# ------------------------------
col_map, col_cards = st.columns([5, 3], gap="large")
with col_map:
    st.markdown("### 🗺️ 썬니데이 침수·해수면 상승 콜아웃 맵")
    st.pydeck_chart(r, use_container_width=True)

with col_cards:
    st.markdown("### 📌 콜아웃 요약")
    for _, r in callouts_df.iterrows():
        st.markdown(
            f"""
            **{r['name']}**  
            _{r['city']} · {r['type']}_  
            {r['desc']}
            """
        )
        st.divider()

# ------------------------------
# Optional: CSV 업로드(사용자 데이터로 교체)
# ------------------------------
with st.expander("🧩 나만의 지점 업로드(선택)"):
    st.write("CSV 열 예시: name,city,type,desc,lat,lon,bearing,distance_km")
    up = st.file_uploader("CSV 업로드", type=["csv"])
    if up is not None:
        try:
            user_df = pd.read_csv(up)
            if not set(["name", "lat", "lon"]).issubset(user_df.columns):
                st.error("필수 열(name, lat, lon)이 없습니다.")
            else:
                # compute callouts
                rows = []
                for _, row in user_df.iterrows():
                    b = float(row.get("bearing", 45))
                    d = float(row.get("distance_km", 2.0))
                    tip_lat, tip_lon = offset_point(float(row["lat"]), float(row["lon"]), b, d)
                    rows.append({
                        **row.to_dict(),
                        "tip_lat": tip_lat,
                        "tip_lon": tip_lon,
                    })
                user_callouts = pd.DataFrame(rows)

                # Build layers for user data
                ulayers = []
                ulayers.append(pdk.Layer("ScatterplotLayer", data=user_df, get_position="[lon, lat]", get_radius=6000, get_fill_color=[220, 120, 0], pickable=True))
                upaths = []
                for _, rr in user_callouts.iterrows():
                    upaths.append({"name": rr["name"], "path": [[rr["lon"], rr["lat"]], [rr["tip_lon"], rr["tip_lat"]]]})
                upath_df = pd.DataFrame(upaths)
                ulayers.append(pdk.Layer("PathLayer", data=upath_df, get_path="path", get_width=4, get_color=[0, 120, 60, 200]))
                ulabel_df = user_callouts.copy()
                ulabel_df["label"] = ulabel_df["name"]
                ulayers.append(pdk.Layer("TextLayer", data=ulabel_df, get_position="[tip_lon, tip_lat]", get_text="label", get_color=[0,0,0,220], get_size=16))

                ur = pdk.Deck(map_style=map_style, initial_view_state=pdk.ViewState(**views[region]), layers=ulayers, tooltip=TOOLTIP)
                st.success("업로드한 데이터로 콜아웃 맵을 생성했습니다.")
                st.pydeck_chart(ur, use_container_width=True)
        except Exception as e:
            st.error(f"CSV 처리 중 오류: {e}")

st.caption("ⓘ 데모 좌표는 보정이 필요할 수 있습니다. 실제 보고서 제출 전 최신 좌표/자료로 업데이트하세요.")