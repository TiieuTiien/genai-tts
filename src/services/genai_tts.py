# To run this code you need to install the following dependencies:
# pip install google-genai

import mimetypes
import os
import pathlib
import shutil
import struct
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to: {file_name}")

def generate_audio_from_text(text_file_path, output_path, voice_name="Leda", model="gemini-2.5-flash-preview-tts"):
    client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY_TTS'))

    model = model
    filepath = pathlib.Path(text_file_path)

    instruction = "Read this novel in a fluent, natural voice with a moderate, soothing pace. Pause naturally at commas and periods. Gently emphasize dialogue and key moments while maintaining a peaceful, warm tone for relaxation."
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=instruction),  # Instruction part
                types.Part.from_bytes(
                    data=filepath.read_bytes(),
                    mime_type='text/plain',
                ),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        response_modalities=[
            "audio",
        ],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=voice_name
                )
            )
        ),
    )

    file_index = 0
    all_audio_data = b""  # Combined audio data
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
            
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            chunk_data = inline_data.data
            
            # Convert to WAV if needed
            if inline_data.mime_type != "audio/wav":
                chunk_data = convert_to_wav(chunk_data, inline_data.mime_type)
            
            # Add to combined audio
            all_audio_data += chunk_data
            
            # Optionally save individual chunks for debugging
            # if save_chunks:
            #     chunk_path = f"{output_path}_chunk_{file_index}.wav"
            #     save_binary_file(chunk_path, chunk_data)
            #     file_index += 1
        else:
            print(chunk.text)
    
    # Save the final combined audio file
    if all_audio_data:
        save_binary_file(output_path, all_audio_data)
        backup_path = os.path.join(os.path.dirname(text_file_path), "backup", os.path.basename(text_file_path))
        shutil.move(text_file_path, backup_path)  # Ensure the file is saved correctly
        print(f"✅ Moved text file to: {backup_path}")
        return output_path
    else:
        print("❌ No audio data received")
        return None

def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    """Generates a WAV file header for the given audio data and parameters.

    Args:
        audio_data: The raw audio data as a bytes object.
        mime_type: Mime type of the audio data.

    Returns:
        A bytes object representing the WAV file header.
    """
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters["bits_per_sample"]
    sample_rate = parameters["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size

    # http://soundfile.sapp.org/doc/WaveFormat/

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",          # ChunkID
        chunk_size,       # ChunkSize (total file size - 8 bytes)
        b"WAVE",          # Format
        b"fmt ",          # Subchunk1ID
        16,               # Subchunk1Size (16 for PCM)
        1,                # AudioFormat (1 for PCM)
        num_channels,     # NumChannels
        sample_rate,      # SampleRate
        byte_rate,        # ByteRate
        block_align,      # BlockAlign
        bits_per_sample,  # BitsPerSample
        b"data",          # Subchunk2ID
        data_size         # Subchunk2Size (size of audio data)
    )
    return header + audio_data

def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
    """Parses bits per sample and rate from an audio MIME type string.

    Assumes bits per sample is encoded like "L16" and rate as "rate=xxxxx".

    Args:
        mime_type: The audio MIME type string (e.g., "audio/L16;rate=24000").

    Returns:
        A dictionary with "bits_per_sample" and "rate" keys. Values will be
        integers if found, otherwise None.
    """
    bits_per_sample = 16
    rate = 24000

    # Extract rate from parameters
    parts = mime_type.split(";")
    for param in parts: # Skip the main type part
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate_str = param.split("=", 1)[1]
                rate = int(rate_str)
            except (ValueError, IndexError):
                # Handle cases like "rate=" with no value or non-integer value
                pass # Keep rate as default
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass # Keep bits_per_sample as default if conversion fails

    return {"bits_per_sample": bits_per_sample, "rate": rate}

if __name__ == "__main__":
    generate_audio_from_text(
        text_file_path="../content/contents/sample1.txt",
        output_path="output/my_audio.wav"  # You control the exact path
    )

"""
+----------+
|  VOICES  |
+----------+
Achernar 
Aoede 
Autonoe 
Callirrhoe 
Despina 
Erinome 
Gacrux 
Kore 
Laomedeia 
Leda 
Sulafat 
Vindemiatrix 
Zephyr 
"""