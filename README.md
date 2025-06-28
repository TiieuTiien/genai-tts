# GenAI TTS Video Pipeline

This project creates complete videos with AI-generated audio and subtitles using Google's GenAI TTS technology.

## Pipeline Overview

The system works in three sequential steps:

1. **Audio Generation** (`genai_tts.py`) - Converts text to speech using Google's GenAI TTS
2. **Subtitle Generation** (`subtitles_gen.py`) - Creates SRT subtitles from the generated audio
3. **Video Composition** (`editor.py`) - Combines audio, subtitles, and visuals into a final video

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Google API key in a `.env` file:
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

3. Install FFmpeg (required for video processing):
```bash
brew install ffmpeg  # macOS
```

## Usage

### Simple Usage (Recommended)

Run the complete pipeline with default settings:

```bash
cd src
python main.py
```

### Advanced Usage

Customize the video creation process:

```bash
python main.py \
  --input-text "../content/contents/my_story.txt" \
  --image "../content/images/background.jpg" \
  --output-dir "../content/output" \
  --project-name "my_video" \
  --voice "Gacrux" \
  --dimensions "1920x1080" \
  --fps 24
```

### Available Command Line Options

- `--input-text`: Path to input text file (default: `../content/contents/sample1.txt`)
- `--image`: Path to background image (default: `../content/images/part1.jpg`)
- `--output-dir`: Output directory (default: `../content/results`)
- `--project-name`: Name prefix for files (default: `complete_video`)
- `--voice`: TTS voice name (default: `Gacrux`)
- `--duration`: Video duration in seconds (default: use audio duration)
- `--dimensions`: Video dimensions as WIDTHxHEIGHT (default: `1920x1080`)
- `--fps`: Frames per second (default: `24`)

## Individual Module Usage

You can also use each module separately:

### Generate Audio Only
```python
from genai_tts import generate_audio_from_text

generate_audio_from_text(
    text_file_path="my_text.txt",
    output_path="my_audio.wav",
    voice_name="Gacrux"
)
```

### Generate Subtitles Only
```python
from subtitles_gen import generate_subtitles

generate_subtitles(
    audio_path="my_audio.wav",
    output_path="my_subtitles.srt"
)
```

### Create Video Only
```python
from editor import create_video_with_subtitles

create_video_with_subtitles(
    image_path="background.jpg",
    srt_path="subtitles.srt",
    audio_path="audio.wav",
    output_path="final_video.mp4"
)
```

## Project Structure

```
genai-tts/
├── src/
│   ├── main.py              # Main orchestrator script
│   ├── genai_tts.py         # Audio generation module
│   ├── subtitles_gen.py     # Subtitle generation module
│   └── editor.py            # Video composition module
├── content/
│   ├── contents/            # Input text files
│   ├── images/              # Background images
│   ├── fonts/               # Font files for subtitles
│   ├── audios/              # Generated audio files
│   ├── subtitles/           # Generated subtitle files
│   └── results/             # Final video outputs
├── requirements.txt
└── README.md
```

## Output Files

The pipeline generates three main files:
- `{project_name}_audio.wav` - Generated audio
- `{project_name}_subtitles.srt` - Generated subtitles
- `{project_name}_final.mp4` - Complete video with audio and subtitles

## Requirements

- Python 3.8+
- Google GenAI API key
- FFmpeg
- MoviePy
- PIL/Pillow for image processing

## Troubleshooting

### Font Issues
If you encounter font-related errors, make sure you have the Arial Unicode font file in the `content/fonts/` directory, or modify the font path in `editor.py`.

### API Key Issues
Ensure your `.env` file is in the project root and contains a valid Google API key.

### FFmpeg Issues
Make sure FFmpeg is installed and accessible in your system PATH.
