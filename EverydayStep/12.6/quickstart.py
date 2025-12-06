import os

from memori import Memori
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup OpenAI (read key from env to avoid committing secrets)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Set OPENAI_API_KEY in your environment before running this demo.")
client = OpenAI(api_key=api_key)

# Setup SQLite
engine = create_engine("sqlite:///memori.db")
Session = sessionmaker(bind=engine)

# Setup Memori - that's it!
mem = Memori(conn=Session).openai.register(client)
mem.attribution(entity_id="user-123", process_id="my-app")
mem.config.storage.build()

# First conversation - establish facts
response1 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "My favorite color is blue"}],
)
print(response1.choices[0].message.content)

# Second conversation - Memori recalls context automatically
response2 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What's my favorite color?"}],
)
print(response2.choices[0].message.content)  # AI remembers: "blue"!
