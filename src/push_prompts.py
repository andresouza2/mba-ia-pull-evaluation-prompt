"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def build_prompt_identifier(base_name: str) -> str:
    """Monta o identificador do prompt no formato {username}/nome quando possível."""
    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if username:
        return f"{username}/{base_name}"
    return base_name


def build_readme(prompt_name: str, prompt_data: dict) -> str:
    """Gera readme do prompt para facilitar rastreabilidade no Hub."""
    techniques = prompt_data.get("techniques_applied", [])
    tags = prompt_data.get("tags", [])
    created_at = prompt_data.get("created_at", "")
    version = prompt_data.get("version", "")

    lines = [
        f"# {prompt_name}",
        "",
        prompt_data.get("description", ""),
        "",
        "## Metadados",
        f"- Version: {version}",
        f"- Created at: {created_at}",
        f"- Tags: {', '.join(tags) if tags else 'n/a'}",
        f"- Techniques: {', '.join(techniques) if techniques else 'n/a'}",
    ]
    return "\n".join(lines)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_prompt = prompt_data["system_prompt"]
        user_template = prompt_data.get('user_prompt_template', '{bug_report}')
        description = prompt_data.get("description")
        tags = prompt_data.get("tags")
        examples = prompt_data.get("examples", [])

        messages = [("system", system_prompt)]

        for example in examples:
            example_input = example.get("input", "")
            example_output = example.get("output", "")
            messages.append(("human", example_input))
            messages.append(("ai", example_output))

        messages.append(("user", user_template))

        prompt = ChatPromptTemplate.from_messages(messages)

        hub.push(
            prompt_name,
            prompt
            , new_repo_is_public=True
            , new_repo_description=description
            , tags=tags
        )

        print(f"✅ Prompt '{prompt_name}' publicado com sucesso!")
        return True

    except Exception as e:
        error_text = str(e)
        if "Nothing to commit" in error_text or "409 Client Error" in error_text:
            print(f"ℹ️ Prompt '{prompt_name}' já está publicado e não houve mudanças para enviar.")
            return True

        print(f"❌ Erro ao publicar prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    prompt_name = "andre-dev/bug_to_user_story_v2"
    print_section_header("PUSH DE PROMPT PARA LANGSMITH")

    prompt_path = "prompts/bug_to_user_story_v2.yml"
    data = load_yaml(prompt_path)
    prompt_data = data["bug_to_user_story_v2"]

    # print(prompt_data)


    if not prompt_data:
        return 1

    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("❌ Prompt inválido:")
        for err in errors:
            print(f"  - {err}")
        return 1

    success = push_prompt_to_langsmith(prompt_name, prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
