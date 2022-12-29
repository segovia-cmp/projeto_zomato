import pandas as pd
import folium
from folium import plugins
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Countries', page_icon='🌎', layout='wide' )


df_raw = pd.read_csv('dataset/zomato.csv')


#===============================================
#Funções
#===============================================

def rename_columns( data ):
    df = data.copy()
    old_cols = df.columns
    new_cols = []
    
    for col in old_cols:
        new = col.lower().replace(' ', '_')
        new_cols.append(new)
        
    df.columns = new_cols
    
    return df

COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}

def country_name(country_id):
  return COUNTRIES[country_id]

def create_price_tye(price_range):

  if price_range == 1:
    return "cheap"
  elif price_range == 2:
    return "normal"
  elif price_range == 3:
    return "expensive"
  else:
    return "gourmet"

COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
  return COLORS[color_code]

#==========================
#Clear Dataframe
#==========================

df = rename_columns(df_raw)

df = df.drop_duplicates()

df = df.dropna(axis = 0, how ='any').reset_index()

df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

df.drop(columns=['index'],inplace=True)

df['country'] = df.loc[:, "country_code"].apply(lambda x: country_name(x))

df["price"] = df.loc[:, "price_range"].apply(lambda x: create_price_tye(x))

df["color"] = df.loc[:, "rating_color"].apply(lambda x: color_name(x))

df['price_in_dollar'] = df[['currency', 'average_cost_for_two']].apply( lambda x: ( x['average_cost_for_two'] / 12.85  ) if x['currency'] == 'Botswana Pula(P)'  else
                                                                                      ( x['average_cost_for_two'] / 5.31  ) if x['currency'] == 'Brazilian Real(R$)' else
                                                                                      ( x['average_cost_for_two'] / 1  ) if x['currency'] == 'Dollar($)' else
                                                                                      ( x['average_cost_for_two'] / 3.67  ) if x['currency'] == 'Emirati Diram(AED)' else
                                                                                      ( x['average_cost_for_two'] / 82.68  ) if x['currency'] == 'Indian Rupees(Rs.)' else
                                                                                      ( x['average_cost_for_two'] / 15608.45  ) if x['currency'] == 'Indonesian Rupiah(IDR)' else
                                                                                      ( x['average_cost_for_two'] / 1.57  ) if x['currency'] == 'NewZealand($)' else
                                                                                      ( x['average_cost_for_two'] / 0.819257  ) if x['currency'] == 'Pounds(£)' else
                                                                                      ( x['average_cost_for_two'] / 3.64  ) if x['currency'] == 'Qatari Rial(QR)' else
                                                                                      ( x['average_cost_for_two'] / 17.59  ) if x['currency'] == 'Rand(R)' else
                                                                                      ( x['average_cost_for_two'] / 366.86  ) if x['currency'] == 'Sri Lankan Rupee(LKR)' else
                                                                                      ( x['average_cost_for_two'] / 18.65  ) if x['currency'] == 'Turkish Lira(TL)' else 0, axis=1 )



#======================
#Barra lateral
#======================


image_path = 'imagem.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)


st.sidebar.markdown('# Fome Zero')

country_options = st.sidebar.multiselect(
                    'Escolha os Paises que Deseja visualizar os Restaurantes', 
                    ['Brazil', 'Australia', 'United States of America','Canada', 'Singapure', 'United Arab Emirates', 'India', 'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa', 'Sri Lanka', 'Turkey'],
                    default=['Brazil', 'Australia', 'Canada','England', 'Qatar', 'South Africa',])

linhas_selecionadas = df['country'].isin(country_options)
df = df.loc[linhas_selecionadas, :]


#===========
#lay out
#==========


st.title( '🌎 Visão Paises')

aux = (df.loc[:,['country', 'restaurant_id']]
         .groupby('country')
         .count()
         .sort_values('restaurant_id', ascending=False)
         .reset_index())


fig = px.bar(aux,x='country',y='restaurant_id'
                ,labels={'country': 'Paises','restaurant_id': 'Quantidade de restaurantes'}
                ,color_discrete_sequence=px.colors.qualitative.T10
                ,template='plotly_white'
                ,text='restaurant_id')
fig.update_layout(title_text='Quantidade de restaurantes registrado por paises', title_x=0.5)
fig.update_traces(textposition='inside',texttemplate='%{text:.2s}')
fig.update_yaxes(showticklabels=False)


st.plotly_chart(fig, use_container_width=True)




aux = (df.loc[:,['country', 'city']]
         .groupby('country')
         .nunique()
         .sort_values('city', ascending=False)
         .reset_index())


fig = px.bar(aux,x='country',y='city'
                ,title='Quantidade de cidades registrada por pais'
                ,labels={'country': 'Paises','city': 'Quantidade de restaurantes'}
                ,color_discrete_sequence=px.colors.qualitative.T10
                ,template='plotly_white'
                ,text='city')
fig.update_layout(title_text='Quantidade de cidades registrada por pais', title_x=0.5)
fig.update_traces(textposition='inside')
fig.update_yaxes(showticklabels=False)

st.plotly_chart(fig, use_container_width=True)

with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            
            
            aux_df = round(df.loc[:,['country', 'votes']]
                             .groupby(['country'])
                             .mean()
                             .sort_values('votes', ascending=False)
                             .reset_index(),2)

            fig = px.bar(aux_df,x='country',y='votes'
                               ,title=('Média de avaliação feita por pais')
                               ,labels={'country': 'Paises','votes': 'Quantidade de avaliações'}
                               ,color_discrete_sequence=px.colors.qualitative.T10
                               ,template='plotly_white'
                               ,text='votes')
            fig.update_layout(title_text=('Média de avaliação feita por pais'), title_x=0.5)
            fig.update_traces(textposition='inside')
            fig.update_yaxes(showticklabels=False)

            st.plotly_chart(fig, use_container_width=True)
        
        
        with col2:
                        
            aux_df = round(df.loc[:,['country', 'average_cost_for_two']]
                             .groupby(['country'])
                             .mean()
                             .sort_values('average_cost_for_two', ascending=False)
                             .reset_index(),2)

            fig = px.bar(aux_df,x='country',y='average_cost_for_two'
                               ,title='Média de preço de prato para duas pessoas'
                               ,labels={'country': 'Paises','average_cost_for_two': 'Preço de prato para duas pessoas'}
                               ,color_discrete_sequence=px.colors.qualitative.T10
                               ,template='plotly_white'
                               ,text='average_cost_for_two')
            fig.update_layout(title_text='Média de preço de prato para duas pessoas', title_x=0.5)
            fig.update_traces(textposition='auto')
            fig.update_yaxes(showticklabels=False)
            
            st.plotly_chart(fig, use_container_width=True)
