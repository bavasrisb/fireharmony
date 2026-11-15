
import calendar
from datetime import date
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="FIREHARMONY",
    page_icon="🔥",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F8F9FC;
        color: #1E293B;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    h1, h2, h3 {
        color: #1E293B;
    }

    .stButton button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        border: none;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 10px;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background-color: #F8F9FC;
        padding: 10px 12px;
        border-radius: 8px;
        margin-bottom: 6px;
        color: #1E293B;
        transition: 0.2s ease;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background-color: #DBEAFE;
        color: #2563EB;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATASET
# =========================================================

DATA_PATH = (
    Path(__file__).parent
    / "data"
    / "Amazon_Combined_Observations.csv"
)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


try:
    df = load_data()
    data_loaded = True
    load_error = None

except FileNotFoundError:
    df = pd.DataFrame()
    data_loaded = False
    load_error = f"Dataset not found: {DATA_PATH}"

except Exception as error:
    df = pd.DataFrame()
    data_loaded = False
    load_error = str(error)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.title("🔥 FIREHARMONY")
st.sidebar.caption("Global Fire Intelligence")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Global Dashboard",
        "Burning Activity Calendar",
        "Sensor Harmonization",
        "Unusual Activity",
        "Event Explorer"
    ]
)



# =========================================================
# MAIN HEADER
# =========================================================

st.html("""
<div style="
    background: linear-gradient(120deg, #1E40AF, #2563EB);
    padding: 28px 30px;
    border-radius: 15px;
    margin-bottom: 22px;
">
    <h1 style="color: white; margin: 0; font-size: 34px;">
        🔥 FIREHARMONY
    </h1>
    <p style="color: #DBEAFE; margin: 8px 0 0 0; font-size: 16px;">
        Global Burning Activity Intelligence Platform
    </p>
    <p style="color: #BFDBFE; margin: 5px 0 0 0; font-size: 12px;">
        NASA Space Apps Challenge 2026
    </p>
</div>
""")

st.subheader("Global Burning Activity Intelligence Platform")

st.markdown(
    "Monitor satellite fire hotspots and explore burning activity "
    "in the currently loaded study area."
)

st.divider()


# =========================================================
# MAIN APPLICATION
# =========================================================

if not data_loaded:

    st.error(load_error)

    st.info(
        "Check that Amazon_Combined_Observations.csv "
        "is inside the project's data folder."
    )

else:

    st.success(
        "Amazon Basin satellite dataset connected successfully!"
    )

    required_columns = [
        "sensor_type",
        "latitude",
        "longitude",
        "acq_date"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        st.error(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    else:

        # =================================================
        # 1. GLOBAL DASHBOARD
        # =================================================

        if page == "Global Dashboard":

            st.header("Amazon Basin Overview")

            st.markdown(
                "### 📊 Satellite Observation Overview"
            )

            st.caption(
                "Summary of the currently loaded Amazon Basin dataset"
            )

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Total Observations",
                f"{len(df):,}"
            )

            col2.metric(
                "MODIS Observations",
                f"{(df['sensor_type'] == 'MODIS').sum():,}"
            )

            col3.metric(
                "VIIRS Observations",
                f"{df['sensor_type'].isin(['VIIRS_J1', 'VIIRS_J2']).sum():,}"
            )

            col4.metric(
                "Satellite Sensors",
                df["sensor_type"].nunique()
            )

            st.subheader(
                "🛰️ Satellite Sensor Distribution"
            )

            st.caption(
                "Number of hotspot observations collected by each sensor"
            )

            sensor_counts = df["sensor_type"].value_counts()

            st.bar_chart(sensor_counts)

            # Sensor map

            st.subheader(
                "🛰️ Sensor-wise Fire Hotspot Map"
            )

            available_sensors = ["All Sensors"] + sorted(
                df["sensor_type"].dropna().unique().tolist()
            )

            selected_sensor = st.selectbox(
                "Choose Satellite Sensor",
                available_sensors
            )

            if selected_sensor == "All Sensors":

                filtered_map = df.copy()

            else:

                filtered_map = df[
                    df["sensor_type"] == selected_sensor
                ].copy()

            filtered_map = filtered_map.dropna(
                subset=["latitude", "longitude"]
            )

            sensor_colors = {
                "MODIS": [255, 140, 0],
                "VIIRS_J1": [0, 120, 255],
                "VIIRS_J2": [220, 40, 60]
            }

            filtered_map["color"] = filtered_map[
                "sensor_type"
            ].map(sensor_colors)

            if not filtered_map.empty:

                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=filtered_map,
                    get_position="[longitude, latitude]",
                    get_fill_color="color",
                    get_radius=1500,
                    pickable=True,
                    auto_highlight=True
                )

                view_state = pdk.ViewState(
                    latitude=float(
                        filtered_map["latitude"].mean()
                    ),
                    longitude=float(
                        filtered_map["longitude"].mean()
                    ),
                    zoom=3,
                    pitch=0
                )

                deck = pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip={
                        "text": "Sensor: {sensor_type}\nDate: {acq_date}"
                    }
                )

                st.pydeck_chart(deck)

            else:

                st.warning(
                    "No valid coordinates are available for this filter."
                )

            st.markdown("""
            <div style="
                display:flex;
                gap:25px;
                flex-wrap:wrap;
                padding:12px 5px;
                font-size:14px;
            ">
                <span>🟠 <b>MODIS</b></span>
                <span>🔵 <b>VIIRS NOAA-20 (J1)</b></span>
                <span>🔴 <b>VIIRS NOAA-21 (J2)</b></span>
            </div>
            """, unsafe_allow_html=True)

            st.caption(
                f"Displaying {len(filtered_map):,} satellite observations"
            )

            st.subheader(
                "📋 Recent Satellite Observations"
            )

            st.caption(
                "Latest 10 records from the Amazon Basin dataset"
            )

            st.dataframe(
                df.head(10),
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Current study area: Amazon Drainage Basin | "
                "Source: NASA FIRMS satellite observations"
            )


        # =================================================
        # 2. BURNING ACTIVITY CALENDAR
        # =================================================

        elif page == "Burning Activity Calendar":

            st.header("📅 Burning Activity Calendar")

            st.markdown(
                "Explore daily satellite hotspot observations "
                "across the Amazon Basin."
            )

            st.caption(
                "Select a month to review observation patterns, "
                "peak days and daily satellite records."
            )

            activity_df = df.copy()

            activity_df["acq_date"] = pd.to_datetime(
                activity_df["acq_date"],
                errors="coerce"
            )

            activity_df = activity_df.dropna(
                subset=["acq_date"]
            )

            activity_df["date_only"] = (
                activity_df["acq_date"].dt.date
            )

            if not activity_df.empty:

                available_months = sorted(
                    activity_df["acq_date"]
                    .dt.to_period("M")
                    .unique()
                )

                selected_month = st.selectbox(
                    "📆 Select Month",
                    available_months,
                    format_func=lambda value: value.strftime(
                        "%B %Y"
                    )
                )

                year = selected_month.year
                month = selected_month.month

                month_df = activity_df[
                    activity_df["acq_date"].dt.to_period("M")
                    == selected_month
                ].copy()

                daily_counts = month_df.groupby(
                    "date_only"
                ).size()

                total_observations = int(
                    daily_counts.sum()
                )

                active_days = int(
                    (daily_counts > 0).sum()
                )

                if not daily_counts.empty:

                    peak_date = daily_counts.idxmax()
                    peak_count = int(daily_counts.max())

                else:

                    peak_date = None
                    peak_count = 0

                # Monthly metrics

                metric1, metric2, metric3 = st.columns(3)

                metric1.metric(
                    "Monthly Observations",
                    f"{total_observations:,}"
                )

                metric2.metric(
                    "Days with Observations",
                    active_days
                )

                if peak_date is not None:

                    metric3.metric(
                        "Peak Observation Day",
                        peak_date.strftime("%d %b %Y"),
                        f"{peak_count:,} observations"
                    )

                else:

                    metric3.metric(
                        "Peak Observation Day",
                        "N/A"
                    )

                st.divider()

                st.subheader(
                    f"🗓️ {calendar.month_name[month]} {year}"
                )

                # Calculate monthly relative activity levels

                positive_counts = daily_counts[
                    daily_counts > 0
                ]

                if not positive_counts.empty:

                    q1 = float(
                        positive_counts.quantile(0.25)
                    )

                    q2 = float(
                        positive_counts.quantile(0.50)
                    )

                    q3 = float(
                        positive_counts.quantile(0.75)
                    )

                else:

                    q1 = q2 = q3 = 0.0

                def activity_style(count):

                    if count == 0:
                        return "#E8EEF5", "No observations"

                    if count <= q1:
                        return "#B9E6C9", "Low"

                    if count <= q2:
                        return "#FDE68A", "Moderate"

                    if count <= q3:
                        return "#FDBA74", "High"

                    return "#F87171", "Very high"

                # Calendar colour legend

                legend_items = [
                    ("#E8EEF5", "No observations"),
                    ("#B9E6C9", "Low"),
                    ("#FDE68A", "Moderate"),
                    ("#FDBA74", "High"),
                    ("#F87171", "Very high")
                ]

                legend_html = """
                <div style="
                    display:flex;
                    flex-wrap:wrap;
                    gap:14px;
                    padding:14px 16px;
                    background:#FFFFFF;
                    border:1px solid #E2E8F0;
                    border-radius:12px;
                    margin:8px 0 16px 0;
                ">
                """

                for color, label in legend_items:

                    legend_html += f"""
                    <div style="
                        display:flex;
                        align-items:center;
                        gap:7px;
                        font-size:12px;
                        font-weight:650;
                        color:#334155;
                    ">
                        <span style="
                            width:17px;
                            height:17px;
                            display:inline-block;
                            background:{color};
                            border:1px solid #CBD5E1;
                            border-radius:4px;
                        "></span>
                        {label}
                    </div>
                    """

                legend_html += "</div>"

                st.html(legend_html)

                
                # Weekday headings

                weekdays = [
                    "MON", "TUE", "WED",
                    "THU", "FRI", "SAT", "SUN"
                ]

                weekday_html = """
                <div style="
                    display:grid;
                    grid-template-columns:repeat(7,minmax(0,1fr));
                    gap:7px;
                    margin-bottom:7px;
                ">
                """

                for weekday in weekdays:

                    weekday_html += f"""
                    <div style="
                        text-align:center;
                        padding:9px 2px;
                        font-size:11px;
                        font-weight:800;
                        color:#64748B;
                        letter-spacing:0.8px;
                    ">{weekday}</div>
                    """

                weekday_html += "</div>"

                st.html(weekday_html)

                # Rectangular calendar date cards

                calendar_html = """
                <div style="
                    display:grid;
                    grid-template-columns:repeat(7,minmax(0,1fr));
                    gap:7px;
                ">
                """

                for week in calendar.monthcalendar(
                    year, month
                ):

                    for day_number in week:

                        if day_number == 0:

                            calendar_html += """
                            <div style="
                                min-height:92px;
                                background:transparent;
                            "></div>
                            """

                            continue

                        current_date = date(
                            year,
                            month,
                            day_number
                        )

                        count = int(
                            daily_counts.get(current_date, 0)
                        )

                        background, level = activity_style(
                            count
                        )

                        calendar_html += f"""
                        <div style="
                            min-height:92px;
                            padding:10px 8px;
                            background:{background};
                            border:1px solid #D7E0EA;
                            border-radius:9px;
                            box-sizing:border-box;
                            display:flex;
                            flex-direction:column;
                            justify-content:space-between;
                        ">
                            <div style="
                                font-size:17px;
                                font-weight:800;
                                color:#1E293B;
                            ">{day_number}</div>

                            <div style="
                                font-size:11px;
                                font-weight:750;
                                color:#334155;
                            ">{count:,} observations</div>

                            <div style="
                                font-size:9px;
                                font-weight:700;
                                color:#475569;
                            ">{level}</div>
                        </div>
                        """

                calendar_html += "</div>"

                st.html(calendar_html)

                st.caption(
                    "Colour levels show relative daily satellite "
                    "observation counts within the selected month. "
                    "They do not represent confirmed fire severity."
                )

                # Daily trend

                st.divider()

                st.subheader(
                    "📊 Daily Observation Trend"
                )

                trend_df = (
                    daily_counts
                    .rename("Observations")
                    .reset_index()
                )

                trend_df.columns = [
                    "Date",
                    "Observations"
                ]

                if not trend_df.empty:

                    st.line_chart(
                        trend_df.set_index("Date"),
                        use_container_width=True
                    )

                else:

                    st.info(
                        "No daily observations are available for this month."
                    )

                # Explore selected date

                st.divider()

                st.subheader(
                    "🔎 Explore a Specific Date"
                )

                if peak_date is not None:

                    default_date = peak_date

                else:

                    default_date = date(year, month, 1)

                selected_date = st.date_input(
                    "Choose a date",
                    value=default_date,
                    min_value=date(year, month, 1),
                    max_value=date(
                        year,
                        month,
                        calendar.monthrange(year, month)[1]
                    ),
                    key="calendar_selected_date"
                )

                selected_data = activity_df[
                    activity_df["date_only"] == selected_date
                ]

                if not selected_data.empty:

                    st.success(
                        f"{len(selected_data):,} satellite observations "
                        f"recorded on "
                        f"{selected_date.strftime('%d %B %Y')}."
                    )

                    sensor_counts = (
                        selected_data["sensor_type"]
                        .value_counts()
                        .rename_axis("Sensor")
                        .reset_index(name="Observations")
                    )

                    st.dataframe(
                        sensor_counts,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.markdown(
                        "#### Observation Details"
                    )

                    st.dataframe(
                        selected_data.drop(
                            columns=["date_only"],
                            errors="ignore"
                        ).head(100),
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.info(
                        "No satellite observations are available for "
                        "this date in the loaded dataset. This does not "
                        "confirm that no fire occurred."
                    )

            else:

                st.warning(
                    "No valid acquisition dates found in the dataset."
                )


        # =================================================
        # 3. SENSOR HARMONIZATION
        # =================================================

        elif page == "Sensor Harmonization":

            st.header(
                "🛰️ MODIS–VIIRS Sensor Comparison"
            )

            st.markdown(
                "Compare satellite observation counts and "
                "Fire Radiative Power (FRP) across sensors."
            )

            if "observation_id" in df.columns:

                sensor_summary = (
                    df.groupby("sensor_type")
                    .agg(
                        observation_count=(
                            "observation_id",
                            "count"
                        )
                    )
                    .reset_index()
                )

            else:

                sensor_summary = (
                    df.groupby("sensor_type")
                    .size()
                    .reset_index(name="observation_count")
                )

            st.subheader(
                "1. Observation Count Comparison"
            )

            st.bar_chart(
                sensor_summary.set_index("sensor_type")
            )

            st.dataframe(
                sensor_summary,
                use_container_width=True,
                hide_index=True
            )

            # Daily sensor observation comparison

            st.subheader(
                "📈 Daily Sensor Observation Trends"
            )

            trend_data = df.copy()

            trend_data["acq_date"] = pd.to_datetime(
                trend_data["acq_date"],
                errors="coerce"
            )

            trend_data = trend_data.dropna(
                subset=["acq_date", "sensor_type"]
            )

            trend_data["observation_date"] = (
                trend_data["acq_date"].dt.date
            )

            daily_sensor_counts = (
                trend_data.groupby(
                    ["observation_date", "sensor_type"]
                )
                .size()
                .unstack(fill_value=0)
            )

            st.line_chart(
                daily_sensor_counts,
                use_container_width=True
            )

            st.caption(
                "Daily satellite hotspot observation counts "
                "for MODIS, VIIRS NOAA-20 and VIIRS NOAA-21."
            )
            
         
          
            # Average FRP comparison

            st.subheader("🔥 Average Fire Radiative Power (FRP)")

            frp_data = df.copy()

            frp_data["frp"] = pd.to_numeric(
                frp_data["frp"],
                errors="coerce"
            )

            frp_summary = (
                frp_data.groupby("sensor_type")["frp"]
                .mean()
                .dropna()
                .round(2)
            )

            if not frp_summary.empty:
                st.bar_chart(
                    frp_summary,
                    use_container_width=True
                )

                st.dataframe(
                    frp_summary.rename(
                        "Average FRP (MW)"
                    ).reset_index(),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No valid FRP data available.")
            
            st.caption(
                "FRP values are exploratory raw sensor comparisons, "
                "not scientifically validated harmonized measurements."
            )
            
            # Sensor Data Quality Analysis

            st.subheader("🔍 Sensor Data Quality Analysis")

            quality_data = df.copy()

            quality_data["frp"] = pd.to_numeric(
                quality_data["frp"],
                errors="coerce"
            )

            quality_summary = (
                quality_data.groupby("sensor_type")
                .agg(
                    Total_Observations=("frp", "size"),
                    Valid_FRP=("frp", "count")
                )
                .reset_index()
            )

            quality_summary["Missing_FRP"] = (
                quality_summary["Total_Observations"]
                - quality_summary["Valid_FRP"]
            )

            quality_summary["Completeness_%"] = (
                quality_summary["Valid_FRP"]
                / quality_summary["Total_Observations"]
                * 100
            ).round(2)

            st.dataframe(
                quality_summary,
                use_container_width=True,
                hide_index=True
            )
            
            st.download_button(
                label="⬇️ Download Sensor Quality Report",
                data=quality_summary.to_csv(index=False).encode("utf-8"),
                file_name="FIREHARMONY_Sensor_Quality_Report.csv",
                mime="text/csv"
            )

            
            # FRP Distribution Analysis

            st.subheader("📊 FRP Distribution Across Sensors")

            distribution_data = df.copy()

            distribution_data["frp"] = pd.to_numeric(
                distribution_data["frp"],
                errors="coerce"
            )

            distribution_data = distribution_data.dropna(
                subset=["frp", "sensor_type"]
            )

            if not distribution_data.empty:

                frp_distribution = (
                    distribution_data.groupby("sensor_type")["frp"]
                    .quantile([0.25, 0.50, 0.75])
                    .unstack()
                )

                frp_distribution.columns = [
                    "25th Percentile",
                    "Median",
                    "75th Percentile"
                ]

                st.bar_chart(
                    frp_distribution,
                    use_container_width=True
                )

                st.dataframe(
                    frp_distribution.round(2),
                    use_container_width=True
                )

            else:
                st.info("No valid FRP values available.")

            st.caption(
                "Exploratory FRP distribution comparison. "
                "Values are not scientifically calibrated across sensors."
            )



        # =================================================
        # 4. UNUSUAL ACTIVITY
        # =================================================

        elif page == "Unusual Activity":

            st.header(
                "🔥 Unusual Fire Activity Detection"
            )

            st.markdown(
                "Identify days with unusually high satellite fire "
                "observations across the Amazon Basin."
            )

            activity_df = df.copy()

            activity_df["acq_date"] = pd.to_datetime(
                activity_df["acq_date"],
                errors="coerce"
            )

            activity_df = activity_df.dropna(
                subset=["acq_date"]
            )

            daily_activity = (
                activity_df.groupby(
                    activity_df["acq_date"].dt.date
                )
                .size()
                .rename_axis("date")
                .reset_index(name="observations")
            )

            if len(daily_activity) >= 2:

                mean_count = (
                    daily_activity["observations"].mean()
                )

                std_count = (
                    daily_activity["observations"].std()
                )

                threshold = mean_count + (2 * std_count)

                daily_activity["status"] = (
                    daily_activity["observations"].apply(
                        lambda value: "Unusual"
                        if value > threshold
                        else "Normal"
                    )
                )

                unusual_days = daily_activity[
                    daily_activity["status"] == "Unusual"
                ]

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Days Analysed",
                    len(daily_activity)
                )

                col2.metric(
                    "Average Daily Observations",
                    f"{mean_count:,.0f}"
                )

                col3.metric(
                    "Unusual Activity Days",
                    len(unusual_days)
                )

                st.subheader(
                    "Daily Burning Activity"
                )

                
                chart_data = daily_activity.set_index(
                    "date"
                )[["observations"]].copy()

                chart_data["Unusual Threshold"] = threshold

                st.line_chart(
                    chart_data,
                    use_container_width=True
                )

                
                st.subheader("🚨 Activity Alert Summary")

                if not unusual_days.empty:

                    st.warning(
                        f"{len(unusual_days)} day(s) recorded "
                        "unusually high hotspot observations."
                    )

                else:

                    st.success(
                        "No unusual activity detected in the "
                        "currently loaded observations."
                    )

                st.subheader(
                    "Unusual Activity Records"
                )

                if not unusual_days.empty:

                    st.dataframe(
                        unusual_days,
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.success(
                        "No days crossed the exploratory "
                        "unusual-activity threshold."
                    )

                st.info(
                    "Method: Daily observation count greater than "
                    "mean + 2 standard deviations. This is an "
                    "exploratory statistical flag, not a confirmed "
                    "wildfire alert."
                )

            else:

                st.warning(
                    "Not enough valid dates to analyse activity."
                )


        # =================================================
        # 5. EVENT EXPLORER
        # =================================================
        

        elif page == "Event Explorer":

            st.header(
                "🔎 Fire Observation Explorer"
            )

            st.markdown(
                "Search, filter and explore individual satellite "
                "fire observations across the Amazon Basin."
            )

            explorer_df = df.copy()

            sensors = sorted(
                explorer_df["sensor_type"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_sensors = st.multiselect(
                "Select Satellite Sensors",
                sensors,
                default=sensors
            )

            explorer_df = explorer_df[
                explorer_df["sensor_type"].isin(
                    selected_sensors
                )
            ]

            explorer_df["acq_date"] = pd.to_datetime(
                explorer_df["acq_date"],
                errors="coerce"
            )

            valid_dates = explorer_df[
                "acq_date"
            ].dropna()

            if not valid_dates.empty:

                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()

                selected_dates = st.date_input(
                    "Select Observation Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="event_explorer_date_range"
                )

                if (
                    isinstance(selected_dates, (tuple, list))
                    and len(selected_dates) == 2
                ):

                    start_date, end_date = selected_dates

                    explorer_df = explorer_df[
                        explorer_df["acq_date"].dt.date.between(
                            start_date,
                            end_date
                        )
                    ]
            
            # FRP Range Filter

            st.subheader("🔥 Filter by Fire Radiative Power")

            explorer_df["frp"] = pd.to_numeric(
                explorer_df["frp"],
                errors="coerce"
            )

            valid_frp = explorer_df["frp"].dropna()

            if not valid_frp.empty:

                min_frp = float(valid_frp.min())
                max_frp = float(valid_frp.max())

                if min_frp < max_frp:

                    frp_range = st.slider(
                        "Select FRP Range (MW)",
                        min_value=min_frp,
                        max_value=max_frp,
                        value=(min_frp, max_frp),
                        key="event_explorer_frp_range"
                    )

                    explorer_df = explorer_df[
                        explorer_df["frp"].between(
                            frp_range[0],
                            frp_range[1]
                        )
                    ]

                else:
                    st.info(
                        f"Available FRP value: {min_frp:.2f} MW"
                    )

            else:
                st.info("No valid FRP values available.")

            st.divider()

            col1, col2 = st.columns(2)

            col1.metric(
                "Matching Observations",
                f"{len(explorer_df):,}"
            )

            col2.metric(
                "Sensors Selected",
                explorer_df["sensor_type"].nunique()
            )
            
            # Interactive Fire Observation Map

            st.subheader("🗺️ Filtered Fire Observation Map")

            map_data = explorer_df.copy()

            map_data["latitude"] = pd.to_numeric(
                map_data["latitude"],
                errors="coerce"
            )

            map_data["longitude"] = pd.to_numeric(
                map_data["longitude"],
                errors="coerce"
            )

            map_data = map_data.dropna(
                subset=["latitude", "longitude"]
            )

            if not map_data.empty:

                fire_layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=map_data,
                    get_position="[longitude, latitude]",
                    get_fill_color=[255, 90, 40, 180],
                    get_radius=1200,
                    pickable=True,
                    auto_highlight=True
                )

                view_state = pdk.ViewState(
                    latitude=map_data["latitude"].mean(),
                    longitude=map_data["longitude"].mean(),
                    zoom=4,
                    pitch=0
                )

                deck = pdk.Deck(
                    layers=[fire_layer],
                    initial_view_state=view_state,
                    tooltip={
                        "text": "Sensor: {sensor_type}\nFRP: {frp} MW"
                    },
                    map_style=None
                )

                st.pydeck_chart(
                    deck,
                    use_container_width=True
                )

                st.caption(
                    "Map displays filtered satellite hotspot "
                    "observations, not confirmed fire boundaries."
                )

            else:
                st.info("No valid coordinates available for mapping.")

            st.subheader(
                "Satellite Observation Records"
            )

            st.dataframe(
                explorer_df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "📥 Download Filtered Observations",
                data=explorer_df.to_csv(index=False),
                file_name="FIREHARMONY_Filtered_Observations.csv",
                mime="text/csv"
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "FIREHARMONY | NASA Space Apps Challenge 2026"
)
