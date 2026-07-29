import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
from analysis.metrics import METRICS
from analysis.smoothing import smooth
from datetime import datetime, timedelta

def plot_year_overview(df, year):
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    grey_months = ['Feb', 'Apr', 'June', 'Aug', 'Oct', 'Dec']
    fig, axs = plt.subplots(
        5,
        2,
        figsize=(12,15),dpi = 1000,
        sharex=True
    )

    for ax, (metric, title) in zip(
        axs.flat,
        METRICS
    ):
        months = df['month']
        y = df[metric]
        y = [i if i is not None else np.nan for i in y]
        x = list(range(len(y)))
        x = [i for i,j in zip(x, y) if np.isfinite(j)]
        y = [i for i in y if np.isfinite(i)]
        
        
        ax.plot(x,y, alpha=.3, c= 'black')
        for grey_month in grey_months:
            indices = [i for i,x in enumerate(months) if month_names[int(x)-1] == grey_month]
            start = indices[0]
            end = indices[-1]
            ax.axvspan(start, end, color = 'gray', alpha = 0.3)
        try:
            xs, ys = smooth(x, y)
            ax.plot(xs, ys, c = 'red')
        except:
            print('Smoothing skipped')
        ax.axhline(
            np.mean(y),
            ls="--", c = 'blue'
        )
        if("Battery" in metric) or ("Perc" in metric):
            ax.set_ylim(0, 100)
        ax.set_xlim(0, df.shape[0])
        ax.set_xticks([])
        loc = []
        for mon in month_names:
            indices = [i for i,x in enumerate(months) if month_names[int(x)-1] == mon]
            loc.append(int(round(np.mean(indices))))
        ax.set_xticks(loc)
        ax.set_xticklabels(month_names)
        ax.tick_params(axis = 'x', labelrotation = 45)
        ax.set_title(title)
        ax.set_ylabel(title)

        ax.grid(alpha=.3)
    fig.supxlabel('Time')
    fig.suptitle(f'{year}')

    plt.tight_layout()

    return fig

def plot_day_overview(df_hr, df_stress, year, month, day, client):
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    mon = month_names[month-1]
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(
        2,
        2,
        figsize=(12,6),dpi = 1000,
        sharex = True
    )
    if month<10:
        month = f'0{month}'
    if day<10:
        day = f'0{day}'
    date_ref = f"{year}-{month}-{day}"
    stats = client.get_stats(date_ref)
    y = df_hr['HR']
    y = [i if i is not None else np.nan for i in y]
    x = [datetime.fromtimestamp(int(i) / 1000) for i in df_hr['Timepoint']]
    x_timestamps = [int(i)/1000 for i in df_hr['Timepoint']]
    x = [i for i,j in zip(x, y) if np.isfinite(j)]
    x_timestamps = [i for i,j in zip(x_timestamps, y) if np.isfinite(j)]
    y = [i for i in y if np.isfinite(i)]
    
    
    ax1.plot(x,y, alpha=.3, c= 'black')
    try:
        sleep = client.get_sleep_data(date_ref)['dailySleepDTO']
        start_sleep = datetime.fromtimestamp(sleep['sleepStartTimestampGMT']/1000)
        end_sleep = datetime.fromtimestamp(sleep['sleepEndTimestampGMT']/1000)
        ax1.axvspan(start_sleep, end_sleep, color = 'gray', alpha = 0.3)
    except:
        print('Sleep skipped')
    
    
        

    activities = client.get_activities_by_date(date_ref, date_ref)
    if len(activities) > 0:
        for activity in activities:
            start_act = datetime.strptime(activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S")
            end_act = start_act + timedelta(seconds = activity['duration'])
            ax1.axvspan(start_act, end_act, color = 'orange', alpha = 0.3)
            
    try:
        xs, ys = smooth(x_timestamps, y)
        xs = [datetime.fromtimestamp(int(round(i))) for i in xs]
        ax1.plot(xs, ys, c = 'red')
    except:
        print('Smoothing skipped')
    ax1.axhline(
        np.mean(y),
        ls="--", c = 'blue'
    )
    
    ax1.tick_params(axis = 'x', labelrotation = 45)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax1.set_ylabel('HR (BPM)')
    ax1.grid(alpha=.3)
    fig.supxlabel('Time')
    
    
    
    
    
    
    y = df_stress['Stress']
    y = [i if i is not None else np.nan for i in y]
    x = [datetime.fromtimestamp(int(i) / 1000) for i in df_stress['Timepoint']]
    x_timestamps = [int(i)/1000 for i in df_stress['Timepoint']]

    x = [i for i,j in zip(x, y) if np.isfinite(j)]
    x_timestamps = [i for i,j in zip(x_timestamps, y) if np.isfinite(j)]

    y = [i for i in y if np.isfinite(i)]
    
    
    ax2.plot(x,y, alpha=.3, c= 'black')
    try:
        ax2.axvspan(start_sleep, end_sleep, color = 'gray', alpha = 0.3)
    except:
        print('Sleep skipped.')
    if len(activities) > 0:
        for activity in activities:
            start_act = datetime.strptime(activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S")
            end_act = start_act + timedelta(seconds = activity['duration'])
            ax2.axvspan(start_act, end_act, color = 'orange', alpha = 0.3)
    try:
        xs, ys = smooth(x_timestamps, y)
        xs = [datetime.fromtimestamp(int(round(i))) for i in xs]
        ax2.plot(xs, ys, c = 'red')
    except:
        print('Smoothing skipped')
    ax2.axhline(
        np.mean(y),
        ls="--", c = 'blue'
    )

    # ax.set_ylim(0, 100)
    ax2.tick_params(axis = 'x', labelrotation = 45)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax2.set_ylabel('Stress %')
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
        ax3.plot(steps_df['startGMT'],steps_df['steps_cumsum'], c= 'blue')
        ax3.fill_between(steps_df['startGMT'],steps_df['steps_cumsum'], color="blue", alpha=0.3)
        try:
            ax3.axvspan(start_sleep, end_sleep, color = 'gray', alpha = 0.3)
        except:
            print('Sleep skipped.')
        if len(activities) > 0:
            for activity in activities:
                start_act = datetime.strptime(activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S")
                end_act = start_act + timedelta(seconds = activity['duration'])
                ax3.axvspan(start_act, end_act, color = 'orange', alpha = 0.3)
        ax3.set_ylim(0, (steps_df['steps_cumsum'].iloc[-1])+3000)
        ax3.tick_params(axis = 'x', labelrotation = 45)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        
    except:
        print('Steps skipped.')
        
    try:
        bb = client.get_body_battery(date_ref)
        bb_df = pd.DataFrame(bb[0]['bodyBatteryValuesArray'], columns = ['Timepoint', 'BB'])
        bb_df['Timepoint'] = [datetime.fromtimestamp(i/1000) for i in bb_df['Timepoint']]
        ax4.plot(bb_df['Timepoint'],bb_df['BB'], color= 'purple')
        ax4.fill_between(bb_df['Timepoint'],bb_df['BB'], color= 'purple', alpha = 0.3)
        try:
            ax4.axvspan(start_sleep, end_sleep, color = 'gray', alpha = 0.3)
        except:
            print('Sleep skipped.')
        if len(activities) > 0:
            for activity in activities:
                start_act = datetime.strptime(activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S")
                end_act = start_act + timedelta(seconds = activity['duration'])
                ax4.axvspan(start_act, end_act, color = 'orange', alpha = 0.3)
        ax4.tick_params(axis = 'x', labelrotation = 45)
        ax4.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        
    except:
        print('Body battery skipped.')
    
    
    fig.supxlabel('Time')
    try: 
        slp_time = stats['sleepingSeconds']/60/60
        fig.suptitle(f"{day} {mon} {year}\n{'{0:02.0f}:{1:02.0f}'.format(*divmod(slp_time * 60, 60))} hours slept - {round(stats['activeKilocalories'])} active calories burned")
    except:
        fig.suptitle(f"{day} {mon} {year}")
    
    
    
    plt.tight_layout()

    return fig

def plot_activity_overview(activity,activity_details):
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
        speed_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'directSpeed'][0]
        di['mpkm'] = [1000/((i['metrics'][speed_index]*60)) if (i['metrics'][speed_index]*60) > 0 else np.nan for i in activity_details['activityDetailMetrics']]
        duration_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'sumDuration'][0]
        di['durationSeconds'] = [(i['metrics'][duration_index])  for i in activity_details['activityDetailMetrics'] ]
        elevation_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'directElevation'][0]
        di['ElevationMeters'] = [(i['metrics'][elevation_index])  for i in activity_details['activityDetailMetrics'] ]
        hr_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'directHeartRate'][0]
        di['HR'] = [(i['metrics'][hr_index])  for i in activity_details['activityDetailMetrics'] ]
        cadence_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'directDoubleCadence'][0]
        di['Cadence'] = [(i['metrics'][cadence_index])  for i in activity_details['activityDetailMetrics'] ]
        temp_index = [i['metricsIndex']  for i in activity_details['metricDescriptors'] if i['key'] == 'directAirTemperature'][0]
        di['Temp'] = [(i['metrics'][temp_index])  for i in activity_details['activityDetailMetrics'] ]

        
        df = pd.DataFrame(di)
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(
            2,
            2,
            figsize=(12,6),dpi = 1000,
            sharex = True
        )
        try:
            ax1.plot(df['durationSeconds'], df['mpkm'], c = 'blue')
            ax1.fill_between(df['durationSeconds'], df['mpkm'], color = 'blue', alpha = 0.3)
            ax1.yaxis.set_major_formatter(FuncFormatter(pace_formatter))
            ax1.set_ylim(0, np.max(df['mpkm'])+1)
        except:
            print('Skipping HR')
        
        ax1.set_xlim(0, df['durationSeconds'].iloc[-1])
        ax1.grid(alpha=.3)
        ax1.set_ylabel('Speed (min/km)')
        ax1_2 = ax1.twinx()
        ax1_2.fill_between(df['durationSeconds'], df['ElevationMeters'], color = 'grey', alpha = 0.3)
        ax1_2.set_yticklabels([])
        ax1_2.set_ylim(0, np.max(df['ElevationMeters'])+20)

        try:
            ax2.plot(df['durationSeconds'], df['Cadence'], c = 'orange')
            ax2.fill_between(df['durationSeconds'], df['Cadence'], color = 'orange', alpha = 0.3)
            ax2.set_ylim(0, np.max(df['Cadence'])+10)
        except:
            print('Skipping cadence')
        
        ax2.set_xlim(0, df['durationSeconds'].iloc[-1])
        ax2.grid(alpha=.3)
        ax2.set_ylabel('Cadence (spm)')
        ax2_2 = ax2.twinx()
        ax2_2.fill_between(df['durationSeconds'], df['ElevationMeters'], color = 'grey', alpha = 0.3)
        ax2_2.set_ylabel('Elevation (meters)')
        ax2_2.set_ylim(0, np.max(df['ElevationMeters'])+20)

        
        try:
            ax3.plot(df['durationSeconds'], df['HR'], c = 'red')
            ax3.fill_between(df['durationSeconds'], df['HR'], color = 'red', alpha = 0.3)
            ax3.set_ylim(0, np.max(df['HR'])+20)
            
        except:
            print('Skipping HR')
        
        ax3.set_xlim(0, df['durationSeconds'].iloc[-1])
        ax3.grid(alpha=.3)
        ax3.set_ylabel('HR (bpm)')
        ax3_2 = ax3.twinx()
        ax3_2.fill_between(df['durationSeconds'], df['ElevationMeters'], color = 'grey', alpha = 0.3)
        ax3_2.set_yticklabels([])
        

        ax3_2.set_ylim(0, np.max(df['ElevationMeters'])+20)
        
        try:
            ax4.plot(df['durationSeconds'], df['Temp'], c = 'purple')
            ax4.fill_between(df['durationSeconds'], df['Temp'], color = 'purple', alpha = 0.3)
            ax4.set_ylim(0, np.max(df['Temp'])+5)
        except:
            print('Skipping Temp')
            
            
        ax4.set_xlim(0, df['durationSeconds'].iloc[-1])
        ax4.grid(alpha=.3)
        ax4.set_ylabel('Temperature (Celsius)')
        ax4_2 = ax4.twinx()
        ax4_2.fill_between(df['durationSeconds'], df['ElevationMeters'], color = 'grey', alpha = 0.3)
        ax4_2.set_ylabel('Elevation (meters)')
        ax4_2.set_ylim(0, np.max(df['ElevationMeters'])+20)
        
        
        fig.supxlabel('Time (seconds)')
        fig.suptitle(f"{activity['startTimeLocal']} - {activity['activityType']['typeKey']} - {activity['activityName']}")
        plt.tight_layout()

        return fig
    else:
        return False