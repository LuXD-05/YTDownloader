import subprocess

def test_search_with_url():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = subprocess.run(["yt-dlp", "--print", "%(title)s", url], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Rick" in result.stdout  # ovviamente dipende dal video

def test_search_with_term():
    term = "ytsearch:rick astley never gonna give you up"
    result = subprocess.run(["yt-dlp", "--print", "%(title)s", term], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Rick" in result.stdout