from abc import ABC, abstractmethod

class LLMService(ABC):
    """Interfaz base para cualquier proveedor LLM."""

    @abstractmethod
    async def get_summary(self, leads: list[dict], idioma: str = "es") -> str:
        raise NotImplementedError