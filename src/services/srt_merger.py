"""
Script to merge multiple SRT files into one based on audio duration and names.
Validates subtitle timings against audio duration and leaves gaps for invalid SRTs.
"""

import os
import re
import wave
import contextlib
from pathlib import Path
from datetime import timedelta
from typing import List, Tuple, Optional

def get_audio_duration(audio_path: str) -> float:
    """Get duration of audio file in seconds."""
    try:
        with contextlib.closing(wave.open(audio_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        print(f"❌ Error reading audio file {audio_path}: {e}")
        return 0.0

def parse_srt_time(time_str: str) -> float:
    """Convert SRT time format (HH:MM:SS,mmm) to seconds."""
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds

def format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT time format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')

def format_chapter_time(seconds: float) -> str:
    """Convert seconds to chapter time format (HH:MM:SS)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def parse_srt_file(srt_path: str, audio_duration: Optional[float] = None) -> List[Tuple[float, float, str]]:
    """Parse SRT file and return list of (start_time, end_time, text)."""
    subtitles = []
    
    if not os.path.exists(srt_path):
        return subtitles
    
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Split by empty lines to get subtitle blocks
        blocks = re.split(r'\n\s*\n', content)
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # Parse timing line (format: start --> end)
                timing_line = lines[1]
                if '-->' in timing_line:
                    start_str, end_str = timing_line.split(' --> ')
                    start_time = parse_srt_time(start_str.strip())
                    end_time = parse_srt_time(end_str.strip())
                    
                    # Join all text lines
                    text = '\n'.join(lines[2:])
                    subtitles.append((start_time, end_time, text))
    
    except Exception as e:
        print(f"❌ Error parsing SRT file {srt_path}: {e}")

    # Remove [END OF TRANSCRIPT] entry if it's the last subtitle
    if subtitles and "[END OF TRANSCRIPT]" in subtitles[-1][2].strip():
        # print(f"🔧 Removing [END OF TRANSCRIPT] from {srt_path}")
        subtitles.pop()
    
    if audio_duration is not None and subtitles and subtitles[-1][1] > audio_duration:
        new_end_time = (subtitles[-1][0], audio_duration, subtitles[-1][2])
        subtitles.pop()
        subtitles.append(new_end_time)
        # print(f"🔧 Adjusted {subtitles[-1]} to match audio duration: {audio_duration}s")
        # print(f"After adjustment, last subtitle is now: {subtitles[-1]}")

    return subtitles

def validate_srt_against_audio(srt_path: str, audio_path: str, subtitles: List[Tuple[float, float, str]]) -> bool:
    """Check if all subtitle timings are within audio duration."""
    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        return False
    
    audio_duration = get_audio_duration(audio_path)
    if audio_duration <= 0:
        return False
    
    if not subtitles:
        print(f"❌ No subtitles found in: {srt_path}")
        return False
    
    # Use the last valid subtitle's end time for validation
    last_subtitle_end = max(end_time for _, end_time, _ in subtitles)
    
    if last_subtitle_end > audio_duration:
        print(f"Last subtitle ends at {last_subtitle_end:.2f}s but audio is only {audio_duration:.2f}s")
        print(f"❌ Invalid SRT: {srt_path} - subtitle ends at {last_subtitle_end:.2f}s but audio is only {audio_duration:.2f}s")
        return False

    return True

def natural_sort_key(filename: str) -> List:
    """
    Generate a sort key for natural sorting of filenames with numbers.
    This ensures Chương 1, Chương 2, ..., Chương 10, Chương 11 order.
    """
    # Split the filename into text and number parts
    parts = re.split(r'(\d+)', filename)
    # Convert numeric parts to integers for proper sorting
    return [int(part) if part.isdigit() else part.lower() for part in parts]

def merge_srt_files(audio_dir: str, srt_dir: str, output_path: str) -> None:
    """
    Merge SRT files based on corresponding audio files.
    
    Args:
        audio_dir: Directory containing audio files
        srt_dir: Directory containing SRT files
        output_path: Path for the merged SRT file
    """
    print(f"🔄 Merging SRT files from '{srt_dir}' based on audio in '{audio_dir}'...")

    if not os.path.exists(audio_dir):
        raise FileNotFoundError(f"Audio directory not found: {audio_dir}")
    
    if not os.path.exists(srt_dir):
        raise FileNotFoundError(f"SRT directory not found: {srt_dir}")
    
    # Get all audio files and sort them
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
    audio_files.sort(key=natural_sort_key)
    
    if not audio_files:
        print("❌ No audio files found in the directory.")
        return
    
    merged_subtitles = []
    current_offset = 0.0
    subtitle_counter = 1

    time_stamps = []

    for i, audio_file in enumerate(audio_files):
        base_name = os.path.splitext(audio_file)[0]
        audio_path = os.path.join(audio_dir, audio_file)
        srt_path = os.path.join(srt_dir, f"{base_name}.srt")
        
        print(f"📝 Processing {i+1}/{len(audio_files)}: {base_name}")
        
        # Get audio duration
        audio_duration = get_audio_duration(audio_path)
        if audio_duration <= 0:
            print(f"❌ Skipping {audio_file} - could not determine duration")
            current_offset += 60.0  # Default gap for unknown duration
            continue

        # Parse and add valid subtitles
        subtitles = parse_srt_file(srt_path, audio_duration)

        if subtitles:
            time_stamp = (format_chapter_time(current_offset + subtitles[0][0]), audio_file.split('.')[0])
            print(f"☝️  First subtitle: {time_stamp}")
            time_stamps.append(time_stamp)

        # Check if SRT file exists and is valid
        if os.path.exists(srt_path) and validate_srt_against_audio(srt_path, audio_path, subtitles):

            for start_time, end_time, text in subtitles:
                # Adjust timing with current offset
                adjusted_start = current_offset + start_time
                adjusted_end = current_offset + end_time
                
                merged_subtitles.append((subtitle_counter, adjusted_start, adjusted_end, text))
                subtitle_counter += 1
            
            print(f"✅ Added {len(subtitles)} subtitles from {base_name}\n")
        else:
            # Leave a gap for invalid/missing SRT
            print(f"⚠️  Leaving gap for {base_name} - SRT invalid or missing\n")
        
        # Move offset to end of current audio + gap
        current_offset += audio_duration

    output_path_name = ''.join(audio_files[0].split('.')[0] + " - " + audio_files[-1].split('.')[0])
    print(f"Output will be saved to: {output_path_name}\n")

    if time_stamps:
        with open(os.path.join(srt_dir, f"timestamps_{output_path_name}.txt"), 'w', encoding='utf-8') as f:
            for line in time_stamps:
                f.write(" ".join(line) + "\n")

    output_path = os.path.join(output_path, f"{output_path_name}.srt")

    # Write merged SRT file
    if merged_subtitles:
        write_merged_srt(merged_subtitles, output_path)
        print(f"✅ Merged SRT file created: {output_path}")
        print(f"📊 Total subtitles: {len(merged_subtitles)}")
        print(f"⏱️  Total duration: {current_offset} seconds")
    else:
        print("❌ No valid subtitles found to merge.")

def write_merged_srt(subtitles: List[Tuple[int, float, float, str]], output_path: str) -> None:
    """Write merged subtitles to SRT file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for counter, start_time, end_time, text in subtitles:
            f.write(f"{counter}\n")
            f.write(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n")
            f.write(f"{text}\n\n")

def main():
    """Example usage of the merge script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Merge SRT files based on audio duration")
    parser.add_argument("--audio-dir", required=True, help="Directory containing audio files")
    parser.add_argument("--srt-dir", required=True, help="Directory containing SRT files")
    parser.add_argument("--output", required=True, help="Output path for merged SRT file")
    
    args = parser.parse_args()
    
    try:
        merge_srt_files(args.audio_dir, args.srt_dir, args.output)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Example usage with your workspace structure
    audio_dir = "../../results/MDSXQLNPLGNC/audios"
    srt_dir = "../../results/MDSXQLNPLGNC/subtitles"
    output_path = "../../results/MDSXQLNPLGNC/subtitles/"

    merge_srt_files(audio_dir, srt_dir, output_path)