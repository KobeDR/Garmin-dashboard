import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from analysis.metrics import METRICS
from analysis.smoothing import smooth
from datetime import datetime, timedelta


def _finite_xy(x, y):
    """Keep the original missing-value behaviour while preparing Plotly data."""
    y = [value if value is not None else np.nan for value in y]
    return ([a for a, b in zip(x, y) if np.isfinite(b)],
            [b for b in y if np.isfinite(b)])


def _add_span(fig, start, end, color, row, col, opacity=.3):
    fig.add_vrect(x0=start, x1=end, fillcolor=color, opacity=opacity,
                  line_width=0, row=row, col=col)


def _add_activity_spans(fig, activities, row, col):
    for activity in activities:
        start = datetime.strptime(activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S") + timedelta(hours=2)
        _add_span(fig, start, start + timedelta(seconds=activity['duration']),
                  'green', row, col)


def _add_timeseries(fig, x, y, row, color, name, fill=False, col=1):
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=name,
                             line=dict(color=color),
                             fill='tozeroy' if fill else None),
                  row=row, col=col)
    if fill:
        fig.data[-1].update(fillcolor={
            'red': 'rgba(255,0,0,.3)', 'orange': 'rgba(255,165,0,.3)',
            'blue': 'rgba(0,0,255,.3)', 'purple': 'rgba(128,0,128,.3)',
            'grey': 'rgba(128,128,128,.3)'
        }.get(color, 'rgba(0,0,0,.2)'))


def _daily_layout(fig, title):
    fig.update_layout(template='plotly_white', width=1600, height=600,
                      title=dict(text=title, x=.5), showlegend=False,
                      paper_bgcolor='white', plot_bgcolor='white',
                      margin=dict(l=60, r=60, t=70, b=60))
    fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,.3)', tickformat='%H:%M')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,.3)')


def plot_year_overview(df, year):
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    grey_months = ['Feb', 'Apr', 'June', 'Aug', 'Oct', 'Dec']
    fig = make_subplots(rows=5, cols=2, shared_xaxes=True,
                        subplot_titles=[title for _, title in METRICS],
                        vertical_spacing=.08)
    months = df['month']
    for index, (metric, title) in enumerate(METRICS):
        row, col = divmod(index, 2)
        row += 1; col += 1
        x, y = _finite_xy(list(range(len(df[metric]))), df[metric])
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=title,
                                 line=dict(color='black'), opacity=.3,
                                 showlegend=False), row=row, col=col)
        for grey_month in grey_months:
            indices = [i for i, value in enumerate(months) if month_names[int(value)-1] == grey_month]
            if indices:
                _add_span(fig, indices[0], indices[-1], 'gray', row, col)
        try:
            xs, ys = smooth(x, y)
            fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines',
                                     line=dict(color='red'), showlegend=False), row=row, col=col)
        except Exception:
            print('Smoothing skipped')
        if y:
            fig.add_hline(y=float(np.mean(y)), line_dash='dash', line_color='blue', row=row, col=col)
        fig.update_xaxes(range=[0, df.shape[0]], tickmode='array',
                         tickvals=[int(round(np.mean([i for i, value in enumerate(months) if month_names[int(value)-1] == mon])))
                                   for mon in month_names if any(month_names[int(value)-1] == mon for value in months)],
                         ticktext=[mon for mon in month_names if any(month_names[int(value)-1] == mon for value in months)],
                         tickangle=45, row=row, col=col)
        fig.update_yaxes(title_text=title, range=[0, 100] if ('Battery' in metric or 'Perc' in metric) else None,
                         showgrid=True, gridcolor='rgba(0,0,0,.3)', row=row, col=col)
    fig.update_layout(template='plotly_white', width=1200, height=1500,
                      title=dict(text=str(year), x=.5), margin=dict(t=70))
    fig.add_annotation(text='Time', x=.5, y=-.04, xref='paper', yref='paper', showarrow=False)
    return fig


def plot_day_overview(df_hr, df_stress, year, month, day, client):
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    mon = month_names[month-1]
    date_ref = f"{year}-{month:02d}-{day:02d}"
    stats = client.get_stats(date_ref)
    fig = make_subplots(rows=2, cols=2, shared_xaxes=True,
                        vertical_spacing=.12, horizontal_spacing=.08)
    activities = client.get_activities_by_date(date_ref, date_ref)
    try:
        sleep = client.get_sleep_data(date_ref)['dailySleepDTO']
        start_sleep = datetime.fromtimestamp(sleep['sleepStartTimestampGMT']/1000) + timedelta(hours=2)
        end_sleep = datetime.fromtimestamp(sleep['sleepEndTimestampGMT']/1000) + timedelta(hours=2)
    except Exception:
        start_sleep = end_sleep = None; print('Sleep skipped')
    for data, value_col, row, col, color, label in ((df_hr, 'HR', 1, 1, 'black', 'HR (BPM)'),
                                                      (df_stress, 'Stress', 1, 2, 'black', 'Stress %')):
        raw_x = [datetime.fromtimestamp(int(v)/1000) + timedelta(hours=2) for v in data['Timepoint']]
        x, y = _finite_xy(raw_x, data[value_col])
        raw_timestamps = [int(v)/1000 for v in data['Timepoint']]
        timestamps, _ = _finite_xy(raw_timestamps, data[value_col])
        _add_timeseries(fig, x, y, row, color, label, col=col)
        try:
            xs, ys = smooth(timestamps, y)
            xs = [datetime.fromtimestamp(int(round(v))) + timedelta(hours=2) for v in xs]
            _add_timeseries(fig, xs, ys, row, 'red', 'Smoothed', col=col)
        except Exception:
            print('Smoothing skipped')
        if y: fig.add_hline(y=float(np.mean(y)), line_dash='dash', line_color='blue', row=row, col=col)
        if start_sleep: _add_span(fig, start_sleep, end_sleep, 'gray', row, col)
        _add_activity_spans(fig, activities, row, col)
        fig.update_yaxes(title_text=label, row=row, col=col)
    try:
        steps_df = pd.DataFrame(client.get_steps_data(date_ref))
        steps_df['startGMT'] = pd.to_datetime(steps_df['startGMT']) + timedelta(hours=2)
        steps_df['steps_cumsum'] = steps_df['steps'].cumsum()
        _add_timeseries(fig, steps_df['startGMT'], steps_df['steps_cumsum'], 2, 'blue', '# Steps', True, 1)
        fig.update_yaxes(title_text='# Steps', range=[0, steps_df['steps_cumsum'].iloc[-1]+3000], row=2, col=1)
        if start_sleep: _add_span(fig, start_sleep, end_sleep, 'gray', 2, 1)
        _add_activity_spans(fig, activities, 2, 1)
    except Exception: print('Steps skipped.')
    try:
        bb_df = pd.DataFrame(client.get_body_battery(date_ref)[0]['bodyBatteryValuesArray'], columns=['Timepoint', 'BB'])
        bb_df['Timepoint'] = [datetime.fromtimestamp(v/1000) + timedelta(hours=2) for v in bb_df['Timepoint']]
        _add_timeseries(fig, bb_df['Timepoint'], bb_df['BB'], 2, 'purple', 'Body battery %', True, 2)
        fig.update_yaxes(title_text='Body battery %', range=[0, 100], row=2, col=2)
        if start_sleep: _add_span(fig, start_sleep, end_sleep, 'gray', 2, 2)
        _add_activity_spans(fig, activities, 2, 2)
    except Exception: print('Body battery skipped.')
    try:
        slp_time = stats['sleepingSeconds']/3600
        subtitle = f"<br>{'{0:02.0f}:{1:02.0f}'.format(*divmod(slp_time * 60, 60))} hours slept - {round(stats['activeKilocalories'])} active calories burned"
    except Exception: subtitle = ''
    _daily_layout(fig, f"{day} {mon} {year}{subtitle}")
    return fig


def plot_running_activity_overview(activity,activity_details):
    if not activity_details['detailsAvailable']:
        return False
    di = {}
    metric_keys = {'directSpeed': 'mpkm', 'sumDuration': 'durationSeconds', 'directElevation': 'ElevationMeters',
                   'directHeartRate': 'HR', 'directDoubleCadence': 'Cadence', 'directAirTemperature': 'Temp'}
    for key, target in metric_keys.items():
        try:
            metric_index = [item['metricsIndex'] for item in activity_details['metricDescriptors'] if item['key'] == key][0]
            values = [item['metrics'][metric_index] for item in activity_details['activityDetailMetrics']]
            di[target] = [1000/(value*60) if value*60 > 0 else np.nan for value in values] if key == 'directSpeed' else values
        except Exception: print('Fail')
    df = pd.DataFrame(di)
    fig = make_subplots(rows=4, cols=2, shared_xaxes=True,
                        specs=[[{}, {'type':'domain', 'rowspan':3}], [{}, None], [{}, None], [{}, {}]],
                        vertical_spacing=.07, horizontal_spacing=.12)
    duration = df['durationSeconds']
    for row, column, color, label in ((1, 'HR', 'red', 'HR (bpm)'), (2, 'mpkm', 'blue', 'Speed (min/km)'),
                                       (3, 'Cadence', 'orange', 'Cadence (spm)'), (4, 'Temp', 'purple', 'Temperature (Celsius)')):
        try:
            _add_timeseries(fig, duration, df[column], row, color, label, True)
            fig.update_yaxes(title_text=label, range=[df[column].quantile(.01)*.95, df[column].quantile(.99)*1.05], row=row, col=1)
        except Exception:
            fig.update_yaxes(range=[0, 100], title_text=label, row=row, col=1); print(f'Skipping {column}')
        try:
            fig.add_trace(go.Scatter(x=duration, y=df['ElevationMeters'], mode='lines', line=dict(color='rgba(100,100,100,0)'),
                                     fill='tozeroy', fillcolor='rgba(128,128,128,.3)', showlegend=False), row=row, col=1)
        except Exception: pass
    fig.update_xaxes(title_text='Time (seconds)', row=4, col=1)
    try: zones = [activity[f'hrTimeInZone_{i}'] for i in range(1, 6)]; labels = [f'Zone {i}' for i in range(1, 6)]; colors = ['#4F7FD9','#5DAA68','#FF8C1A','#D83A34','#7E3FA3']
    except Exception: zones, labels, colors = [100], ['No data'], ['grey']
    fig.add_trace(go.Pie(values=zones, labels=labels, hole=.42, marker=dict(colors=colors),
                         textinfo='percent', textfont=dict(color='white'), name='HR Zones'), row=1, col=2)
    values = []
    for label, key, formatter in [('Average pace', 'averageSpeed', lambda v: f"{int(1000/v//60)}:{int((1000/v)%60):02d} min/km"),
                                  ('Max pace', 'maxSpeed', lambda v: f"{int(1000/v//60)}:{int((1000/v)%60):02d} min/km"),
                                  ('Average HR', 'averageHR', lambda v: f'{round(v)} bpm'), ('Max HR', 'maxHR', lambda v: f'{round(v)} bpm'),
                                  ('Elevation gain', 'elevationGain', lambda v: f'{v:.0f} m'), ('vO2Max', 'vO2MaxValue', lambda v: f'{v:.0f}'),
                                  ('Calories burned', 'calories', lambda v: f'{v:.0f}')]:
        try: values.append(f'<b>{label}</b>: {formatter(activity[key])}')
        except Exception: values.append(f'<b>{label}</b>:')
    fig.add_annotation(text='<br>'.join(values), x=.75, y=.105, xref='paper', yref='paper', showarrow=False,
                       align='left', xanchor='center', yanchor='middle')
    fig.add_annotation(text='Time in HR Zones', x=.75, y=.98, xref='paper', yref='paper', showarrow=False,
                       font=dict(size=16))
    fig.add_annotation(text=f"{timedelta(seconds=int(duration.iloc[-1]))}<br><span style='font-size:10px'>Total Time</span>", x=.75, y=.61, xref='paper', yref='paper', showarrow=False)
    fig.update_layout(template='plotly_white', width=1600, height=700, showlegend=False,
                      paper_bgcolor='white', plot_bgcolor='white',
                      title=dict(text=f"{activity['startTimeLocal']} - {activity['activityType']['typeKey']} - {activity['activityName']}", x=.5))
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,.3)', col=1)
    return fig


def plot_day_overview2(df_hr, df_stress, year, month, day, client):
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    mon = month_names[month-1]; date_ref = f"{year}-{month:02d}-{day:02d}"
    stats = client.get_stats(date_ref)
    fig = make_subplots(rows=4, cols=2, shared_xaxes=True,
                        specs=[[{}, {'type':'domain', 'rowspan':3}], [{}, None], [{}, None], [{}, {}]],
                        vertical_spacing=.07, horizontal_spacing=.12)
    activities = client.get_activities_by_date(date_ref, date_ref)
    try:
        sleep = client.get_sleep_data(date_ref)['dailySleepDTO']
        start_sleep = datetime.fromtimestamp(sleep['sleepStartTimestampGMT']/1000) + timedelta(hours=2)
        end_sleep = datetime.fromtimestamp(sleep['sleepEndTimestampGMT']/1000) + timedelta(hours=2)
    except Exception: sleep = {}; start_sleep = end_sleep = None; print('Sleep skipped')
    limits = []
    for data, field, row, color, label in ((df_hr, 'HR', 1, 'red', 'HR (BPM)'), (df_stress, 'Stress', 2, 'orange', 'Stress %')):
        x, y = _finite_xy([datetime.fromtimestamp(int(v)/1000)+timedelta(hours=2) for v in data['Timepoint']], data[field])
        if x: limits.extend([x[0], x[-1]])
        _add_timeseries(fig, x, y, row, color, label, True)
        try: fig.update_yaxes(title_text=label, range=[pd.Series(y).quantile(.01)*.95, pd.Series(y).quantile(.99)*1.05], row=row, col=1)
        except Exception: fig.update_yaxes(title_text=label, range=[0, 100], row=row, col=1); print('Fail')
        if start_sleep: _add_span(fig, start_sleep, end_sleep, 'gray', row, 1)
        _add_activity_spans(fig, activities, row, 1)
    try:
        steps_df = pd.DataFrame(client.get_steps_data(date_ref)); steps_df['startGMT'] = pd.to_datetime(steps_df['startGMT'])+timedelta(hours=2); steps_df['steps_cumsum'] = steps_df['steps'].cumsum()
        limits.extend([steps_df['startGMT'].iloc[0], steps_df['startGMT'].iloc[-1]])
        _add_timeseries(fig, steps_df['startGMT'], steps_df['steps_cumsum'], 3, 'blue', '# Steps', True); fig.update_yaxes(title_text='# Steps', range=[0, steps_df['steps_cumsum'].iloc[-1]+3000], row=3, col=1)
    except Exception: steps_df = pd.DataFrame(); fig.update_yaxes(title_text='# Steps', range=[0,100], row=3,col=1); print('Steps skipped.')
    try:
        bb_df = pd.DataFrame(client.get_body_battery(date_ref)[0]['bodyBatteryValuesArray'], columns=['Timepoint','BB']); bb_df['Timepoint'] = [datetime.fromtimestamp(v/1000)+timedelta(hours=2) for v in bb_df['Timepoint']]
        limits.extend([bb_df['Timepoint'].iloc[0], bb_df['Timepoint'].iloc[-1]])
        _add_timeseries(fig, bb_df['Timepoint'], bb_df['BB'], 4, 'purple', 'Body battery %', True); fig.update_yaxes(title_text='Body battery %', range=[0,100], row=4,col=1)
    except Exception: print('Body battery skipped.')
    for row in (3,4):
        if start_sleep: _add_span(fig, start_sleep, end_sleep, 'gray', row, 1)
        _add_activity_spans(fig, activities, row, 1)
    if limits: fig.update_xaxes(range=[min(limits), max(limits)], col=1)
    try: zones = [sleep['sleepScores'][name]['value'] for name in ('remPercentage','lightPercentage','deepPercentage')]; labels = ['REM','Light','Deep']; colors = ['#4F7FD9','#FF8C1A','#D83A34']
    except Exception: zones, labels, colors = [100], ['No data'], ['grey']
    fig.add_trace(go.Pie(values=zones, labels=labels, hole=.42, marker=dict(colors=colors), textinfo='percent', textfont=dict(color='white')), row=1, col=2)
    summary = []
    try: summary.append(f"<b>Average HR</b>: {round(np.mean(df_hr['HR']))} bpm")
    except Exception: pass
    try: summary.append(f"<b>Max HR</b>: {round(np.max(df_hr['HR']))} bpm")
    except Exception: pass
    try: summary.append(f"<b># Steps</b>: {steps_df['steps'].cumsum().iloc[-1]}")
    except Exception: pass
    for label, value in [('Active calories burned', stats.get('activeKilocalories')), ('Overall sleep score', sleep.get('sleepScores',{}).get('overall',{}).get('value')), ('Sleep stress', sleep.get('sleepScores',{}).get('stress',{}).get('qualifierKey'))]:
        if value is not None: summary.append(f'<b>{label}</b>: {value}')
    fig.add_annotation(text='<br>'.join(summary), x=.75, y=.105, xref='paper', yref='paper', showarrow=False,
                       align='left', xanchor='center', yanchor='middle')
    fig.add_annotation(text='Sleep analysis', x=.75, y=.98, xref='paper', yref='paper', showarrow=False,
                       font=dict(size=16))
    _daily_layout(fig, f'{day} {mon} {year}')
    fig.update_layout(height=700)
    return fig
