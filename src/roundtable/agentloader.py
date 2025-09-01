from pathlib import Path
import yaml
from pydantic import BaseModel
from typing import Optional


class AgentSpec(BaseModel):
    """Specification for an AI agent.

    Args:
        name (str): The name of the agent (e.g. Musk).
        instructions (str): The instructions/prompt for the agent.
        model (str): The model to use for the agent.
        handoff (str, Optional): Handoff description for the agent. Defaults to None.
    """

    name: str
    instructions: str
    model: str
    handoff: Optional[str] = None


def load_agent_spec(path: str) -> AgentSpec:
    """Load an agent specification from a YAML file.

    Args:
        path (str): Path to the YAML file.
        Returns:
        AgentSpec: The loaded agent specification.
    """
    raw = yaml.safe_load(Path(path).read_text())
    return AgentSpec(**raw)
