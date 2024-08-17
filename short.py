from moviepy.editor import *
import numpy as np
from PIL import Image
import os
import random

# Constants
WIDTH, HEIGHT = 1080, 1920  # Instagram Reel dimensions
DURATION = 15  # Fixed duration of 15 seconds
VIDEO_FPS = 30
BACKGROUND_MUSIC_VOLUME = 0.1

# Paths
IMAGE_FOLDER = 'media/images/'
VOICEOVER_PATH = 'media/music/background.mp3'
BG_MUSIC_PATH = 'media/music/background.mp3'
OUTPUT_PATH = 'media/output/short.mp4'

def get_image_paths(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg','.webp'))][:4]

def create_image_clip(image_path, duration):
    img = Image.open(image_path)
    img_ratio = img.width / img.height
    screen_ratio = WIDTH / HEIGHT

    if img_ratio > screen_ratio:
        new_height = int(WIDTH / img_ratio)
        img = img.resize((WIDTH, new_height), Image.LANCZOS)
    else:
        new_width = int(HEIGHT * img_ratio)
        img = img.resize((new_width, HEIGHT), Image.LANCZOS)

    # Ensure image is always at least as large as the screen
    if img.width < WIDTH:
        scale_factor = WIDTH / img.width
        img = img.resize((WIDTH, int(img.height * scale_factor)), Image.LANCZOS)
    if img.height < HEIGHT:
        scale_factor = HEIGHT / img.height
        img = img.resize((int(img.width * scale_factor), HEIGHT), Image.LANCZOS)

    # Randomly choose panning direction
    #pan_direction = random.choice(['left_to_right', 'right_to_left', 'top_to_bottom', 'bottom_to_top'])
    pan_direction = random.choice(['left_to_right', 'right_to_left'])

    def make_frame(t):
        progress = t / duration

        # Panning effect
        if pan_direction == 'left_to_right':
            x = int(progress * (img.width - WIDTH))
            y = (img.height - HEIGHT) // 2
        elif pan_direction == 'right_to_left':
            x = int((1 - progress) * (img.width - WIDTH))
            y = (img.height - HEIGHT) // 2
        elif pan_direction == 'top_to_bottom':
            x = (img.width - WIDTH) // 2
            y = int(progress * (img.height - HEIGHT))
        else:  # bottom_to_top
            x = (img.width - WIDTH) // 2
            y = int((1 - progress) * (img.height - HEIGHT))

        # Ensure we're not out of bounds
        x = max(0, min(x, img.width - WIDTH))
        y = max(0, min(y, img.height - HEIGHT))

        cropped = img.crop((x, y, x + WIDTH, y + HEIGHT))
        return np.array(cropped)

    return VideoClip(make_frame, duration=duration)

def create_instagram_reel(image_folder, voiceover, bg_music):
    # Load audio
    voiceover_audio = AudioFileClip(voiceover)
    
    # Get image paths
    image_paths = get_image_paths(image_folder)
    
    # Calculate image duration
    IMAGE_DURATION = DURATION / len(image_paths)

    image_clips = []
    for img_path in image_paths:
        clip = create_image_clip(img_path, IMAGE_DURATION)
        image_clips.append(clip)
    
    video = concatenate_videoclips(image_clips)
    
    bg_music = AudioFileClip(bg_music).volumex(BACKGROUND_MUSIC_VOLUME)
    bg_music = bg_music.set_duration(DURATION)
    audio = CompositeAudioClip([voiceover_audio, bg_music])
    final_video = video.set_audio(audio)
    
    final_video = final_video.set_duration(DURATION)
    return final_video

# Main execution
if __name__ == "__main__":
    reel = create_instagram_reel(IMAGE_FOLDER, VOICEOVER_PATH, BG_MUSIC_PATH)
    reel.write_videofile(OUTPUT_PATH, fps=VIDEO_FPS, codec='libx264', audio_codec='aac')