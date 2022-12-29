import pandas as pd
import folium
from folium import plugins
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Cuisines', page_icon='🍲', layout='wide' )


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



st.sidebar.markdown("""___""")


num_slider = st.sidebar.slider('Selecione a quantidade de restaurantes que deseja visualizar',0, 20,10)

st.sidebar.markdown(num_slider)


#===========
#lay out
#==========

st.title( ' 🍲 Visão Tipos de Cusinhas')

st.header('Melhores Restaurantes dos Principais tipos Culinários')

with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            
            aux = round(df.loc[:, ['country', 'city','restaurant_name','cuisines','aggregate_rating']]
              .groupby(['country', 'city','restaurant_name','cuisines'])
              .mean()
              .sort_values('aggregate_rating', ascending=False)
              .reset_index(),2)

            
            aux_prt = aux.loc[0,'restaurant_name']+ '/' +aux.loc[0,'cuisines']
            aux_n = aux.loc[0,'aggregate_rating']

            df_cuisine_1 = aux_n
            col1.metric ( aux_prt, df_cuisine_1 )
            
        with col2:
            
            aux = round(df.loc[:, ['country', 'city','restaurant_name','cuisines','aggregate_rating']]
              .groupby(['country', 'city','restaurant_name','cuisines'])
              .mean()
              .sort_values('aggregate_rating', ascending=False)
              .reset_index(),2)

            
            aux_prt = aux.loc[1,'restaurant_name']+ '/' +aux.loc[1,'cuisines']
            aux_n = aux.loc[1,'aggregate_rating']

            df_cuisine_1 = aux_n
            col2.metric ( aux_prt, df_cuisine_1 )
            
        with col3:
            
            aux = round(df.loc[:, ['country', 'city','restaurant_name','cuisines','aggregate_rating']]
              .groupby(['country', 'city','restaurant_name','cuisines'])
              .mean()
              .sort_values('aggregate_rating', ascending=False)
              .reset_index(),2)

            
            aux_prt = aux.loc[2,'restaurant_name']+ '/' +aux.loc[2,'cuisines']
            aux_n = aux.loc[2,'aggregate_rating']

            df_cuisine_1 = aux_n
            col3.metric ( aux_prt, df_cuisine_1 )

            
        with col4:
            
            aux = round(df.loc[:, ['country', 'city','restaurant_name','cuisines','aggregate_rating']]
              .groupby(['country', 'city','restaurant_name','cuisines'])
              .mean()
              .sort_values('aggregate_rating', ascending=False)
              .reset_index(),2)

            
            aux_prt = aux.loc[3,'restaurant_name']+ '/' +aux.loc[3,'cuisines']
            aux_n = aux.loc[3,'aggregate_rating']

            df_cuisine_1 = aux_n
            col4.metric ( aux_prt, df_cuisine_1 )
            
        with col5:
            
            aux = round(df.loc[:, ['country', 'city','restaurant_name','cuisines','aggregate_rating']]
              .groupby(['country', 'city','restaurant_name','cuisines'])
              .mean()
              .sort_values('aggregate_rating', ascending=False)
              .reset_index(),2)

            
            aux_prt = aux.loc[4,'restaurant_name']+ '/' +aux.loc[4,'cuisines']
            aux_n = aux.loc[4,'aggregate_rating']

            df_cuisine_1 = aux_n
            col5.metric ( aux_prt, df_cuisine_1 )
            
st.header(f'Top {num_slider} Restaurantes')
            
            
aux = round(df.loc[:, ['country', 'city','restaurant_name','cuisines','aggregate_rating']]
              .groupby(['country', 'city','restaurant_name','cuisines'])
              .mean()
              .sort_values('aggregate_rating', ascending=False)
              .reset_index()
              .head(num_slider),2)

st.dataframe(aux)


with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            
            aux = round(df.loc[:, ['cuisines','aggregate_rating']]
              .groupby(['cuisines'])
              .median()
              .sort_values('aggregate_rating', ascending=False)
              .reset_index()
              .head(num_slider),2)

            fig = px.bar(aux,x='cuisines',y='aggregate_rating'
                            ,labels={'cuisines': 'Tipo de culinária','aggregate_rating': 'Média da avaliação'}
                            ,color_discrete_sequence=px.colors.qualitative.T10
                            ,template='plotly_dark'
                            ,text='aggregate_rating')
            fig.update_layout(title_text=(f'Top {num_slider} melhores tipos de culinária'), title_x=0.5)
            fig.update_traces(textposition='inside',texttemplate='%{text:.2s}')
            fig.update_yaxes(showticklabels=False)
            
            st.plotly_chart(fig ,use_container_width=True)
            
        with col2:


            aux = round(df.loc[:, ['cuisines','aggregate_rating']]
              .groupby(['cuisines'])
              .median()
              .sort_values('aggregate_rating', ascending=True)
              .reset_index()
              .head(num_slider),2)

            fig = px.bar(aux,x='cuisines',y='aggregate_rating'
                            ,labels={'cuisines': 'Tipo de culinária','aggregate_rating': 'Média da avaliação'}
                            ,color_discrete_sequence=px.colors.qualitative.T10
                            ,template='plotly_dark'
                            ,text='aggregate_rating')
            fig.update_layout(title_text=(f'Top {num_slider} piores tipos de culinária'), title_x=0.5)
            fig.update_traces(textposition='inside',texttemplate='%{text:.2s}')
            fig.update_yaxes(showticklabels=False)
            
            st.plotly_chart(fig ,use_container_width=True)
