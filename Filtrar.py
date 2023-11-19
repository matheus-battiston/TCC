import pandas as pd
from tqdm import tqdm
from arquivos import arquivoDezembro

# Lê o arquivo CSV
df = pd.read_csv(arquivoDezembro)

# Inicializa um conjunto para manter as sessões com ação 'cart'
sessions_with_cart = set()

# Inicializa uma variável para contar o número de sessões com 'cart'
cart_sessions_count = 0

# Itera pelas linhas do DataFrame com tqdm para exibir a barra de progresso
for index, row in tqdm(df.iterrows(), total=len(df)):
    session_id = row['user_session']
    action = row['event_type']

    # Verifica se a ação é 'cart' e adiciona a sessão ao conjunto
    if action == 'cart' and session_id not in sessions_with_cart:
        sessions_with_cart.add(session_id)

# Filtra o DataFrame original para manter apenas as sessões com 'cart'
filtered_df = df[df['user_session'].isin(sessions_with_cart)]

# Salva o DataFrame filtrado em um novo arquivo CSV
filtered_df.to_csv('OutubroFiltrado.csv', index=False)
