# analysis/tasks.py
import json
from celery import shared_task
from .circuit_breaker import RedisCircuitBreaker, CircuitOpen
from django.utils import timezone
from django.core.cache import cache
from .models import AnalysisResult
from .ml_inference import execute
import logging
logger = logging.getLogger(__name__)

execute_breaker = RedisCircuitBreaker(name="execute", max_failures=5, reset_timeout=60)

@shared_task(bind=True)
def launch_analysis_task(self, analysis_id):
    """
    Tarea Celery que:
      1. Carga el AnalysisResult.
      2. Garantiza que parameters siempre esté ligado a un dict.
      3. Valida vector_2d.
      4. Ejecuta inferencia y captura métricas y ruta.
      5. Persiste métricas, output_path y estado.
    """
    metrics = {}
    output_path = ""
    status = "FAILURE"
    analysis = AnalysisResult.objects.get(pk=analysis_id)

    params = analysis.parameters

    if not isinstance(params, dict):
        raise ValueError(f"parameters debe ser un dict, no {type(params).__name__}")

    vector = params.get("vector_2d")
    if not isinstance(vector, list):
        raise ValueError(f"vector_2d faltante o inválido: {vector!r}")


    try:
        wrapped_execute = execute_breaker(execute)
        metrics, output_path = wrapped_execute(
            model_path=analysis.model.file.path,
            framework=analysis.model.framework,
            dataset_path=analysis.dataset.file.path,
            parameters={"inputs": vector},
            analysis_id=analysis.id
        )
        status = "SUCCESS"
        analysis.completed_at = timezone.now()
    except CircuitOpen:
        analysis.error_message = "Servicio temporalmente no disponible (Circuit abierto)."
        status = "FAILURE"
        metrics, output_path = {}, ""

    except Exception as exc:
                # Esto vuelca el stack trace en los logs
        logger.exception("Error al ejecutar execute() para AnalysisResult %s", analysis_id)
        # Guarda también el mensaje en BD si lo deseas
        analysis.error_message = str(exc)
        analysis.status = "FAILURE"
        analysis.save(update_fields=['error_message', 'status'])
        # O relanza el error para que Celery lo marque como FAILURE:
        raise

    analysis.metrics     = metrics
    analysis.output_path = output_path
    analysis.status      = status
    analysis.save(update_fields=["metrics", "output_path", "status", "completed_at", "error_message"])


