"""
Example usage of the complete GenAI TTS video pipeline.

This script demonstrates how to create a complete video from a text file
using the modular approach.
"""

import os
from main import generate_audio_step, generate_subtitles_step, setup_environment

def example_individual_modules():
    """Example of using individual modules separately."""
    print("🎬 Example: Individual module usage")
    
    # Set up environment
    # setup_environment()    
    results_dir = "../results/MDSXQLNPLGNC/"
    input_dir = os.path.join(results_dir, "texts")
    audio_dir = os.path.join(results_dir, "audios")
    srt_dir   = os.path.join(results_dir, "subtitles")

    # Step 1: Generate audio
    print("Generating audio...")
    generate_audio_step(
        input_dir=input_dir,
        output_dir=audio_dir,
        max_workers=10,
        delay_seconds=180,
        voice_name="Leda"
    )
    
    # Step 2: Generate subtitles
    # print("Generating subtitles...")
    # generate_subtitles_step(
    #     audio_dir=audio_dir,
    #     srt_dir=srt_dir,
    #     max_workers=10,
    #     delay_seconds=120
    # )
    
    # Step 3: Create video
    # print("Creating video...")
    # video_path = "../content/results/example_final.mp4"
    # create_video_with_subtitles(
    #     image_path="../content/images/part1.jpg",
    #     srt_path=srt_path,
    #     audio_path=audio_path,
    #     output_path=video_path,
    #     dimensions=(1920, 1080),
    #     fps=24,
    # )
    
    print(f"✅ Individual modules video created: {results_dir}")

if __name__ == "__main__":
    print("🚀 GenAI TTS Video Pipeline Examples\n")
    
    try:        
        # Run individual modules example
        example_individual_modules()
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
