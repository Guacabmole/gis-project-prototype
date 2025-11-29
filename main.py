import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import GroupedLayerControl
import json
import pandas as pd

st.set_page_config(layout = "wide")
st.markdown("""
    <style>
        /* Remove excessive top padding from the main app area */
        section[data-testid="stHeader"] {visibility: hidden;}
        div.block-container {
            padding-top: 1rem !important;   /* reduce from ~6rem default */
        }
        .stMultiSelect [data-baseweb="tag"] {
            background-color: #4a4a4a !important;  /* gray tags */
            color: #ffffff !important;
            border-radius: 999px !important;
        }
        .stMultiSelect div[data-baseweb="select"] > div {
            max-height: 60px !important;   
            overflow-y: auto !important;   
        }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def read_geojson(path):
    with open(path, "r") as dir:
        data = json.load(dir)
    return data
country_geojson = read_geojson("data/countries_filtered.geo.json")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

survey_data = load_data("data/mock_survey_data.csv")
country_data = load_data("data/mock_country_data_new.csv")
best_interventions = load_data("data/best_interventions_with_stats.csv")

@st.cache_data
def get_country_aggregates(df):
    agg = df[df["intervention"] == "control"]\
        .groupby("country_code")[["belief_cc", "policy_support", "share_social_media", "wept"]]\
        .mean().reset_index()
    return agg

country_aggregates = get_country_aggregates(survey_data)

risk_factor_mapper = {
    None : "None", 
    "risk_factor_1" : "Risk Factor 1",
    "risk_factor_2": "Risk Factor 2"
}

outcome_var_mapper = {
    "belief_cc" : "Belief in Climate Change",
    "policy_support": "Policy Support",
    "share_social_media": "Sharing information on Social Media",
    "wept": "Work for Environmental Protection Task"
}

intervention_mapper = {
    "psychological_distance": "Psychological Distance",
    "letter_future_gen": "Letter to Future Generations",
    "effective_collective_action": "Effective Collective Action",
    "future_self_continuity": "Future Self Continuity",
    "system_justification": "System Justification",
    "scientific_consensus": "Scientific Consensus",
    "binding_moral_foundations": "Binding Moral Foundations",
    "dynamic_social_norms": "Dynamic Social Norms",
    "pluralistic_ignorance": "Pluralistic Ignorance",
    "negative_emotions": "Negative Emotions",
    "working_together_normative_appeal": "Working Together Normative Appeal"
}

st.title("Psychology of Climate Change - Prototype")

with st.sidebar:
    with st.container(border=True, gap=None):
        st.subheader("Region")
        region_options = sorted(country_data["region"].dropna().unique().tolist())
        region_filter = st.multiselect(
            "Please select the region to visualise:",
            options=region_options,
            default=region_options,   # all selected by default
        )

    with st.container(border=True, gap=None):
        st.subheader("Country income groups")
        income_options = sorted(country_data["income_group"].dropna().unique().tolist())
        income_group_filter = st.multiselect(
            "Please select income groups to visualise:",
            options=income_options,
            default=income_options,
        )

with st.sidebar:

    with st.container(border=True, gap=None):
        st.subheader("Country Risk Factor")
        risk_factor_selection = st.selectbox(
            "Please select a risk factor to visualise:",
            options=risk_factor_mapper,
            format_func=lambda x: risk_factor_mapper[x]
        )
        if risk_factor_selection:
            with st.popover("info"):
                st.write(f"Detailed information about {risk_factor_mapper[risk_factor_selection]}.")

    with st.container(border=True, gap=None):
        st.subheader("Outcome Variable")
        outcome_var_selection = st.selectbox(
            "Please select an outcome variable to visualise:",
            options=outcome_var_mapper,
            format_func=lambda x: outcome_var_mapper[x]
        )
        with st.popover("info"):
            st.write(f"Detailed information about {outcome_var_mapper[outcome_var_selection]}.")

    st.title("Demographic filters")

    with st.expander("Click to expand"):
        age_filter = st.slider("Select age range:", 18, 70, (18, 70))
        gender_filter = st.multiselect("Select gender(s):", options=["male", "female", "nonbinary or other"])
        education_filter = st.multiselect("Select education level(s):", options=["0 to 6 years", "7 to 12 years", "13 to 16 years", "17 or more years"])
        personal_income_filter = st.multiselect(  
            "Select income level(s):",
            options=["less than 10K", "10K to 15K", "15K to 25K", "25K to 50K", "50K to 100K", "100K to 150K", "150K to 200K", "more than 200K"]
        )
        perc_ses_filter = st.multiselect("Select perceived socioeconomic status level(s):", options=["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"])
        sp_ideology_filter = st.slider("Select range for sociopolitical ideology:", 0, 100, (0, 100))
        econ_ideology_filter = st.slider("Select range for economic ideology:", 0, 100, (0, 100))


if risk_factor_selection:
    st.write("""
             You can display country colours based on either the risk factor or the average outcome variable. 
             You can select this from the layer control at the top-right of the map.
             """)
st.write("To display more information on the selected outcome variable for a country, please select a risk factor and click on the bubble.")

# ----- filter countries by region + income group -----
mask = pd.Series(True, index=country_data.index)

if region_filter:  # if at least one region is selected
    mask &= country_data["region"].isin(region_filter)

if income_group_filter:  # if at least one income group is selected
    mask &= country_data["income_group"].isin(income_group_filter)

filtered_country_data = country_data[mask]

# filter the aggregates to those countries
filtered_country_aggregates = country_aggregates[
    country_aggregates["country_code"].isin(
        filtered_country_data["country_code"]
    )
]

m = folium.Map(
    zoom_start=2.5,
    location=[20, 0],
    tiles="CartoDB positron"
)

# outcome choropleth uses the filtered aggregates
outcome_choropleth = folium.Choropleth(
    geo_data=country_geojson,
    data=filtered_country_aggregates,
    columns=["country_code", outcome_var_selection],
    key_on="feature.id",
    fill_color="YlGn",
    bins=8,
    fill_opacity=0.8,
    line_opacity=0,  
    highlight=False,
    name=outcome_var_mapper[outcome_var_selection],
    legend_name=f"Scale for {outcome_var_mapper[outcome_var_selection]}"
).add_to(m)

# Encoding Risk Factor as Bubbles
if risk_factor_selection:
    risk_df = filtered_country_data.dropna(
        subset=[risk_factor_selection, "lat", "lon"]
    ).copy()

    if not risk_df.empty:
        vmin = risk_df[risk_factor_selection].min()
        vmax = risk_df[risk_factor_selection].max()

        def scale_radius(value, vmin, vmax, rmin=4, rmax=18):
            if pd.isna(value) or vmax == vmin:
                return (rmin + rmax) / 2
            return rmin + (value - vmin) * (rmax - vmin) / (vmax - vmin)

        risk_layer = folium.FeatureGroup(
            name=f"Risk factor: {risk_factor_mapper[risk_factor_selection]}"
        )

        for _, row in risk_df.iterrows():
            country_code = row["country_code"]
            country_label = row.get("country", country_code)

            risk_label = risk_factor_mapper[risk_factor_selection]
            risk_val = row.get(risk_factor_selection, pd.NA)
            risk_text = "" if pd.isna(risk_val) else f"{risk_val:.2f}"

            stats_row = best_interventions[
                (best_interventions["country_code"] == country_code) &
                (best_interventions["outcome"] == outcome_var_selection)
            ]

            if not stats_row.empty:
                stats_row = stats_row.iloc[0]

                mean_val = stats_row["mean_value"]
                ci_low = stats_row["ci_low"]
                ci_high = stats_row["ci_high"]
                p_val = stats_row["p_value"]

                raw_int = str(stats_row["intervention"])   
                best_label = raw_int.replace("_", " ").title()

                mean_text = f"{mean_val:.2f}"
                ci_text = f"[{ci_low:.2f}, {ci_high:.2f}]"
                p_text = f"{p_val:.3f}"
            else:
                best_label = "No data"
                mean_text = ci_text = p_text = "–"

            outcome_label = outcome_var_mapper[outcome_var_selection]

            # ----- styled HTML popup for this bubble -----
            popup_html = f"""
            <div style="font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        font-size: 12px;
                        line-height: 1.4;
                        max-width: 260px;">
                <div style="font-weight: 700; font-size: 14px; margin-bottom: 4px;">
                    {country_label} ({country_code})
                </div>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 4px 0 6px 0;" />

                <div style="margin-bottom: 4px;">
                    <span style="font-weight: 600;">{risk_label}:</span>
                    <span>{risk_text}</span>
                </div>

                <div style="margin-bottom: 4px;">
                    <span style="font-weight: 600;">{outcome_label} (mean):</span><br/>
                    <span>{mean_text}</span>
                </div>

                <div style="margin-bottom: 4px;">
                    <span style="font-weight: 600;">95% CI:</span><br/>
                    <span>{ci_text}</span>
                </div>

                <div style="margin-bottom: 4px;">
                    <span style="font-weight: 600;">p-value:</span>
                    <span>{p_text}</span>
                </div>

                <div style="margin-top: 6px;">
                    <span style="font-weight: 600;">Most effective intervention:</span><br/>
                    <span>{best_label}</span>
                </div>
            </div>
            """

            radius = scale_radius(row[risk_factor_selection], vmin, vmax)

            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=radius,
                fill=True,
                fill_opacity=0.68,
                color=None,
                fill_color="orangered",
                popup=folium.Popup(popup_html, max_width=280)
            ).add_to(risk_layer)

        risk_layer.add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)

# auto-zoom based on region selection ->> TO BE IMPROVED
if region_filter:
    zoom_data = country_data[
        country_data["region"].isin(region_filter)
    ].dropna(subset=["lat", "lon"])
else:
    zoom_data = country_data.dropna(subset=["lat", "lon"])

if not zoom_data.empty:
    m.fit_bounds([
        [zoom_data["lat"].min(), zoom_data["lon"].min()],
        [zoom_data["lat"].max(), zoom_data["lon"].max()]
    ])


map = st_folium(m, use_container_width=True)
