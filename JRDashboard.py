import streamlit as st
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import altair as alt
import json


st.set_page_config(
    page_title="Dashboard Gambaran Kecelakaan",
    layout="wide",  # or "centered"
    initial_sidebar_state="expanded"
)
menu_utama = st.sidebar.radio("Menu", ["Dashboard Analisa", "Forecasting"])
dfw=pd.read_csv('Data_Laka_Weekly.csv')
dfw["Kecamatan"] = dfw["Kecamatan"].str.strip().str.title()  
# Convert 'week' to sortable datetime (ISO format uses 'W' for week)
dfw["week_dt"] = pd.to_datetime(dfw["week"] + "-1", format="%Y-%W-%w")  # '-1' = Monday

def general_analysis(dfw):
    
    # Sort weeks for dropdown
    sorted_weeks = sorted(dfw["week"].unique())

    # Sidebar selectors
    st.sidebar.title("📆 Filter Minggu")
    start_week = st.sidebar.selectbox("Start Week", sorted_weeks, index=0)
    end_week = st.sidebar.selectbox("End Week", sorted_weeks, index=len(sorted_weeks)-1)
        

    # Convert selected weeks to datetime
    start_dt = pd.to_datetime(start_week + "-1", format="%Y-%W-%w")
    end_dt = pd.to_datetime(end_week + "-1", format="%Y-%W-%w")
    
    total_week=((end_dt-start_dt).days//7)+1

    # Filter DataFrame
    filtered_df = dfw[(dfw["week_dt"] >= start_dt) & (dfw["week_dt"] <= end_dt)]
    
     # Extract month name
    filtered_df["month_name"] = filtered_df["week_dt"].dt.strftime("%B")
    
    # Optional: also year-month format
    filtered_df["month_year"] = filtered_df["week_dt"].dt.strftime("%B %Y")

    
    st.header("🚔 Dashboard Jumlah Kecelakaan Mingguan")
    st.write(f"Data dari Minggu ke- **{start_week}** hingga Minggu ke- **{end_week}** untuk {total_week} minggu")
    st.dataframe(filtered_df[["week", "month_name", "month_year","Kecamatan", "Jumlah_Kecelakaan"]], 
                 use_container_width=True, hide_index=True)
    
    
    chart_data =(filtered_df.groupby("Kecamatan")["Jumlah_Kecelakaan"].sum().reset_index().sort_values(by="Jumlah_Kecelakaan", ascending=False).head(10))
    
    
    # Display Top 10 Kecamatan dengan Jumlah Kecelakaan Terbanyak
    
    bar_chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X("Kecamatan:N", sort="-y"),
        y=alt.Y("Jumlah_Kecelakaan:Q"),
        tooltip=["Kecamatan", "Jumlah_Kecelakaan"]).properties(
        width=700,height=400,title=f"Top 10 Kecamatan dengan Jumlah Kecelakaan Tertinggi dari Minggu ke- {start_week} hingga Minggu ke- {end_week} untuk {total_week} minggu")

    st.altair_chart(bar_chart, use_container_width=True)
    
    
    # Display Top 10 Kecamatan dengan rata-rata Jumlah Kecelakaan Terbanyak
    
    mean_data =(filtered_df.groupby("Kecamatan")["Jumlah_Kecelakaan"].mean().reset_index().sort_values(by="Jumlah_Kecelakaan", ascending=False).head(10))
    
    
    mean_chart = alt.Chart(mean_data).mark_bar(color='green').encode(
        x=alt.X("Kecamatan:N", sort="-y"),
        y=alt.Y("Jumlah_Kecelakaan:Q"),
        tooltip=["Kecamatan", "Jumlah_Kecelakaan"]).properties(
        width=500,height=400,title=f"Top 10 Kecamatan dengan Rata-Rata Jumlah Kecelakaan Tertinggi dari Minggu ke- {start_week} hingga Minggu ke- {end_week} untuk {total_week} minggu")

    st.altair_chart(mean_chart, use_container_width=True)
    

def area_analysis(dfw):

    # Sort weeks for dropdown
    sorted_weeks = sorted(dfw["week"].unique())
    
    st.sidebar.header('Filter Lokasi')
    daftar_lokasi = sorted(dfw["Kecamatan"].unique())
    lokasi_pilihan = st.sidebar.selectbox('Pilih Lokasi', daftar_lokasi)

    # Sidebar selectors
    st.sidebar.title("📆 Filter Minggu")
    start_week = st.sidebar.selectbox("Start Week", sorted_weeks, index=0)
    end_week = st.sidebar.selectbox("End Week", sorted_weeks, index=len(sorted_weeks)-1)
        

    # Convert selected weeks to datetime
    start_dt = pd.to_datetime(start_week + "-1", format="%Y-%W-%w")
    end_dt = pd.to_datetime(end_week + "-1", format="%Y-%W-%w")
    
    total_week=(end_dt-start_dt).days//7

    # Filter DataFrame
    filtered_df = dfw[(dfw["Kecamatan"]==lokasi_pilihan) & (dfw["week_dt"] >= start_dt) & (dfw["week_dt"] <= end_dt)]
    
     # Extract month name
    filtered_df ["month_name"] = filtered_df["week_dt"].dt.strftime("%B")
    
    # Optional: also year-month format
    filtered_df["month_year"] = filtered_df["week_dt"].dt.strftime("%B %Y")
    
    st.header("🚔 Dashboard Jumlah Kecelakaan Mingguan per Kecamatan")
    st.write(f"Data dari Minggu ke- **{start_week}** hingga Minggu ke- **{end_week}** untuk {total_week} minggu pada Kecamatan {lokasi_pilihan}")
    st.dataframe(filtered_df[["week", "month_name", "month_year","Kecamatan", "Jumlah_Kecelakaan"]], 
                 use_container_width=True, hide_index=True)
    
    
    #Display Total jumlah kecelakaan menggunakan line chart
    line = alt.Chart(filtered_df).mark_line(point=True).encode(
    x=alt.X("week_dt:T", title="Week"),
    y=alt.Y("Jumlah_Kecelakaan:Q", title="Total Jumlah Kecelakaan"),
    tooltip=["week_dt", "Jumlah_Kecelakaan"]).properties(title=f"Jumlah Kecelakaan dalam Periode {total_week} Minggu", width=700, height=400)

    st.altair_chart(line, use_container_width=True)
    
    mean_data =(filtered_df.groupby("month_year")["Jumlah_Kecelakaan"].mean().reset_index().sort_values(by="Jumlah_Kecelakaan",ascending=False).head(10))
    
    #Display Rata-rata jumlah kecelakaan menggunakan bar chart dengan filter
    # Threshold value
    threshold = 3

    # Add a column to tag colors
    mean_data["Color"] = mean_data[ "Jumlah_Kecelakaan"].apply(lambda x: "Above Threshold" if x > threshold else "Below Threshold")

    # Altair chart
    bar_chart = alt.Chart(mean_data).mark_bar().encode(x=alt.X("month_year:N", sort="-y"),
                                                        y=alt.Y( "Jumlah_Kecelakaan:Q"),
                                                        color=alt.Color("Color:N", scale=alt.Scale(domain=["Above Threshold", "Below Threshold"], range=["red", "steelblue"])),
                                                        tooltip=["month_year", "Jumlah_Kecelakaan"]).properties(width=700,height=400,
                                                        title=f"Top 10 Waktu dengan Rata-rata jumlah kecelakaan Tertinggi pada Kecamatan {lokasi_pilihan} dalam periode {total_week} Minggu")

    st.altair_chart(bar_chart, use_container_width=True)

def forecasting():
    #load data
    df_0=pd.read_csv('cluster_0.csv')
    df_1=pd.read_csv('cluster_1.csv')
    df=pd.read_csv('weekly_data.csv')
    
    
    #load model
    model_0=load_model('model_cluster0.keras')
    model_1=load_model('model_cluster1.keras')
    
    st.sidebar.header('Filter Data')
    #lokasi kecamatan
    excluded = ['Week']
    daftar_lokasi = sorted([col for col in df.columns.unique() if col not in excluded])
    lokasi_pilihan = st.sidebar.selectbox('Pilih Lokasi', daftar_lokasi)
    
    # Convert 'week' to sortable datetime (ISO format uses 'W' for week)
    df["week_dt"] = pd.to_datetime(df["Week"] + "-1", format="%Y-%W-%w")  # '-1' = Monday
    df["month_year"] = df["week_dt"].dt.strftime("%B %Y")
    
    #waktu
    unique_weeks=sorted(df["Week"].unique())
    
    #periode forcasting
    selected_date = st.selectbox('Pilih Waktu forecasting (mingguan):', unique_weeks)
    week_awal= df["week_dt"][df["Week"]==selected_date].iloc[0]
    # Hitung tanggal 7 minggu sebelumnya
    week_akhir=week_awal- pd.Timedelta(weeks=7)
    
    st.write(f'Waktu yang dipilih Minggu ke-**{selected_date}**, Bulan-Tahun **{df["month_year"][df["Week"]==selected_date].iloc[0]}**')
    periode_forecast=st.slider('Pilih periode forecasting (Minggu)', 1, 6)
    
    #cek kecamatan tiap cluster
    kec0=df_0['Kecamatan'].unique()
    kec1=df_1['Kecamatan'].unique()
    
    
    if lokasi_pilihan in kec0:
        forbidden_week=df["week_dt"].iloc[0:7]
        #check data availability       
        if week_akhir >=forbidden_week.iloc[6]: 
            #check index
            value= df.index[df['Week'] == selected_date][0]
            
            #mengambil data dari 7 minggu sebelum tanggal yang akan diprediksi
            data = df[lokasi_pilihan].loc[value-7:value]
            sequence = data.tolist()
            
            week_dis=[]
            monthYear_dis=[]
            
            # Predict
            for x in range(periode_forecast):  
                input_array = np.array(sequence[-7:]).reshape(1, 7, -1)
                next_pred = model_0.predict(input_array)
                
                # Append prediction as next step and time
                sequence.append(next_pred[0].item())  # assuming output is (1, features)
                week_add=week_awal+pd.Timedelta(days=(7*x))
                monthYear=pd.to_datetime(week_add).strftime("%B %Y")
                week_dis.append(week_add)
                monthYear_dis.append(monthYear)
                
            # Show result
            df_preds = pd.DataFrame({
                'Week': [week_dis[i] for i in range(periode_forecast)],
                'Month-Year':[monthYear_dis[i] for i in range(periode_forecast)],
                'Prediction': [np.ceil(p) for p in sequence[-periode_forecast:]]}) 
            
            
            st.write(df_preds)
             #Display hasil forecasting jumlah kecelakaan menggunakan bar chart dengan filter
            # Threshold value
            threshold = 3

            # Add a column to tag colors
            df_preds["Color"] = df_preds[ "Prediction"].apply(lambda x: "Above Threshold" if x > threshold else "Below Threshold")

            # Altair chart
            bar_chart = alt.Chart(df_preds).mark_bar().encode(x=alt.X("Week:T", sort="-y"),
                                                        y=alt.Y( "Prediction:Q"),
                                                        color=alt.Color("Color:N", scale=alt.Scale(domain=["Above Threshold", "Below Threshold"], range=["red","steelblue"])),
                                                        tooltip=["Week", "Prediction"]).properties(width=700,height=400,
                                                        title=f"Hasil Forecasting di {lokasi_pilihan} dalam periode {periode_forecast} Minggu Berikutnya")

            st.altair_chart(bar_chart, use_container_width=True)
     
            st.success("Forecasting Selesai")     
       
        else:
            st.warning(f"Data TIDAK tersedia.")
                
    elif lokasi_pilihan in kec1:
        forbidden_week=df["week_dt"].iloc[0:3]
        
        #check data availability       
        if week_akhir >=forbidden_week.iloc[2]: 
            #check index
            value= df.index[df['Week'] == selected_date][0]
            
            #mengambil data dari 3 minggu sebelum tanggal yang akan diprediksi
            data = df[lokasi_pilihan].loc[value-3:value]
            sequence = data.tolist()
           
            week_dis=[]
            monthYear_dis=[]
            
            # Predict
            for x in range(periode_forecast):  
                input_array = np.array(sequence[-3:]).reshape(1, 3, -1)
                next_pred = model_1.predict(input_array)
                                            
                                            
                # Append prediction as next step and time
                sequence.append(next_pred[0].item())  # assuming output is (1, features)
                week_add=week_awal+pd.Timedelta(days=(7*x))
                monthYear=pd.to_datetime(week_add).strftime("%B %Y")
                week_dis.append(week_add)
                monthYear_dis.append(monthYear)
            
            # Show result
            df_preds = pd.DataFrame({
                'Week': [week_dis[i] for i in range(periode_forecast)],
                'Month-Year':[monthYear_dis[i] for i in range(periode_forecast)],
                'Prediction': [np.ceil(p) for p in sequence[-periode_forecast:]]})    
                
                  
            st.write(df_preds)
            
             #Display hasil forecasting jumlah kecelakaan menggunakan bar chart dengan filter
            # Threshold value
            threshold = 3

            # Add a column to tag colors
            df_preds["Color"] = df_preds[ "Prediction"].apply(lambda x: "Above Threshold" if x > threshold else "Below Threshold")

            # Altair chart
            bar_chart = alt.Chart(df_preds).mark_bar().encode(x=alt.X("Week:T", sort="-y"),
                                                        y=alt.Y( "Prediction:Q"),
                                                        color=alt.Color("Color:N", scale=alt.Scale(domain=["Above Threshold", "Below Threshold"], range=["red","steelblue"])),
                                                        tooltip=["Week", "Prediction"]).properties(width=700,height=400,
                                                        title=f"Hasil Forecasting di {lokasi_pilihan} dalam periode {periode_forecast} Minggu Berikutnya")

            st.altair_chart(bar_chart, use_container_width=True)
            st.success("Forecasting Selesai")   
            
        else:
            st.warning(f"Data TIDAK tersedia.")
                     

# Sidebar menu

if menu_utama == "Dashboard Analisa":
    st.title("📊 Dashboard Analisa")
    menu = st.sidebar.selectbox("Analisa", ["Analisa Umum", "Analisa Kecamatan"])
    if menu == "Analisa Umum":
        general_analysis(dfw)
    elif menu == "Analisa Kecamatan":
        area_analysis(dfw)   

elif menu_utama == "Forecasting":
    st.title("🔮 Forecasting")
    forecasting()
    



    
