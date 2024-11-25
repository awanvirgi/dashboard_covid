# Import libraries
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap
import plotly.express as px


# Konfigurasi halaman
st.set_page_config(layout="wide")

# Load dataset
df_selected = pd.read_csv("df_selected.csv")

# Convert Date to datetime
df_selected['Date'] = pd.to_datetime(df_selected['Date'])
df_selected['Year'] = df_selected['Date'].dt.year

# Sidebar filters
st.sidebar.header("Filter Data")
location = st.sidebar.selectbox("Pilih Lokasi", ["Semua"] + df_selected["Province"].unique().tolist())
year = st.sidebar.selectbox("Pilih Tahun", ["Semua"] + df_selected["Year"].unique().tolist())

# Filter dataset
def filter_data(df, location, year):
    if location != "Semua":
        df = df[df['Province'] == location]
    if year != "Semua":
        df = df[df['Year'] == int(year)]
    return df

# Apply the filter function with both location and year
df_filtered = filter_data(df_selected, location, year)

# Format numbers
def format_number(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}M"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.1f}Juta"
    elif n >= 1_000:
        return f"{n/1_000:.1f}Ribu"
    return str(n)


# Display metrics
st.title("Dashboard COVID-19 di Indonesia")

tab1, tab2 = st.tabs(["Informasi", "Dashboard Data"])

with tab1:
# Gambaran umum pandemi
    st.markdown("""
    #### Dampak Pandemi COVID-19 di Indonesia

    Pandemi COVID-19 yang melanda dunia, termasuk Indonesia, telah memberikan dampak besar pada berbagai sektor, khususnya dalam bidang kesehatan, ekonomi, dan sosial. Sejak kasus pertama terkonfirmasi pada Maret 2020, jumlah masyarakat yang terinfeksi mengalami peningkatan yang signifikan, meskipun pemerintah beserta instansi terkait telah berupaya melakukan berbagai langkah penanggulangan, seperti penerapan protokol kesehatan, pembatasan sosial, dan pelaksanaan program vaksinasi massal. Data terkait jumlah kasus COVID-19 di Indonesia menjadi salah satu informasi penting yang berperan dalam memantau perkembangan pandemi, memahami tingkat penyebaran di berbagai wilayah, serta mengidentifikasi tren yang mungkin terjadi dalam waktu dekat.

    Visualisasi data jumlah kasus COVID-19 di Indonesia bukan hanya berfungsi sebagai arsip krisis kesehatan yang telah dihadapi, tetapi juga sebagai sarana pembelajaran untuk meningkatkan kesiapsiagaan dalam menghadapi potensi wabah di masa mendatang. Dengan analisis atas tren, pola penyebaran, serta evaluasi terhadap respons yang efektif maupun yang belum optimal, pemerintah dan masyarakat dapat merancang langkah-langkah yang lebih cepat dan tepat apabila terjadi wabah lainnya. Melalui pembelajaran dari data COVID-19, diharapkan Indonesia dapat lebih tanggap dalam menghadapi ancaman kesehatan serupa, baik melalui kebijakan yang responsif, peningkatan sumber daya kesehatan, maupun kolaborasi yang erat antara pemerintah dan masyarakat.
    """)

    st.markdown("""
    #### Tujuan dan Jenis Visualisasi
    
    | No | Tujuan Visualisasi | Jenis Visualisasi | Deskripsi | Alat/Metode yang Digunakan |
    |----|--------------------|-------------------|-----------|----------------------------|
    | 1  | Memantau jumlah kasus baru COVID-19 di Indonesia | Trend Line | Menampilkan perkembangan jumlah kasus baru setiap bulan untuk menganalisis tren penyebaran virus | Python (Matplotlib, Seaborn, Plotly) |
    | 2  | Memantau jumlah kematian akibat COVID-19 di Indonesia | Trend Line | Menampilkan jumlah kematian per bulan untuk memahami dampak fatal dari pandemi | Python (Matplotlib, Seaborn, Plotly) |
    | 3  | Menyajikan data rata-rata pasien sembuh per tahun | Bar Chart | Menampilkan perbandingan jumlah pasien yang sembuh tiap tahun | Python (Matplotlib, Seaborn, Plotly) |
    | 4  | Menyajikan penyebaran COVID-19 secara geografis | Map | Menampilkan peta penyebaran kasus COVID-19 di Indonesia berdasarkan lokasi geografis | Python (Folium, Plotly, GeoPandas) |
    | 5  | Menampilkan penyebaran kasus per provinsi | Bar Chart | Menampilkan jumlah kasus per provinsi untuk melihat distribusi kasus COVID-19 di Indonesia | Python (Matplotlib, Seaborn, Plotly) |
    """)

    # Display global metrics
    st.markdown("""
    #### Dampak Utama Pandemi:
    - **Kasus COVID-19** telah melampaui ratusan juta di seluruh dunia.
    - **Angka kematian** global mencapai jutaan, dengan kerugian besar pada banyak aspek kehidupan.
    - **Kemajuan vaksinasi** telah membantu menekan penyebaran dan dampaknya.
    """)
    
    

with tab2 :
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Kasus", format_number(df_filtered["Total Cases"].sum()))
    col2.metric("Total Kematian", format_number(df_filtered["Total Deaths"].sum()))
    col3.metric("Total Sembuh", format_number(df_filtered["Total Recovered"].sum()))
    col4.metric("Kasus Aktif", format_number(df_filtered["Total Active Cases"].sum()))

    # Display Heatmap and Trend side-by-side
    st.markdown("## Visualisasi Data")

    # Adjusting column widths for full usage
    col1, col2 = st.columns([7, 6])

    # Membuat peta dasar dengan rata-rata lokasi
    m = folium.Map(location=[df_filtered['Latitude'].mean(), df_filtered['Longitude'].mean()], zoom_start=5)

    # Sampling data untuk mengurangi beban visualisasi
    sampled_df = df_filtered.sample(n=min(len(df_filtered), 1000), random_state=42)

    # Membuat data heatmap
    heat_data = [[row['Latitude'], row['Longitude'], row['Total Cases']] for _, row in sampled_df.iterrows()]

    # Gradien warna untuk heatmap
    gradient = {
        0.0: 'yellow',
        0.2: '#ffff66',
        0.4: '#ffcc00',
        0.6: '#ff6600',
        0.8: '#ff3300',
        1.0: '#cc0000'
    }

    # Menambahkan HeatMap ke peta
    HeatMap(
        heat_data,
        min_opacity=0.4,
        radius=40,
        blur=25,
        max_zoom=20,
        gradient=gradient
    ).add_to(m)

    # Menambahkan tooltip untuk setiap lokasi
    for _, row in sampled_df.iterrows():
        label = (f"Province: {row['Province']}<br>"
                f"Total Cases: {row['Total Cases']}<br>"
                f"Total Deaths: {row['Total Deaths']}")

        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=0,
            color='red',
            fill=True,
            fill_opacity=0,
            tooltip=label
        ).add_to(m)

    # Menampilkan peta di Streamlit
    with col1:
        st.markdown("### Visualisasi Heatmap dengan Tooltip")
        st_folium(m, width="100%", height=500)

    with col2:
        st.markdown("### Tren Total Kasus")

        df_filtered['6_Month_Period'] = df_filtered['Date'].dt.to_period('6M')
        six_month_cases = df_filtered.groupby('6_Month_Period')['Total Cases'].sum()

        data_plot_cases = pd.DataFrame({
            "Periode": six_month_cases.index.astype(str),
            "Cases": six_month_cases.values
        })

        scatter_cases = go.Scatter(
            x=data_plot_cases["Periode"],
            y=data_plot_cases["Cases"],
            mode="markers",
            marker=dict(
                size=10,
                color=data_plot_cases["Cases"],
                colorscale="Reds",
                showscale=True
            ),
            text=[f"Periode: {p}<br>Cases: {c:,.0f}" for p, c in zip(data_plot_cases["Periode"], data_plot_cases["Cases"])],
            hoverinfo="text",
            name="Data"
        )

        trendline_cases = go.Scatter(
            x=data_plot_cases["Periode"],
            y=data_plot_cases["Cases"],
            mode="lines",
            line=dict(color="red", width=2),
            name="Tren Cases"
        )

        layout_cases = go.Layout(
            title="Tren Total Kasus per 6 Bulan",
            xaxis_title="Periode (6 Bulan)",
            yaxis_title="Jumlah Total Kasus",
            hovermode="closest"
        )

        fig_cases = go.Figure(data=[scatter_cases, trendline_cases], layout=layout_cases)
        st.plotly_chart(fig_cases, use_container_width=True)

    # Visualisasi Rata-Rata Kasus Sembuh per Tahun
    col1, col2 = st.columns(2)

    # Average Total Recovered per Year
    with col1:
        st.markdown("### Rata-Rata Kasus Sembuh per Tahun")
        avg_recovered_per_year = df_filtered.groupby('Year')['Total Recovered'].mean().reset_index()
        fig_recovered = go.Figure()

        fig_recovered.add_trace(
            go.Bar(
                y=avg_recovered_per_year['Year'],
                x=avg_recovered_per_year['Total Recovered'],
                orientation='h',
                marker=dict(color='green', opacity=0.8),
                text=avg_recovered_per_year['Total Recovered'].apply(lambda x: f"{x/1000:.2f}K"),
                textposition='outside'
            )
        )

        fig_recovered.update_layout(
            title='Rata-Rata Kasus Sembuh per Tahun',
            xaxis_title='Rata-rata Kasus Sembuh',
            yaxis_title='Tahun',
            template='plotly_white'
        )

        st.plotly_chart(fig_recovered, use_container_width=True)

    # Total Deaths per 6 Months
    with col2:
        st.markdown("### Tren Total Kematian")

        six_month_deaths = df_filtered.groupby('6_Month_Period')['Total Deaths'].sum()

        data_plot_deaths = pd.DataFrame({
            "Periode": six_month_deaths.index.astype(str),
            "Deaths": six_month_deaths.values
        })

        scatter_deaths = go.Scatter(
        x=data_plot_deaths["Periode"],
        y=data_plot_deaths["Deaths"],
        mode="markers",
        marker=dict(
            size=10,
            color=data_plot_deaths["Deaths"],
            colorscale="YlOrBr",  # Skema warna kuning
            showscale=True
        ),
        text=[f"Periode: {p}<br>Deaths: {d:,}" for p, d in zip(data_plot_deaths["Periode"], data_plot_deaths["Deaths"])],
        hoverinfo="text",
        name="Data"
        )

        trendline_deaths = go.Scatter(
            x=data_plot_deaths["Periode"],
            y=data_plot_deaths["Deaths"],
            mode="lines",
            line=dict(color="gold", width=2),  # Menggunakan warna emas (kuning cerah)
            name="Tren Deaths"
        )


        layout_deaths = go.Layout(
            title="Tren Total Kematian per 6 Bulan",
            xaxis_title="Periode (6 Bulan)",
            yaxis_title="Jumlah Total Deaths",
            hovermode="closest"
        )

        fig_deaths = go.Figure(data=[scatter_deaths, trendline_deaths], layout=layout_deaths)

        st.plotly_chart(fig_deaths, use_container_width=True)


    # Menambahkan visualisasi tambahan (10 provinsi dan proporsi pulau)
    st.markdown("## Analisis Berdasarkan Provinsi dan Pulau")

    # Membuat dua kolom untuk visualisasi berdampingan
    col1, col2 = st.columns(2)

    # Menambahkan dua slider untuk memilih jumlah provinsi dan jumlah pulau yang ditampilkan
    with col1:
        top_n_provinces = st.slider("Pilih Jumlah Provinsi untuk Ditampilkan", 5, 20, 10)

    with col2:
        top_n_islands = st.slider("Pilih Jumlah Pulau untuk Ditampilkan", 3, 7, 7)

    # Visualisasi: 10 Provinsi dengan Kasus Tertinggi
    with col1:
        st.markdown("### Provinsi dengan Total Kasus Terbaru Tertinggi")
        
        # Menyiapkan data untuk visualisasi
        df_latest_province = df_filtered.loc[df_filtered.groupby('Province')['Date'].idxmax()]
        province_cases = df_latest_province.sort_values('Total Cases', ascending=False).head(top_n_provinces)

        data_plot_province = pd.DataFrame({
            "Provinsi": province_cases['Province'],
            "Kasus": province_cases['Total Cases'],
            "Kematian": province_cases['Total Deaths'],
            "Kasus Aktif": province_cases['Total Active Cases'],
            "Sembuh": province_cases['Total Recovered']
        })

        data_plot_province = data_plot_province.sort_values("Kasus", ascending=True)

        bar_chart_province = go.Bar(
            x=data_plot_province["Kasus"],
            y=data_plot_province["Provinsi"],
            orientation="h",
            marker=dict(
                color=data_plot_province["Kasus"],
                colorscale="YlOrRd",
                showscale=True
            ),
            text=[f"{kasus:,} Kasus" for kasus in data_plot_province["Kasus"]],
            hovertemplate=( 
                "Provinsi: %{y}<br>" + 
                "Total Kasus: %{x:,}<br>" + 
                "Total Kematian: %{customdata[0]:,}<br>" +
                "Kasus Aktif: %{customdata[1]:,}<br>" +
                "Sembuh: %{customdata[2]:,}<extra></extra>"
            ),
            customdata=data_plot_province[["Kematian", "Kasus Aktif", "Sembuh"]].values,
            name="Total Kasus"
        )

        layout_province = go.Layout(
            xaxis_title="Jumlah Kasus",
            yaxis_title="Provinsi",
            hovermode="closest"
        )

        fig_province = go.Figure(data=[bar_chart_province], layout=layout_province)
        st.plotly_chart(fig_province, use_container_width=True)

    # Visualisasi: Proporsi Kasus di Pulau Teratas
    with col2:
        st.markdown("### Proporsi Kasus COVID-19 di Pulau Teratas")
        
        # Menyiapkan data untuk visualisasi
        df_latest_island = df_filtered.loc[df_filtered.groupby('Island')['Date'].idxmax()]
        top_islands = df_latest_island.sort_values('Total Cases', ascending=False).head(top_n_islands)

        data_plot_island = pd.DataFrame({
            "Island": top_islands['Island'],
            "Kasus": top_islands['Total Cases']
        })

        fig_island = px.pie(data_plot_island,
                            names='Island',
                            values='Kasus',
                            hover_data=["Kasus"],
                            labels={"Kasus": "Total Kasus", "Island": "Pulau"})

        fig_island.update_traces(marker=dict(colors=px.colors.sequential.YlOrRd[::-1][:len(top_islands)]))
        fig_island.update_layout(title="Proporsi Kasus COVID-19 di Pulau Teratas")
        st.plotly_chart(fig_island, use_container_width=True)
