import streamlit as st
from garminconnect import Garmin
from data.fetch import get_year_data, get_day_hr_data, get_day_stress_data, get_client
from plots.plots import plot_year_overview, plot_day_overview, plot_activity_overview
import datetime
from datetime import date
current_year = datetime.datetime.now().year

st.set_page_config(
    page_title="Garmin Dashboard",
    layout="wide"
)
st.title("Garmin Dashboard")

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


    st.divider()
    st.header('View')
    view = st.radio(
        "View",
        ['Yearly', 'Daily']
    )
    st.header('Yearly')
    year_ov = st.number_input(
        "Year",
        min_value=2015,
        max_value=current_year,
        value=current_year,
        step=1,
    )
    st.divider()
    st.header('Daily')

    date = st.date_input(
        "Date",
        value=date.today()
    )
    month = date.month
    day = date.day
    year = date.year
    generate = st.form_submit_button("Generate plot")
        
if ((not generate) and (not "initial_press" in st.session_state)):
    st.stop()
else:
    st.session_state.initial_press = True
    
if not email or not password:
    st.info("Please enter your Garmin email and password in the sidebar.")
    st.stop()
try:
    client = get_client(email, password)
except:
    st.info("Problem logging in - check email and password.")
if view == 'Daily':
    day_tab, activity_tab = st.tabs([
        "Daily",
        "Activity"
        ]) 
    
    with day_tab:
        df_hr = get_day_hr_data(date, client, email)
        df_stress = get_day_stress_data(date, client, email)
        fig_day = plot_day_overview(df_hr, df_stress, year, month, day, client)
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
            fig_act = plot_activity_overview(activity,details)
            
            if isinstance(fig_act, bool):
                st.info('No details found.')
            else:
                st.pyplot(fig_act, use_container_width=True)
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

