import asyncio

from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace, ModelSettings
from roundtable.agentloader import load_agent_spec
from dotenv import load_dotenv

load_dotenv()

"""
This script creates an AI-agent round-table. The moderator agent receives a user message and
then gathers responses from the round-table, calling them as tools. 
Inspired by: https://github.com/openai/openai-agents-python/blob/main/examples/agent_patterns/agents_as_tools.py
"""

agent_spec_files = [
    "buffett",
    "stoic",
    "thiel",
    "musk",
    "feynman",
    "ravikant",
    "synthesizer",
    "moderator",
]

agents = {}


for slug in agent_spec_files:
    spec = load_agent_spec(f"configs/agents/{slug}.yaml")
    if spec.name in agents:
        raise ValueError(f"Duplicate agent name: {spec.name}")
    agents[spec.name] = Agent(
        name=f"{spec.name}_agent",
        instructions=spec.instructions,
        handoff_description=spec.handoff,
        model=spec.model,
    )

assert "moderator" in agent_spec_files, "Moderator agent spec is required."
assert "synthesizer" in agent_spec_files, "Synthesizer agent spec is required."


agents["moderator"].tools = [
    agent.as_tool(
        tool_name=f"call_{agent.name}",
        tool_description=f"Call the {agent.name}",
    )
    for name, agent in agents.items()
    if name not in ["moderator", "synthesizer"]
]
agents["moderator"].model_settings = ModelSettings(
    parallel_tool_calls=True,
    tool_choice="required",
)


async def main():
    msg = input("What do you want to discuss? ")

    # Run the entire orchestration in a single trace
    with trace("moderator evaluator"):
        moderator_result = await Runner.run(agents["moderator"], msg)

        for item in moderator_result.new_items:
            if isinstance(item, MessageOutputItem):
                text = ItemHelpers.text_message_output(item)
                if text:
                    print(f"  - Moderator step: {text}")

        synthesizer_result = await Runner.run(
            agents["synthesizer"], moderator_result.to_input_list()
        )

    print(f"\n\nFinal response:\n{synthesizer_result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
