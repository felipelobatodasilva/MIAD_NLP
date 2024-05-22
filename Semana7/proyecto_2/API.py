# Importação de bibliotecas
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from werkzeug.utils import cached_property
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pandas as pd
import numpy as np
import joblib
import traceback
import nltk
import string

# Cargar el modelo
model = joblib.load('modelo.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Crear la aplicación Flask con el nombre "api_grupo5"
app = Flask("api_grupo5")

# Definir la API Flask con Flask-Restx
api = Api(
    app,
    version='1.0',
    title='Movie Genre Classification API',
    description='Classify the genre of a movie based on its features'
)

# Faça o download dos recursos necessários do NLTK (se ainda não tiver feito)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Função de pré-processamento de texto
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    # Convertendo para minúsculas
    text = text.lower()
    # Tokenização
    tokens = word_tokenize(text)
    # Removendo stopwords, pontuações e números
    tokens = [word for word in tokens if word not in stop_words and word not in string.punctuation and not word.isdigit()]
    # Lematização
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    # Unindo os tokens novamente em uma string
    processed_text = ' '.join(tokens)
    return processed_text

movie_genre_model = api.model('MovieGenreModel', {
    'plot': fields.String(required=True, description='Plot of the movie')
})

# Definir la ruta para la API
@api.route('/classify')
class MovieGenreClassification(Resource):
    @api.expect(movie_genre_model)
    def post(self):
        try:
            # Obtener los datos de entrada
            data = request.json
            print("Datos recibidos:", data)
            X_input = pd.DataFrame([data])
            print("DataFrame de entrada:", X_input)

            # Aplicar el preprocesamiento del texto
            processed_input = X_input['plot'].apply(preprocess_text)
            print("Texto procesado:", processed_input)

            # Vectorizar el texto preprocesado
            vectorized_text = vectorizer.transform(processed_input)
            print("Texto vectorizado:", vectorized_text)

            # Realizar la predicción directamente con el modelo
            prediction = model.predict(vectorized_text)
            print("Predicción:", prediction)

            # Devolver la predicción
            return {'prediction': prediction.tolist()}

        except Exception as e:
            traceback.print_exc()
            return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
