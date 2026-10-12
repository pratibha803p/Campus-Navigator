import re
import datetime
from collections import deque

import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="VIT Bhopal Digital Twin & Wayfinding System",
    page_icon="🎓",
    layout="wide"
)

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def now_ist():
    return datetime.datetime.now(IST)


def escape_md(text):
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|<>~$])", r"\\\1", text)


if "reported_issues" not in st.session_state:
    st.session_state.reported_issues = [
        {"location": "Block AB1", "issue": "Lift #2 is under maintenance",
         "reporter": "Student Council", "time": "10:30 AM"}
    ]

st.sidebar.title("🎨 Appearance Settings")
dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode", value=False)

if dark_mode:
    st.markdown(
        """
        <style>
        .stApp, [data-testid="stHeader"] {
            background-color: #0e1117;
            color: #ffffff;
        }
        [data-testid="stSidebar"] {
            background-color: #161a23;
        }
        .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
        .stApp span, .stApp li, .stApp div[data-testid="stMarkdownContainer"] {
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏛️ VIT Bhopal University")
st.sidebar.caption("Digital Campus Twin & Navigation System")

campus_graph = {
    "Block AB1": ["Block AB2", "Library (AB1)", "Lab AB1", "Central Mess", "Main Gate",
                  "Computer Lab Building", "Medical Center (Dr. Morepen Pharmacy)"],
    "Block AB2": ["Block AB1", "Library (AB2)", "Lab AB2", "Labs Complex", "Sports Ground",
                  "Architecture Block"],
    "Computer Lab Building": ["Block AB1", "Labs Complex"],
    "Architecture Block": ["Block AB2", "Boys Hostel Block", "Girls Hostel Block"],
    "Library (AB1)": ["Block AB1", "Lab AB1", "Labs Complex", "CTS Office"],
    "Library (AB2)": ["Block AB2", "Lab AB2", "Computer Lab Building"],
    "Lab AB1": ["Block AB1", "Library (AB1)"],
    "Lab AB2": ["Block AB2", "Library (AB2)"],
    "Labs Complex": ["Block AB2", "Library (AB1)", "Boys Hostel Block", "Computer Lab Building"],
    "Central Mess": ["Block AB1", "Cafeteria", "Main Gate"],
    "Cafeteria": ["Central Mess", "Boys Hostel Block"],
    "Boys Hostel Block": ["Architecture Block", "Labs Complex", "Cafeteria", "Girls Hostel Block",
                          "Medical Center (Dr. Morepen Pharmacy)"],
    "Girls Hostel Block": ["Boys Hostel Block", "Architecture Block"],
    "Sports Ground": ["Block AB2"],
    "CTS Office": ["Library (AB1)"],
    "Main Gate": ["Block AB1", "Central Mess"],
    "Medical Center (Dr. Morepen Pharmacy)": ["Block AB1", "Girls Hostel Block"]
}

for _a, _neighbors in list(campus_graph.items()):
    for _b in _neighbors:
        if _a not in campus_graph.setdefault(_b, []):
            campus_graph[_b].append(_a)

campus_coords = {
    "Block AB1": (23.07827746128565, 76.85123903795754),
    "Block AB2": (23.073980028642616, 76.85781340569753),
    "Computer Lab Building": (23.078077, 76.851239),
    "Architecture Block": (23.073780, 76.857813),
    "Library (AB1)": (23.078477, 76.851239),
    "Library (AB2)": (23.074180, 76.857813),
    "Lab AB1": (23.078277, 76.851439),
    "Lab AB2": (23.073980, 76.858013),
    "Labs Complex": (23.078623491507567, 76.84998708831283),
    "Central Mess": (23.075124, 76.854965),
    "Cafeteria": (23.075123787210636, 76.85476533714842),
    "Boys Hostel Block": (23.07546380886868, 76.85969640868795),
    "Girls Hostel Block": (23.075639524936353, 76.85356771180827),
    "Sports Ground": (23.07484746856346, 76.85708642770133),
    "CTS Office": (23.078477, 76.851439),
    "Main Gate": (23.078218609043212, 76.85171612636778),
    "Medical Center (Dr. Morepen Pharmacy)": (23.076169174051266, 76.84991143413616),
}

location_details = {
    "Block AB1": {
        "description": "Primary Academic Block for First-Year and Core Engineering Classes.",
        "floors": "Ground + 4 Floors",
        "open_time": "08:00:00",
        "close_time": "20:00:00",
        "key_spots": {
            "AB1-101": "Lecture Hall 1 (Ground Floor)",
            "AB1-204": "Department of Computer Science HOD Office (1st Floor)"
        }
    },
    "Block AB2": {
        "description": "Advanced Engineering and Core Research Block.",
        "floors": "Ground + 5 Floors",
        "open_time": "08:00:00",
        "close_time": "20:00:00",
        "key_spots": {
            "AB2-102": "Mechanical CAD Lab (1st Floor)",
            "AB2-203": "AI & Machine Learning Research Center (2nd Floor)"
        }
    },
    "Boys Hostel Block": {
        "description": "Multi-storey residential accommodation facility for male students.",
        "floors": "Ground + 7 Floors",
        "open_time": "00:00:00",
        "close_time": "23:59:59",
        "key_spots": {
            "Boys Warden Office": "Ground Floor Main Entry Lobby",
            "Hostel Mess": "Dedicated Dining Facility"
        }
    },
    "Girls Hostel Block": {
        "description": "Secure multi-storey residential accommodation facility for female students.",
        "floors": "Ground + 7 Floors",
        "open_time": "00:00:00",
        "close_time": "23:59:59",
        "key_spots": {
            "Girls Warden Office": "Ground Floor Secure Lobby",
            "Reading Room": "Dedicated Study Hall"
        }
    },
    "Medical Center (Dr. Morepen Pharmacy)": {
        "description": "24/7 Healthcare and Emergency Center featuring Dr. Morepen Pharmacy partnership.",
        "floors": "Ground Floor",
        "open_time": "00:00:00",
        "close_time": "23:59:59",
        "key_spots": {
            "Emergency Ward": "First Aid & Doctor Consultation",
            "Dr. Morepen Pharmacy": "Medicines & Healthcare Essentials Counter"
        }
    },
    "Computer Lab Building": {
        "description": "Dedicated high-end computing facility for programming and software labs.",
        "floors": "Ground + 3 Floors",
        "open_time": "08:30:00",
        "close_time": "21:00:00",
        "key_spots": {"CL-101": "Programming Lab 1"}
    },
    "Architecture Block": {
        "description": "Specialized design studios and workshops for B.Arch students.",
        "floors": "Ground + 4 Floors",
        "open_time": "08:00:00",
        "close_time": "18:00:00",
        "key_spots": {"ARC-101": "Design Studio 1"}
    },
    "Library (AB1)": {
        "description": "Academic Block 1 Library Branch.",
        "floors": "Ground Floor",
        "open_time": "09:00:00",
        "close_time": "21:00:00",
        "key_spots": {"AB1-Lib Desk": "Book Issue Counter"}
    },
    "Library (AB2)": {
        "description": "Academic Block 2 Advanced Reference Library.",
        "floors": "1st Floor",
        "open_time": "09:00:00",
        "close_time": "22:00:00",
        "key_spots": {"AB2-Lib Desk": "Reference Desk"}
    },
    "Lab AB1": {
        "description": "Departmental laboratory wing inside AB1.",
        "floors": "Ground Floor",
        "open_time": "08:00:00",
        "close_time": "18:00:00",
        "key_spots": {"Lab AB1-01": "Basic Electrical Lab"}
    },
    "Lab AB2": {
        "description": "Technical experimentation laboratory wing inside AB2.",
        "floors": "2nd Floor",
        "open_time": "08:00:00",
        "close_time": "18:00:00",
        "key_spots": {"Lab AB2-01": "Microprocessors Lab"}
    },
    "Labs Complex": {
        "description": "High-performance computing clusters.",
        "floors": "Ground + 3 Floors",
        "open_time": "08:30:00",
        "close_time": "19:30:00",
        "key_spots": {"Lab 01": "Data Science Hub"}
    },
    "Central Mess": {
        "description": "Main campus dining facility.",
        "floors": "Ground + 1 Floor",
        "open_time": "07:00:00",
        "close_time": "22:00:00",
        "key_spots": {"Ground Dining": "Main Mess Hall"}
    },
    "Cafeteria": {
        "description": "Hangout zone with food stalls.",
        "floors": "Ground Floor",
        "open_time": "09:00:00",
        "close_time": "20:00:00",
        "key_spots": {"Stall 1": "Snacks & Beverages"}
    },
    "Sports Ground": {
        "description": "Open-air playground for sports.",
        "floors": "Outdoor Facility",
        "open_time": "06:00:00",
        "close_time": "21:00:00",
        "key_spots": {"Pavilion": "Changing Rooms"}
    },
    "CTS Office": {
        "description": "Center for Technical Support & Helpdesk, near Library (AB1).",
        "floors": "Ground Floor",
        "open_time": "09:00:00",
        "close_time": "17:30:00",
        "key_spots": {"Helpdesk": "IT Support"}
    },
    "Main Gate": {
        "description": "Primary campus security checkpoint.",
        "floors": "Ground Level",
        "open_time": "00:00:00",
        "close_time": "23:59:59",
        "key_spots": {"Security Cabin": "Guard Station"}
    }
}


def bfs_shortest_path(graph, start, goal):
    if start == goal:
        return [start]

    queue = deque([[start]])
    visited = {start}

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == goal:
            return path

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return None


def draw_route_map(path):
    points = [campus_coords[name] for name in path if name in campus_coords]
    if len(points) < 2:
        return None

    m = folium.Map(location=points[0], zoom_start=17)
    folium.PolyLine(points, color="blue", weight=5, opacity=0.8).add_to(m)

    for i, name in enumerate(path):
        if name not in campus_coords:
            continue
        if i == 0:
            color = "green"
        elif i == len(path) - 1:
            color = "red"
        else:
            color = "blue"
        folium.Marker(
            campus_coords[name],
            tooltip=name,
            popup=f"{i + 1}. {name}",
            icon=folium.Icon(color=color),
        ).add_to(m)

    m.fit_bounds(points)
    return m


def draw_all_buildings_map():
    pts = list(campus_coords.values())
    center = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
    m = folium.Map(location=center, zoom_start=17)
    for name, coord in campus_coords.items():
        folium.Marker(
            coord, tooltip=name, popup=name,
            icon=folium.Icon(color="gray")
        ).add_to(m)
    m.fit_bounds(pts)
    return m


st.sidebar.title("🧭 Navigation & Directory")
app_mode = st.sidebar.radio(
    "Choose Mode:",
    [
        "🗺️ Find Shortest Route",
        "🔍 Exact Room & Office Finder",
        "🔎 Universal Search Bar",
        "🛠️ Campus Issue Reporting Form",
        "⏱️ Live Facility Status Timings",
        "🏥 Emergency & Essential Facilities",
        "🚀 Future Scope & Presentation Guide"
    ]
)

st.title("🎓 VIT Bhopal Digital Twin & Smart Pathfinding System")
st.markdown("**Official Smart Campus Pathfinding & Room Finder System**")
st.markdown("---")

if app_mode == "🗺️ Find Shortest Route":
    st.subheader("📍 Campus Route Finder")

    locations = list(campus_graph.keys())
    col1, col2 = st.columns(2)
    with col1:
        start_loc = st.selectbox("Select Current Location:", locations)
    with col2:
        dest_loc = st.selectbox("Select Destination:", locations, index=1)

    if st.button("🚀 Find Route & Directions", type="primary"):
        if start_loc == dest_loc:
            st.warning("⚠️ Current Location and Destination cannot be the same!")
        else:
            path = bfs_shortest_path(campus_graph, start_loc, dest_loc)
            if path:
                st.success(f"✅ Shortest Route Found! Total Steps: {len(path) - 1}")

                st.markdown("### 🚶 Step-by-Step Directions:")
                for i in range(len(path) - 1):
                    u = path[i]
                    v = path[i + 1]
                    st.info(f"Step {i + 1}: Move from **{u}** ➔ **{v}**")

                st.markdown("### 🗺️ Route on Map")
                route_map = draw_route_map(path)
                if route_map:
                    st_folium(route_map, width=900, height=500, returned_objects=[])
                else:
                    st.warning("Map coordinates are missing for this route.")
            else:
                st.error("❌ No path available matching your criteria.")

    with st.expander("📌 Show all campus buildings on map"):
        st_folium(draw_all_buildings_map(), width=900, height=450, returned_objects=[])

elif app_mode == "🔍 Exact Room & Office Finder":
    st.subheader("🏢 Building Directory: Rooms, Labs & Offices")
    selected_building = st.selectbox("Select Building / Block:", list(location_details.keys()))

    details = location_details[selected_building]
    st.markdown(f"### 📍 {selected_building}")
    st.write(f"**Overview:** {details['description']}")
    st.write(f"**Building Structure:** {details['floors']}")

    st.markdown("#### 🚪 Exact Room Numbers & Offices:")
    for spot, room_info in details["key_spots"].items():
        st.success(f"• **{spot}:** `{room_info}`")

elif app_mode == "🔎 Universal Search Bar":
    st.subheader("🔍 Universal Room & Office Search")
    query = st.text_input(
        "Type any room number, lab name, or office (e.g., Dr. Morepen, Boys Hostel, AB1-101):"
    ).strip().lower()

    if query:
        found = False
        for bldg, info in location_details.items():
            for spot, desc in info["key_spots"].items():
                if query in spot.lower() or query in desc.lower() or query in bldg.lower():
                    found = True
                    st.success(f"Match found in **{bldg}**!")
                    st.write(f"• **Location/Spot:** {spot}")
                    st.write(f"• **Details:** {desc}")
                    st.write(f"• **Building Overview:** {info['description']}")
                    st.markdown("---")
        if not found:
            st.error("❌ No matching room or office found.")

elif app_mode == "🛠️ Campus Issue Reporting Form":
    st.subheader("🛠️ Live Campus Maintenance & Issue Reporting")
    with st.form("issue_form", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            issue_location = st.selectbox("Select Location / Block:", list(campus_graph.keys()))
        with col_f2:
            reporter_name = st.text_input("Your Name / Role:", "Student Volunteer")

        issue_description = st.text_area("Describe the Issue:")
        submitted = st.form_submit_button("🚀 Submit Issue Report", type="primary")

        if submitted:
            if issue_description.strip():
                current_time = now_ist().strftime("%I:%M %p")
                st.session_state.reported_issues.insert(0, {
                    "location": issue_location,
                    "issue": issue_description.strip(),
                    "reporter": reporter_name.strip() or "Anonymous",
                    "time": current_time
                })
                st.success("✅ Issue successfully reported and synced!")
            else:
                st.warning("⚠️ Please provide a description.")

    st.markdown("---")
    st.markdown("### 📋 Active Campus Issues Log:")
    for idx, item in enumerate(st.session_state.reported_issues):
        st.warning(
            f"**#{idx + 1} [{item['location']}]** - {escape_md(item['issue'])}\n\n"
            f"*Reported by {escape_md(item['reporter'])} at {item['time']}*"
        )

elif app_mode == "⏱️ Live Facility Status Timings":
    st.subheader("⏱️ Live Facility Status (Open/Closed Indicator)")
    now = now_ist()
    current_time_obj = now.time()
    st.info(f"🕒 **Current Time (IST):** {now.strftime('%I:%M %p (%A, %d %B %Y)')}")

    col_s1, col_s2 = st.columns(2)
    for idx, (bldg, info) in enumerate(location_details.items()):
        open_t = datetime.datetime.strptime(info["open_time"], "%H:%M:%S").time()
        close_t = datetime.datetime.strptime(info["close_time"], "%H:%M:%S").time()
        is_open = open_t <= current_time_obj <= close_t
        status_label = "🟢 OPEN NOW" if is_open else "🔴 CLOSED"

        target_col = col_s1 if idx % 2 == 0 else col_s2
        with target_col:
            msg = (f"**{bldg}**: {status_label}\n\n"
                   f"*Timing: {info['open_time'][:5]} to {info['close_time'][:5]}*")
            if is_open:
                st.success(msg)
            else:
                st.error(msg)

elif app_mode == "🏥 Emergency & Essential Facilities":
    st.subheader("🚨 Emergency & Essential Facilities")
    emergency_spots = {
        "Medical Center & Dr. Morepen Pharmacy": "Located strategically on campus. Provides 24/7 medical assistance, emergency first-aid, doctor consultation, and health essentials via Dr. Morepen Pharmacy.",
        "Main Gate Security": "Primary campus security checkpoint for visitor verification and safety.",
        "CTS Helpdesk": "Technical support and campus IT helpline located near Library (AB1)."
    }
    for place, info in emergency_spots.items():
        st.warning(f"🛡️ **{place}**\n\n{info}")

elif app_mode == "🚀 Future Scope & Presentation Guide":
    st.subheader("🚀 Future Scope & Presentation Talking Points")

    st.markdown("### 🎤 Presentation Line")
    st.markdown(
        "> **\"This is not just a static navigation map. It is a Digital Twin "
        "prototype combining graph-based shortest-path routing, room discovery, "
        "facility status, issue reporting and emergency navigation.\"**"
    )

    st.markdown("### 🔮 Future Scope")
    st.markdown(
        "- 🤖 AI-based natural-language Campus Assistant\n"
        "- 🗺️ Interactive visual campus map\n"
        "- 📍 GPS / indoor positioning\n"
        "- ♿ Accessibility-aware routing\n"
        "- 🔔 Real-time campus notifications\n"
        "- 🗄️ Cloud database\n"
        "- 👥 Student/Admin login system\n"
        "- 📚 Automatic timetable integration\n"
        "- 📊 Campus analytics dashboard\n"
        "- 🔐 Role-based access control"
    )

st.sidebar.markdown("---")
st.sidebar.caption("Campus Twin Navigator V2 • Prototype")
