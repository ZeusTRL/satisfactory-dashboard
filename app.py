import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__)

df = pd.DataFrame({
    "Factory Section": ["Uranium", "Plutonium", "Ficsonium"],
    "Production Rate": [100, 50, 75]
})

fig = px.bar(df, x="Factory Section", y="Production Rate",
             title="Satisfactory Factory Production Rates")

app.layout = html.Div([
    html.H1("Satisfactory Factory Dashboard"),
    dcc.Graph(figure=fig),
    html.P("Dashboard running inside Docker on LXC container!")
])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
