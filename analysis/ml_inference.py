# analysis/inference.py

import os
import pandas as pd
from django.conf import settings
from .adapters import ADAPTERS
from django.utils.text import slugify

def load_dataset(path):
    """
    - Si son CSV, carga con pandas.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(path)
    # otros casos…
    raise ValueError(f"Formato de dataset no soportado: {ext}")

def execute(model_path, framework, dataset_path, parameters, analysis_id):
    """
    1. Selecciona adaptador según framework.
    2. Abre el archivo de modelo (file-like).
    3. Carga y ejecuta predict con data + parámetros.
    4. Devuelve métricas crudas y ruta de salida.
    """
    adapter = ADAPTERS.get(framework)
    if not adapter:
        raise ValueError(f"Framework no soportado: {framework}")

    # 1. Prepara la data
    data = load_dataset(dataset_path)

    # 2. Carga el modelo desde filesystem (file-like)
    with open(model_path, 'rb') as f:
        model_obj = adapter.load(f)

    inputs = parameters.get('inputs')  # [[...]]
    if inputs is None:
        raise ValueError('Faltan inputs vectorizados en parameters.inputs')    

    # 3. Ejecuta inferencia
    predictions = adapter.predict(model_obj, inputs)

    # 4. (Opcional) calcula métricas sencillas
    metrics = {
        'samples': len(predictions),
        # puedes añadir accuracy, RMSE, etc., si cuentas con ground-truth
    }

    # 1) Directorio de salida
    out_dir = os.path.join(settings.MEDIA_ROOT, 'data/results')
    os.makedirs(out_dir, exist_ok=True)

    # 2) Sanear el nombre del modelo
    #    Ej: model_path="/…/My Model v2.pkl" → base_name="My Model v2"
    base_name  = os.path.splitext(os.path.basename(model_path))[0]
    model_slug = slugify(base_name)  # "my-model-v2"

    # 3) Construir el filename según el id del análisis si viene
    if analysis_id:
        filename = f"out_{model_slug}_{analysis_id}.json"
    else:
        filename = f"out_{model_slug}.json"

    out_path = os.path.join(out_dir, filename)
    with open(out_path, 'w') as fp:
        import json; json.dump(predictions, fp)

    return metrics, out_path
