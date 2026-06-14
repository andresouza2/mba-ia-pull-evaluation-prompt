"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_ID = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = Path("prompts/raw_prompts.yml")


def pull_prompts_from_langsmith():
    """Faz pull do prompt no LangSmith Hub e retorna serialização"""
    print_section_header("Pulling prompt from LangSmith")

    # valida variáveis obrigatórias
    check_env_vars(
        ["LANGCHAIN_API_KEY"]
    )

    # pull do prompt
    prompt = hub.pull(PROMPT_ID)

    # serialização nativa do LangChain
    serialized_prompt = prompt.dict()

    return {
        "id": PROMPT_ID,
        "prompt": serialized_prompt,
    }


def main():
    """Função principal"""
    prompt_data = pull_prompts_from_langsmith()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    save_yaml(prompt_data, OUTPUT_PATH)

    print(f"\n✅ Prompt salvo com sucesso: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
