import streamlit as st
from data.fetch import get_year_data, get_day_hr_data, get_day_stress_data, get_client
from plots.plots import plot_year_overview, plot_day_overview,plot_day_overview2, plot_running_activity_overview
import datetime
from datetime import date
current_year = datetime.datetime.now().year

st.set_page_config(
    page_title="Biometric Dashboard",
    layout="wide"
)
st.title("Biometric Dashboard")

with st.sidebar.form("plot_form"):

    st.header("Garmin Login")

    email = st.text_input(
        "Email",
        placeholder="you@example.com"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    generate = st.form_submit_button("Generate plot")

if ((not generate) and (not "initial_press" in st.session_state)):
    st.stop()
else:
    st.session_state.initial_press = True
with st.sidebar.form("plot_form1"):
    st.divider()
    st.header('View')
    view = st.radio(
        "",
        ['Daily', 'Yearly']
    )
    if view == 'Daily':
        st.header('Daily')

        date = st.date_input(
            "Date",
            value=date.today()
        )
        month = date.month
        day = date.day
        year = date.year
    

    else:    
        st.header('Yearly')
        year_ov = st.number_input(
            "Year",
            min_value=2015,
            max_value=current_year,
            value=current_year,
            step=1,
        )
    
if not email or not password:
    st.info("Please enter your Garmin email and password in the sidebar.")
    st.stop()
info1 = st.info(f"Logging in {email}...")
if ("client" not in st.session_state):
    client = get_client(email, password)
    st.session_state.client = client
client = st.session_state.client
info1.empty()
if view == 'Daily':
    day_tab, activity_tab = st.tabs([
        "Daily",
        "Activity"
        ]) 
    
    with day_tab:
        df_hr = get_day_hr_data(date, client, email)
        df_stress = get_day_stress_data(date, client, email)
        fig_day = plot_day_overview2(df_hr, df_stress, year, month, day, client)
        st.pyplot(fig_day, use_container_width=True)
    
    
    with activity_tab:
        if month<10:
            month = f'0{month}'
        if day<10:
            day = f'0{day}'
        date_ref = f"{year}-{month}-{day}"
        activities = client.get_activities_by_date(date_ref, date_ref)
        
        activity_names = [
        f"{a['startTimeLocal'][11:16]} - {a['activityType']['typeKey']} - {a['activityName']}"
        for a in activities
        ]
        if len(activity_names)>0:
            selected = st.sidebar.selectbox(
            "Activity",
            activity_names, index = 0
            )
        else:
            selected = 'None'

        if selected != "None":
            idx = activity_names.index(selected)
            activity = activities[idx]

            activity_id = activity["activityId"]

            details = client.get_activity_details(activity_id)
            try:
                if activity['activityType']['typeKey'] != 'running':
                    st.info('No running activity selected.')

                else:
                    fig_act = plot_running_activity_overview(activity,details)
                    if isinstance(fig_act, bool):
                        st.info('No details found.')
                    else:
                        st.pyplot(fig_act, use_container_width=True)
            except:
                st.info('Problem occurred.')
        else:
            activity = None
            st.info("No activity selected.")            
        
else:
    year_tab = st.tabs([
            "Year",
            ])[0]
    with year_tab:
        df = get_year_data(year_ov, client, email)
        fig = plot_year_overview(df, year_ov)
        st.pyplot(fig, use_container_width=True)

