from typing import List


def build_chat_prompt(
    system_prompt: str,
    memori_context: str,
    milvus_chunks: List[str],
    user_message: str,
) -> str:
    hits = "\n".join(f"- {chunk}" for chunk in milvus_chunks) or "No similar history."
    return (
        f"{system_prompt}\n\n"
        "Structured memory (Memori):\n"
        f"{memori_context}\n\n"
        "Similar chat snippets (Milvus):\n"
        f"{hits}\n\n"
        "User:\n"
        f"{user_message}"
    )


SYSTEM_PROMPT = (
    "You are a friendly AI companion. Blend structured facts (Memori) and similar chat "
    "history (Milvus) to answer concisely while keeping context consistent."
)
