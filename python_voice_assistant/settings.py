from pydantic import BaseSettings


class Settings(BaseSettings):
    # LISTENER ENVS
    models_path: str
    recognizing_model_path: str

    # SPEAKER ENVS
    language: str = "ru"
    model_id: str = "ru_v3"
    sample_rate: int = 48000
    speaker: str = "random"
    put_accent: bool = True
    put_yo: bool = True
    device_type: str = "cpu"
    repo_or_dir: str = "snakers4/silero-models"
    model: str = "silero_tts"

    # HELPER ENVS
    name: str = "Настя"
    gender: int = 1


settings = Settings(
    _env_file=".env",
    _env_file_encoding="utf-8",
)
