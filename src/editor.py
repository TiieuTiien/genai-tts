from moviepy import TextClip, CompositeVideoClip, vfx, ImageClip, VideoFileClip, ColorClip, AudioFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
import os

def create_text_generator(font_path, font_size=48, color="#ffffff", stroke_color="#000000", stroke_width=3, dimensions=(1920, 1080)):
    """Creates a text generator function for subtitles.
    
    Args:
        font_path: Path to the font file
        font_size: Size of the font
        color: Text color in hex format
        stroke_color: Stroke color in hex format
        stroke_width: Width of the text stroke
        dimensions: Video dimensions as (width, height)
        
    Returns:
        Generator function for creating TextClip objects
    """
    return lambda txt: TextClip(
        font=font_path,
        text=txt,
        font_size=font_size,
        color=color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        text_align='center',
        horizontal_align='center',
        vertical_align='center',
        size=dimensions
    )

def load_subtitles_clip(srt_path, text_generator, encoding="utf-8"):
    """Loads subtitles from an SRT file.
    
    Args:
        srt_path: Path to the SRT file
        text_generator: Function to generate text clips
        encoding: File encoding
        
    Returns:
        SubtitlesClip object
    """
    print("Subtitles loaded!")
    return SubtitlesClip(srt_path, make_textclip=text_generator, encoding=encoding)

def load_image_clip(image_path, duration):
    """Loads an image clip with specified duration.
    
    Args:
        image_path: Path to the image file
        duration: Duration of the clip in seconds
        
    Returns:
        ImageClip object
    """
    print("Image loaded!")
    return ImageClip(image_path, duration=duration)

def load_audio_clip(audio_path, duration=None):
    """Loads an audio clip with optional duration limit.
    
    Args:
        audio_path: Path to the audio file
        duration: Maximum duration in seconds (None for full duration)
        
    Returns:
        AudioFileClip object
    """
    audio_clip = AudioFileClip(audio_path)
    if duration:
        audio_clip = audio_clip.with_duration(duration)
    print("Audio loaded!")
    return audio_clip

def create_color_background(size, color, duration):
    """Creates a colored background clip.
    
    Args:
        size: Dimensions as (width, height)
        color: RGB color tuple
        duration: Duration in seconds
        
    Returns:
        ColorClip object
    """
    return ColorClip(size=size, color=color, duration=duration)

def compose_video(clips):
    """Composes multiple clips into a single video.
    
    Args:
        clips: List of video clips to compose
        duration: Total duration of the composed video
        
    Returns:
        CompositeVideoClip object
    """
    compose_clip = CompositeVideoClip(clips)    
    print("Video composed! Duration: ", compose_clip.duration)
    compose_clip.write_videofile
    return compose_clip

def add_audio_to_video(video_clip, audio_clip):
    """Adds audio to a video clip.
    
    Args:
        video_clip: The video clip
        audio_clip: The audio clip to add
        
    Returns:
        Video clip with audio
    """
    return video_clip.with_audio(audio_clip)

def apply_effects(clip, fade_in_duration=None, fade_out_duration=None):
    """Applies visual effects to a clip.
    
    Args:
        clip: The clip to apply effects to
        fade_in_duration: Duration of fade in effect
        fade_out_duration: Duration of fade out effect
        
    Returns:
        Clip with effects applied
    """
    effects = []
    if fade_in_duration:
        effects.append(vfx.FadeIn(fade_in_duration))
    if fade_out_duration:
        effects.append(vfx.FadeOut(fade_out_duration))
    
    if effects:
        return clip.with_effects(effects)
    return clip

def export_video(clip, output_path, fps=24):
    """Exports the final video to a file.
    
    Args:
        clip: The video clip to export
        output_path: Path where to save the video
        fps: Frames per second for the output video
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print('Output path ok!')
    clip.write_videofile(output_path, fps=fps)

def create_video_with_subtitles(image_path, srt_path, audio_path, output_path, 
                               duration=10, dimensions=(1920, 1080), fps=24):
    """Main function to create a video with subtitles.
    
    Args:
        image_path: Path to the background image
        srt_path: Path to the subtitles file
        audio_path: Path to the audio file
        output_path: Path for the output video
        duration: Duration of the video in seconds
        dimensions: Video dimensions as (width, height)
        fps: Frames per second for output
    """
    # Create text generator
    text_generator = create_text_generator(
        font_path='../content/fonts/Arial Unicode.ttf',
        font_size=48,
        dimensions=dimensions
    )
    
    # Load clips
    audio_clip = load_audio_clip(audio_path, None)
    clip_duration = audio_clip.duration
    subtitles_clip = load_subtitles_clip(srt_path, text_generator).with_duration(clip_duration)
    image_clip = load_image_clip(image_path, duration=clip_duration)
    
    # Compose video
    video_clips = [image_clip, subtitles_clip]
    composed_video = compose_video(video_clips)
    
    # Add audio
    final_clip = add_audio_to_video(composed_video, audio_clip)
    
    # Optional: Apply effects
    # final_clip = apply_effects(final_clip, fade_in_duration=0.5, fade_out_duration=0.5)
    
    # Export video
    export_video(final_clip, output_path, fps)

if __name__ == "__main__":
    # Configuration
    config = {
        'image_path': '../content/images/part1.jpg',
        'srt_path': '../content/results/video_subtitles.srt',
        'audio_path': '../content/results/video_audio.wav',
        'output_path': '../content/results/video_output.mp4',
        'duration': None,
        'dimensions': (1920, 1080),
        'fps': 24
    }
    
    # Create video
    create_video_with_subtitles(**config)