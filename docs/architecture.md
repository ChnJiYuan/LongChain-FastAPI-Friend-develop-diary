## Repository layout
LongChain-FastAPI-Friend/
  backend/
    main.py                FastAPI entry
    config.py              Model configs and GPU detection
    routers/
      chat.py              Text chat API
      memory.py            User memory APIs (profile, recall)
      image.py             Image upload and analysis
      generate.py          Image generation API
    chains/
      conversation.py      LangChain conversational chain
      rag.py               RAG pipeline using chat logs
      vision.py            Image understanding chain
      agent.py             Tool-calling chain
      multimodal.py        Text + image combined reasoning
    gpu_inference/         CUDA-accelerated models
      local_llm.py         Local LLM running on GPU
      sd_generator.py      Stable Diffusion image generator
      utils.py             GPU utilities and model loaders
    db/
      chroma/              Vector store for RAG
      user_profile.json    Long-term memory data
    utils/
      image_utils.py       Image preprocessing helpers
      prompts.py           Prompt templates
      logging.py           Structured logging setup
  docs/
    architecture.md        High-level design
    development-diary.md   Build notes and experiments
    prompt-design.md       Prompting strategies
  examples/
    api-demo.ipynb         Demo notebook
  tests/
    README.md              Test plan and coverage notes
  frontend/               React UI scaffold (src/, public/, package.json)