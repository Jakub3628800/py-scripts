#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
# "openai",
# ]
# ///

import os
import sys
import openai
import logging
import json
import subprocess
from pathlib import Path

# Set up logging
logger = logging.getLogger("transcribe")
handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Default to only showing warnings and errors
logger.setLevel(logging.WARNING)

def send_notification(title, message, debug=False):
    """Send desktop notification if debug is enabled"""
    if debug:
        try:
            subprocess.run(["notify-send", "-t", "3000", title, message], check=False)
        except Exception as e:
            logger.warning(f"Could not send notification: {e}")

def transcribe_audio(audio_file_path, debug=False, language=None, prompt=None,
                    temperature=0.0, timestamps=False):
    """Transcribe audio file using OpenAI Whisper API"""
    # Enable debug logging if requested
    if debug:
        logger.setLevel(logging.INFO)
        logger.info("Debug mode enabled")
        send_notification("Transcription Debug", "Debug mode enabled", debug)

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        send_notification("Transcription Error", "OPENAI_API_KEY not set", debug)
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    openai.api_key = api_key

    # Check if file exists
    audio_path = Path(audio_file_path)
    if not audio_path.exists():
        send_notification("Transcription Error", f"File {audio_file_path} not found", debug)
        logger.error(f"File {audio_file_path} not found")
        sys.exit(1)

    logger.info(f"Transcribing {audio_file_path}...")
    send_notification("Transcription Started", f"Processing {audio_path.name}", debug)

    if language:
        logger.info(f"Language hint: {language}")
    if prompt:
        logger.info(f"Using prompt: {prompt}")
    if temperature != 0.0:
        logger.info(f"Temperature: {temperature}")
    if timestamps:
        logger.info("Including timestamps")

    try:
        # Open the file in binary mode
        with open(audio_file_path, "rb") as audio_file:
            # Call the OpenAI Whisper API
            client = openai.OpenAI()
            logger.info("Sending request to OpenAI API...")
            send_notification("Transcription Progress", "Sending request to OpenAI API...", debug)

            # Prepare parameters
            params = {
                "model": "whisper-1",  # Best available Whisper model
                "file": audio_file,
                "response_format": "verbose_json" if timestamps else "text",
                "temperature": temperature
            }

            # Add optional parameters if provided
            if language:
                params["language"] = language
            if prompt:
                params["prompt"] = prompt

            response = client.audio.transcriptions.create(**params)

        # Process and output the transcription
        send_notification("Transcription Complete", "Successfully transcribed audio", debug)

        if timestamps:
            # For json response, there is a text field and other timestamp data
            # Print the full transcription text to stdout
            result = json.loads(response)
            print(result["text"])
        else:
            # For text response, the response is already the text
            print(response)

        return response

    except openai.OpenAIError as e:
        send_notification("Transcription Error", f"OpenAI API error: {str(e)[:50]}...", debug)
        logger.error(f"Error with OpenAI API: {e}")
        sys.exit(1)
    except Exception as e:
        send_notification("Transcription Error", f"Error: {str(e)[:50]}...", debug)
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Transcribe audio using OpenAI Whisper API")
    parser.add_argument("audio_file", help="Path to the audio file to transcribe")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--language", help="Specify language code (e.g., 'en', 'fr', 'es')")
    parser.add_argument("--prompt", help="Provide context to guide the transcription")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="Temperature for sampling. Higher values like 0.2-0.8 make output more random")
    parser.add_argument("--timestamps", action="store_true",
                        help="Include timestamps in the output")

    args = parser.parse_args()

    transcribe_audio(args.audio_file, debug=args.debug, language=args.language,
                    prompt=args.prompt, temperature=args.temperature,
                    timestamps=args.timestamps)
