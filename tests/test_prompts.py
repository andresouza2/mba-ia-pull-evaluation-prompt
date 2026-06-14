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
        data = yaml.safe_load(f)
        return next(iter(data.values()))  # Retorna o conteúdo do prompt (assumindo que há apenas um)

class TestPrompts:

    PROMPT_PATH = "prompts/bug_to_user_story_v2.yml"

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompt = load_prompts(self.PROMPT_PATH)
        assert "system_prompt" in prompt
        assert prompt["system_prompt"].strip() != ""

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""

        prompt = load_prompts(self.PROMPT_PATH)
        system_prompt = prompt.get("system_prompt", "").lower()
        
        role_keywords = ["você é", "you are", "product manager", "product owner"]

        assert any(k in system_prompt for k in role_keywords), \
            "O prompt deve definir uma persona clara"

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        
        prompt = load_prompts(self.PROMPT_PATH)
        
        system_prompt = prompt.get("system_prompt", "").lower()

        format_keywords = [
            "user story", 
            "como", 
            "markdown",
            "formato",
            "estrutura"
        ]

        assert any(k in system_prompt for k in format_keywords), \
            "O prompt deve mencionar claramente o formato esperado para a resposta (ex: 'Responda no formato de User Story ou Markdown')."

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        
        prompt = load_prompts(self.PROMPT_PATH)
        examples = prompt.get("examples", [])

        assert isinstance(examples, list)
        assert len(examples) >= 1, "É esperado pelo menos 1 exemplo few-shot"

        example = examples[0]
        assert "input" in example
        assert "output" in example

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        
        prompt = load_prompts(self.PROMPT_PATH)
        
        text = yaml.dump(prompt)
        
        assert "TODO" not in text, "Prompt ainda contém TODOs"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        
        prompt = load_prompts(self.PROMPT_PATH)
        
        techniques = prompt.get("techniques", [])

        assert isinstance(techniques, list)
        
        assert len(techniques) >= 2, \
            "Prompt deve listar pelo menos 2 técnicas de prompt engineering"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])