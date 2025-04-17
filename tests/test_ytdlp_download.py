import os
import logging
from pathlib import Path
import pytest
from downloader import Downloader
from .utils import assert_single_file, assert_chapter_structure, assert_playlist_structure

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Links
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=x9qojgBjJ1M"
TEST_VIDEO_CHAPTERS_URL = "https://www.youtube.com/watch?v=x9qojgBjJ1M"
TEST_PLAYLIST_URL = "https://youtube.com/playlist?list=PLED87UDh2Ybh7avvaAcNU3i4ybQ1pgLGk"
TEST_PLAYLIST_CHAPTERS_URL = "https://youtube.com/playlist?list=PLED87UDh2Ybh7avvaAcNU3i4ybQ1pgLGk" #TODO test
TEST_PLAYLIST_MIX_URLS = [
    "https://www.youtube.com/playlist?list=FIRST_ID",
    "https://www.youtube.com/playlist?list=SECOND_ID"
]

@pytest.fixture
def clean_tmp_path(tmp_path):
    yield tmp_path
    # Cleans files after tests
    for item in tmp_path.iterdir():
        if item.is_dir():
            os.rmdir(item)
        else:
            os.remove(item)

def test_single_video(clean_tmp_path):
    manager = Downloader()
    manager.default_download_path = str(clean_tmp_path)
    manager.format = "mp3"
    manager.split_chapters = False

    logger.info(f"Inizio download video: {TEST_VIDEO_URL}")
    manager.download_item(TEST_VIDEO_URL, type="single")

    assert_single_file(clean_tmp_path, ".mp3")
    logger.info("Test video singolo completato.")

def test_video_with_chapters(clean_tmp_path):
    manager = Downloader()
    manager.default_download_path = str(clean_tmp_path)
    manager.format = "mp3"
    manager.split_chapters = True

    logger.info(f"Inizio download video con capitoli: {TEST_VIDEO_CHAPTERS_URL}")
    manager.download_item(TEST_VIDEO_CHAPTERS_URL, type="chapters")

    assert_chapter_structure(clean_tmp_path, ".mp3")
    logger.info("Test video con capitoli completato.")

def test_playlist(clean_tmp_path):
    manager = Downloader()
    manager.default_download_path = str(clean_tmp_path)
    manager.format = "mp3"
    manager.split_chapters = False

    logger.info(f"Inizio download playlist: {TEST_PLAYLIST_URL}")
    manager.download_item(TEST_PLAYLIST_URL, type="playlist")

    assert_playlist_structure(clean_tmp_path, ".mp3")
    logger.info("Test playlist completato.")

def test_playlist_with_chapters(clean_tmp_path):
    manager = Downloader()
    manager.default_download_path = str(clean_tmp_path)
    manager.format = "mp3"
    manager.split_chapters = True

    logger.info(f"Inizio download playlist con capitoli: {TEST_PLAYLIST_URL}")
    manager.download_item(TEST_PLAYLIST_URL, type="playlist")

    assert_playlist_structure(clean_tmp_path, ".mp3", expect_chapters=True)
    logger.info("Test playlist con capitoli completato.")

def test_multiple_playlists(clean_tmp_path):
    manager = Downloader()
    manager.default_download_path = str(clean_tmp_path)
    manager.format = "mp3"
    manager.split_chapters = True

    for url in TEST_PLAYLIST_MIX_URLS:
        logger.info(f"Inizio download playlist multipla: {url}")
        manager.download_item(url, type="playlist")

    assert len(list(clean_tmp_path.iterdir())) == len(TEST_PLAYLIST_MIX_URLS)
    for folder in clean_tmp_path.iterdir():
        assert_playlist_structure(folder, ".mp3", expect_chapters=True)
    logger.info("Test playlist multipla completato.")