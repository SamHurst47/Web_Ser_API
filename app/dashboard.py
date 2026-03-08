import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuration
API_BASE_URL = "https://web-ser-api.onrender.com"

st.set_page_config(page_title="TimeSlice F1 Analytics", layout="wide")
st.title("🏎️ TimeSlice: F1 Performance Dashboard")

# --- Session State Management ---
if "access_token" not in st.session_state:
    st.session_state.access_token = None

# --- Sidebar: Authentication ---
with st.sidebar:
    st.header("👤 Account Access")
    if not st.session_state.access_token:
        mode = st.radio("Choose Action", ["Login", "Register"])
        user_email = st.text_input("Email", key="auth_email")
        user_pass = st.text_input("Password", type="password", key="auth_pass")
        
        if st.button("Submit"):
            if mode == "Register":
                reg_resp = requests.post(
                    f"{API_BASE_URL}/api/v1/accounts/register", 
                    json={"email": user_email, "password": user_pass}
                )
                # Check if the response is actually JSON before parsing
                if reg_resp.status_code == 201: 
                    st.success("Account created! Switch to Login.")
                else:
                    try:
                        error_detail = reg_resp.json().get('detail', 'Unknown Error')
                        st.error(f"Registration Failed: {error_detail}")
                    except Exception:
                        # If it's not JSON, show the raw text or status code
                        st.error(f"Server Error ({reg_resp.status_code}): The API didn't return a valid response.")
            else:
                login_resp = requests.post(f"{API_BASE_URL}/api/v1/accounts/login", 
                                          data={"username": user_email, "password": user_pass})
                if login_resp.status_code == 200:
                    st.session_state.access_token = login_resp.json()["access_token"]
                    st.rerun()
                else: st.error("Login Failed. Check credentials.")
    else:
        st.write("✅ Authenticated")
        if st.button("Logout"):
            st.session_state.access_token = None
            st.rerun()
        
        # --- NEW: Account Deletion (Danger Zone) ---
        st.markdown("---")
        with st.expander("⚠️ Danger Zone"):
            st.write("Deleting your account will remove all your saved lap data permanently.")
            confirm_delete = st.checkbox("I understand the consequences")
            if st.button("Delete My Account", type="primary", disabled=not confirm_delete):
                # Call your account deletion endpoint
                # Assuming your endpoint is DELETE /api/v1/accounts/me or similar
                headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
                del_resp = requests.delete(f"{API_BASE_URL}/api/v1/accounts/me", headers=headers)
                
                if del_resp.status_code == 204:
                    st.success("Account deleted successfully.")
                    st.session_state.access_token = None
                    st.rerun()
                else:
                    st.error("Could not delete account. Check server logs.")

# --- Main Dashboard Logic ---
if st.session_state.access_token:
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

    # --- READ: Analytics Suite ---
    with st.expander("📊 Racing Analytics Suite", expanded=True):
        col1, col2, col3 = st.columns(3)
        loc = col1.text_input("Location", value="Belgium", key="ana_loc")
        yr = col2.number_input("Year", value=2023, step=1, key="ana_yr")
        endpoint_choice = col3.selectbox("Analysis Type", ["True Pace", "Ideal Laps", "Pace Trend"])

        if st.button("Run Analytics"):
            path_map = {
                "True Pace": "/api/v1/analytics/true-pace",
                "Ideal Laps": "/api/v1/analytics/ideal-laps",
                "Pace Trend": "/api/v1/analytics/pace-trend"
            }
            resp = requests.get(f"{API_BASE_URL}{path_map[endpoint_choice]}", 
                                params={"year": yr, "location": loc}, headers=headers)

            if resp.status_code == 200:
                data = resp.json()
                if endpoint_choice == "True Pace":
                    df = pd.DataFrame(data)
                    
                    # Ensure driver numbers are treated as categorical labels
                    df['driver_label'] = "Driver #" + df['driver_number'].astype(str)
                    
                    # Sort by time so the bars are in order of performance
                    df = df.sort_values("true_average_pace")

                    # Create the Bar Chart without the color scale
                    fig = px.bar(df, 
                                 x="driver_label", 
                                 y="true_average_pace", 
                                 title=f"Average Lap Times: {loc} {yr}",
                                 labels={"true_average_pace": "Time (s)", "driver_label": "Driver"},
                                 text_auto='.3f') # Shows the exact time on top of the bar

                    # Zoom in the Y-axis to make small time differences visible
                    min_time = df['true_average_pace'].min() * 0.98
                    max_time = df['true_average_pace'].max() * 1.02
                    fig.update_yaxes(range=[min_time, max_time])

                    # Ensure the color bar/legend is completely removed
                    fig.update_layout(showlegend=False, coloraxis_showscale=False)
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                elif endpoint_choice == "Pace Trend":
                    all_laps = []
                    for trend in data['trends']:
                        d_num = str(trend['driver_number'])
                        for lap in trend['laps']:
                            all_laps.append({
                                "Driver": f"#{d_num}", 
                                "Lap": lap['lap_number'], 
                                "Time": lap['lap_duration']
                            })
                    df_trend = pd.DataFrame(all_laps)
                    
                    # Multi-line chart for lap-by-lap comparison
                    fig = px.line(df_trend, x="Lap", y="Time", color="Driver", markers=True, 
                                 title=f"Lap-by-Lap Comparison: {loc}")
                    
                    fig.update_yaxes(autorange="reversed")
                    st.plotly_chart(fig, use_container_width=True)
                
                elif endpoint_choice == "Pace Trend":
                    all_laps = []
                    for trend in data['trends']:
                        d_num = str(trend['driver_number'])
                        for lap in trend['laps']:
                            all_laps.append({"Driver": f"#{d_num}", "Lap": lap['lap_number'], "Duration": lap['lap_duration']})
                    df_trend = pd.DataFrame(all_laps)
                    fig = px.line(df_trend, x="Lap", y="Duration", color="Driver", markers=True, title=f"Pace Trend: {loc}")
                    fig.update_yaxes(autorange="reversed")
                    st.plotly_chart(fig, use_container_width=True)

                elif endpoint_choice == "Ideal Laps":
                    df_ideal = pd.DataFrame(data['driver_ideal_laps'])
                    df_ideal['driver_number'] = df_ideal['driver_number'].astype(str)
                    fig = px.scatter(df_ideal, x="actual_best_lap_time", y="ideal_lap_time", text="driver_number", 
                                     size="potential_improvement", color="potential_improvement", title=f"Consistency: {loc}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("No data found for this selection.")

    # --- CRUD: Data Management ---
    with st.expander("⚙️ Data Management (CRUD)"):
        tab1, tab2, tab3, tab4 = st.tabs(["List (Read)", "Import (Create)", "Update", "Delete"])

        # READ: List Data with Filters
        with tab1:
            st.subheader("🔍 Query Database")
            
            # Layout for filters
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                r_loc = st.text_input("Filter by Location", value="", placeholder="e.g. Belgium")
                r_year = st.number_input("Filter by Year", value=0, help="Leave 0 to ignore year")
            with r_col2:
                r_driver = st.number_input("Filter by Driver #", value=0, help="Leave 0 to ignore driver")
                r_sess = st.selectbox("Filter by Session", ["All", "Race", "Qualifying", "Sprint"])

            if st.button("Refresh Table"):
                # Build the query parameters dictionary
                params = {}
                if r_loc: params["location"] = r_loc
                if r_year > 0: params["year"] = r_year
                if r_driver > 0: params["driver_number"] = r_driver
                if r_sess != "All": params["session_name"] = r_sess

                resp = requests.get(f"{API_BASE_URL}/api/v1/lap_summaries", 
                                   params=params, headers=headers)
                
                if resp.status_code == 200:
                    data = resp.json()
                    if data:
                        st.dataframe(pd.DataFrame(data), use_container_width=True)
                    else:
                        st.info("No data found matching those filters.")
                else:
                    st.error(f"Error fetching data: {resp.status_code}")

        # CREATE (User-Friendly Import)
        with tab2:
            st.subheader("Import from OpenF1")
            imp_loc = st.text_input("Location", value="Belgium", key="imp_loc")
            imp_yr = st.number_input("Year", value=2023, key="imp_yr")
            imp_sess = st.selectbox("Session", ["Race", "Qualifying", "Sprint"], key="imp_sess")
            imp_driver = st.number_input("Driver Number", value=1, key="imp_drv")
            
            if st.button("Execute Import"):
                res = requests.post(f"{API_BASE_URL}/api/v1/lap_summaries/import_from_openf1", 
                                   params={"year": imp_yr, "location": imp_loc, "session_name": imp_sess, "driver_number": imp_driver}, 
                                   headers=headers)
                if res.status_code == 202: st.success("Import processing...")
                else: st.error(f"Import failed: {res.text}")

        # UPDATE
        with tab3:
            st.subheader("Update Metadata")
            u_driver = st.number_input("Driver #", value=1, key="upd_d")
            u_loc = st.text_input("Location", value="Belgium", key="upd_l")
            u_label = st.text_input("New Label", placeholder="e.g., Purple Lap")
            if st.button("Push Update"):
                res = requests.put(f"{API_BASE_URL}/api/v1/lap_summaries", 
                                  params={"driver_number": u_driver, "location": u_loc},
                                  json={"label": u_label}, headers=headers)
                if res.status_code == 200: st.success("Updated successfully.")

        # DELETE
        with tab4:
            st.subheader("Remove Data")
            d_driver = st.number_input("Driver #", value=1, key="del_d")
            d_loc = st.text_input("Location", value="Belgium", key="del_l")
            st.warning("This action cannot be undone.")
            if st.button("Confirm Delete", type="primary"):
                res = requests.delete(f"{API_BASE_URL}/api/v1/lap_summaries", 
                                     params={"driver_number": d_driver, "location": d_loc}, headers=headers)
                if res.status_code == 204: st.success("Data deleted.")
                else: st.error("Delete failed.")
else:
    st.info("Log in or Register to access the Dashboard.")