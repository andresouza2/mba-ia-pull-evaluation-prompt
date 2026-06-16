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

from langsmith import Client
from langchain_openai import OpenAI

load_dotenv()


def pull_prompts_from_langsmith():
    """Faz pull dos prompts do LangSmith Prompt Hub e salva localmente."""

    # Conectar ao LangSmith e puxar os prompts
    client = Client()
    try:
        print("Connecting to LangSmith...")
        prompt = client.pull_prompt("leonanluppi/bug_to_user_story_v1")
        model = OpenAI(model="gpt-4o-mini")
        chain = prompt | model

        result = chain.invoke({"bug_report": "O sistema trava quando o usuário tenta salvar um arquivo grande."})

        print(result)

        return

    except Exception as e:
        print(f"Error pulling prompts: {e}")
        sys.exit(1)

    # Salvar os prompts localmente
    output_path = Path("prompts/bug_to_user_story_v1.yml")
    try:
        print(f"Saving prompts to {output_path}...")
        save_yaml(result, output_path)
        print("Prompts saved successfully.")
    except Exception as e:
        print(f"Error saving prompts: {e}")
        sys.exit(1)


def main():
    """Função principal"""
    pull_prompts_from_langsmith()


if __name__ == "__main__":
    sys.exit(main())
