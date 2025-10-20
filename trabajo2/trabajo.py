import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# === Cargar dataset ===
df = pd.read_csv("Sample - Superstore.csv", encoding="latin-1")
df['Order Date'] = pd.to_datetime(df['Order Date'])

# === Inicializar app ===
app = Dash(__name__)
app.title = "Tablero Empresarial con Dash y Plotly"

# === Estilos generales ===
CARD_STYLE = {
    'backgroundColor': 'white',
    'padding': '20px',
    'borderRadius': '12px',
    'boxShadow': '0px 4px 10px rgba(0,0,0,0.1)',
    'marginBottom': '20px'
}

GRAPH_STYLE = {
    'boxShadow': '0px 3px 8px rgba(0,0,0,0.08)',
    'borderRadius': '10px',
    'backgroundColor': 'white',
    'padding': '10px'
}

# === Layout ===
app.layout = html.Div(
    style={
        'fontFamily': 'Segoe UI, Arial, sans-serif',
        'backgroundColor': '#f4f6f8',
        'padding': '30px'
    },
    children=[
        html.H1(
            " Tablero Empresarial - Superstore",
            style={
                'textAlign': 'center',
                'color': '#2c3e50',
                'marginBottom': '40px',
                'fontWeight': 'bold'
            }
        ),

        # --- FILTROS ---
        html.Div([
            html.Div([
                html.Label(" Rango de tiempo", style={'fontWeight': 'bold'}),
                dcc.RadioItems(
                    id='time_filter',
                    options=[
                        {'label': 'Últimos 3 meses', 'value': '3m'},
                        {'label': 'Último semestre', 'value': '6m'},
                        {'label': 'Último año', 'value': '1y'},
                        {'label': 'Todo', 'value': 'all'}
                    ],
                    value='all',
                    inline=True,
                    style={'marginTop': '10px'}
                )
            ], style=CARD_STYLE),

            html.Div([
                html.Label(" Región", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='region_filter',
                    options=[{'label': r, 'value': r} for r in sorted(df['Region'].unique())] +
                            [{'label': 'Todas', 'value': 'all'}],
                    value='all',
                    clearable=False
                )
            ], style={**CARD_STYLE, 'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

            html.Div([
                html.Label(" Categoría de producto", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='category_filter',
                    options=[{'label': c, 'value': c} for c in sorted(df['Category'].unique())] +
                            [{'label': 'Todas', 'value': 'all'}],
                    value='all',
                    clearable=False
                )
            ], style={**CARD_STYLE, 'width': '48%', 'display': 'inline-block', 'marginLeft': '2%', 'verticalAlign': 'top'})
        ], style={'marginBottom': '40px'}),

        # --- GRÁFICOS ---
        html.Div([
            html.Div([dcc.Graph(id='sales_over_time', style=GRAPH_STYLE)], style={'width': '49%', 'display': 'inline-block'}),
            html.Div([dcc.Graph(id='sales_by_category', style=GRAPH_STYLE)], style={'width': '49%', 'display': 'inline-block', 'marginLeft': '2%'}),
        ], style={'marginBottom': '30px'}),

        html.Div([
            html.Div([dcc.Graph(id='profit_by_region', style=GRAPH_STYLE)], style={'width': '49%', 'display': 'inline-block'}),
            html.Div([dcc.Graph(id='profit_vs_sales', style=GRAPH_STYLE)], style={'width': '49%', 'display': 'inline-block', 'marginLeft': '2%'}),
        ]),
    ]
)


# === Funciones auxiliares ===
def filter_by_time(df, period):
    max_date = df['Order Date'].max()
    if period == '3m':
        return df[df['Order Date'] >= (max_date - pd.DateOffset(months=3))]
    elif period == '6m':
        return df[df['Order Date'] >= (max_date - pd.DateOffset(months=6))]
    elif period == '1y':
        return df[df['Order Date'] >= (max_date - pd.DateOffset(years=1))]
    return df


# === Callback principal ===
@app.callback(
    [Output('sales_over_time', 'figure'),
     Output('sales_by_category', 'figure'),
     Output('profit_by_region', 'figure'),
     Output('profit_vs_sales', 'figure')],
    [Input('time_filter', 'value'),
     Input('region_filter', 'value'),
     Input('category_filter', 'value')]
)
def update_graphs(period, region, category):
    dff = filter_by_time(df, period)

    if region != 'all':
        dff = dff[dff['Region'] == region]
    if category != 'all':
        dff = dff[dff['Category'] == category]

    # === 1. Ventas en el tiempo ===
    sales_time = dff.groupby('Order Date')['Sales'].sum().reset_index()
    fig1 = px.line(sales_time, x='Order Date', y='Sales', title="Ventas en el tiempo", color_discrete_sequence=['#1f77b4'])
    fig1.update_layout(title_x=0.5, plot_bgcolor='white', paper_bgcolor='white')

    # === 2. Ventas por subcategoría ===
    sales_subcat = dff.groupby('Sub-Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)
    fig2 = px.bar(sales_subcat, x='Sub-Category', y='Sales', color='Sales', title="Ventas por Subcategoría",
                  color_continuous_scale='Blues')
    fig2.update_layout(title_x=0.5, plot_bgcolor='white', paper_bgcolor='white')

    # === 3. Ganancias por región ===
    profit_region = dff.groupby('Region')['Profit'].sum().reset_index()
    fig3 = px.pie(profit_region, names='Region', values='Profit', title="Distribución de Ganancias por Región",
                  color_discrete_sequence=px.colors.qualitative.Safe)
    fig3.update_layout(title_x=0.5)

    # === 4. Relación Ventas vs Ganancias ===
    profit_sales = dff.groupby('Order Date')[['Sales', 'Profit']].sum().reset_index()
    fig4 = px.scatter(profit_sales, x='Sales', y='Profit', size='Sales', color='Profit',
                      title="Relación entre Ventas y Ganancias", color_continuous_scale='Tealgrn')
    fig4.update_layout(title_x=0.5, plot_bgcolor='white', paper_bgcolor='white')

    return fig1, fig2, fig3, fig4


if __name__ == '__main__':
    app.run(debug=True)
