import logging
import os
import shutil
import colorama
import pytube
from aiogram import types
from source.helper.helper import wrap_as_async


def download_video(video_url: str, target_path=None) -> str | None:
    """
    Downloads and returns the selected video file
    :param video_url: The url of the video
    :param target_path: The path for the video to be saved. If None, the default is the path to Desktop.
    :return: Downloaded Video file
    """
    try:
        yt = pytube.YouTube(video_url)
        video = yt.streams.filter(only_audio=True).first()
        file = video.download(output_path=target_path)
        logging.debug(f"Song [{video.title}] has been successfully downloaded.")
        return file
    except pytube.exceptions.RegexMatchError:
        logging.debug("Link is not valid")
    except Exception as err:
        logging.debug(err)


def convert_to_mp3(file: str) -> str:
    """
    Converts video to mp3
    :param file: The path to the given file
    :return: None | Recursion
    """
    base, ext = os.path.splitext(file)
    new_file = base + ".mp3"
    try:
        os.rename(file, new_file)
        return new_file
    except FileExistsError:
        os.remove(new_file)
        return convert_to_mp3(file)


@wrap_as_async
def download_playlist(url: str) -> str | None:
    """
    Downloads the given playlist
    :param url: (str) The url of the playlist
    :return: current dir path
    """
    current_dir = os.path.dirname(__file__)

    playlist = pytube.Playlist(url)
    playlist_folder = os.path.join(current_dir, playlist.title)
    try:
        os.mkdir(playlist_folder)
    except FileExistsError:
        shutil.rmtree(playlist_folder)
        logging.debug(
            f"{colorama.Fore.GREEN}Previous folder [{playlist_folder.title()}] was deleted"
            f"{colorama.Style.RESET_ALL}"
        )
        os.mkdir(playlist_folder)
        logging.debug(f"A new folder [{playlist_folder.title()}] is created")
    try:
        for video_url in playlist.video_urls:
            video = download_video(video_url=video_url, target_path=playlist_folder)
            convert_to_mp3(video)
        logging.debug(
            f"{colorama.Fore.GREEN}"
            f"Playlist [{playlist.title}] has been successfully downloaded and saved in {playlist_folder}."
            f"{colorama.Style.RESET_ALL}"
        )
        return playlist_folder
    except pytube.exceptions.RegexMatchError as err:
        logging.debug(f"{colorama.Fore.RED}Link is not valid \n {err}{colorama.Style.RESET_ALL}")
    except Exception as err:
        logging.debug(err)


@wrap_as_async
def download_send(message: types.Message) -> types.InputFile:
    """Downloads the video from the url in the message and return the uploaded file"""
    current_dir = os.path.dirname(__file__)
    logging.debug(f"message text: {message.text}")
    file = download_video(video_url=message.text, target_path=current_dir)
    file = convert_to_mp3(file)
    file = types.InputFile(file)
    return file
