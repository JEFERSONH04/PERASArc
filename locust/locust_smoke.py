# locust_smoke.py
"""
Locust smoke test script.
- Usuario: usuarioprueba / hola1234
- Model id: 1
- Dataset id: 1

Uso:
  locust -f locust_smoke.py --host=http://localhost:8000
o en headless:
  locust -f locust_smoke.py --headless -u 5 -r 1 --run-time 2m --host=http://localhost:8000
"""

import os
import time
import random
from locust import HttpUser, task, between, SequentialTaskSet, events, constant

USERNAME = "usuarioprueba"
PASSWORD = "hola1234"
DEFAULT_MODEL_ID = 1
DEFAULT_DATASET_ID = 1

def auth_headers(token):
    if not token:
        return {"Content-Type": "application/json"}
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

class SmokeFlow(SequentialTaskSet):
    def on_start(self):
        """
        Intento de autenticación:
          1) JWT endpoints comunes
          2) Si falla, intento login por sesión (CSRF)
        Guarda self.token (si JWT) o session cookie en self.client.
        """
        self.token = None
        self.session_auth = False
        username = USERNAME
        password = PASSWORD

        # 1) Intento JWT en endpoints comunes (ajusta si tu endpoint es distinto)
        jwt_endpoints = [
            "/api/v1/accounts/login/"
        ]
        for ep in jwt_endpoints:
            try:
                resp = self.client.post(ep, json={"username": username, "password": password}, name="auth:jwt", timeout=10)
            except Exception:
                resp = None
            if resp and resp.status_code in (200, 201):
                try:
                    data = resp.json()
                    token = data.get("access") or data.get("token") or data.get("access_token")
                except Exception:
                    token = None
                if token:
                    self.token = token
                    return


    @task(1)
    def create_and_wait_analysis(self):
        """
        Crea un análisis y, dentro de la misma tarea, realiza el polling del estado
        y descarga el resultado si corresponde. Así evitamos peticiones duplicadas
        provocadas por la reprogramación de tareas de Locust.
        """
        payload = {
            "model": DEFAULT_MODEL_ID,
            "dataset": DEFAULT_DATASET_ID,
            "param_1": round(random.uniform(0, 6), 1),
            "param_2": round(random.uniform(0, 6), 1),
            "param_3": round(random.uniform(0, 6), 1),
            "param_4": round(random.uniform(0, 6), 1),
        }
        headers = auth_headers(self.token)
        create_name = "POST /api/v1/analysis/"
        with self.client.post("/api/v1/analysis/", json=payload, headers=headers, catch_response=True, name=create_name, timeout=30) as resp:
            if resp.status_code in (200, 201, 202):
                try:
                    analysis_id = resp.json().get("id")
                except Exception:
                    analysis_id = None
            else:
                msg = f"Create analysis failed: {resp.status_code}"
                try:
                    msg += " body: " + resp.text[:200]
                except Exception:
                    pass
                resp.failure(msg)
                return  # no continuar si falla la creación

        if not analysis_id:
            return

        # Poll único y controlado dentro de la misma tarea
        poll_headers = auth_headers(self.token) if self.token else {"Content-Type": "application/json"}
        max_polls = 12
        poll_interval = 5
        status = None

        for attempt in range(1, max_polls + 1):
            # UNA sola petición GET por iteración
            res = self.client.get(f"/analisis/{analysis_id}/", headers=poll_headers, name="GET /analisis/:id", timeout=10)
            if res.status_code == 200:
                try:
                    status = res.json().get("status")
                except Exception:
                    status = None
                if status in ("SUCCESS", "FAILURE"):
                    break
            else:
                if res.status_code == 403:
                    # Fallo de auth detectado, registrarlo como fallo y no seguir poll
                    res.failure("403 when polling analysis; auth likely failed")
                    return
                # otros códigos se consideran intentos, continuar

            # Backoff progresivo simple para no saturar el endpoint
            if attempt >= 8:
                time.sleep(poll_interval * 3)
            elif attempt >= 4:
                time.sleep(poll_interval * 2)
            else:
                time.sleep(poll_interval)




class SmokeUser(HttpUser):
    tasks = [SmokeFlow]
    wait_time = constant(5)

# Eventos para logging simple al comenzar y terminar la prueba
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Starting Locust smoke test. Host:", environment.host)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Stopping Locust smoke test.")
