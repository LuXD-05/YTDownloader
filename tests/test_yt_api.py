import subprocess

def test_yt_api_accessible():
    result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "20" in result.stdout