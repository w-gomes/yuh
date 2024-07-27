# A smol script that uses ffmpeg

import os
import subprocess
import shutil
import tempfile
from sys import argv


def help():
    PROGRAM_NAME = 'yuh'

    print('Smol tool to clip, merge videos, create a video from images, extract the audio from a video, and encode video for youtube.\n')
    print(f'usage: python {PROGRAM_NAME} [-c path/to/input start end] [-a path/to/input] [-m path/to/input_txt_file] [-v [path/to/folder]] [-yt path/to/input]')
    print('\noptions:\n\t-h\t\t\t\tshow this help message and exit')
    print('\t-c path/to/input start end\tcreate a clip video. Eg start and end: 00:00:03.00 00:00:06.00')
    print('\t-a path/to/input start end\textract audio. optional: give start and end')
    print('\t-m path/to/input_txt_file\tmerge two or more inside input, input must be a .txt; input.txt contains the path.')
    print('\t-v [path/to/folder]\t\tcreate a video off of images. Put the images inside inputs folder or provide the path to the folder.')
    print('\t-yt path/to/input\t\tencode a video for youtube.')


def images_to_video(path):
    folder_path = path[0] if path else 'inputs/'
    input_files = []

    # TODO: check if folder is empty

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            input_files.append(file_path)

    if not input_files:
        print(f'{folder_path} is empty')
        return

    print(f'creating a video from images in {folder_path}\n')

    temp_dir = tempfile.mkdtemp()
    print(f'created temporary directory {temp_dir}\n')

    output_file = f'{folder_path}/images_to_video-out.mp4'

    command = [
        'ffmpeg',
        '-y',
        '-framerate', '1/5',
        '-i', f"{temp_dir}\\img%d.png",
        '-c:v', 'libx264',
        '-r', '30',
        '-pix_fmt', 'yuv420p',
        output_file
    ]

    try:
        total_images = 0
        for idx, src_file in enumerate(input_files, start=1):
            tmp_file = f"img{idx}.png"
            dest_file = os.path.join(temp_dir, tmp_file)
            shutil.copy2(src_file, dest_file)
            total_images = idx
        print(f"Copied {total_images} images.\n")
        print("Running ffmpeg...\n")
        run_ffmpeg(command)

    finally:
        shutil.rmtree(temp_dir)
        print(f"Temporary directory {temp_dir} has been removed.\n")


def run_ffmpeg(command):
    process = subprocess.Popen(
                command, stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, text=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())

    result = process.wait()

    if result == 0:
        print("\nProcess completed!")
    else:
        print(f"\nProcess failed with error code {result}")


def main():
    match argv[1:]:
        case []:
            print('missing argument, -h for help.')

        case ['-h']:
            help()

        case ['-c', filename, start, end]:
            # TODO: add option for different container, mp4 or mkv
            START = start
            END = end
            FILENAME = filename
            OUTPUT_FILE = f"{filename.split('.')[0]}-out.mp4"
            command = [
                'ffmpeg',
                '-y',
                '-i', FILENAME,
                '-ss', START,
                '-to', END,
                OUTPUT_FILE
            ]
            print(f'creating a clip of {FILENAME} [{START}...{END}] -> {OUTPUT_FILE}\n\n')
            run_ffmpeg(command)

        case ['-a', filename]:
            # TODO: add option for different container, mp3 or aac
            FILENAME = filename
            OUTPUT_FILE = f"{filename.split('.')[0]}-out.mp3"
            command = [
                'ffmpeg',
                '-y',
                '-i', FILENAME,
                '-vn',
                '-c:a', 'mp3',
                OUTPUT_FILE
            ]
            print(f'extracting audio of {FILENAME} -> {OUTPUT_FILE}\n\n')
            run_ffmpeg(command)

        case ['-m', filename]:
            # TODO: implement this.
            """
            if filename.endswith('.txt'):
                LIST = filename
                OUTPUT_FILE = "merged_inputs-out.mp4"
                command = [
                    'ffmpeg',
                    '-y',
                    '-f', 'concat',
                    '-i', LIST,
                    '-c', 'copy',
                    OUTPUT_FILE
                ]

                # TODO: check contents from list.txt
                print(f"merging inputs from {LIST} -> {OUTPUT_FILE}\n\n")
                run_ffmpeg(command)
            else:
                print('input file must be .txt')
            """
            print('Currently not supported\n\n')

        case ['-v', *path]:
            images_to_video(path) 

        case ['-yt', filename]:
            # TODO: add more options for preset, audio bitrate
            FILENAME = filename
            OUTPUT_FILE = f"{filename.split('.')[0]}-out.mp4"
            command = [
                'ffmpeg',
                '-y',
                '-i', FILENAME,
                '-c:v', 'libx264',
                '-crf', '18',
                '-preset', 'ultrafast',
                '-c:a', 'aac',
                '-b:a', '384k',
                '-pix_fmt', 'yuv420p',
                OUTPUT_FILE
            ]
            print(f'encoding video ({filename}) for youtube.\n\n') 
            run_ffmpeg(command)

        case _:
            print(f"Sorry, I couldn't understand: {argv[1:]}. Perhaps inputs are missing.       ")


if __name__ == "__main__":
    main()
