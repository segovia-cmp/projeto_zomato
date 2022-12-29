import pandas as pd
import folium
from folium import plugins
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import branca

#==========
#Read data
#==========

st.set_page_config( page_title='Main Page', page_icon='📊', layout='wide' )


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




#===========
#lay out
#==========

st.title( '🍴 Fome zero')

st.header('O Melhor lugar para encontrar seu mais novo restaurante favorito!')

st.header('Temos as seguintes marcas dentro da nossa plataforma:')

     
              
with st.container():
    col1, col2, col3, col4, col5 = st.columns(5, gap='large')
        
    with col1:
        
        df_rest_cadas = df['restaurant_id'].nunique()
        col1.metric ('Restaurantes Cadastrados', df_rest_cadas)

               
    with col2:
        
        df_coutry = df['country_code'].nunique()
        col2.metric ('Países Cadastrados', df_coutry)
        
    with col3:
    
        df_city = df['city'].nunique()
        col3.metric ('Cidades Cadastrados', df_city)
            
    with col4:
    
        df_vote = df['votes'].sum().astype(int)
        col4.metric ('Avaliações Feitas', '{0:,}'.format(df_vote).replace(',','.'))
        
    with col5:
        
        df_cuisines = df['cuisines'].nunique()
        col5.metric ('Tipos de Culinárias ', df_cuisines)
        

df_aux = (df.loc[:,['restaurant_name', 'aggregate_rating','cuisines','latitude', 'longitude']])
            
                

map = folium.Map(location=[0, 0],zoom_start=2)


	
marker_cluster = plugins.MarkerCluster().add_to(map)

for index, location_info in df_aux.iterrows():
    folium.Marker([location_info['latitude'],location_info['longitude']],popup=folium.Popup(f"<h5><b>{location_info['restaurant_name']}</b></h5>Média: {location_info['aggregate_rating']}<br>Cuisines: {location_info['cuisines']}", max_width=300,min_width=150),
                 tooltip=location_info["restaurant_name"],
                 icon=folium.Icon(color='green', icon='home', prefix='fa')).add_to (marker_cluster)

folium_static (map, width=960, height=500)
