import logging
import os
import shutil
import time

import colorama
import pytube
from aiogram import types
from src.helper.helper import wrap_as_async

logger = logging.getLogger(__name__)


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
        logger.debug(f"Song [{video.title}] has been successfully downloaded.")
        return file
    except pytube.exceptions.RegexMatchError:
        logger.warning("Link is not valid")
    except Exception as err:
        logger.debug(err)


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
def download_playlist(url: str) -> str:
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
        logger.debug(
            f"{colorama.Fore.GREEN}Previous folder [{playlist_folder.title()}] was deleted"
            f"{colorama.Style.RESET_ALL}"
        )
        os.mkdir(playlist_folder)
        logger.debug(f"A new folder [{playlist_folder.title()}] is created")
    for video_url in playlist.video_urls:
        try:
            video = download_video(video_url=video_url, target_path=playlist_folder)
            convert_to_mp3(video)
            time.sleep(0.1)  # Not to raise Http 429 Too many requests
            logger.debug(
                f"{colorama.Fore.GREEN}"
                f"Playlist [{playlist.title}] has been successfully downloaded and saved in {playlist_folder}."
                f"{colorama.Style.RESET_ALL}"
            )
        except pytube.exceptions.RegexMatchError as err:
            logger.debug(f"{colorama.Fore.RED}Link is not valid \n {err}{colorama.Style.RESET_ALL}")
        except Exception as err:
            logger.debug(err)

    return playlist_folder


@wrap_as_async
def download_send(message: types.Message) -> types.InputFile:
    """Downloads the video from the url in the message and return the uploaded file"""
    current_dir = os.path.dirname(__file__)
    logger.debug(f"message text: {message.text}")
    file = download_video(video_url=message.text, target_path=current_dir)
    file = convert_to_mp3(file)
    file = types.InputFile(file)
    return file
