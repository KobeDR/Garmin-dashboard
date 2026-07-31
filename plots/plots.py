import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd
from analysis.metrics import METRICS
from analysis.smoothing import smooth
from datetime import datetime, timedelta
import io
fact = 1

def plot_year_overview2(df, year, client):
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    grey_months = ['Feb', 'Apr', 'June', 'Aug', 'Oct', 'Dec']
    activities = client.get_activities_by_date(f"{year}-01-01", f"{year}-12-31")
    running_dist = 0
    vo2max_list = []
    num_of_activities = len(activities)
    activityTypes = []
    for activity in activities:
        try:
            activityTypes.append(activity['activityType']['typeKey'])
            if activity['activityType']['typeKey'] == 'running':
                vo2max_list.append(activity['vO2MaxValue'])
                running_dist+= activity['distance']
        except:
            continue
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Inter'

    # Optional: Ensure minus signs render correctly with custom fonts
    plt.rcParams['axes.unicode_minus'] = False
    fig = plt.figure(figsize=(16*fact, 7*fact), dpi=500, constrained_layout=True)
    
    gs = GridSpec(
        4,
        2,
        figure=fig,
        width_ratios=[2, 2],   # left plots wider
        hspace=0.15,
        wspace=0.2,
    )

    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[0, 0])
    ax3 = fig.add_subplot(gs[2, 0])
    ax4 = fig.add_subplot(gs[3, 0])
    ax_pie     = fig.add_subplot(gs[:3, 1])
    ax_summary = fig.add_subplot(gs[3, 1])   # top half
    colors = ('red', 'purple', 'blue', 'orange')
    color_ind = 0
    for ax, (metric, title) in zip(
        (ax1, ax2, ax3, ax4),METRICS):
        months = df['month']
        y = df[metric]
        y = [i if i is not None else np.nan for i in y]
        x = list(range(len(y)))
        x = [i for i,j in zip(x, y) if np.isfinite(j)]
        y = [i for i in y if np.isfinite(i)]
        
        color = colors[color_ind]
        ax.plot(x,y, c= color)
        ax.fill_between(x, y, color = color, alpha = 0.3)
        color_ind+=1
        for grey_month in grey_months:
            indices = [i for i,x in enumerate(months) if month_names[int(x)-1] == grey_month]
            start = indices[0]
            end = indices[-1]
            ax.axvspan(start, end, color = 'gray', alpha = 0.3)
        try:
            xs, ys = smooth(x, y)
            ax.plot(xs, ys, c = 'black')
        except:
            print('Smoothing skipped')


        ax.set_xlim(0, df.shape[0])
        ymax = pd.Series(y).quantile(0.99)
        ymin = pd.Series(y).quantile(0.01)
        ax.set_ylim(ymin*0.95, ymax * 1.05)
        ax.set_ylabel(title)
        ax.set_xticks([])
        ax.grid(alpha=.3)
    ax4.set_xlabel('Time')
    ax4.set_ylim(0, 100)
    loc = []
    for mon in month_names:
        indices = [i for i,x in enumerate(months) if month_names[int(x)-1] == mon]
        loc.append(int(round(np.mean(indices))))
    ax4.set_xticks(loc)
    ax4.set_xticklabels(month_names)
    ax4.tick_params(axis = 'x', labelrotation = 45)
    
    ax_summary.axis("off")
    try:
        avg_resthr = f"{round(np.mean([i for i in df['restingHeartRate'] if i >0]))} bpm"
    except:
        avg_resthr = ""

    try:
        avg_bb = f"{round(np.mean([i for i in df['bodyBatteryHighestValue'] if i >0]))} %"
    except:
        avg_bb = ""
    try:
        avg_sleeping_time = f"{round(np.mean([i/60/60 for i in df['sleepingSeconds'] if i >0]))} h"
    except:
        avg_sleeping_time = ""        
    
    try:
        avg_active_time = f"{round(np.mean([(i+j)/60 for i,j in zip(df['highlyActiveSeconds'], df['activeSeconds']) if ((i >0) or (j>0))]))} min"
    except:
        avg_active_time = ""
    try:
        avg_steps = f"{round(np.mean([i for i in df['totalSteps'] if i >0]))}"
    except:
        avg_steps = "" 
    try:
        vO2MaxValue = f"{vo2max_list[-1]}"
    except:
        vO2MaxValue = "" 
    try:
        calories = f"{round(np.mean([i for i in df['totalKilocalories'] if i >0]))}"
    except:
        calories = ""
    if num_of_activities>0:
        num_activities = f"{num_of_activities}"
    else:
        num_activities= ""
    
    if running_dist >0:
        run_dist= f"{round(running_dist/1000)} km"
    else:
        run_dist = ""


    stats = [
        ("Average rest HR", avg_resthr),
        ("Average waking body battery", avg_bb),
        ("Average sleeping time", avg_sleeping_time),
        ("Average active time", avg_active_time),
        ("Average steps", avg_steps),
        ('Average calories', calories),
        ('# Activities', num_activities),
        ('Total running distance', run_dist),
        ('VO2Max', vO2MaxValue),
    ]

    y = 0.9

    for label, value in stats:

        ax_summary.text(
            0.2,
            y,
            label,
            fontsize=11,
            color="gray",
        )

        ax_summary.text(
            0.7,
            y,
            value,
            fontsize=12,
        )

        y -= 0.2


    plt.rcParams['font.family'] = 'sans-serif'

    plt.rcParams['font.sans-serif'] = 'Inter'

    # Optional: Ensure minus signs render correctly with custom fonts
    plt.rcParams['axes.unicode_minus'] = False
    try:
        activity_names = [i.title() for i in list(pd.Series(activityTypes).value_counts().index)]
        zones = []
        for nam in activity_names:
            zones.append(len([i for i in activityTypes if i.title() == nam]))

        labels = activity_names

        colors = [
            "#2E91E5", "#E15F99", "#1CA71C", "#FB0D0D",
            "#DA16FF", "#222A2A", "#B68100", "#750D86",
            "#EB663B", "#511CFB", "#00A08B", "#FB00D1",
            "#FC0080", "#B2828D", "#6C7C32", "#778AAE",
            "#862A16", "#A777F1", "#620042", "#1616A7"
        ]

        wedges, texts, autotexts = ax_pie.pie(
            zones,
            labels=labels,                 # legend elsewhere
            colors=colors,
            startangle=90,
            counterclock=False,
            autopct="%1.0f%%",

            # <-- Move percentages outward
            pctdistance=0.76,

            # Donut
            wedgeprops={
                "width":0.42,
                "edgecolor":"white",
                "linewidth":2,
            },

            # <-- White percentages
            textprops={
                "color":"white",
                "fontsize":10,
                "fontweight":"bold",
            },
        )
    except:
        zones = [
            100
        ]


        labels = [
            "No data"
        ]
        colors = [
            "grey",  # Zone 5
        ]

        wedges, texts, autotexts = ax_pie.pie(
            zones,
            labels=labels,                 # legend elsewhere
            colors=colors,
            startangle=90,
            counterclock=False,
            autopct="%1.0f%%",

            # <-- Move percentages outward
            pctdistance=0.76,

            # Donut
            wedgeprops={
                "width":0.42,
                "edgecolor":"white",
                "linewidth":2,
            },

            # <-- White percentages
            textprops={
                "color":"white",
                "fontsize":10,
                "fontweight":"bold",
            },
        )
    ax_pie.legend(
        wedges,
        labels,
        title="Activities",
        loc="center left",
        bbox_to_anchor=(1.05, 0.5),
        frameon=False,
    )

    # Centre text
    ax_pie.set_title("Activities")

    ax_pie.set(aspect="equal")
    
    fig.suptitle(f'{year}')

    plt.tight_layout()

    return fig
def plot_running_activity_overview(activity,activity_details):
    def pace_formatter(x, pos):
        minutes = int(x)
        seconds = int(round((x - minutes) * 60))

        # Handle rounding (e.g. 5.999 -> 6:00)
        if seconds == 60:
            minutes += 1
            seconds = 0

        return f"{minutes}:{seconds:02d}"
    
    if activity_details['detailsAvailable']:
        di = {}
        try:
            speed_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'directSpeed'][0]
            di['mpkm'] = [1000/((i['metrics'][speed_index]*60)) if (i['metrics'][speed_index]*60) > 0 else np.nan for i in activity_details['activityDetailMetrics']]
        except:
            print('Fail')
        try: 
            duration_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'sumDuration'][0]
            di['durationSeconds'] = [(i['metrics'][duration_index])  for i in activity_details['activityDetailMetrics'] ]
        except:
            print('Fail')
        try:
            elevation_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'directElevation'][0]
            di['ElevationMeters'] = [(i['metrics'][elevation_index])  for i in activity_details['activityDetailMetrics'] ]
        except:
            print('Fail')
        try:
            hr_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'directHeartRate'][0]
            di['HR'] = [(i['metrics'][hr_index])  for i in activity_details['activityDetailMetrics'] ]
        except:
            print('Fail')
        try:
            cadence_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'directDoubleCadence'][0]
            di['Cadence'] = [(i['metrics'][cadence_index])  for i in activity_details['activityDetailMetrics'] ]
        except:
            print('Fail')    
        try:
            temp_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'directAirTemperature'][0]
            di['Temp'] = [(i['metrics'][temp_index])  for i in activity_details['activityDetailMetrics'] ]
        except:
            print('Fail')
        
        df = pd.DataFrame(di)
        fig = plt.figure(figsize=(16*fact, 7*fact), dpi=500, constrained_layout=True)

        gs = GridSpec(
            4,
            2,
            figure=fig,
            width_ratios=[2, 2],   # left plots wider
            hspace=0.15,
            wspace=0.2,
        )

        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
        ax3 = fig.add_subplot(gs[2, 0], sharex=ax1)
        ax4 = fig.add_subplot(gs[3, 0], sharex=ax1)

        ax_pie     = fig.add_subplot(gs[:3, 1])
        ax_summary = fig.add_subplot(gs[3, 1])   # top half
            # spans all rows
        
        for ax in (ax1, ax2, ax3):
            ax.tick_params(labelbottom=False)
        
        try:
            ax2.plot(df['durationSeconds'], df['mpkm'], c = 'blue')
            ax2.fill_between(df['durationSeconds'], df['mpkm'], color = 'blue', alpha = 0.3)
            ax2.yaxis.set_major_formatter(FuncFormatter(pace_formatter))
            ymax = df["mpkm"].quantile(0.99)
            ymin = df["mpkm"].quantile(0.01)
            ax2.set_ylim(ymin*0.95, ymax * 1.05)
        except:
            ax2.set_ylim(0, 100)
            print('Skipping HR')
        
        ax2.set_xlim(0, df['durationSeconds'].iloc[-1])
        ax2.grid(alpha=.3)
        ax2.set_ylabel('Speed (min/km)')
        ax2_2 = ax2.twinx()
        ax2_2.fill_between(df['durationSeconds'], df['ElevationMeters'], color = 'grey', alpha = 0.3)
        ax2_2.set_yticks([])
        ax2_2.set_ylim(0, np.max(df['ElevationMeters'])+20)

        try:
            ax3.plot(df['durationSeconds'], df['Cadence'], c = 'orange')
            ax3.fill_between(df['durationSeconds'], df['Cadence'], color = 'orange', alpha = 0.3)
            ymax = df["Cadence"].quantile(0.99)
            ymin = df["Cadence"].quantile(0.01)
            ax3.set_ylim(ymin*0.95, ymax * 1.05)
        except:
            print('Skipping cadence')
            ax3.set_ylim(0, 100)
        
        ax3.set_xlim(0, df['durationSeconds'].iloc[-1])
        ax3.grid(alpha=.3)
        ax3.set_ylabel('Cadence (spm)')
        ax3_2 = ax3.twinx()
        ax3_2.fill_between(df['durationSeconds'], df['ElevationMeters'], color = 'grey', alpha = 0.3)
        ax3_2.set_yticks([])

        ax3_2.set_ylim(0, np.max(df['ElevationMeters'])+20)

        
        try:
            ax1.plot(df['durationSeconds'], df['HR'], c = 'red')
            ax1.fill_between(df['durationSeconds'], df['HR'], color = 'red', alpha = 0.3)
            ymax = df["HR"].quantile(0.99)
            ymin = df["HR"].quantile(0.01)
            ax1.set_ylim(ymin*0.95, ymax * 1.05)
            
            
        except:
            ax1.set_ylim(0, 100)
            print('Skipping HR')
        
        ax1.set_xlim(0, df['durationSeconds'].iloc[-1])
        ax1.grid(alpha=.3)
        ax1.set_ylabel('HR (bpm)')
        ax1_2 = ax1.twinx()
        ax1_2.set_yticks([])
        ax1_2.fill_between(df['durationSeconds'], df['ElevationMeters'], color = 'grey', alpha = 0.3)

        

        ax1_2.set_ylim(0, np.max(df['ElevationMeters'])+20)
        
        try:
            ax4.plot(df['durationSeconds'], df['Temp'], c = 'purple')
            ax4.fill_between(df['durationSeconds'], df['Temp'], color = 'purple', alpha = 0.3)
            ymax = df["Temp"].quantile(0.99)
            ymin = df["Temp"].quantile(0.01)
            ax4.set_ylim(ymin*0.95, ymax * 1.05)
        except:
            ax4.set_ylim(0, 100)
            print('Skipping Temp')
            
            
        ax4.set_xlim(0, df['durationSeconds'].iloc[-1])
        ax4.grid(alpha=.3)
        ax4.set_ylabel('Temperature (Celsius)')
        ax4_2 = ax4.twinx()
        ax4_2.fill_between(df['durationSeconds'], df['ElevationMeters'], color = 'grey', alpha = 0.3)
        ax4_2.set_yticks([])
        ax4_2.set_ylim(0, np.max(df['ElevationMeters'])+20)
        
        ax4.set_xlabel('Time (seconds)')

        

        ax_summary.axis("off")
        try:
            avg_pace = f"{int(activity['averageSpeed']**-1 * 1000 // 60)}:{int((1000/activity['averageSpeed']) % 60):02d} min/km"
        except:
            avg_pace = ""

        try:
            max_pace = f"{int(activity['maxSpeed']**-1 * 1000 // 60)}:{int((1000/activity['maxSpeed']) % 60):02d} min/km"
        except:
            max_pace = ""
        try:
            avg_hr = f"{round(activity['averageHR'])} bpm"
        except:
            avg_hr = ""        
        
        try:
            max_hr = f"{round(activity['maxHR'])} bpm"
        except:
            max_hr = ""  
        try:
            elev = f"{activity['elevationGain']:.0f} m"
        except:
            elev = "" 
        try:
            vO2MaxValue = f"{activity['vO2MaxValue']:.0f}"
        except:
            vO2MaxValue = "" 
        try:
            calories = f"{activity['calories']:.0f}"
        except:
            calories = ""

        try:
            duration = str(timedelta(seconds=int(activity["duration"])))
        except:
            duration = "00:00:00"


        stats = [
            ("Average pace", avg_pace),
            ("Max pace", max_pace),
            ("Average HR", avg_hr),
            ("Max HR", max_hr),
            ("Elevation gain", elev),
            ('vO2Max', vO2MaxValue),
            ('Calories burned', calories)
        ]

        y = 0.9

        for label, value in stats:

            ax_summary.text(
                0.2,
                y,
                label,
                fontsize=11,
                color="gray",
            )

            ax_summary.text(
                0.7,
                y,
                value,
                fontsize=12,
            )

            y -= 0.2


        plt.rcParams['font.family'] = 'sans-serif'

        plt.rcParams['font.sans-serif'] = 'Inter'

        # Optional: Ensure minus signs render correctly with custom fonts
        plt.rcParams['axes.unicode_minus'] = False
        try:
            zones = [
                activity['hrTimeInZone_1'],
                activity['hrTimeInZone_2'],
                activity['hrTimeInZone_3'],
                activity['hrTimeInZone_4'],
                activity['hrTimeInZone_5']
            ]


            labels = [
                "Zone 1",
                "Zone 2",
                "Zone 3",
                "Zone 4",
                "Zone 5"
            ]
            colors = [
                "#4F7FD9",  # Zone 1
                "#5DAA68",  # Zone 2
                "#FF8C1A",  # Zone 3
                "#D83A34",  # Zone 4
                "#7E3FA3",  # Zone 5
            ]

            wedges, texts, autotexts = ax_pie.pie(
                zones,
                labels=labels,                 # legend elsewhere
                colors=colors,
                startangle=90,
                counterclock=False,
                autopct="%1.0f%%",

                # <-- Move percentages outward
                pctdistance=0.76,

                # Donut
                wedgeprops={
                    "width":0.42,
                    "edgecolor":"white",
                    "linewidth":2,
                },

                # <-- White percentages
                textprops={
                    "color":"white",
                    "fontsize":10,
                    "fontweight":"bold",
                },
            )
        except:
            zones = [
                100
            ]


            labels = [
                "No data"
            ]
            colors = [
                "grey",  # Zone 5
            ]

            wedges, texts, autotexts = ax_pie.pie(
                zones,
                labels=labels,                 # legend elsewhere
                colors=colors,
                startangle=90,
                counterclock=False,
                autopct="%1.0f%%",

                # <-- Move percentages outward
                pctdistance=0.76,

                # Donut
                wedgeprops={
                    "width":0.42,
                    "edgecolor":"white",
                    "linewidth":2,
                },

                # <-- White percentages
                textprops={
                    "color":"white",
                    "fontsize":10,
                    "fontweight":"bold",
                },
            )
        ax_pie.legend(
            wedges,
            labels,
            title="HR Zones",
            loc="center left",
            bbox_to_anchor=(1.05, 0.5),
            frameon=False,
        )

        # Centre text
        ax_pie.set_title("Time in HR Zones")
        ax_pie.text(
            0,
            0.05,
            str(timedelta(seconds=df['durationSeconds'].iloc[-1])),
            ha="center",
            va="center",
            fontsize=15,
            fontweight="bold",
        )

        ax_pie.text(
            0,
            -0.12,
            "Total Time",
            ha="center",
            va="center",
            fontsize=10,
            color="dimgray",
        )

        ax_pie.set(aspect="equal")
        
        fig.suptitle(f"{activity['startTimeLocal']} - {activity['activityType']['typeKey']} - {activity['activityName']}")
        plt.tight_layout()

        return fig
    else:
        return False
    
    
def plot_day_overview2(df_hr, df_stress, year, month, day, client):
    xlims_min = []
    xlims_max = []
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    mon = month_names[month-1]
    fig = plt.figure(figsize=(16*fact, 7*fact), dpi=500, constrained_layout=True)
    
    gs = GridSpec(
        4,
        2,
        figure=fig,
        width_ratios=[2, 2],   # left plots wider
        hspace=0.15,
        wspace=0.2,
    )

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
    ax3 = fig.add_subplot(gs[2, 0], sharex=ax1)
    ax4 = fig.add_subplot(gs[3, 0], sharex=ax1)

    ax_pie     = fig.add_subplot(gs[:3, 1])
    ax_summary = fig.add_subplot(gs[3, 1])
    for ax in (ax1, ax2, ax3):
        ax.tick_params(labelbottom=False)
    if month<10:
        month = f'0{month}'
    if day<10:
        day = f'0{day}'
    date_ref = f"{year}-{month}-{day}"
    stats = client.get_stats(date_ref)
    y = df_hr['HR']
    y = [i if i is not None else np.nan for i in y]
    x = [datetime.fromtimestamp(int(i) / 1000) + timedelta(hours = 2) for i in df_hr['Timepoint']]
    x_timestamps = [int(i)/1000 for i in df_hr['Timepoint']]
    x = [i for i,j in zip(x, y) if np.isfinite(j)]
    x_timestamps = [i for i,j in zip(x_timestamps, y) if np.isfinite(j)]
    y = [i for i in y if np.isfinite(i)]
    try:
        xlims_min.append(x[0])
        xlims_max.append(x[-1])
    except:
        print('Fail')
    
    
    ax1.plot(x,y, c= 'red')
    ax1.fill_between(x,y, alpha=.3, color= 'red')
    try:
        ymax = pd.Series(y).quantile(0.99)
        ymin = pd.Series(y).quantile(0.01)
        ax1.set_ylim(ymin*0.95, ymax * 1.05)
    except:
        ax1.set_ylim(0, 100)
        print('Fail')
    try:
        all_sleep = client.get_sleep_data(date_ref)
        sleep = all_sleep['dailySleepDTO']
        start_sleep = datetime.fromtimestamp(sleep['sleepStartTimestampGMT']/1000) + timedelta(hours = 2)
        end_sleep = datetime.fromtimestamp(sleep['sleepEndTimestampGMT']/1000) + timedelta(hours = 2)
        ax1.axvspan(start_sleep, end_sleep, color = 'gray', alpha = 0.3)
    except:
        print('Sleep skipped')
    
    
        

    activities = client.get_activities_by_date(date_ref, date_ref)
    if len(activities) > 0:
        for activity in activities:
            start_act = datetime.strptime(activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S") + timedelta(hours = 2)
            end_act = start_act + timedelta(seconds = activity['duration'])
            ax1.axvspan(start_act, end_act, color = 'green', alpha = 0.3)
            

    
    ax1.tick_params(axis = 'x', labelrotation = 45)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax1.set_ylabel('HR (BPM)')
    ax1.grid(alpha=.3)
    
    
    
    
    
    
    y = df_stress['Stress']
    y = [i if i is not None else np.nan for i in y]
    x = [datetime.fromtimestamp(int(i) / 1000) + timedelta(hours = 2) for i in df_stress['Timepoint']]
    x_timestamps = [int(i)/1000 for i in df_stress['Timepoint']]

    x = [i for i,j in zip(x, y) if np.isfinite(j)]
    x_timestamps = [i for i,j in zip(x_timestamps, y) if np.isfinite(j)]

    y = [i for i in y if np.isfinite(i)]
    
    try:
        xlims_min.append(x[0])
        xlims_max.append(x[-1])
    except:
        print('Fail')
    ax2.plot(x,y, c= 'orange')
    ax2.fill_between(x,y, alpha=.3, color= 'orange')
    try:
        ax2.axvspan(start_sleep, end_sleep, color = 'gray', alpha = 0.3)
    except:
        print('Sleep skipped.')
    if len(activities) > 0:
        for activity in activities:
            start_act = datetime.strptime(activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S") + timedelta(hours = 2)
            end_act = start_act + timedelta(seconds = activity['duration'])
            ax2.axvspan(start_act, end_act, color = 'green', alpha = 0.3)



    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax2.set_ylabel('Stress %')
    try:
        ymax = pd.Series(y).quantile(0.99)
        ymin = pd.Series(y).quantile(0.01)
        ax2.set_ylim(ymin*0.95, ymax * 1.05)
    except:
        ax2.set_ylim(0, 100)
        print('Fail')
    ax2.grid(alpha=.3)
    ax3.grid(alpha=.3)
    ax3.set_ylabel('# Steps')
    ax4.grid(alpha=.3)
    ax4.set_ylabel('Body battery %')
    ax4.set_ylim(0, 100)
    try:
        steps = client.get_steps_data(date_ref)
        steps_df = pd.DataFrame(steps)
        steps_df['startGMT'] = pd.to_datetime(steps_df['startGMT'])+ timedelta(hours = 2)
        steps_df['steps_cumsum'] = steps_df['steps'].cumsum()
        xlims_min.append(steps_df['startGMT'].iloc[0])
        xlims_max.append(steps_df['startGMT'].iloc[-1])
        ax3.plot(steps_df['startGMT'],steps_df['steps_cumsum'], c= 'blue')
        ax3.fill_between(steps_df['startGMT'],steps_df['steps_cumsum'], color="blue", alpha=0.3)
        try:
            ax3.axvspan(start_sleep, end_sleep, color = 'gray', alpha = 0.3)
        except:
            print('Sleep skipped.')
        if len(activities) > 0:
            for activity in activities:
                start_act = datetime.strptime(activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S") + timedelta(hours = 2)
                end_act = start_act + timedelta(seconds = activity['duration'])
                ax3.axvspan(start_act, end_act, color = 'green', alpha = 0.3)
        ax3.set_ylim(0, (steps_df['steps_cumsum'].iloc[-1])+3000)
        ax3.tick_params(axis = 'x', labelrotation = 45)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        
    except:
        ax3.set_ylim(0, 100)
        print('Steps skipped.')
        
    try:
        bb = client.get_body_battery(date_ref)
        bb_df = pd.DataFrame(bb[0]['bodyBatteryValuesArray'], columns = ['Timepoint', 'BB'])
        bb_df['Timepoint'] = [datetime.fromtimestamp(i/1000) + timedelta(hours = 2) for i in bb_df['Timepoint']]
        xlims_min.append(bb_df['Timepoint'].iloc[0])
        xlims_max.append(bb_df['Timepoint'].iloc[-1])
        ax4.plot(bb_df['Timepoint'],bb_df['BB'], color= 'purple')
        ax4.fill_between(bb_df['Timepoint'],bb_df['BB'], color= 'purple', alpha = 0.3)
        try:
            ax4.axvspan(start_sleep, end_sleep, color = 'gray', alpha = 0.3)
        except:
            print('Sleep skipped.')
        if len(activities) > 0:
            for activity in activities:
                start_act = datetime.strptime(activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S") + timedelta(hours = 2)
                end_act = start_act + timedelta(seconds = activity['duration'])
                ax4.axvspan(start_act, end_act, color = 'green', alpha = 0.3)
        ax4.tick_params(axis = 'x', labelrotation = 45)
        ax4.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        
    except:
        ax4.set_ylim(0, 100)
        print('Body battery skipped.')
    now = datetime.now()
    datetime_now = pd.to_datetime(now) + timedelta(hours = 2)
    try:
        td = np.min(xlims_min)
        td = td.replace(hour = 0)
        td = td.replace(minute = 0)
        td = td.replace(second = 0)
        nd = td + timedelta(hours=24)
        for ax in (ax1, ax2, ax3, ax4):
            ax.set_xlim(td, nd)
            if ((datetime_now < nd) and (datetime_now > td)):
                ax.axvline(x = datetime_now, color = 'black', ls = '--', lw = 0.5, label = 'now')
            
        
            
    except:
        print('Fail')
    ax4.set_ylabel('Time')
    try:
        if ((datetime_now < nd) and (datetime_now > td)):
            if (now.hour+2) <10:
                hour_now = f'0{now.hour+2}'
            else:
                hour_now = now.hour+2
            if now.minute<10:
                minute_now = f'0{now.minute}'
            else:
                minute_now = now.minute
            fig.suptitle(f"{day} {mon} {year} - {hour_now}:{minute_now}")
        else:
            fig.suptitle(f"{day} {mon} {year}")
    except:
        fig.suptitle(f"{day} {mon} {year}")
    
    
    ax_summary.axis("off")
    




    

    
    try:
        sleep_overall = f"{sleep['sleepScores']['overall']['value']} - {sleep['sleepScores']['overall']['qualifierKey']}"
    except:
        sleep_overall = ""
    try:
        slp_time = stats['sleepingSeconds']/60/60
        sleep_time = f'{'{0:02.0f}:{1:02.0f}'.format(*divmod(slp_time * 60, 60))} h'
    except:
        sleep_time = ""
    try:
        sleep_awakecount = sleep['sleepScores']['awakeCount']['qualifierKey']
    except:
        sleep_awakecount=""
    try:
        sleep_restlessness = sleep['sleepScores']['restlessness']['qualifierKey']
    except:
        sleep_restlessness = ""
    try:
        sleep_stress = sleep['sleepScores']['stress']['qualifierKey']
    except:
        sleep_stress = ""
    try:
        avg_hr = f"{round(np.mean(df_hr['HR']))} bpm"
    except:
        avg_hr = ""
    try:
        max_hr = f"{round(np.max(df_hr['HR']))} bpm"
    except:
        max_hr = ""    
    try:
        activekcal = f"{round(stats['activeKilocalories'])} calories"
    except:
        activekcal = ""        
    try:
        steps_n = steps_df['steps'].cumsum().iloc[-1]
    except:
        steps_n = ""

        
    stats = [
        ("Average HR", avg_hr),
        ("Max HR", max_hr),
        ("# Steps", steps_n),
        ('Active calories burned', activekcal),
        ("Overall sleep score", sleep_overall),
        ("Sleep time", sleep_time),
        ('Sleep stress', sleep_stress),
        ('Sleep awakeness', sleep_awakecount),
        ('Sleep restlessness', sleep_restlessness),
        
    ]

    y = 0.9

    for label, value in stats:

        ax_summary.text(
            0.2,
            y,
            label,
            fontsize=11,
            color="gray",
        )

        ax_summary.text(
            0.7,
            y,
            value,
            fontsize=12,
        )

        y -= 0.2



    plt.rcParams['font.family'] = 'sans-serif'

    plt.rcParams['font.sans-serif'] ='Inter'

    # Optional: Ensure minus signs render correctly with custom fonts
    plt.rcParams['axes.unicode_minus'] = False    
    
    try:
        colors = [
                "#4F7FD9",  # Zone 1
                "#FF8C1A",  # Zone 3
                "#D83A34",  # Zone 4
        ]
            
        zones = [
                sleep['sleepScores']['remPercentage']['value'],
                sleep['sleepScores']['lightPercentage']['value'],
                sleep['sleepScores']['deepPercentage']['value'],
        ]
        
        
        labels = [
            "REM",
            "Light",
            "Deep"
        ]
        
        wedges, texts, autotexts = ax_pie.pie(
            zones,
            labels=labels,                 # legend elsewhere
            colors=colors,
            startangle=90,
            counterclock=False,
            autopct="%1.0f%%",

            # <-- Move percentages outward
            pctdistance=0.76,

            # Donut
            wedgeprops={
                "width":0.42,
                "edgecolor":"white",
                "linewidth":2,
            },

            # <-- White percentages
            textprops={
                "color":"white",
                "fontsize":10,
                "fontweight":"bold",
            },
        )
    
    except:
        colors = [
                "grey"
        ]
        
        zones = [
                100
            ]
        
        
        labels = [
            "No data"
        ]
        
        wedges, texts, autotexts = ax_pie.pie(
            zones,
            labels=labels,                 # legend elsewhere
            colors=colors,
            startangle=90,
            counterclock=False,
            autopct="%1.0f%%",

            # <-- Move percentages outward
            pctdistance=0.76,

            # Donut
            wedgeprops={
                "width":0.42,
                "edgecolor":"white",
                "linewidth":2,
            },

            # <-- White percentages
            textprops={
                "color":"white",
                "fontsize":10,
                "fontweight":"bold",
            },
        )
        
    ax_pie.legend(
        wedges,
        labels,
        title="Sleep zones",
        loc="center left",
        bbox_to_anchor=(1.05, 0.5),
        frameon=False,
    )

    # Centre text
    ax_pie.set_title("Sleep analysis")
    ax4.set_xlabel('Time (seconds)')


    ax_pie.set(aspect="equal")
    
    plt.tight_layout()

    return fig