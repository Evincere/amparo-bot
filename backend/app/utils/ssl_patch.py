import urllib3
import httpx
import requests
import logging

logger = logging.getLogger(__name__)

def apply_ssl_bypass():
    """
    Aplica monkeypatches a httpx y requests para deshabilitar la verificación de SSL.
    Necesario para entornos con proxies corporativos que usan certificados self-signed.
    """
    logger.info("Aplicando parches de bypass SSL (bypass corporativo)...")
    
    # Deshabilitar advertencias de urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Patch httpx
    _original_httpx_init = httpx.Client.__init__
    _original_httpx_async_init = httpx.AsyncClient.__init__

    def _patched_httpx_init(self, *args, **kwargs):
        kwargs['verify'] = False
        return _original_httpx_init(self, *args, **kwargs)

    def _patched_httpx_async_init(self, *args, **kwargs):
        kwargs['verify'] = False
        return _original_httpx_async_init(self, *args, **kwargs)

    httpx.Client.__init__ = _patched_httpx_init
    httpx.AsyncClient.__init__ = _patched_httpx_async_init

    # Patch requests
    _original_request = requests.Session.request
    def _patched_request(self, method, url, *args, **kwargs):
        kwargs['verify'] = False
        return _original_request(self, method, url, *args, **kwargs)
    requests.Session.request = _patched_request
    
    logger.info("SSL bypass aplicado correctamente.")
