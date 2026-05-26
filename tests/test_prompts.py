"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_prompt_data() -> dict:
    """Retorna o dicionário do prompt v2."""
    prompts = load_prompts(str(PROMPT_FILE))
    assert prompts is not None, "Falha ao carregar YAML de prompts"
    assert PROMPT_KEY in prompts, f"Chave '{PROMPT_KEY}' não encontrada no YAML"
    return prompts[PROMPT_KEY]


class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompt_data = get_prompt_data()
        assert "system_prompt" in prompt_data
        assert isinstance(prompt_data["system_prompt"], str)
        assert prompt_data["system_prompt"].strip() != ""

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompt_data = get_prompt_data()
        system_prompt = prompt_data.get("system_prompt", "")

        role_markers = [
            "você é",
            "product manager",
            "senior product manager",
            "assistente",
            "especialista",
        ]

        assert any(marker in system_prompt.lower() for marker in role_markers), (
            "system_prompt deve definir explicitamente uma persona"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt_data = get_prompt_data()
        system_prompt = prompt_data.get("system_prompt", "").lower()
        user_prompt = prompt_data.get("user_prompt", "").lower()

        mentions_markdown = "markdown" in system_prompt or "markdown" in user_prompt
        mentions_user_story_format = (
            "como <persona>, eu quero <objetivo>, para que <benefício>." in system_prompt
            or "user story" in system_prompt
        )

        assert mentions_markdown or mentions_user_story_format, (
            "Prompt deve exigir Markdown ou padrão explícito de User Story"
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt_data = get_prompt_data()
        system_prompt = prompt_data.get("system_prompt", "").lower()

        has_few_shot_label = "few-shot" in system_prompt or "few shot" in system_prompt
        has_input_output_pattern = (
            "entrada (bug_report):" in system_prompt
            and "saída esperada:" in system_prompt
        )
        example_count = system_prompt.count("exemplo ")

        assert has_few_shot_label
        assert has_input_output_pattern
        assert example_count >= 2, "Prompt deve conter pelo menos 2 exemplos few-shot"

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_data = get_prompt_data()
        all_text = "\n".join([
            prompt_data.get("description", ""),
            prompt_data.get("system_prompt", ""),
            prompt_data.get("user_prompt", ""),
        ])
        assert "[TODO]" not in all_text

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompt_data = get_prompt_data()

        # Garante consistência com validação estrutural usada no projeto.
        is_valid, errors = validate_prompt_structure(prompt_data)
        assert is_valid, f"Estrutura inválida: {errors}"

        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list)
        assert len(techniques) >= 2, "Mínimo de 2 técnicas em techniques_applied"
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])