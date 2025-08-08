# performance_test_datasets.py

import asyncio
import httpx
import time
import io
from statistics import mean

API_URL       = "http://localhost:8000/api/v1/datasets/"
ACCESS_TOKEN  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0NjY4NjU1LCJpYXQiOjE3NTQ2NjgzNTUsImp0aSI6ImM4N2UzOTVhZmRiZTRkODdiYjhlNGMyMWU1Nzc5NTIyIiwidXNlcl9pZCI6IjEiLCJ1c2VybmFtZSI6IkplZmVyRGFyaW8ifQ.Ogjs1G8CSjGMoVMOOKWqyHncuAYKQBs3GXnEUi52Zc0"
CONCURRENCY   = 800

# Genera un archivo CSV en memoria
def make_csv_bytes():
    header = "col1,col2,col3\n"
    rows   = "".join(f"{i},{i+1},{i+2}\n" for i in range(100))
    data   = header + rows
    return io.BytesIO(data.encode("utf-8"))

async def post_dataset(client: httpx.AsyncClient, idx: int):
    """
    Envía una petición POST para crear un dataset.
    Devuelve el tiempo de respuesta en segundos.
    """
    files = {
        "name":        (None, f"perf-dataset-{idx}"),
        "description": (None, "Prueba de rendimiento concurrente"),
        "file":        ("data.csv", make_csv_bytes(), "text/csv"),
    }
    start = time.perf_counter()
    response = await client.post(API_URL, files=files)
    elapsed = time.perf_counter() - start

    if response.status_code != 201:
        # Opcional: loggea errores
        print(f"[ERROR {response.status_code}] idx={idx}", response.text)

    return elapsed

async def run_performance_test():
    """
    Lanza CONCURRENCY peticiones concurrently y mide tiempos.
    Imprime promedio, mínimo y máximo.
    """
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    async with httpx.AsyncClient(headers=headers, timeout=210.0) as client:
        tasks = [
            asyncio.create_task(post_dataset(client, i))
            for i in range(CONCURRENCY)
        ]

        # Espera a que todas las tareas finalicen
        times = await asyncio.gather(*tasks)

    avg_time = mean(times)
    min_time = min(times)
    max_time = max(times)
    total    = sum(times)

    print("\n--- Resultados de rendimiento ---")
    print(f"Concurrent requests : {CONCURRENCY}")
    print(f"Total time          : {total:.2f} s")
    print(f"Average time/req    : {avg_time:.3f} s")
    print(f"Fastest req         : {min_time:.3f} s")
    print(f"Slowest req         : {max_time:.3f} s")

if __name__ == "__main__":
    # Ejecuta el bucle de eventos
    asyncio.run(run_performance_test())
