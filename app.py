import os
import time
from flask import Flask, Response, render_template
import requests

app = Flask(__name__)

cache_file = 'cache.csv'
cache_duration = 30 * 24 * 60 * 60  # 30 jours en secondes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_data')
def fetch_data():
    try:
        # Vérifier si le fichier de cache existe et est à jour
        if os.path.exists(cache_file):
            last_modified = os.path.getmtime(cache_file)
            if time.time() - last_modified < cache_duration:
                # Lire les données depuis le cache
                with open(cache_file, 'rb') as f:
                    data = f.read()
                return Response(data, mimetype='text/plain')

        # Sinon, récupérer les nouvelles données depuis la NASA
        url = 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.content

        # Enregistrer les données dans le cache
        with open(cache_file, 'wb') as f:
            f.write(data)

        return Response(data, mimetype='text/plain')
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Erreur lors de la récupération des données : {e}")
        
        # En cas d'erreur, essayer de servir les données depuis le cache si disponible
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                data = f.read()
            return Response(data, mimetype='text/plain')
        else:
            return Response('Erreur lors de la récupération des données.', status=500)

if __name__ == '__main__':
    app.run(debug=True)
