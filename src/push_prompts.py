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
    prompt_identifier = build_prompt_identifier(prompt_name)

    template = ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("human", prompt_data["user_prompt"]),
    ])

    tags = list(prompt_data.get("tags", []))
    techniques = prompt_data.get("techniques_applied", [])
    tags.extend([f"technique:{t}" for t in techniques])
    tags = sorted(set(tags))

    client = Client()
    try:
        result = client.push_prompt(
            prompt_identifier,
            object=template,
            is_public=True,
            description=prompt_data.get("description", ""),
            readme=build_readme(prompt_identifier, prompt_data),
            tags=tags,
        )

        print(f"✅ Prompt publicado publicamente com sucesso: {prompt_identifier}")
        print(f"🔗 URL/Commit: {result}")
        if "/" not in prompt_identifier:
            print(
                "⚠️ USERNAME_LANGSMITH_HUB não definido. "
                "Configure para usar formato {username}/prompt_name."
            )
        return True
    except Exception as e:
        message = str(e)
        if "Cannot create a public prompt" in message:
            print("⚠️ Hub handle público não configurado. Tentando salvar prompt como PRIVADO...")
            try:
                result = client.push_prompt(
                    prompt_identifier,
                    object=template,
                    is_public=False,
                    description=prompt_data.get("description", ""),
                    readme=build_readme(prompt_identifier, prompt_data),
                    tags=tags,
                )
                print(f"✅ Prompt salvo com sucesso (privado): {prompt_identifier}")
                print(f"🔗 URL/Commit: {result}")
                print(
                    "ℹ️ Para deixar público: crie seu Hub handle em "
                    "https://smith.langchain.com/prompts e rode o script novamente."
                )
                return True
            except Exception as fallback_error:
                print(f"❌ Erro no fallback privado para '{prompt_name}': {fallback_error}")
                return False

        print(f"❌ Erro ao publicar prompt '{prompt_name}': {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    _, errors = validate_prompt_structure(prompt_data)

    if not prompt_data.get("user_prompt", "").strip():
        errors.append("Campo obrigatório faltando ou vazio: user_prompt")

    if "{bug_report}" not in prompt_data.get("user_prompt", ""):
        errors.append("user_prompt deve conter placeholder {bug_report}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS (v2)")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    prompts_path = Path("prompts/bug_to_user_story_v2.yml")
    data = load_yaml(str(prompts_path))
    if not data:
        print(f"❌ Não foi possível carregar: {prompts_path}")
        return 1

    prompt_name = "bug_to_user_story_v2"
    prompt_data = data.get(prompt_name)
    if not prompt_data:
        print(f"❌ Chave '{prompt_name}' não encontrada no YAML")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido. Corrija os erros abaixo:")
        for err in errors:
            print(f"   - {err}")
        return 1

    print(f"📄 Arquivo carregado: {prompts_path}")
    print(f"🏷️ Prompt: {prompt_name}")
    print(f"🧪 Técnicas: {', '.join(prompt_data.get('techniques_applied', []))}")

    success = push_prompt_to_langsmith(prompt_name, prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
