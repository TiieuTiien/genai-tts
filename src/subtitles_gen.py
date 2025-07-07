import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def create_srt_prompt():
    """Creates prompt for subtitles generation."""
    return """Your task is to create a transcript of an audio file in the SRT (SubRip Subtitle) format.

            The SRT format for each entry is very specific. Follow this structure exactly:

            <INDEX>
            <START_TIME> --> <END_TIME>
            <SUBTITLE_TEXT>

            (A blank line separates each entry)

            ---

            **DETAILED INSTRUCTIONS:**

            1.  **INDEX:** A sequential number starting from 1 for each subtitle block.
            2.  **TIMESTAMPS:**
                * The format must be strictly `HH:MM:SS,ms` (e.g., `00:05:23,500`).
                * **Crucially, always include two digits for the hour (`HH`), even if it is zero.** For example, a timestamp at 3 minutes and 31 seconds must be written as `00:03:31,100`, not `03:31,100`.
                * `START_TIME` is when the subtitle should appear.
                * `END_TIME` is when the subtitle should disappear.
                * Timestamps should not overlap.
            3.  **SUBTITLE TEXT:**
                * **IMPORTANT: Each subtitle line must be short, around 10-15 words or not exceeds 60 characters.** This is to ensure it displays correctly on screen.
                * The text should be a clean transcription of the speech.
                * If a sentence is long, you MUST split it across multiple subtitle blocks with appropriate timestamps.
                * For non-speech sounds, describe them in parentheses on their own line. For example: `(upbeat theme music)` or `(phone ringing)`.
            4.  **GENERAL RULES:**
                * Do not use any Markdown formatting (like **bold** or *italics*).
                * Ensure spelling, especially for proper nouns, is accurate based on context.
                * Conclude the entire transcript with `[END OF TRANSCRIPT]` as the final subtitle text.

            ---

            **EXAMPLE OF CORRECT OUTPUT:**

            1
            00:00:01,250 --> 00:00:03,800
            Hey everyone, and welcome back to the show.

            2
            00:00:04,100 --> 00:00:05,500
            (intro jingle plays)

            3
            00:01:17,500 --> 00:01:24,420
            Today we have a very special topic to discuss.

            ...
            
            10
            00:20:386 --> 00:20:386
            [END OF TRANSCRIPT]

            ---

            Now, please generate the SRT transcript for the provided audio.
            """

def upload_audio_file(client, file_path):
    """Uploads an audio file to the Vertex AI API.
    
    Args:
        client: The Vertex AI client
        file_path: Path to the audio file
        
    Returns:
        The uploaded file object
    """
    uploaded_file = client.files.upload(file=file_path)
    print("Upload completed. File name: ", uploaded_file)
    return uploaded_file


def save_subtitles(content, output_path):
    """Saves the subtitles to a file.
    
    Args:
        content: The subtitle content
        output_path: Path to save the subtitles
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Subtitle saved to {output_path}")
    
    
def generate_subtitles(audio_path, output_path, model="gemini-2.5-flash"):
    """Generates subtitles for an audio file.
    
    Args:
        audio_path: Path to the audio file
        output_path: Path to save the subtitles
        model: The model to use for generation
    """
    client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
    
    # Create the prompt
    prompt = create_srt_prompt()
    
    # Upload the audio file
    uploaded_file = upload_audio_file(client, audio_path)
    
    response = client.models.generate_content(
        model=model,
        contents=[prompt, uploaded_file],
    )
    
    # Save the output
    save_subtitles(response.text, output_path)
    
    

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Define file paths
    audio_path  = "./output/my_audio.wav"
    output_path = "../content/subtitles/sample.srt"
    
    # Generate subtitles
    generate_subtitles(audio_path, output_path)