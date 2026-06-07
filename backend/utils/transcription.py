import os
import whisper

class TranscriptionService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            # We use the 'small' model for better accuracy than 'base'.
            # Note: This will download the model on first use (~460MB).
            cls._model = whisper.load_model("small")
        return cls._model

    @classmethod
    def transcribe(cls, file_path):
        """
        Transcribes the audio file at the given path.
        Returns the transcript text.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        model = cls.get_model()
        result = model.transcribe(file_path, language="en", fp16=False, temperature=0.0)
        return result.get("text", "").strip()

# Singleton instance
transcription_service = TranscriptionService()
