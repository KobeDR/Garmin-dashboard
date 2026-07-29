# Garmin Dashboard

# Garmin Dashboard

A personal dashboard for visualizing health, wellness, and activity data from Garmin Connect. The application is built with **Streamlit** and uses the **python-garminconnect** library to retrieve data from a Garmin account.

## Features

* 📊 **Yearly overview**

  * Daily activity summaries
  * Body Battery
  * Resting heart rate
  * Stress
  * Steps
  * Calories
  * Other Garmin wellness metrics

* 📅 **Daily overview**

  * Heart rate throughout the day
  * Stress timeline
  * Steps taken
  * Body battery

* 🏃 **Activity analysis**

  * Select any activity recorded on a given day
  * View detailed activity metrics
  * Visualization of pace, heart rate, elevation, cadence and temperature

* ⚡ Local caching to reduce Garmin API requests and improve loading times.

## Project Structure

```text
garmin-dashboard/
├── app.py
├── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── analysis/
├── data/
├── plots/
├── cache/
└── README.md
```

## Requirements

* Python 3.12+
* Garmin Connect account
* Docker Desktop (recommended)

## Installation

### Option 1 — Docker (Recommended)

Clone the repository:

```bash
git clone https://github.com/KobeDR/garmin-dashboard.git
cd garmin-dashboard
```

Build and start the application:

```bash
docker compose up --build
```

The dashboard will be available at:

```text
http://localhost:8501
```

---

### Option 2 — Local Python Environment

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows:

```powershell
.\.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```

## Caching

Downloaded Garmin data is cached locally to:

```text
cache/
```

This reduces loading times and minimizes repeated API calls.

## Technologies

* Python
* Streamlit
* Pandas
* NumPy
* Matplotlib
* SciPy
* python-garminconnect
* Docker

## Notes

This is a personal project and is not affiliated with or endorsed by Garmin.

Garmin Connect is a trademark of Garmin Ltd.

## License

This project is licensed under the MIT License. Feel free to modify and use it for personal projects.

