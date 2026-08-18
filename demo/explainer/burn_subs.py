"""Burn Hebrew subtitles without libass: render each cue as a transparent PNG (PIL + bidi)
and overlay it on the video with ffmpeg overlay+enable. Usage: burn_subs.py in.mp4 subs.srt out.mp4"""
import re, sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
W, H = 1280, 720
FONT = "/Library/Fonts/Arial Unicode.ttf"
if not os.path.exists(FONT): FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
font = ImageFont.truetype(FONT, 34)
def parse(srt):
    cues=[]
    for m in re.finditer(r"(\d+)\n(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)\n(.+?)(?:\n\n|\Z)", open(srt,encoding="utf-8").read(), re.S):
        g=list(map(int,m.groups()[1:9])); a=g[0]*3600+g[1]*60+g[2]+g[3]/1000; b=g[4]*3600+g[5]*60+g[6]+g[7]/1000
        cues.append((a,b,m.group(10).strip()))
    return cues
def render(text, path):
    vis=get_display(text, base_dir='R')
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    bbox=d.textbbox((0,0),vis,font=font); tw,th=bbox[2]-bbox[0], bbox[3]-bbox[1]
    x=(W-tw)//2; y=H-58-th
    pad=14
    d.rounded_rectangle([x-pad,y-pad+2,x+tw+pad,y+th+pad+2],radius=10,fill=(15,23,42,190))
    for dx,dy in [(-1,-1),(1,-1),(-1,1),(1,1),(0,2)]:
        d.text((x+dx-bbox[0],y+dy-bbox[1]),vis,font=font,fill=(0,0,0,220))
    d.text((x-bbox[0],y-bbox[1]),vis,font=font,fill=(255,255,255,255))
    img.save(path)
def main(inp, srt, out):
    cues=parse(srt); os.makedirs("build/subs",exist_ok=True)
    args=["ffmpeg","-y","-hide_banner","-loglevel","error","-i",inp]
    for i,(a,b,t) in enumerate(cues):
        p=f"build/subs/cue{i:03d}.png"; render(t,p); args+=["-i",p]
    fc=""; prev="[0:v]"
    for i,(a,b,t) in enumerate(cues):
        nxt=f"[v{i}]" if i<len(cues)-1 else "[vout]"
        fc+=f"{prev}[{i+1}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'{nxt};"
        prev=nxt
    args+=["-filter_complex",fc.rstrip(";"),"-map","[vout]","-map","0:a","-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-c:a","copy",out]
    subprocess.run(args,check=True); print("burned",len(cues),"cues ->",out)
if __name__=="__main__": main(*sys.argv[1:4])
