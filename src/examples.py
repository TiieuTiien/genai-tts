"""
Example usage of the complete GenAI TTS video pipeline.

This script demonstrates how to create a complete video from a text file
using the modular approach.
"""

import os
from main import create_complete_video, generate_audio_step, setup_environment, create_video_step

def example_basic_usage():
    """Example of basic usage with default settings."""
    print("🎬 Example: Basic video creation")
    
    # Set up environment
    setup_environment()
    
    # Create video with default settings
    video_path = create_complete_video(
        input_text_path="../content/contents/sample1.txt",
        image_path="../content/images/sample_horizontal.jpg",
        output_dir="../content/results", 
        project_name="debug",
    )
    
    print(f"✅ Video created: {video_path}")

def debug_example():
    """Debug example"""
    print("🎬 Debugging: Basic video creation")
    output_dir="../media/truyen"

    generate_audio_step(
        input_dir="../media/content/MDSXQLNPGNC",
        output_dir=output_dir,
        voice_name="Leda"
    )

def example_custom_settings():
    """Example of customized video creation."""
    print("🎬 Example: Custom video creation")
    
    # Set up environment  
    setup_environment()
    
    # Create video with custom settings
    video_path = create_complete_video(
        input_text_path="../content/contents/sample1.txt",
        image_path="../content/images/part1.jpg",
        output_dir="../content/custom_output",
        project_name="my_custom_video",
        voice_name="Gacrux",
        dimensions=(1280, 720),  # HD instead of Full HD
        fps=30  # Higher frame rate
    )
    
    print(f"✅ Custom video created: {video_path}")

def example_individual_modules():
    """Example of using individual modules separately."""
    print("🎬 Example: Individual module usage")
    
    from genai_tts import generate_audio_from_text
    from subtitles_gen import generate_subtitles
    from editor import create_video_with_subtitles
    
    # Set up environment
    setup_environment()
    
    # Step 1: Generate audio
    print("Generating audio...")
    audio_path = "../content/results/example_audio.wav"
    generate_audio_from_text(
        text_file_path="../content/contents/sample1.txt",
        output_path=audio_path,
        voice_name="Gacrux"
    )
    
    # Step 2: Generate subtitles
    print("Generating subtitles...")
    srt_path = "../content/results/example_subtitles.srt"
    generate_subtitles(
        audio_path=audio_path,
        output_path=srt_path
    )
    
    # Step 3: Create video
    print("Creating video...")
    video_path = "../content/results/example_final.mp4"
    create_video_with_subtitles(
        image_path="../content/images/part1.jpg",
        srt_path=srt_path,
        audio_path=audio_path,
        output_path=video_path,
        dimensions=(1920, 1080),
        fps=24,
    )
    
    print(f"✅ Individual modules video created: {video_path}")

if __name__ == "__main__":
    print("🚀 GenAI TTS Video Pipeline Examples\n")
    
    try:
        # Run basic example
        # example_basic_usage()
        # print()
        
        # Run debug example
        debug_example()
        print()
        
        # Run custom example
        # example_custom_settings()
        # print()
        
        # Run individual modules example
        # example_individual_modules()
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
