# North Carolina Education Dashboard

Interactive dashboard built with [Dash](https://dash.plotly.com/) for exploring public school data across North Carolina counties.

A demo of the app is available at: <https://nc-dashboard-77977471369.us-central1.run.app/>

## Features
- View enrollment trends including racial breakdowns
- Analyze local, state and federal funding over time
- Explore current expense categories and personnel statistics
- Examine graduate intentions for each county

## Data Sources
The repository includes a `Data/` directory (~60MB) with a prepared Parquet file and the raw CSV data used to build it. These files were downloaded from:

1. [OSBM LINC Education Table](https://linc.osbm.nc.gov/explore/dataset/education/table)
2. [OSBM LINC Government Table](https://linc.osbm.nc.gov/explore/dataset/government/table/)
3. [North Carolina Public School Statistical Profile](http://apps.schools.nc.gov/ords/f?p=145:1::::::)

## Running Locally
1. Install Python 3.9 or later.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the Dash server:
   ```bash
   python app.py
   ```
   The app runs on <http://localhost:8080> by default.

## Docker
You can containerize the application with the included `Dockerfile`:
```bash
docker build -t nc-education-dashboard .
docker run -p 8080:8080 nc-education-dashboard
```

A `cloudbuild.yaml` file is provided for deploying the image to Google Cloud Run.

## Repository Layout
- `app.py` – single-file Dash application and callbacks
- `Data/` – data sources and aggregated Parquet file
- `Dockerfile` / `.dockerignore` – container configuration
- `cloudbuild.yaml` – deployment instructions for Cloud Build
- `requirements.txt` – Python package requirements
- `venv/` – example virtual environment

---
This dashboard demonstrates how public school finance and enrollment metrics vary by county. Explore the code in `app.py` to see how the charts are generated.
