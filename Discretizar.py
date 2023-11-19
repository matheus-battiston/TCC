import pandas as pd

# Carregue o arquivo CSV
df = pd.read_csv('FeatureEngineering.csv')

# Use a função qcut para discretizar a coluna 'session_duration' em 3 intervalos com quantidades iguais
df['Session_Duration_Discretizada'] = pd.qcut(df['session_duration'], q=20, duplicates='drop')
df['Num_Categories_Discretiada'] = pd.qcut(df['num_categories_viewed'], q=20, duplicates='drop')
df['Avg_Cart_Discretiada'] = pd.qcut(df['avg_price_in_cart'], q=20, duplicates='drop')
df['Num_Products_Discretiada'] = pd.qcut(df['num_products_viewed'], q=20, duplicates='drop')
df['AvgTimeClick_Discretiada'] = pd.qcut(df['average_time_between_clicks'], q=20, duplicates='drop')
df['ViewCart_Discretiada'] = pd.qcut(df['time_between_view_and_cart'], q=20, duplicates='drop')
df['PurchaseDayDiscretize'] = pd.qcut(df['purchase_day'], q=31, duplicates='drop')

# Discretize a coluna 'last_added_product_brand' em 100 intervalos com base na frequência
coluna = 'last_added_product_brand'
top_brands = df[coluna].value_counts().head(100).index
df['Brand_Discretizada'] = df[coluna].apply(lambda x: x if x in top_brands else 'Other')

# Salve o DataFrame em um novo arquivo CSV
df.to_csv('ArquivoDiscretizado.csv', index=False)
