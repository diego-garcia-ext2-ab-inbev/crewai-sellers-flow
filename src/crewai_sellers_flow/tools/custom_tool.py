from typing import Type
import json
import os

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class JSONTool(BaseTool):
    name: str = "JSON Reader Tool"
    description: str = (
        "Ferramenta para ler e retornar o conteúdo de um arquivo JSON."
    )

    def _run(self) -> dict:
        try:          
            # Lê o arquivo JSON
            with open('2025_06_11_03_26_fill_rate_data_full.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            # Retorna o conteúdo formatado
            # return json.dumps(data, indent=4, ensure_ascii=False)
            return data
            
        except json.JSONDecodeError:
            return "Erro: O arquivo não contém um JSON válido"
        except Exception as e:
            return f"Erro ao ler o arquivo: {str(e)}"
