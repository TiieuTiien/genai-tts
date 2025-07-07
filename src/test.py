from moviepy import *
from moviepy.video.tools.subtitles import SubtitlesClip

text_generator = lambda txt: TextClip(
        font="../fonts/MarkerFelt.ttc",
        text=txt,
        font_size=24,
        color='#ffffff',
        stroke_color='#000000',
        stroke_width=3,
        text_align='center',
        horizontal_align='center',
        vertical_align='center',
        size=(1920, 1080),
    )


audio = AudioFileClip('../content/results/debug_audio.wav')
print(audio.duration)
image_clip = ImageClip("../content/images/sample_horizontal.jpg", duration=audio.duration)
subtitle = SubtitlesClip("../content/results/debug_subtitles.srt", make_textclip=text_generator, encoding="utf-8")
videos = [image_clip, subtitle]
compose = CompositeVideoClip(videos)
print(compose.duration)

final = compose.with_audio(audio)

final.write_videofile("../content/results/debug_test.mp4", fps=1)