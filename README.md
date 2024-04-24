#################PREPROCESAMIENTO ########################################################################
# Importación librerías
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, PolynomialFeatures
from sklearn.metrics import make_scorer
from sklearn.impute import SimpleImputer
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split, RandomizedSearchCV,cross_val_score
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error

#METRICA
def root_mean_squared_error(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

#funcion para limpieza 
def quitartildes(column):
    a, b = 'áéíóúüñÁÉÍÓÚÜàèìòù', 'aeiouunAEIOUUaeiou'
    trans = str.maketrans(a, b)
    column = column.str.strip().str.upper().str.translate(trans)
    return column

# Carga de datos de archivo .csv
dataTraining = pd.read_csv('https://raw.githubusercontent.com/davidzarruk/MIAD_ML_NLP_2023/main/datasets/dataTrain_carListings.zip')
dataTesting = pd.read_csv('https://raw.githubusercontent.com/davidzarruk/MIAD_ML_NLP_2023/main/datasets/dataTest_carListings.zip', index_col=0)
duplicados = dataTraining.duplicated().sum()
df_train2 = dataTraining.drop_duplicates()
Q1 = df_train2['Price'].quantile(0.25)
Q3 = df_train2['Price'].quantile(0.75)
IQR = Q3 - Q1
limite_inferior = Q1 - 1.5 * IQR
limite_superior = Q3 + 1.5 * IQR

# Identificar valores atípicos del precio y quitandolos
valores_atipicos = df_train2[(df_train2['Price'] < limite_inferior) | (df_train2['Price'] > limite_superior)]
df_train3 = df_train2[(df_train2['Price'] >= limite_inferior) & (df_train2['Price'] <= limite_superior)]

#Identificando valores atipicos de Mileage y quitandolos 
df_train3 = df_train3[df_train3['Mileage'] <= 1500000]
print(df_train2.shape)
print(df_train3.shape)

# Supongamos que tienes tus datos en un DataFrame llamado df_train3
# División de datos en características y variable objetivo
X = df_train3.drop('Price', axis=1)
y = df_train3['Price']

#limpieza de vbles categoricas
X['State'] = quitartildes(X['State'])
X['Model'] = quitartildes(X['Model'])
X['Make'] = quitartildes(X['Make'])

#Ingenieria de caracteristicas
current_year = datetime.now().year
X['Car_Age'] = current_year - X['Year']
X['Mileage_Year'] = X['Year'] / X['Mileage']
X['Brand_Model'] = X['Make'] + '_' + X['Model']

# Listas de características numéricas y categóricas
numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
categorical_features = X.select_dtypes(include=['object']).columns

# Definición de transformadores para características numéricas y categóricas
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
])

# ColumnTransformer para aplicar transformadores a diferentes tipos de características
preprocessor = ColumnTransformer(
    transformers=[
        #('remove_accents', RemoveAccentsTransformer(), ['State', 'Model', 'Make']),
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])

# Pipeline que incluye el preprocesamiento y el modelo
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor)])

# Aplicar el pipeline a los datos
X_preprocessed = pipeline.fit_transform(X)

# Division de los datos
X_train, X_test, y_train, y_test = train_test_split(X_preprocessed, y, test_size=0.33, random_state=42)

##############PONER MODEL##############################################

##############PREPROCESAMIENTO DE LA BASE PARA KGGL#####################
#data de competencia
dataTesting['State'] = quitartildes(dataTesting['State'])
dataTesting['Model'] = quitartildes(dataTesting['Model'])
dataTesting['Make'] = quitartildes(dataTesting['Make'])
dataTesting['Car_Age'] = current_year - dataTesting['Year']
dataTesting['Mileage_Year'] = dataTesting['Year'] / dataTesting['Mileage']
dataTesting['Brand_Model'] = dataTesting['Make'] + '_' + dataTesting['Model']

X_testcru = pipeline.transform(dataTesting)
y_predmodelo1 = xgboost_model.predict(X_testcru)
print(y_predmodelo1[:5]) 
df = pd.DataFrame(y_predmodelo1) 
# Rename the default column (likely '0') to 'Price'
df = df.rename(columns={0: 'Price'}) 
# Save to CSV 
df.to_csv(r"C:\Users\anasoto\Downloads\modeloxgboost9.csv", index_label='ID') 
#4144 en kaggle
