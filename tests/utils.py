from pathlib import Path

def assert_single_file(path: Path, ext: str):
    files = list(path.glob(f"*{ext}"))
    assert len(files) == 1, f"Expected 1 {ext} file, got {len(files)}: {files}"

def assert_chapter_structure(path: Path, ext: str):
    subdirs = list(path.iterdir())
    assert len(subdirs) == 1 and subdirs[0].is_dir(), "Expected one directory for chapter split"
    chapter_files = list(subdirs[0].glob(f"*{ext}"))
    assert len(chapter_files) > 1, f"Expected multiple chapter files in {ext}, got {len(chapter_files)}"

def assert_playlist_structure(path: Path, ext: str, expect_chapters=False):
    playlist_dirs = list(path.iterdir())
    assert any(p.is_dir() for p in playlist_dirs), "Expected at least one playlist folder"
    for item in playlist_dirs:
        if item.is_dir():
            if expect_chapters:
                # At least one file or one folder with mp3s
                for sub in item.iterdir():
                    if sub.is_dir():
                        assert any(sub.glob(f"*{ext}")), f"No chapter files in {sub}"
                    else:
                        assert sub.suffix == ext
            else:
                assert any(item.glob(f"*{ext}")), f"No media files in {item}"