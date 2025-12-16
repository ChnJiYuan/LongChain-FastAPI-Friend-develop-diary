from pydantic import BaseModel, Field


class ImageRequest(BaseModel):
  prompt: str = Field(..., min_length=1, max_length=2000)
  negative_prompt: str | None = None
  steps: int = Field(20, ge=1, le=100)
  width: int = Field(512, ge=64, le=2048)
  height: int = Field(512, ge=64, le=2048)
  provider: str | None = Field(
      None, description="local | cloud | auto; overrides IMAGE_PROVIDER if set"
  )


class ImageResponse(BaseModel):
  image_base64: str
  provider: str
  trace_id: str
  file_path: str | None = Field(None, description="Absolute file path of the saved image, if persisted to disk")
