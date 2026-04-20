from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError
from app.core.settings import settings
from app.services.llm.base import LLMService

SYSTEM_PROMPT = """
Eres un analista de marketing y ventas especializado en embudos de captación digital
para creadores de contenido y negocios online. Tu función es analizar bases de datos
de leads y generar informes ejecutivos claros, accionables y orientados a resultados.

Al recibir un conjunto de leads, siempre debes:
1. Identificar patrones en las fuentes de captación y su rendimiento relativo.
2. Evaluar la calidad del pipeline según presupuesto declarado y productos de interés.
3. Detectar anomalías, oportunidades o riesgos en los datos.
4. Emitir recomendaciones ejecutivas priorizadas por impacto potencial.

Formato de respuesta obligatorio:
- Usa secciones claras con títulos en negrita.
- Sé directo y conciso. Nada de relleno.
- Las recomendaciones deben ser específicas y ejecutables, no genéricas.
- Si los datos son insuficientes para una conclusión, indícalo explícitamente.

Tono: profesional, analítico, orientado a negocio.
""".strip()


class OpenAIClient(LLMService):

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.AI_API_KEY)
        self._model = settings.AI_MODEL  # e.g. "gpt-4o-mini"

    async def get_summary(self, leads: list[dict], idioma: str = "es") -> str:
        user_prompt = self._build_user_prompt(leads, idioma)
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=800,
            )
            content = response.choices[0].message.content
            if content is None:
                raise LLMServiceError("La respuesta del modelo IA está vacía o malformada.")
            return content.strip()

        except RateLimitError:
            raise LLMServiceError("Límite de requests al proveedor IA alcanzado. Intenta más tarde.")
        except APIConnectionError:
            raise LLMServiceError("No se pudo conectar con el proveedor IA.")
        except APIError as e:
            raise LLMServiceError(f"Error del proveedor IA: {e.message}")

    def _build_user_prompt(self, leads: list[dict], idioma: str) -> str:
        total = len(leads)
        fuentes = {}
        presupuestos = [l["presupuesto"] for l in leads if l.get("presupuesto")]
        promedio_presupuesto = round(sum(presupuestos) / len(presupuestos), 2) if presupuestos else "N/A"

        for lead in leads:
            fuente = lead.get("fuente", "desconocida")
            fuentes[fuente] = fuentes.get(fuente, 0) + 1

        fuentes_str = "\n".join(f"  - {k}: {v} leads" for k, v in sorted(fuentes.items(), key=lambda x: -x[1]))

        leads_detalle = "\n".join(
            f"  [{i+1}] {l.get('nombre')} | fuente: {l.get('fuente')} | "
            f"presupuesto: ${l.get('presupuesto', 'N/A')} | "
            f"producto: {l.get('producto_interes', 'N/A')} | "
            f"registrado: {l.get('created_at', 'N/A')}"
            for i, l in enumerate(leads[:50])  # cap para no exceder tokens
        )

        return f"""
Genera un informe ejecutivo en idioma: **{idioma}**.

## Resumen del dataset
- Total de leads analizados: {total}
- Promedio de presupuesto declarado: ${promedio_presupuesto} USD
- Distribución por fuente:
{fuentes_str}

## Detalle de leads
{leads_detalle}

{"[NOTA: Se muestran los primeros 50 leads de un total mayor.]" if total > 50 else ""}

Por favor genera el informe ejecutivo siguiendo el formato indicado.
""".strip()


class LLMServiceError(Exception):
    """Error controlado del servicio LLM."""
    pass