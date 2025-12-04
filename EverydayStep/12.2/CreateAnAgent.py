from langchain.agents import create_agent
from langchain_ollama import ChatOllama

def get_weather(city:str) -> str:
    """Gets the weather for a given city."""
    return f"The weather in {city} is sunny."


# Use a local Ollama chat model (e.g., `ollama run llama3` must be available).
# Adjust the model name if you pulled a different one locally.
agent = create_agent(
    # Use a model that supports tool calling; Ollama's llama3.1 has function calling enabled.
    model=ChatOllama(model="llama3.1:8b"),
    tools=[get_weather],
    system_prompt="You're a helpful assistant that provides weather information.",
)

#Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather like in Sydney?"}]}
)
