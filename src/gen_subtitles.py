"""
Example usage of the complete GenAI TTS video pipeline.

This script demonstrates how to create a complete video from a text file
using the modular approach.
"""

import os
from main import generate_audio_step, generate_subtitles_step, setup_environment

def gen_subtitles_modules():
    """Example of using individual modules separately."""
    print("🎬 Example: Individual module usage")
    
    # Set up environment
    # setup_environment()    
    results_dir = "../results/MDSXQLNPLGNC/"
    input_dir = os.path.join(results_dir, "texts")
    audio_dir = os.path.join(results_dir, "audios")
    srt_dir   = os.path.join(results_dir, "subtitles")

    print("Generating subtitles...")
    generate_subtitles_step(
        audio_dir=audio_dir,
        srt_dir=srt_dir,
        max_workers=10,
        delay_seconds=120
    )

    print(f"✅ Generate subtitles success: {results_dir}")

if __name__ == "__main__":
    print("🚀 GenAI subtitles creation Pipeline\n")

    try:
        # Run individual modules example
        gen_subtitles_modules()
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
