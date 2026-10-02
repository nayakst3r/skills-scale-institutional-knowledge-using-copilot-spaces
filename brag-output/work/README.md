# Rebuilding brag.mp4

Sources for the video in `../brag.mp4`, made with the /brag-slim skill (github.com/latent-spaces/brag).

- `brag.html`: the composition; every frame is `render(t)`, a pure function of time
- `render.cjs`: renders review stills or the full video with headless Chromium + ffmpeg
- `soundtrack.py`: music and effects synthesized in one pass (120 bpm, A minor), needs numpy
- `real-output.txt`: the framework's real terminal output used on screen
- `fonts/`: Inter and JetBrains Mono (SIL Open Font License)

```bash
node render.cjs video 22.0 video-silent.mp4
python soundtrack.py
node render.cjs stills 13.9 && cp "stills/t=13.9.png" poster.png
cd .. && ffmpeg -y -i work/video-silent.mp4 -i work/poster.png -i work/soundtrack.wav \
  -filter_complex "[0:v][1:v]overlay=0:0:enable='eq(n,0)',format=yuv420p[v]" -map "[v]" -map 2:a \
  -c:v libx264 -preset slow -crf 17 -c:a aac -b:a 192k -movflags +faststart -shortest brag.mp4
```
