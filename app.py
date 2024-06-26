import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('vehicles_us.csv')
df['manufacturer'] = df['model'].apply(lambda x: x.split()[0])

#Fill in median value of column for year and verify 
df['model_year'].fillna(df['model_year'].median(), inplace=True)

#cylindres: group by model fill by median cylindres odometer:
df['cylinders'].fillna(df.groupby('model')['cylinders'].transform('median'), inplace=True)

#group by model year(or year+model) fill by median(mean) odometer
df['odometer'].fillna(df.groupby('model')['odometer'].transform('median'), inplace=True)

# Calculate Q1 (25th percentile) and Q3 (75th percentile)
Q1 = df['price'].quantile(0.25)
Q3 = df['price'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

#Remove outliers
df = df[(df['price'] >= lower_bound) & (df['price'] <= upper_bound)]

# Calculate Q1 (25th percentile) and Q3 (75th percentile)
Q1 = df['model_year'].quantile(0.25)
Q3 = df['model_year'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
#Remove outliers
df = df[(df['model_year'] >= lower_bound) & (df['model_year'] <= upper_bound)]

st.header('View Data by Transmission Type')
show_trans = st.checkbox('Not Automatic')
if show_trans:
    df = df[df['transmission'] != 'automatic']
else:
    df = df[df['transmission'] == 'automatic']

st.dataframe(df)
st.header('Vehicle types by manufacturer')
st.write(px.histogram(df, x='manufacturer', color='type'))
st.header('Histogram of `price` vs `condition`')

# -------------------------------------------------------
# histograms in plotly:
# fig = go.Figure()
# fig.add_trace(go.Histogram(x=df[df['condition']=='good']['model_year'], name='good'))
# fig.add_trace(go.Histogram(x=df[df['condition']=='excellent']['model_year'], name='excellent'))
# fig.update_layout(barmode='stack')
# st.write(fig)
# works, but too many lines of code
# -------------------------------------------------------

# histograms in plotly_express:
st.write(px.histogram(df, x='price', color='condition'))
# a lot more concise!
# -------------------------------------------------------

st.header('Compare price distribution between manufacturers')
manufac_list = sorted(df['manufacturer'].unique())
manufacturer_1 = st.selectbox('Select manufacturer 1',
                              manufac_list, index=manufac_list.index('chevrolet'))

manufacturer_2 = st.selectbox('Select manufacturer 2',
                              manufac_list, index=manufac_list.index('hyundai'))
mask_filter = (df['manufacturer'] == manufacturer_1) | (df['manufacturer'] == manufacturer_2)
df_filtered = df[mask_filter]
normalize = st.checkbox('Normalize histogram', value=True)
if normalize:
    histnorm = 'percent'
else:
    histnorm = None
st.write(px.histogram(df_filtered,
                      x='price',
                      nbins=30,
                      color='manufacturer',
                      histnorm=histnorm,
                      barmode='overlay'))

st.header('Odometer Relation to Pricing')
scatter_plot = px.scatter(df, x="price", y="odometer",  color='manufacturer')
st.plotly_chart(scatter_plot)

