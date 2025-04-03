import os
import sys
import json
from typing import Dict
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from manim import logger 

from manim_voiceover.helper import (
    create_dotenv_file,
    remove_bookmarks,
)
from manim_voiceover.services.base import SpeechService

import requests
import base64


load_dotenv(find_dotenv(usecwd=True))


class SarvamTTS(SpeechService):
    """
    Speech service class for Sarvam TTS Service. Refer to their documentation: https://docs.sarvam.ai/api-reference-docs/endpoints/text-to-speech
    Explore sarvam documentation for more voices and models.
    """
    
    def __init__(
        self, 
        voice: str = "meera",
        model: str = "bulbul:v1",
        transcription_model="base",
        **kwargs
    ):
        """
        Args:
            voice (str, optional): The voice to use. See the Sarvam documentation for voices available.
            model (str, optional): The TTS model to use. 
                Available Options: ['bulbul:v1', 'bulbul:2']
        """
        self.voice = voice
        self.model = model

        SpeechService.__init__(self, transcription_model=transcription_model, **kwargs)

    def generate_from_text(
        self, text, cache_dir = None, path = None, **kwargs
    ):
        if cache_dir is None:
            cache_dir = self.cache_dir

        speed = kwargs.get("speed", 1.0)
        lang = kwargs.get("language_code", "en-IN")
        loud = kwargs.get("loud", 1.55)


        if not (0.25 <= speed <= 2.0):
            raise ValueError("The speed must be between 0.25 to 4.0")
        input_text = remove_bookmarks(text)

        input_data = {
            "inputs": [input_text],
            "target_language_code": lang,
            "speaker": self.voice,
            "pitch": 0,
            "pace": speed,
            "loudness": 1.55,
            "speech_sample_rate": 8000,
            "enable_preprocessing": True,
            "model": self.model
        }

        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            return cached_result
        
        if path is None:
            audio_path = self.get_audio_basename(input_data) + ".mp3"
        else:
            audio_path = path

        if os.getenv("SARVAM_API_KEY") is None or os.getenv("SARVAM_API_URL") is None:
            create_dotenv_file()

        headers = {
            "API-Subscription-Key": os.getenv("SARVAM_API_KEY"),
            "Content-Type": "application/json"
        }

        proxies = {
            "http": None,
            "https": None
        }

        response = requests.request("POST", os.getenv("SARVAM_API_URL"), json=input_data, headers=headers, proxies=proxies)
        json_response = json.loads(response.text)

        self._save_to_file(json_response, str(Path(cache_dir) / audio_path))

        json_dict = {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path
        }

        return json_dict
    
    def _save_to_file(self, response: Dict, file_path):
        base64_decoded = base64.b64decode(response['audios'][0])
        with open(str(Path(file_path)), "wb") as audio_file:
            audio_file.write(base64_decoded)
