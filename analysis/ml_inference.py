# analysis/inference.py

import os, json
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
    # 1. Selecciona adaptador
    adapter = ADAPTERS.get(framework)
    if not adapter:
        # Error 1: Framework no soportado
        raise ValueError(f"Framework no soportado: {framework}")

    # 2. Prepara la data
    try:
        data = load_dataset(dataset_path)
    except FileNotFoundError:
        # Error 2.1: Dataset no encontrado
        raise FileNotFoundError(f"El dataset seleccionado no se encuentra en el sistema. Por favor, carguelo nuevamente.")
    except Exception as e:
        # Error 2.2: Otro error al cargar el dataset
        raise RuntimeError(f"Error al cargar el dataset. Intentelo de nuevo.")

    # 3. Carga el modelo desde filesystem (file-like)
    try:
        with open(model_path, 'rb') as f:
            model_obj = adapter.load(f)
    except FileNotFoundError:
        # Error 3.1: Modelo no encontrado
        raise FileNotFoundError(f"El archivo del modelo no se encontró en el directorio. Por favor, reporte este insidenTE.")
    except PermissionError:
        # Error 3.2: Permisos insuficientes
        raise PermissionError(f"Permiso denegado para acceder al archivo del modelo.")
    except Exception as e:
        # Error 3.3: Error de deserialización o carga del adaptador
        raise RuntimeError(f"Error al cargar el modelo con el adaptador '{framework}' desde {model_path}: {e}")

    # 4. Verifica y obtiene inputs
    inputs = parameters.get('inputs')  # [[...]]
    if inputs is None:
        # Error 4: Inputs faltantes
        raise ValueError('Faltan inputs vectorizados en parameters.inputs')

    # 5. Ejecuta inferencia
    try:
        predictions = adapter.predict(model_obj, inputs)
    except Exception as e:
        # Error 5: Fallo durante la predicción
        raise RuntimeError(f"Error durante la ejecucion del modelo '{model_path}': {e}")

    # 6. (Opcional) calcula métricas sencillas
    metrics = {
        'samples': len(predictions),
        # puedes añadir accuracy, RMSE, etc., si cuentas con ground-truth
    }

    # 7. Guarda resultados
    try:
        # 1) Directorio de salida
        out_dir = os.path.join(settings.MEDIA_ROOT, 'data/results')
        os.makedirs(out_dir, exist_ok=True)
        
        # 2) Sanear el nombre del modelo
        base_name  = os.path.splitext(os.path.basename(model_path))[0]
        model_slug = slugify(base_name)  # "my-model-v2"

        # 3) Construir el filename según el id del análisis si viene
        if analysis_id:
            filename = f"out_{model_slug}_{analysis_id}.json"
        else:
            filename = f"out_{model_slug}.json"

        out_path = os.path.join(out_dir, filename)
        
        # 4) Escribir el archivo
        with open(out_path, 'w') as fp:
            json.dump(predictions, fp)
            
    except OSError as e:
        # Error 6.1: Problemas con la creación de directorios o permisos de escritura
        raise OSError(f"Error de sistema al crear el directorio de salida o escribir el resultado. Por favor, reporte este insidente.")
    except Exception as e:
        # Error 6.2: Otro error al guardar
        raise RuntimeError(f"Error inesperado al guardar los resultados. Por favor, reporte este insidente e intentelo nuevamente.")

    # 8. Retorno exitoso
    return metrics, out_path
