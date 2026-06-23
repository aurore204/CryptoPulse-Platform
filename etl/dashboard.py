import pandas as pd
import psycopg2
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = os.getenv('DB_PORT', '5432')
DB_NAME     = os.getenv('POSTGRES_DB', os.getenv('DB_NAME', 'cryptopulse'))
DB_USER     = os.getenv('POSTGRES_USER', os.getenv('DB_USER'))
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', os.getenv('DB_PASSWORD'))

conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

df_history = pd.read_sql("""
    SELECT name, symbol, current_price, market_cap, total_volume,
           price_change_percentage_24h, last_updated
    FROM crypto_prices ORDER BY last_updated ASC
""", conn)

df_latest = pd.read_sql("""
    SELECT DISTINCT ON (symbol)
        name, symbol, current_price, market_cap, total_volume,
        high_24h, low_24h, price_change_percentage_24h, last_updated
    FROM crypto_prices
    ORDER BY symbol, last_updated DESC
""", conn)

conn.close()

df_history['last_updated'] = pd.to_datetime(df_history['last_updated'])
df_history['symbol'] = df_history['symbol'].str.upper()
df_latest['symbol']  = df_latest['symbol'].str.upper()

print(f" {len(df_history)} lignes chargées  {df_latest['symbol'].nunique()} cryptos")

# GRAPHIQUE 1 — Évolution du prix
top3 = df_history.groupby('symbol').size().nlargest(3).index.tolist()
fig1 = go.Figure()
for symbol in top3:
    df_s = df_history[df_history['symbol'] == symbol]
    fig1.add_trace(go.Scatter(x=df_s['last_updated'], y=df_s['current_price'], mode='lines', name=symbol))
fig1.update_layout(title='Évolution du prix dans le temps', xaxis_title='Date', yaxis_title='Prix (USD)')

# GRAPHIQUE 2 — Volatilité 24h
df_vol = df_latest.dropna(subset=['price_change_percentage_24h'])
df_vol = df_vol.sort_values('price_change_percentage_24h', ascending=True).copy()
colors = ['#00C853' if x >= 0 else '#D50000' for x in df_vol['price_change_percentage_24h']]
fig2 = go.Figure(go.Bar(
    x=df_vol['price_change_percentage_24h'],
    y=df_vol['symbol'],
    orientation='h',
    marker_color=colors
))
fig2.update_layout(title='Variation de prix sur 24h (%)', xaxis_title='Variation 24h (%)', yaxis_title='Crypto')

# GRAPHIQUE 3 — Market Cap Top 10
df_mc = df_latest.sort_values('market_cap', ascending=False).head(10)
fig3 = go.Figure(go.Bar(
    x=df_mc['symbol'],
    y=df_mc['market_cap'],
    text=df_mc['market_cap'].apply(lambda x: f'{x/1e9:.1f}B'),
    textposition='auto'
))
fig3.update_layout(title=' Top 10 : Market Cap', xaxis_title='Crypto', yaxis_title='Market Cap (USD)')

# GRAPHIQUE 4 — Volume vs Prix
df_vp = df_latest.dropna(subset=['total_volume', 'current_price', 'market_cap'])
fig4 = go.Figure(go.Scatter(
    x=df_vp['total_volume'],
    y=df_vp['current_price'],
    mode='markers',
    marker=dict(size=df_vp['market_cap'] / df_vp['market_cap'].max() * 50, opacity=0.7),
    text=df_vp['symbol'],
    hovertemplate='<b>%{text}</b><br>Volume: %{x}<br>Prix: %{y}<extra></extra>'
))
fig4.update_layout(
    title=' Volume vs Prix',
    xaxis_title='Volume total', yaxis_title='Prix (USD)',
    xaxis_type='log', yaxis_type='log'
)

# GRAPHIQUE 5 — Corrélations
df_pivot = df_history.pivot_table(index='last_updated', columns='symbol', values='current_price')
corr = df_pivot.corr()
fig5 = go.Figure(go.Heatmap(
    z=corr.values,
    x=corr.columns.tolist(),
    y=corr.index.tolist(),
    colorscale='RdBu_r',
    zmin=-1, zmax=1,
    text=corr.round(2).values,
    texttemplate='%{text}'
))
fig5.update_layout(title=' Corrélations entre les prix des cryptos')

# APP DASH
app = Dash(__name__)
app.layout = html.Div([
    html.H1("CryptoPulse Dashboard", style={'textAlign': 'center', 'fontFamily': 'Arial', 'padding': '20px'}),
    dcc.Graph(figure=fig1),
    dcc.Graph(figure=fig2),
    dcc.Graph(figure=fig3),
    dcc.Graph(figure=fig4),
    dcc.Graph(figure=fig5),
], style={'backgroundColor': '#f9f9f9'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)
