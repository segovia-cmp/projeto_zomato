import pandas as pd
import folium
from folium import plugins
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Cities', page_icon='🌆', layout='wide' )


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

st.title( ' 🌆 Visão Cidades')

aux = (df.loc[:,['city', 'restaurant_id','country']]
         .groupby(['city', 'country'])
         .count().sort_values('restaurant_id', ascending=False)
         .reset_index()
         .head(10))
         
fig = px.bar(aux,x='city',y='restaurant_id'
                ,labels={'city': 'Cidades','restaurant_id': 'Quantidade de restaurantes','country': 'País'}
                ,color='country'
                ,template='plotly_dark'
                ,text='restaurant_id')

fig.update_layout(title_text='Top 10 com mais restaurates na base de dados', title_x=0.5)
fig.update_traces(textposition='auto',texttemplate='%{text:.2s}')
fig.update_yaxes(showticklabels=False)

st.plotly_chart(fig, use_container_width=True)

with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            
            
            aux_rating_mean = (df.loc[:, ['city','country','aggregate_rating', 'restaurant_id']]
                                 .groupby(['country','city','restaurant_id'])
                                 .mean()
                                 .reset_index())


            aux = (aux_rating_mean.loc[aux_rating_mean['aggregate_rating'] >= 4,:]
                                  .sort_values('aggregate_rating', ascending=False)
                                  .reset_index())

            aux = (aux.loc[:, ['city','country', 'restaurant_id']]
                      .groupby(['country','city'])
                      .count()
                      .sort_values('restaurant_id', ascending=False)
                      .reset_index()
                      .head(7))


            fig = px.bar(aux,x='city',y='restaurant_id'
                            ,labels={'city': 'Cidades','restaurant_id': 'Quantidade de restaurantes','country': 'País'}
                            ,color='country'
                            ,template='plotly_dark'
                            ,text='restaurant_id')

            fig.update_layout(title_text='Top 7 de restaurantes com média acima da 4', title_x=0.5)
            fig.update_traces(textposition='auto',texttemplate='%{text:.2s}')
            fig.update_yaxes(showticklabels=False)
            
            st.plotly_chart(fig, use_container_width=True)

        
        
        with col2:
                        
            aux_rating_mean = (df.loc[:, ['city','country','aggregate_rating', 'restaurant_id']]
                     .groupby(['country','city','restaurant_id'])
                     .mean()
                     .reset_index())


            aux = (aux_rating_mean.loc[aux_rating_mean['aggregate_rating'] <= 2.5,:]
                                  .sort_values('aggregate_rating', ascending=True)
                                  .reset_index())

            aux = (aux.loc[:, ['city','country', 'restaurant_id']]
                      .groupby(['country','city'])
                      .count()
                      .sort_values('restaurant_id', ascending=False)
                      .reset_index()
                      .head(7))


            fig = px.bar(aux,x='city',y='restaurant_id'
                            ,labels={'city': 'Cidades','restaurant_id': 'Quantidade de restaurantes','city': 'Cidades'}
                            ,color='country'
                            ,template='plotly_dark'
                            ,text='restaurant_id')

            fig.update_layout(title_text='Top 7 com restaurante com média abaixo de 2.5', title_x=0.5)
            fig.update_traces(textposition='auto',texttemplate='%{text:.2s}')
            fig.update_yaxes(showticklabels=False)

            st.plotly_chart(fig, use_container_width=True)

            
aux_cuisines = (df.loc[:, ['city', 'cuisines','country']]
                  .groupby(['country','city'])['cuisines']
                  .nunique()
                  .sort_values(ascending=False)
                  .reset_index()
                  .head(10))


fig = px.bar(aux_cuisines,x='city',y='cuisines'
                         ,labels={'city': 'Cidades','cuisines': 'Quantidade de tipo de culinaria','Country': 'País'}
                         ,color='country'
                         ,template='plotly_dark'
                         ,text='cuisines')

fig.update_layout(title_text='Top 10 de cidades com restaurantes com tipo culinários distintos', title_x=0.5)
fig.update_traces(textposition='auto',texttemplate='%{text:.2s}')
fig.update_yaxes(showticklabels=False)

st.plotly_chart(fig, use_container_width=True)