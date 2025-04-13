# yt-dlp 如何下载 webm 和 ogg.md

## 下载 webm

```bash
uv run yt-dlp -f 251 "https://music.youtube.com/watch?v=zON6tyIp5wA"
```

-f 251：指定下载 YouTube 上通常用于 Opus 音频的特定格式代码。

## 下载 Ogg Vorbis

```bash
uv run yt-dlp -x --audio-format vorbis --ffmpeg-location ".venv\share\ffpyplayer\ffmpeg\bin" "https://music.youtube.com/watch?v=zON6tyIp5wA"
```

注意，用了 `-x` 就需要指定 ffmpeg 地址。