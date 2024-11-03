# A smol script that uses ffmpeg
# TODO: Handle better the paths for output.

import os
import subprocess
import shutil
import tempfile

from argparse import ArgumentParser, Namespace
from enum import Enum


class Yuh(Enum):
    CLIP = [
        "ffmpeg",
        "-y",
        "-ss",
        "START",
        "-i",
        "INPUT",
        "-to",
        "END",
        "-c",
        "copy",
        "-copyts",
        "OUTPUT",
    ]
    AUDIO = ["ffmpeg", "-y", "-i", "INPUT", "-vn", "-c:a", "mp3", "OUTPUT"]
    MERGE = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-i",
        "LIST",
        "-c",
        "copy",
        "OUTPUT",
    ]
    YOUTUBE = [
        "ffmpeg",
        "-y",
        "-i",
        "INPUT",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-preset",
        "ultrafast",
        "-c:a",
        "aac",
        "-b:a",
        "384k",
        "-pix_fmt",
        "yuv420p",
        "OUTPUT",
    ]
    ENCODE = [
        "ffmpeg",
        "-y",
        "-i",
        "INPUT",
        "-c:v",
        "libx264",
        "-crf",
        "30",
        "-c:a",
        "copy",
        "OUTPUT",
    ]


def images_to_video(path, framerate):
    folder_path = path
    input_files = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            input_files.append(file_path)

    if not input_files:
        print(f"{folder_path} is empty")
        return

    print(
        f"creating a video from images in {folder_path} with framerate 1/{framerate}\n"
    )
    if framerate > 10:
        print("framerate is too high!")

    if framerate < 1:
        print("framerate is less than 1! Cancelling...")
        return

    temp_dir = tempfile.mkdtemp()
    print(f"created temporary directory {temp_dir}\n")

    output_file = f"{folder_path}/images_to_video-out.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-framerate",
        "1/5",
        "-i",
        f"{temp_dir}\\img%d.png",
        "-c:v",
        "libx264",
        "-r",
        "30",
        "-pix_fmt",
        "yuv420p",
        output_file,
    ]
    command[3] = f"1/{framerate}"

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
    # TODO: add an away to check if ffmpeg executable exists and/or is in path.
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())

    result = process.wait()

    if result == 0:
        print("\nProcess completed!")
    else:
        print(f"\nProcess failed with error code {result}")


def main():
    parser = ArgumentParser(
        description="Smol tool to clip, merge videos, create a video from images, extract the audio from a video, and encode video for youtube."
    )

    parser.add_argument("input", nargs=1, type=str, help="Input file path")
    parser.add_argument("output", nargs="?", type=str, help="Output file path")
    parser.add_argument("start", nargs="?", type=str, help="Starting position")
    parser.add_argument("end", nargs="?", type=str, help="Ending position")

    parser.add_argument(
        "-c", "--clip", action="store_true", help="creates a clip"
    )
    parser.add_argument(
        "-a", "--audio", action="store_true", help="extracts audio"
    )
    parser.add_argument(
        "-m",
        "--merge",
        action="store_true",
        help="merges two or more inputs. input must be a .txt file",
    )
    parser.add_argument(
        "-v",
        "--video",
        action="store_true",
        help="creates a video off of images",
    )
    parser.add_argument(
        "--framerate",
        nargs="?",
        default=5,
        type=int,
        help="Framerate for video made from images",
    )
    parser.add_argument(
        "-yt",
        "--youtube",
        action="store_true",
        help="encodes a video for youtube",
    )
    parser.add_argument(
        "-e",
        "--encode",
        action="store_true",
        help="encodes a video with a specific option: libx264 -crf 30 audio stream is copied. used for clips",
    )

    args = parser.parse_args()

    match args:
        case Namespace(clip=True):
            if args.start is None or args.end is None:
                print("clip option requires start and end")
                return

            print(
                f"creating a clip of {args.input[0]} [{args.start}...{args.end}] -> {args.output}\n\n"
            )
            cmd_args = {
                "INPUT": args.input[0],
                "START": args.start,
                "END": args.end,
                "OUTPUT": args.output,
            }
            command = [cmd_args.get(item, item) for item in Yuh.CLIP.value]
            run_ffmpeg(command)
        case Namespace(audio=True):
            if args.output is None:
                print("audio option requires output")
                return

            # TODO: add a way to use the same input path and name to output.
            print(f"extracting audio of {args.input[0]} -> {args.output}\n\n")
            cmd_args = {"INPUT": args.input[0], "OUTPUT": args.output}
            command = [cmd_args.get(item, item) for item in Yuh.AUDIO.value]
            run_ffmpeg(command)
        case Namespace(merge=True):
            # if args.input[0].endswitch('.txt'):
            #    print(f"merging inputs from {args.input[0]} -> {args.output}\n\n")
            #    cmd_args = {'LIST': args.input[0], 'OUTPUT': args.output}
            #    command = [cmd_args.get(item, item) for item in Yuh.MERGE.value]
            #    run_ffmpeg(command)
            # else:
            #    print(f'error trying to merge: {args.input}')
            print("not implemented")
        case Namespace(video=True):
            images_to_video(args.input[0], args.framerate)
        case Namespace(youtube=True):
            if args.output is None:
                print("youtube option requires output")
                return

            print(f"encoding video ({args.input[0]}) for youtube.\n\n")
            cmd_args = {"INPUT": args.input[0], "OUTPUT": args.output}
            command = [cmd_args.get(item, item) for item in Yuh.YOUTUBE.value]
            run_ffmpeg(command)
        case Namespace(encode=True):
            if args.output is None:
                print("encode option requires output")
                return

            print(
                f"encoding {args.input[0]} with libx264 crf=30 audio stream copied -> {args.output}\n\n"
            )
            cmd_args = {"INPUT": args.input[0], "OUTPUT": args.output}
            command = [cmd_args.get(item, item) for item in Yuh.ENCODE.value]
            run_ffmpeg(command)


if __name__ == "__main__":
    main()
