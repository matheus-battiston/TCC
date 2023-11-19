import pandas as pd
import calendar
from tqdm import tqdm

# Carregue o arquivo CSV em um DataFrame
df = pd.read_csv('DezembroFiltrado.csv')

# Ordene o DataFrame pelo user_id e event_time
df['event_time'] = pd.to_datetime(df['event_time'], format='%Y-%m-%d %H:%M:%S UTC')
df = df.sort_values(by=['user_id', 'event_time'])

# Inicialização de variáveis para rastrear a sessão atual
id_do_usuario = None
comeco_da_sessao = None
produtos_adicionados_ao_carrinho = []  # Lista para rastrear produtos adicionados ao carrinho
marca_do_produto_adicionado = None  # Marca do último produto adicionado ao carrinho
categorias_vistas = set()  # Conjunto para rastrear categorias visualizadas
marcas_vistas = set()  # Conjunto para rastrear marcas visualizadas

# Agrupe o DataFrame por user_session
session_groups = df.groupby('user_session')

# Inicialização de variáveis para rastrear a sessão atual
sessoes = []

# Dicionário para rastrear se um usuário fez uma compra em alguma sessão anterior
user_purchase_dict = {}

# Dicionário para rastrear as marcas de produtos compradas pelo usuário
user_brand_purchase_dict = {}

# Use tqdm para mostrar a barra de progresso
pbar = tqdm(total=len(session_groups))

# Iterar sobre os grupos
for session_id, dados_da_sessao in session_groups:
    dados_da_sessao = dados_da_sessao.sort_values(by='event_time')  # Ordenar os dados da sessão

    comeco_da_sessao = dados_da_sessao.iloc[0]['event_time']
    horario_fim_sessao = dados_da_sessao.iloc[-1]['event_time']
    duracao_da_sessao = (horario_fim_sessao - comeco_da_sessao).total_seconds()

    adicionou_ao_carrinho = 'cart' in dados_da_sessao['event_type'].values
    numero_categorias_vistas = len(dados_da_sessao[dados_da_sessao['event_type'] == 'view']['category_id'].unique())
    realizou_compra = 'purchase' in dados_da_sessao['event_type'].values
    preco_medio_no_carrinho = dados_da_sessao[dados_da_sessao['event_type'] == 'cart']['price'].mean()
    numero_de_produtos_vistos = dados_da_sessao[dados_da_sessao['event_type'] == 'view']['product_id'].nunique()

    # Adicionar o dia do mês em que a compra foi feita
    data_da_compra = dados_da_sessao[dados_da_sessao['event_type'] == 'cart']['event_time'].max()
    dia_da_compra = data_da_compra.day

    # Adicionar o dia da semana em que a compra foi feita
    dia_da_semana = calendar.day_name[data_da_compra.weekday()]

    # Transformar o campo de categoria em uma string
    categoria = dados_da_sessao[dados_da_sessao['event_type'] == 'cart']['category_code'].values[0]
    categoria = str(categoria) if not pd.isna(categoria) else ''

    # Dividir a categoria em duas partes
    divisao_cateogira = categoria.split('.', 1)
    categoria_part1 = divisao_cateogira[0] if len(divisao_cateogira) > 0 else ''
    categoria_part2 = divisao_cateogira[1].split('.')[0] if len(divisao_cateogira) > 1 else ''

    # Verificar se o usuário visualizou produtos da mesma marca antes de adicionar ao carrinho
    marcas_visualizadas = set(dados_da_sessao[dados_da_sessao['event_type'] == 'view']['brand'].unique())
    visualizou_mesma_marca = marca_do_produto_adicionado in marcas_visualizadas

    # Atualizar a marca do último produto adicionado ao carrinho
    if adicionou_ao_carrinho:
        marca_do_produto_adicionado = dados_da_sessao[
            (dados_da_sessao['event_type'] == 'cart') &
            (dados_da_sessao['user_session'] == session_id)
            ]['brand'].values[0]

    # Atualizar os produtos adicionados ao carrinho e marcas visualizadas
    if adicionou_ao_carrinho:
        produtos_adicionados_ao_carrinho = list(dados_da_sessao[dados_da_sessao['event_type'] == 'cart']['product_id'].unique())
        marcas_vistas.update(dados_da_sessao[dados_da_sessao['event_type'] == 'view']['brand'].unique())

    # Verificar se o usuário fez uma compra em alguma sessão anterior
    user_id = dados_da_sessao.iloc[0]['user_id']
    tem_compra_anterior = user_purchase_dict.get(user_id, False)

    # Verificar se o usuário já comprou produtos da mesma marca anteriormente
    if adicionou_ao_carrinho and marca_do_produto_adicionado:
        compra_previa_marca = user_brand_purchase_dict.get(user_id, {}).get(marca_do_produto_adicionado, False)
    else:
        compra_previa_marca = False

    # Atualizar o dicionário de compras por usuário
    if realizou_compra:
        user_purchase_dict[user_id] = True

    # Atualizar o dicionário de marcas compradas pelo usuário
    if adicionou_ao_carrinho and marca_do_produto_adicionado:
        if user_id not in user_brand_purchase_dict:
            user_brand_purchase_dict[user_id] = {}
        user_brand_purchase_dict[user_id][marca_do_produto_adicionado] = True

    # Calcular o tempo médio entre cliques do usuário
    numero_de_acoes = len(dados_da_sessao)
    tempo_medio_entre_cliques = duracao_da_sessao / numero_de_acoes if numero_de_acoes > 0 else 0

    # Calcular o tempo em segundos entre a visualização e a adição ao carrinho
    tempo_entre_visualizar_e_adicionar_ao_carrinho = 0
    if adicionou_ao_carrinho and marca_do_produto_adicionado:
        evento_carrinho = dados_da_sessao[(dados_da_sessao['event_type'] == 'cart') & (dados_da_sessao['user_session'] == session_id)]
        visualizacao = dados_da_sessao[
            (dados_da_sessao['event_type'] == 'view') &
            (dados_da_sessao['product_id'] == evento_carrinho['product_id'].values[0])
            ]
        if not visualizacao.empty:
            tempo_entre_visualizar_e_adicionar_ao_carrinho = (evento_carrinho['event_time'].iloc[0] - visualizacao['event_time'].iloc[0]).total_seconds()

    # Verificar se o usuário visualizou o produto após adicioná-lo ao carrinho
    visualizou_apos_carrinho = False
    if adicionou_ao_carrinho and marca_do_produto_adicionado:
        evento_carrinho = dados_da_sessao[(dados_da_sessao['event_type'] == 'cart') & (dados_da_sessao['user_session'] == session_id)]
        view_events_after_cart = dados_da_sessao[
            (dados_da_sessao['event_type'] == 'view') &
            (dados_da_sessao['product_id'] == evento_carrinho['product_id'].values[0]) &
            (dados_da_sessao['event_time'] > evento_carrinho['event_time'].iloc[0])
            ]
        visualizou_apos_carrinho = not view_events_after_cart.empty

    sessoes.append({
        'user_session': session_id,
        'session_duration': duracao_da_sessao,
        'had_cart_action': adicionou_ao_carrinho,
        'num_categories_viewed': numero_categorias_vistas,
        'had_purchase': realizou_compra,
        'avg_price_in_cart': preco_medio_no_carrinho,
        'num_products_viewed': numero_de_produtos_vistos,
        'purchase_day': dia_da_compra,
        'purchase_weekday': dia_da_semana,
        'category_part1': categoria_part1,
        'category_part2': categoria_part2,
        'viewed_same_brand': visualizou_mesma_marca,
        'has_previous_purchase': tem_compra_anterior,
        'last_added_product_brand': marca_do_produto_adicionado,
        'previous_brand_purchase': compra_previa_marca,
        'average_time_between_clicks': tempo_medio_entre_cliques,
        'time_between_view_and_cart': tempo_entre_visualizar_e_adicionar_ao_carrinho,  # Adicione a nova coluna
        'viewed_after_cart': visualizou_apos_carrinho # Nova coluna que indica se o usuário visualizou após adicionar ao carrinho

    })

    # Atualizar a barra de progresso
    pbar.update(1)

# Feche a barra de progresso
pbar.close()

# Converter as sessões em um novo DataFrame
session_df = pd.DataFrame(sessoes)

# Filtre apenas as sessões em que um produto foi adicionado ao carrinho
session_df = session_df[session_df['had_cart_action']]

# Salvar o DataFrame resultante em um arquivo CSV
session_df.to_csv('FeatureEngineering.csv', index=False)
