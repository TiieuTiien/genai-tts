import os
import shutil
from dotenv import load_dotenv
from google import genai
from services.srt_validate import validate_and_fix_srt, print_validation_results

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
                * The format must be strictly `HH:MM:SS,mmm` (e.g., `00:05:23,500`).
                * **Crucially, always include two digits for the hour (`HH`), even if it is zero.** 
                * For example, a timestamp at 3 minutes and 31 seconds must be written as `00:03:31,100`, not `03:31,100`.
                * Timestamps should not overlap.

            3.  **SUBTITLE TEXT & SPLITTING:**
                * The text should be a clean transcription of the speech.
                * **CRUCIAL RULE:** A single spoken sentence MUST be split across multiple, separate subtitle blocks if it is long. The goal is readability.
                * Each subtitle block should ideally contain only one line of text and not exceed 60 characters. A maximum of two short lines is acceptable only if absolutely necessary.
                * **Do not cram multiple lines of a long sentence into a single timestamped block.** 
                * Instead, create a new block with a new index and new timestamps for the next part of the sentence.

            ---
            
            **CRUCIAL EXAMPLE: CORRECTLY SPLITTING SENTENCES**

            This is the most important rule. A long sentence must be broken down into separate blocks.

            **INCORRECT (A single block with multiple lines):**
            ```
            9
            00:00:44,550 --> 00:00:49,900
            Lê Mạn nhếch mép cười, thầm nói:
            "Làn da của thân thể này giống y hệt
            kiếp trước của nàng,
            ```

            **CORRECT (The sentence is split into multiple blocks):**
            ```
            9
            00:00:44,550 --> 00:00:45,600
            Lê Mạn nhếch mép cười, thầm nói:

            10
            00:00:45,600 --> 00:00:47,132
            "Làn da của thân thể này giống y hệt

            11
            00:00:47,132 --> 00:00:49,900
            kiếp trước của nàng,
            ```

            ---

            **OVERALL FORMAT EXAMPLE:**

            This example shows the general structure, including non-speech sounds and the end-of-transcript marker.

            1
            00:00:01,250 --> 00:00:03,800
            Hey everyone, and welcome back to the show.

            2
            00:00:04,100 --> 00:00:05,500
            So today we have a very special topic to discuss.

            3
            00:00:17,500 --> 00:00:24,420
            We'll be diving deep into the world of AI and its impact on our daily lives.

            ...

            10
            00:00:20,386 --> 00:00:20,386
            Thanks for tuning in!

            ---
            
            **FINAL RULES:**
            * Do not use any Markdown formatting (like **bold** or *italics*) in the final SRT output.
            * Ensure spelling is accurate.

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
    # print("Upload completed. File name: ", uploaded_file)
    print("Upload completed. File name: ", uploaded_file.name)
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
    
    
def generate_subtitles(audio_file_path, srt_output_path, model="gemini-2.5-flash"):
    """Generates subtitles for an audio file.
    
    Args:
        audio_file_path: Path to the audio file
        srt_output_path: Path to save the subtitles
        model: The model to use for generation
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    # print(f"Using API key: {api_key}")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")
    client = genai.Client(api_key=api_key)
    
    # Create the prompt
    prompt = create_srt_prompt()
    
    # Upload the audio file
    uploaded_file = upload_audio_file(client, audio_file_path)

    response = client.models.generate_content(
        model=model,
        contents=[prompt, uploaded_file],
    )
    
    # Save the output
    save_subtitles(response.text, srt_output_path)
    done_path = os.path.join(os.path.dirname(audio_file_path), "done", os.path.basename(audio_file_path))
    shutil.move(audio_file_path, done_path)  # Ensure the file is saved correctly
    print(f"✅ Moved text file to: {done_path}")

    result = validate_and_fix_srt(srt_output_path)
    print_validation_results(result['validation_result'])
    
    if result['was_fixed']:
        print(f"    ✅ SRT file was fixed and saved at: {srt_output_path}")
    else:
        print(f"    ❌ SRT file was not fixed, original content remains unchanged.")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Define file paths
    results_dir = "../results/MDSXQLNPLGNC/"
    audio_dir = os.path.join(results_dir, "audios/Chương 1.wav")
    srt_dir   = os.path.join(results_dir, "subtitles/Chương 1.srt")
    
    # Generate subtitles
    generate_subtitles(audio_dir, srt_dir)