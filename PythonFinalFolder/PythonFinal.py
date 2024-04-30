""" Name: Devin Perugini CS230: Section 6 Data: Bridges in Georgia URL: Link to your web application on Streamlit Cloud (if posted)

Description: This Program takes a compilation of data on 10,000 bridges in Georgia and performs calculations and
functions in order to utilize the data to create charts, graphs, and maps that display specific information about the
bridge information from the dataset.
"""


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

st.set_page_config(
    page_title="Georgia Bridges Data Analysis",
    page_icon="🌉",
    layout="centered",
    initial_sidebar_state="auto"
)
#[DA1]
def bridge_data():
    df = pd.read_csv('bridges_georgia_dataset.csv').set_index("Structure Number")
    df.fillna("No Data Present", inplace=True)

    return df
#[PY3] first usage
df = bridge_data()
#[ST1]
st.set_option('deprecation.showPyplotGlobalUse', False)

#[ST4]
sidebar_option = st.sidebar.selectbox("Select Page", ["Home", "County Information", "Bridge Map"])
if sidebar_option == "Home":

    #[ST4]
    st.title("Georgia Bridges Data Analysis")
    st.image("Georgia_bridge.png", caption="Sidney Lanier Bridge", use_column_width=True)

#[PY1]
#Pie Chart for main material distribution #[VIZ1]
    def plot_bridge_distribution(data, weight=6):
        bridge_counts = data["43A - Main Span Material"].value_counts()

        other_count = bridge_counts[bridge_counts / bridge_counts.sum() * 100 < weight].sum()
        filtered_counts = bridge_counts[bridge_counts / bridge_counts.sum() * 100 >= weight]
        filtered_counts["Other Span Material"] = other_count

        plt.figure(figsize=(8, 8))
        plt.pie(filtered_counts, labels=filtered_counts.index, autopct='%1.1f%%', startangle=140)
        plt.title("Distribution of Bridges by Main Span Material")
        plt.axis('equal')
        st.pyplot()


    plot_bridge_distribution(df)



#Bar Chart of Reconstructions #[VIZ2]
    reconstruction_years = df['106 - Year Reconstructed'].dropna().astype(int)  # Drop NaN values and convert to int
    reconstruction_counts = reconstruction_years.value_counts().sort_index()
    reconstruction_counts = reconstruction_counts.loc[1975:2022]

    plt.figure(figsize=(10, 6))
    reconstruction_counts.plot(kind='bar', color='skyblue')
    plt.title('Number of Reconstructed Bridges Since 1975')
    plt.xlabel('Reconstruction Year')
    plt.ylabel('Number of Bridges')
    plt.ylim(0,130)
    plt.tight_layout()
    st.pyplot()



elif sidebar_option == "County Information":

    st.title("County Specific Information")

#[ST1]
    def selected_counties():
        #[DA2]
        county_options = sorted(df["County Name"].unique())
        #[ST2]
        selected_counties = st.multiselect("Select County or Counties", county_options, default=county_options[0:2])
        return selected_counties


#Line Chart of bridges being built over the years per county #[VIZ3]

    selected_counties = selected_counties()

    plt.figure(figsize=(10, 6))

    for county in selected_counties:
        #[DA4]
        county_data = df[df['County Name'] == county]
        county_years = county_data['Year Built'].dropna().astype(int)
        county_counts = county_years.value_counts().sort_index()
        county_counts = county_counts.loc[1885:county_counts.index.max()]

        plt.plot(county_counts.index, county_counts.values, marker='o', label=county)

    plt.title(f'Number of Bridges Built Each Year Per County (1885 - Present)')
    plt.xlabel('Year Built')
    plt.ylabel('Number of Bridges')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='County', title_fontsize='13', loc='upper right')

    plt.tight_layout()
    st.pyplot()
    #[DA9] #[PY3] second usage
    selected_df = df[df['County Name'].isin(selected_counties)]

    avg_structure_length_by_county = selected_df.groupby('County Name')['49 - Structure Length (ft.)'].mean()
    #[DA6]
    pivot_table = pd.pivot_table(selected_df, values='49 - Structure Length (ft.)', index='County Name', aggfunc='mean')

    st.write(pivot_table.reset_index().rename(columns={'49 - Structure Length (ft.)': 'Average Structure Length'}), use_container_width=True)


elif sidebar_option == "Bridge Map":

    st.title("Map of Top Longest Bridges in Georgia")

    #[ST3]
    top_bridges = st.slider('Choose Amount of Longest Bridges', min_value=50, max_value=1000, value=500)

    #[PY2]
    def get_summary_statistics(df):
        locations = df["City - InfoBridge Place Name"].tolist()
        lengths = df["49 - Structure Length (ft.)"].tolist()
        ages = df["Bridge Age (yr)"].tolist()

        return locations, lengths, ages
    #[DA3]
    longest_bridges = df.nlargest(top_bridges, '49 - Structure Length (ft.)')

    locations, lengths, ages = get_summary_statistics(longest_bridges)
    data = longest_bridges[['17 - Longitude (decimal)', '16 - Latitude (decimal)']].values.tolist()

    #[PY5]
    location_dict = {'location_' + str(i): location for i, location in enumerate(data)}
    #[DA7]
    bridge_info = []
    for loc, length, age in zip(locations, lengths, ages):
        bridge_info.append({"Location": loc, "Length (ft)": length, "Age": age})

    #[PY4]
    dictdata = [{"position": location} for location, in
                zip(location_dict.values())]

    tooltip_text = [
        {"html": f"<b>{point['Location']}</b><br>Length: <b>{point['Length (ft)']}</b><br>Age: <b>{point['Age']}</b>"}
        for point in bridge_info
    ]
    #[VIZ4]
    scatterplot_layer = pdk.Layer(
        "ScatterplotLayer",
        data=dictdata,
        get_position="position",
        get_radius=2500,
        get_fill_color=[255, 0, 0],
        pickable=True,
        tooltip=tooltip_text
    )

    view_state = pdk.ViewState(
        longitude=float(longest_bridges['17 - Longitude (decimal)'].mean()),
        latitude=float(longest_bridges['16 - Latitude (decimal)'].mean()),
        zoom=6
    )

    map = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[scatterplot_layer]
    )
    st.pydeck_chart(map)
    st.write("Top 10 Info:")
    st.write(bridge_info[0:10])

