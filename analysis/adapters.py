# analysis/adapters.py

import io
from abc import ABC, abstractmethod
import joblib
import torch
import tensorflow as tf
import onnxruntime as ort
import numpy as np

ADAPTERS = {}

def register_adapter(name):
    """Decorator para registrar cada adaptador por clave 'sklearn', 'pytorch', etc."""
    def decorator(cls):
        ADAPTERS[name] = cls()
        return cls
    return decorator

class BaseAdapter(ABC):
    """Interfaz común: carga un modelo y ofrece un método `predict(data, **params)`."""

    @abstractmethod
    def load(self, file_obj):
        """Carga el modelo desde un file-like object y retorna un objeto runnable."""
        pass

    @abstractmethod
    def predict(self, model, data, **params):
        """Ejecuta inferencia. ‘data’ puede ser array, CSV, DataFrame, etc."""
        pass

@register_adapter('sklearn')
class SklearnAdapter(BaseAdapter):
    def load(self, file_obj):
        return joblib.load(file_obj)

    def predict(self, model, data_2d):
        X = np.array(data_2d)  # shape (batch, n_features)
        return model.predict(X).tolist()

@register_adapter('pytorch')
class PyTorchAdapter(BaseAdapter):
    def load(self, file_obj):
        return torch.load(file_obj, map_location='cpu')

    def predict(self, model, data, **params):
        model.eval()
        inputs = torch.tensor(data, **params.get('tensor_kwargs', {}))
        with torch.no_grad():
            return model(inputs).numpy().tolist()

@register_adapter('tensorflow')
class TFAdapter(BaseAdapter):
    def load(self, file_obj):
        return tf.keras.models.load_model(file_obj)

    def predict(self, model, data, **params):
        return model.predict(data, **params).tolist()

@register_adapter('onnx')
class ONNXAdapter(BaseAdapter):
    def load(self, file_obj):
        sess = ort.InferenceSession(file_obj.read_bytes())
        return sess

    def predict(self, model, data, **params):
        input_name = model.get_inputs()[0].name
        return model.run(None, {input_name: data})[0].tolist()
