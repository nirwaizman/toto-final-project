#!/bin/bash
# Local assembler (server-side explainer_video is unavailable in this CLI build):
# each block = exactly 10s of clip video + voice take centered in the block
# (pitch-safe atempo only when the take exceeds 9.6s), concat, then burn Hebrew subs.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
: > build/concat.txt
python3 - <<'PY'
import json,subprocess
timing={}
for b in range(1,13):
    f=f"voices/voice{b:02d}.mp3"
    d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f],capture_output=True,text=True).stdout)
    tempo=max(1.0, d/9.6)
    eff=d/tempo
    start=(10.0-eff)/2
    timing[str(b)]={"orig":round(d,3),"tempo":round(tempo,4),"dur":round(eff,3),"start":round(start,3)}
json.dump(timing,open("build/timing.json","w"),indent=1)
print(json.dumps(timing,indent=1))
PY
for b in $(seq 1 12); do
  bb=$(printf %02d $b)
  tempo=$(python3 -c "import json;print(json.load(open('build/timing.json'))['$b']['tempo'])")
  start=$(python3 -c "import json;print(json.load(open('build/timing.json'))['$b']['start'])")
  startms=$(python3 -c "print(int(round($start*1000)))")
  ffmpeg -y -hide_banner -loglevel error -i "clips/clip$bb.mp4" -i "voices/voice$bb.mp3" \
    -filter_complex "[0:v]trim=0:10,setpts=PTS-STARTPTS,scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30[v]; \
      [0:a]atrim=0:10,asetpts=PTS-STARTPTS,volume=0.25,aformat=sample_rates=48000:channel_layouts=stereo[amb]; \
      [1:a]atempo=$tempo,adelay=${startms}|${startms},apad,atrim=0:10,asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[vo]; \
      [amb][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]" \
    -map "[v]" -map "[a]" -t 10 -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k "build/block$bb.mp4"
  echo "file 'block$bb.mp4'" >> build/concat.txt
  echo "block $b ok (tempo $tempo, start ${startms}ms)"
done
ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i build/concat.txt -c copy build/toto-explainer-nosubs.mp4
python3 subs_he.py build/timing.json build/subs_he.srt
# Burn Hebrew subtitles (PIL-rendered PNG overlays; ffmpeg here has no libass)
../../.venv/bin/python burn_subs.py build/toto-explainer-nosubs.mp4 build/subs_he.srt toto-explainer-he.mp4
ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0 toto-explainer-he.mp4
