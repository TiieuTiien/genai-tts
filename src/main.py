#!/usr/bin/env python3
"""
Main orchestrator for the complete GenAI TTS video creation pipeline.

This script combines three modules in sequence:
1. genai_tts.py - Generates audio from text using Google's GenAI TTS
2. subtitles_gen.py - Creates SRT subtitles from the generated audio
3. editor.py - Composes audio, subtitles, and visuals into a final video

Usage:
    python main.py [--input-text TEXT_FILE] [--output-dir OUTPUT_DIR]
"""

import json
import os
import sys
import argparse
import pathlib
import concurrent.futures
import time

from dotenv import load_dotenv

# Import our custom modules
from services.genai_tts import generate_audio_from_text
from services.subtitles_gen import generate_subtitles
from services.editor import create_video_with_subtitles
from utils.gemini_logger import log_gemini_error

def setup_environment():
    """Load environment variables and check dependencies."""
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY_SUBTITLES')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY_SUBTITLES not found in environment variables. Make sure it's set in your .env file")
    
    return api_key

def ensure_directories(paths):
    """Ensure all required directories exist."""
    for path in paths:
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

def generate_audio_step(input_dir, output_dir, max_workers=3, delay_seconds=70, voice_name="Leda"):
    """Step 1: Generate audio from text using GenAI TTS.
    
    Args:
        input_dir: Path to the input directory
        output_dir: Path where audio will be saved
        voice_name: Voice to use for TTS generation
    """
    print(f"🎵 Generating audio from '{input_dir}'...")

    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input text file not found: {input_dir}")

    file_names = os.listdir(input_dir)
    file_names.sort()

    tasks = []
    for file_name in file_names:
        if file_name.endswith('.txt'):
            text_file_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}.wav")
            # print(f"Text file: {text_file_path} -> Audio output: {output_path}")
            tasks.append((text_file_path, output_path, voice_name))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(0, len(tasks), max_workers):
            batch_start_time = time.time()
            batch = tasks[i:i + max_workers]
            futures = []
            
            # Submit batch of tasks
            for j, task_args in enumerate(batch):
                print(f"🚀 Starting task {i+j+1}/{len(tasks)}: {os.path.basename(task_args[0])}")
                future = executor.submit(generate_audio_from_text, *task_args)
                futures.append((future, task_args[0]))
            
            # Wait for all tasks in the batch to complete
            for future, text_file_path in futures:
                try:
                    future.result()
                    print(f"✅ Audio generated successfully for: {text_file_path}")
                except Exception as e:
                    log_gemini_error(e, context="generating audio", file_path=text_file_path)
            
            # Calculate elapsed time and wait if necessary
            elapsed_time = time.time() - batch_start_time
            if elapsed_time < delay_seconds and i + max_workers < len(tasks):
                remaining_wait = delay_seconds - elapsed_time
                print(f"⏳ Batch completed in {elapsed_time:.1f}s. Waiting {remaining_wait:.1f}s more to reach {delay_seconds}s interval...")
                time.sleep(remaining_wait)
            elif i + max_workers < len(tasks):
                print(f"⏳ Batch completed in {elapsed_time:.1f}s (>= {delay_seconds}s). Processing next batch immediately...")

def generate_subtitles_step(audio_dir, srt_dir, max_workers=10, delay_seconds=90):
    """Step 2: Generate SRT subtitles from audio.
    
    Args:
        audio_dir: Path to the audio file
        srt_dir: Path where SRT file will be saved
    """
    print(f"📝 Generating subtitles from '{audio_dir}'...")
    
    if not os.path.exists(audio_dir):
        raise FileNotFoundError(f"Audio file not found: {audio_dir}")
    
    # Get all audio files in the directory
    file_names = os.listdir(audio_dir)
    file_names.sort()

    # Create tasks for each audio file
    tasks = []
    for file_name in file_names:
        if file_name.endswith('.wav'):
            audio_file_path = os.path.join(audio_dir, file_name)

            srt_file_path = f"{os.path.splitext(file_name)[0]}.srt"
            srt_output_path = os.path.join(srt_dir, srt_file_path)
            tasks.append((audio_file_path, srt_output_path))

            # print(f"Audio file: {audio_file_path}")

    if not tasks:
        print("❌ No audio files found in the directory.")
        return

    # Process files in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, task_args in enumerate(tasks):
            print(f"🚀 Starting task {i+1}/{len(tasks)}: {os.path.basename(task_args[0])}")

            future = executor.submit(generate_subtitles, task_args[0], task_args[1])
            futures.append((future, task_args[0]))

            # Add delay to avoid rate limits
            if (i + 1) % max_workers == 0 and (i + 1) < len(tasks):
                print(f"⏳ Waiting {delay_seconds} seconds to avoid rate limit...")
                time.sleep(delay_seconds)

        for future, audio_file_path in futures:
            try:
                future.result()
                print(f"✅ Subtitles generated successfully for: {audio_file_path}")
            except Exception as e:
                log_gemini_error(e, context="generating subtitles", file_path=audio_file_path)

    print(f"✅ All subtitles generated successfully: {srt_dir}")

def create_video_step(image_path, srt_path, audio_path, output_video_path, 
                     duration=None, dimensions=(1920, 1080), fps=24):
    """Step 3: Create final video with audio, subtitles, and visuals.
    
    Args:
        image_path: Path to the background image
        srt_path: Path to the SRT subtitles file
        audio_path: Path to the audio file
        output_video_path: Path where final video will be saved
        duration: Duration in seconds (None for audio duration)
        dimensions: Video dimensions as (width, height)
        fps: Frames per second for output video
    """
    print(f"🎬 Step 3: Creating final video...")
    
    # Check if all required files exist
    required_files = [image_path, srt_path, audio_path]
    for file_path in required_files:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Required file not found: {file_path}")
    
    # If duration is not specified, we'll let the editor determine it from audio
    create_video_with_subtitles(
        image_path=image_path,
        srt_path=srt_path,
        audio_path=audio_path,
        output_path=output_video_path,
        duration=duration,
        dimensions=dimensions,
        fps=fps
    )
    
    print(f"✅ Video created successfully: {output_video_path}")

def create_complete_video(input_text_path, image_path, duration=None, output_dir="output", 
                         project_name="video", voice_name="Gacrux",
                         dimensions=(1920, 1080), fps=24):
    """Main function to create a complete video from text input.
    
    Args:
        input_text_path: Path to the input text file
        image_path: Path to the background image
        output_dir: Directory to save all output files
        project_name: Name prefix for output files
        voice_name: Voice to use for TTS generation
        duration: Video duration in seconds (None for audio duration)
        dimensions: Video dimensions as (width, height)
        fps: Frames per second for output video
        
    Returns:
        Path to the final video file
    """
    # Define output paths
    audio_path = os.path.join(output_dir, f"{project_name}_audio.wav")
    srt_path = os.path.join(output_dir, f"{project_name}_subtitles.srt")
    video_path = os.path.join(output_dir, f"{project_name}_final.mp4")
    
    # Ensure output directories exist
    ensure_directories([audio_path, srt_path, video_path])
    
    try:
        # Step 1: Generate audio
        generate_audio_step(input_text_path, audio_path, voice_name)
        
        # Step 2: Generate subtitles
        generate_subtitles_step(audio_path, srt_path)
        
        # Step 3: Create final video
        create_video_step(
            image_path=image_path,
            srt_path=srt_path,
            audio_path=audio_path,
            output_video_path=video_path,
            duration=duration,
            dimensions=dimensions,
            fps=fps
        )
        
        print(f"\n🎉 Complete video creation successful!")
        print(f"📁 Output files:")
        print(f"   Audio: {audio_path}")
        print(f"   Subtitles: {srt_path}")
        print(f"   Video: {video_path}")
        
        return video_path
        
    except Exception as e:
        print(f"❌ Error during video creation: {str(e)}")
        sys.exit(1)

def main():
    """Command line interface for the video creation pipeline."""
    parser = argparse.ArgumentParser(
        description="Create a complete video with AI-generated audio and subtitles"
    )
    
    parser.add_argument(
        "--input-text", 
        default="../content/contents/sample1.txt",
        help="Path to input text file (default: ../content/contents/sample1.txt)"
    )
    
    parser.add_argument(
        "--image",
        default="../content/images/part1.jpg", 
        help="Path to background image (default: ../content/images/part1.jpg)"
    )
    
    parser.add_argument(
        "--output-dir",
        default="../content/results",
        help="Output directory for generated files (default: ../content/results)"
    )
    
    parser.add_argument(
        "--project-name",
        default="complete_video",
        help="Name prefix for output files (default: complete_video)"
    )
    
    parser.add_argument(
        "--voice",
        default="Gacrux",
        help="Voice name for TTS (default: Gacrux)"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        help="Video duration in seconds (default: use audio duration)"
    )
    
    parser.add_argument(
        "--dimensions",
        default="1920x1080",
        help="Video dimensions as WIDTHxHEIGHT (default: 1920x1080)"
    )
    
    parser.add_argument(
        "--fps",
        type=int,
        default=24,
        help="Frames per second for output video (default: 24)"
    )
    
    args = parser.parse_args()
    
    # Parse dimensions
    try:
        width, height = map(int, args.dimensions.split('x'))
        dimensions = (width, height)
    except ValueError:
        print("❌ Invalid dimensions format. Use WIDTHxHEIGHT (e.g., 1920x1080)")
        sys.exit(1)
    
    # Set up environment
    # try:
    #     setup_environment()
    # except ValueError as e:
    #     print(f"❌ Environment setup error: {e}")
    #     sys.exit(1)
    
    # Create the complete video
    create_complete_video(
        input_text_path=args.input_text,
        image_path=args.image,
        output_dir=args.output_dir,
        project_name=args.project_name,
        voice_name=args.voice,
        duration=args.duration,
        dimensions=dimensions,
        fps=args.fps
    )

if __name__ == "__main__":
    main()
