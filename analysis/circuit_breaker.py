# analysis/circuit_breaker.py
"""
RedisCircuitBreaker
Implementación compatible con backends Django cache (django-redis o LocMemCache).
Incluye _safe_incr para soportar backends sin argumento `default` en incr.
Uso:
    from analysis.circuit_breaker import RedisCircuitBreaker, CircuitOpen
    breaker = RedisCircuitBreaker("execute", max_failures=5, reset_timeout=60)
    wrapped = breaker(execute)  # wrap sin decorator
    # o usar como decorator:
    @breaker()
    def mycall(...): ...
"""

import time
import logging
from functools import wraps
from typing import Callable, Optional, Any
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CircuitOpen(Exception):
    """Se lanza cuando el circuito está abierto y la llamada es rechazada."""
    pass


class RedisCircuitBreaker:
    def __init__(
        self,
        name: str,
        max_failures: int = 5,
        reset_timeout: int = 60,
        expiry: int = 3600,
    ):
        """
        name: clave base en cache para este breaker.
        max_failures: número de fallos consecutivos para abrir el circuito.
        reset_timeout: tiempo (segundos) que estará abierto antes de pasar a half-open.
        expiry: expiración en segundos de las keys de cache para limpieza.
        """
        self.name = str(name)
        self.max_failures = int(max_failures)
        self.reset_timeout = int(reset_timeout)
        self.expiry = int(expiry)

        self.fail_key = f"cb:{self.name}:fails"
        self.state_key = f"cb:{self.name}:state"      # valores: 'closed','open','half-open'
        self.open_at_key = f"cb:{self.name}:open_at"  # timestamp cuando se abrió

    def _now(self) -> int:
        return int(time.time())

    def _safe_incr(self, key: str) -> int:
        """
        Incrementa de forma segura la clave en cache devolviendo el nuevo valor.
        Compatible con LocMemCache y django-redis.
        """
        try:
            # Intento directo: muchos backends soportan incr(key)
            return cache.incr(key)
        except ValueError:
            # LocMemCache lanza ValueError si la key no existe
            cache.set(key, 1, timeout=self.expiry)
            return 1
        except TypeError:
            # Algunos backends puede que rechacen la firma, fallback get/set
            val = cache.get(key)
            if val is None:
                cache.set(key, 1, timeout=self.expiry)
                return 1
            try:
                new = int(val) + 1
            except Exception:
                new = 1
            cache.set(key, new, timeout=self.expiry)
            return new
        except Exception as exc:
            # En caso de error inesperado, logueamos y tratamos como 1 para no bloquear
            logger.exception("Error en _safe_incr cache.incr: %s", exc)
            # fallback seguro
            val = cache.get(key)
            if val is None:
                cache.set(key, 1, timeout=self.expiry)
                return 1
            try:
                new = int(val) + 1
            except Exception:
                new = 1
            cache.set(key, new, timeout=self.expiry)
            return new

    def get_state(self) -> str:
        """
        Recupera el estado actual del circuito. Si está 'open' y ha pasado
        reset_timeout, se transita a 'half-open' y se guarda en cache.
        """
        state = cache.get(self.state_key) or 'closed'
        if state == 'open':
            open_at = cache.get(self.open_at_key) or 0
            if self._now() - int(open_at) >= self.reset_timeout:
                # transitar a half-open
                cache.set(self.state_key, 'half-open', timeout=self.expiry)
                logger.info("Circuit %s transitions open -> half-open (timeout elapsed)", self.name)
                return 'half-open'
        return state

    def increment_failure(self) -> None:
        """
        Incrementa el contador de fallos y abre el circuito si se supera el umbral.
        Maneja compatibilidad con diferentes backends.
        """
        fails = self._safe_incr(self.fail_key)
        # Asegurar que la key tenga timeout configurado
        try:
            # django-redis expone expire; si no existe, set será suficiente
            expire_func = getattr(cache, 'expire', None)
            if callable(expire_func):
                expire_func(self.fail_key, self.expiry)
            else:
                cache.set(self.fail_key, fails, timeout=self.expiry)
        except Exception:
            # No interrumpir por fallo de expiración
            try:
                cache.set(self.fail_key, fails, timeout=self.expiry)
            except Exception:
                logger.exception("No se pudo asegurar expiración de fail_key para %s", self.name)

        if fails >= self.max_failures:
            cache.set(self.state_key, 'open', timeout=self.expiry)
            cache.set(self.open_at_key, self._now(), timeout=self.expiry)
            logger.warning("Circuit %s opened after %s failures", self.name, fails)

    def reset(self) -> None:
        """Cierra el circuito y resetea contadores."""
        try:
            cache.delete(self.fail_key)
            cache.set(self.state_key, 'closed', timeout=self.expiry)
            cache.delete(self.open_at_key)
            logger.info("Circuit %s reset -> closed", self.name)
        except Exception:
            logger.exception("Error al resetear Circuit %s", self.name)

    def half_open_success(self) -> None:
        """Éxito durante half-open: cerrar circuito y resetear contadores."""
        self.reset()

    def half_open_failure(self) -> None:
        """Fallo durante half-open: volver a abrir con timestamp actualizado."""
        try:
            cache.set(self.state_key, 'open', timeout=self.expiry)
            cache.set(self.open_at_key, self._now(), timeout=self.expiry)
            logger.warning("Circuit %s re-opened from half-open", self.name)
        except Exception:
            logger.exception("Error al re-open Circuit %s desde half-open", self.name)

    def __call__(self, func: Optional[Callable] = None, *, fallback: Optional[Callable] = None):
        """
        Permite usar la instancia como decorator o como wrapper:
          @breaker()         # como decorator
          def f(...): ...

          wrapped = breaker(func)  # devuelve función envuelta
        fallback: callable que se ejecuta cuando el circuito está abierto.
        """
        def decorator(f: Callable):
            @wraps(f)
            def _wrapped(*args, **kwargs):
                state = self.get_state()
                if state == 'open':
                    logger.error("Circuit %s is open; refusing call", self.name)
                    if fallback:
                        try:
                            return fallback(*args, **kwargs)
                        except Exception:
                            logger.exception("Fallback for circuit %s raised an exception", self.name)
                            raise CircuitOpen(f"Circuit {self.name} is open and fallback failed")
                    raise CircuitOpen(f"Circuit {self.name} is open")
                try:
                    result = f(*args, **kwargs)
                except Exception as exc:
                    # Si estábamos en half-open, reabrimos inmediatamente
                    if state == 'half-open':
                        self.half_open_failure()
                    else:
                        self.increment_failure()
                    raise
                else:
                    # En caso de éxito y estado half-open -> cerrar y resetear
                    if state == 'half-open':
                        self.half_open_success()
                    else:
                        # Política: al éxito normal podemos limpiar contador de fallos
                        try:
                            cache.delete(self.fail_key)
                        except Exception:
                            logger.debug("No se pudo borrar fail_key tras éxito para %s", self.name)
                    return result
            return _wrapped

        # Soporta usage directo: breaker(func) y decorator: @breaker()
        if callable(func):
            return decorator(func)
        return decorator

    # Métodos de ayuda para inspección/monitoring
    def stats(self) -> dict:
        """
        Retorna un dict con información actual del breaker.
        Útil para endpoints de health/monitoring.
        """
        try:
            state = self.get_state()
            fails = cache.get(self.fail_key) or 0
            open_at = cache.get(self.open_at_key) or None
            return {
                "name": self.name,
                "state": state,
                "fails": int(fails),
                "open_at": int(open_at) if open_at else None,
                "max_failures": self.max_failures,
                "reset_timeout": self.reset_timeout,
            }
        except Exception:
            logger.exception("Error leyendo stats del circuit %s", self.name)
            return {
                "name": self.name,
                "state": "unknown",
                "fails": None,
                "open_at": None,
                "max_failures": self.max_failures,
                "reset_timeout": self.reset_timeout,
            }
