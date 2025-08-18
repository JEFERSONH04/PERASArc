from celery import shared_task
import time, random

@shared_task
def sumar(a, b):
    if a is None or b is None:
        raise ValueError("Argumentos inválidos: a y b no pueden ser None")
    return a + b

@shared_task
def sumar_masivo():
    resultados = []
    errores = 0

    for _ in range(100):
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        try:
            resultado = sumar(a, b)
            resultados.append({
                "a": a,
                "b": b,
                "resultado": resultado
            })
        except Exception as e:
            errores += 1
            resultados.append({
                "a": a,
                "b": b,
                "error": str(e)
            })

    tasa_exito = (100 - errores) / 100 * 100
    return {
        "total": 100,
        "exitos": 100 - errores,
        "fallos": errores,
        "tasa_exito": f"{tasa_exito:.2f}%",
        "resultados": resultados[:5]  # muestra los primeros 5 como ejemplo
    }
