import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# --- 1. Preparação e Cálculo de Dados ---

# Dados de 6 meses
data = {
    'Mês': pd.to_datetime(['2025-04-01', '2025-05-01', '2025-06-01', '2025-07-01', '2025-08-01', '2025-09-01']),
    'Faturamento': [7100, 6500, 7500, 6800, 8200, 7900],
    'Gastos': [3500, 3200, 3400, 3800, 3900, 3700]
}
df = pd.DataFrame(data)
df['Lucro'] = df['Faturamento'] - df['Gastos']
df['Mês_Str'] = df['Mês'].dt.strftime('%b/%y') 

# KPIs Totais (Chave)
total_faturamento = df['Faturamento'].sum()
total_gastos = df['Gastos'].sum()
lucro_liquido = df['Lucro'].sum()

# Dados de Gastos por Categoria
data_gastos_cat = {
    'Categoria': ['Aluguel/Estrutura', 'Matéria-prima', 'Pró-Labore', 'Impostos'],
    'Valor': [15000, 10500, 5000, 1000]
}
df_gastos_cat = pd.DataFrame(data_gastos_cat).sort_values(by='Valor', ascending=False)


# Função Auxiliar de Formatação
def format_real(value):
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# --- 2. Definição do Tema NextStep (CORES E FONTE ATUALIZADAS) ---
THEME = {
    'background': '#F0F4F7',      
    'card_background': '#FFFFFF', 
    'text_primary': '#164360',    # Azul Escuro/Petróleo da marca
    'text_secondary': '#6C757D',  # Cinza para textos secundários
    'faturamento_color': '#164360', # Azul Petróleo (Principal para Faturamento)
    'gastos_color': '#D8A033',      # Dourado/Amarelo (Principal para Gastos)
    'lucro_color': '#4CAF50',       # Verde (Mantido para Lucro Positivo)
    'font_family': 'Open Sans, sans-serif' # Nova Fonte
}

# Cor do Lucro Líquido
cor_lucro = THEME['lucro_color'] if lucro_liquido >= 0 else THEME['gastos_color']

# --- 3. Componentes Reutilizáveis (Cards de KPI) ---

def create_kpi_card(title, value, color_hex, kpi_id=None):
    div_props = {
        'className': 'card', 
        'children': [
            html.P(title, style={'color': THEME['text_secondary'], 'fontSize': '0.9em', 'marginBottom': '5px'}),
            html.H3(value, style={'color': color_hex, 'fontSize': '1.8em', 'fontWeight': 'bold', 'margin': '0'}),
        ],
        'style': {
            'textAlign': 'center', 
            'padding': '15px 10px'
        }
    }
    
    # Adiciona o ID SOMENTE se for fornecido
    if kpi_id is not None:
        div_props['id'] = kpi_id

    return html.Div(**div_props) 

# --- 4. Inicialização do Aplicativo Dash (CORRIGIDO) ---

external_css = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css', 
]

app = dash.Dash(
    __name__, 
    external_stylesheets=external_css
    # Removidos 'dev_tools_ui' e 'dev_tools_props_check' da inicialização
)

# --- 5. Layout do Dashboard ---

app.layout = html.Div(
    className='main-container', 
    children=[
    
    html.H1("Visão Geral Financeira | NextStep", className='dashboard-header'),

    # LINHA SUPERIOR: CARDS DE KPI 
    html.Div(
        className='kpi-grid',
        children=[
            # KPI Dinâmico de Variação
            html.Div(
                id='kpi-comparacao-variacao',
                children=create_kpi_card("Selecione 2 Meses", "0.0%", THEME['text_secondary'])
            ),
            
            # KPIs Principais
            create_kpi_card("Faturamento Total (6M)", format_real(total_faturamento), THEME['faturamento_color']),
            create_kpi_card("Gastos Totais (6M)", format_real(total_gastos), THEME['gastos_color']),
            create_kpi_card("Lucro Líquido", format_real(lucro_liquido), cor_lucro),
        ]
    ),

    # LINHA INTERMEDIÁRIA: GRÁFICO PRINCIPAL
    html.Div(
        className='card',
        children=[
            html.H2("Tendência Mensal de Faturamento e Gastos", style={'fontSize': '1.4em', 'marginBottom': '15px', 'color': THEME['text_primary']}),
            html.P("Clique em dois meses no gráfico abaixo para ativar a comparação.", style={'color': THEME['text_secondary'], 'marginTop': '-10px'}),
            dcc.Graph(
                id='line-graph',
                style={'height': '450px'}, 
                config={'displayModeBar': False} 
            ),
            dcc.Store(id='meses-selecionados', data=[])
        ]
    ),
    
    # LINHA INFERIOR: GRÁFICOS SECUNDÁRIOS
    html.Div(
        className='secondary-grid',
        style={'marginTop': '30px'},
        children=[
            # GRÁFICO 1: Distribuição de Gastos (Donut)
            html.Div(
                className='card',
                children=[
                    html.H2("Onde Está o Seu Dinheiro (Total de Gastos)", style={'fontSize': '1.4em', 'marginBottom': '15px', 'color': THEME['text_primary']}),
                    dcc.Graph(
                        id='gastos-donut-chart',
                        style={'height': '350px'}, 
                        config={'displayModeBar': False}, 
                        figure=px.pie(df_gastos_cat, 
                                      names='Categoria', 
                                      values='Valor',
                                      title='',
                                      hole=.5, 
                                      # Sequência de cores alinhada com o tema
                                      color_discrete_sequence=['#164360', '#2E6A8A', '#4F94B0', '#D8A033'], 
                                      ).update_traces(textinfo='percent+label', marker={'line': {'color': 'white', 'width': 1}})
                                       .update_layout(
                                            showlegend=True,
                                            margin={'l': 20, 'r': 20, 't': 20, 'b': 20},
                                            plot_bgcolor=THEME['card_background'],
                                            paper_bgcolor=THEME['card_background'],
                                            font_family=THEME['font_family'],
                                            font_color=THEME['text_primary']
                                        )
                    )
                ]
            ),
            
            # GRÁFICO 2: GRÁFICO DE COMPARAÇÃO DINÂMICA
            html.Div(
                className='card',
                children=[
                    html.H2(id='comparacao-titulo', children="Selecione 2 meses no gráfico de linha", style={'fontSize': '1.4em', 'marginBottom': '15px', 'color': THEME['text_primary']}),
                    dcc.Graph(
                        id='comparacao-bar-chart',
                        style={'height': '350px'}, 
                        config={'displayModeBar': False}, 
                        figure={'data': [], 'layout': {'plot_bgcolor': THEME['card_background'], 'paper_bgcolor': THEME['card_background'], 'font': {'color': THEME['text_secondary'], 'family': THEME['font_family']}}}
                    )
                ]
            ),
        ]
    ),

    # BLOCO DE GLOSSÁRIO (VISUALIZAÇÃO SIMPLES E ÚNICA)
    html.Div(
        className='card info-section', 
        style={'padding': '25px', 'marginTop': '10px'},
        children=[
            html.H2("Glossário: Termos Financeiros Essenciais", style={'fontSize': '1.4em', 'marginBottom': '15px', 'color': THEME['faturamento_color']}),
            
            # Glossário em duas colunas
            html.Div(className='secondary-grid', children=[ 
                html.Div(children=[
                    html.P(html.Strong("Faturamento Total:"), style={'color': THEME['faturamento_color'], 'marginBottom': '0'}),
                    html.P("Todo o dinheiro que entrou no negócio (Valor Bruto).", style={'color': THEME['text_secondary'], 'marginTop': '0', 'fontSize': '0.9em'}),
                    
                    html.P(html.Strong("Lucro Líquido:"), style={'color': THEME['lucro_color'], 'marginBottom': '0', 'marginTop': '15px'}),
                    html.P("O que sobra após pagar todos os Gastos (Resultado Final).", style={'color': THEME['text_secondary'], 'marginTop': '0', 'fontSize': '0.9em'}),
                ]),
                
                html.Div(children=[
                    html.P(html.Strong("Gastos Totais:"), style={'color': THEME['gastos_color'], 'marginBottom': '0'}),
                    html.P("A soma de todas as despesas no período (Aluguel, impostos, etc.).", style={'color': THEME['text_secondary'], 'marginTop': '0', 'fontSize': '0.9em'}),

                    html.P(html.Strong("Pró-Labore:"), style={'color': THEME['text_primary'], 'marginBottom': '0', 'marginTop': '15px'}),
                    html.P("Remuneração do MEI, separada das contas da empresa.", style={'color': THEME['text_secondary'], 'marginTop': '0', 'fontSize': '0.9em'}),
                ]),
            ]),
        ]
    ),
]) 

# ----------------------------------------------------------------------
# CALLBACKS 
# ----------------------------------------------------------------------

# 1. Callback para Renderizar o Gráfico de Linha (Zoom Desativado)
@app.callback(
    Output('line-graph', 'figure'),
    [Input('line-graph', 'id')] 
)
def update_line_graph(_):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Mês_Str'], y=df['Faturamento'], mode='lines+markers+text', name='Faturamento', line={'color': THEME['faturamento_color'], 'width': 3}, text=[f"R$ {v:,.0f}" for v in df['Faturamento']], textposition="top center", hovertemplate='Faturamento: R$ %{y:,.2f}<extra></extra>'))
    fig.add_trace(go.Scatter(x=df['Mês_Str'], y=df['Gastos'], mode='lines+markers+text', name='Gastos', line={'dash': 'dot', 'color': THEME['gastos_color'], 'width': 3}, text=[f"R$ {v:,.0f}" for v in df['Gastos']], textposition="bottom center", hovertemplate='Gastos: R$ %{y:,.2f}<extra></extra>'))
    
    fig.update_layout(
        template='plotly_white', 
        plot_bgcolor=THEME['card_background'], 
        paper_bgcolor=THEME['card_background'], 
        xaxis_title=None, 
        yaxis_title="Valor (R$)", 
        font_color=THEME['text_primary'], 
        font_family=THEME['font_family'], 
        hovermode="x unified", 
        legend={'orientation': "h", 'yanchor': "bottom", 'y': 1.02, 'xanchor': "right", 'x': 1}, 
        
        # DESATIVA O ZOOM
        xaxis={'fixedrange': True},
        yaxis={'tickprefix': 'R$ ', 'tickformat': '.,0f', 'fixedrange': True}
    )
    return fig


# 2. Callback para Armazenar 2 Cliques (Meses) 
@app.callback(
    Output('meses-selecionados', 'data'),
    [Input('line-graph', 'clickData')],
    [State('meses-selecionados', 'data')]
)
def store_clicks(clickData, meses_atuais):
    if clickData is None:
        return meses_atuais 
    
    mes_clicado = clickData['points'][0]['x']
    
    if mes_clicado in meses_atuais:
        meses_atuais.remove(mes_clicado)
    elif len(meses_atuais) == 2:
        meses_atuais = [mes_clicado]
    else:
        meses_atuais.append(mes_clicado)
        
    meses_atuais = meses_atuais[-2:]

    df_temp = df[df['Mês_Str'].isin(meses_atuais)]
    
    if len(df_temp) == 2:
        meses_ordenados = df_temp.sort_values('Mês')['Mês_Str'].tolist()
        return meses_ordenados
    
    return meses_atuais


# 3. Callback para Atualizar o Gráfico de Comparação e o KPI Superior
@app.callback(
    [Output('comparacao-bar-chart', 'figure'),
     Output('comparacao-titulo', 'children'),
     Output('kpi-comparacao-variacao', 'children')],
    [Input('meses-selecionados', 'data')]
)
def update_comparison_charts(meses_selecionados):
    if len(meses_selecionados) < 2:
        empty_figure = {'data': [], 'layout': {'plot_bgcolor': THEME['card_background'], 'paper_bgcolor': THEME['card_background'], 'font': {'color': THEME['text_secondary'], 'family': THEME['font_family']}}}
        kpi_placeholder = create_kpi_card("Selecione 2 Meses", "0.0%", THEME['text_secondary']) 
        return empty_figure, "Selecione 2 meses no gráfico de linha", kpi_placeholder

    mes_antigo, mes_novo = meses_selecionados
    
    df_comparacao = df[df['Mês_Str'].isin([mes_antigo, mes_novo])]
    df_plot = df_comparacao.set_index('Mês_Str')[['Faturamento', 'Gastos', 'Lucro']].T.reset_index()
    
    df_plot.columns = ['Tipo', mes_antigo, mes_novo] 
    
    lucro_antigo = df_comparacao[df_comparacao['Mês_Str'] == mes_antigo]['Lucro'].iloc[0]
    lucro_novo = df_comparacao[df_comparacao['Mês_Str'] == mes_novo]['Lucro'].iloc[0]
    
    if lucro_antigo == 0:
         variacao_porcentual = 100 if lucro_novo > 0 else 0
    else:
        variacao_porcentual = ((lucro_novo - lucro_antigo) / lucro_antigo) * 100
        
    cor_variacao = THEME['lucro_color'] if variacao_porcentual >= 0 else THEME['gastos_color']
    
    kpi_variacao = create_kpi_card(
        f"Variação Lucro ({mes_antigo} \u2192 {mes_novo})",
        f"{variacao_porcentual:+.1f}%", 
        cor_variacao
    )

    fig = px.bar(
        df_plot,
        x='Tipo',
        y=[mes_antigo, mes_novo], 
        barmode='group',
        color_discrete_map={mes_antigo: THEME['text_secondary'], mes_novo: THEME['faturamento_color']},
        title=''
    )
    
    fig.update_layout(
        template='plotly_white',
        plot_bgcolor=THEME['card_background'],
        paper_bgcolor=THEME['card_background'],
        font_color=THEME['text_primary'],
        font_family=THEME['font_family'],
        
        yaxis={
            'tickprefix': 'R$ ', 
            'tickformat': '.,0f', 
            'title': 'Valor (R$)',
            'fixedrange': True 
        },
        xaxis={
            'title': None,
            'fixedrange': True 
        },
        
        legend_title_text='Período',
        margin={'t': 50, 'b': 20, 'l': 40, 'r': 10} 
    )
    
    titulo_comparacao = f"Comparação: {mes_antigo} vs {mes_novo}"
    
    return fig, titulo_comparacao, kpi_variacao

# --- 7. Execução do Aplicativo ---

if __name__ == '__main__':
    print("Dashboard rodando em http://127.0.0.1:8050/")
    app.run(debug=True)