#!/usr/bin/env python3
"""喜界島まとめ動画 v2 をビルドする。

- 音楽（支給音源）を全編に流し、現地音は波の音のシーンだけ残す
- 曲の構成（イントロ・盛り上がり・間奏・アウトロ）にセクションの切れ目を合わせる
- スマホの縦動画・縦写真は 16:9 いっぱいに切り出す。動画は手ぶれ補正と色合わせもする

使い方:
    python3 scripts/build_v2.py <素材ディレクトリ> <出力ディレクトリ>

素材ディレクトリには Google Drive の2フォルダを drive1/ drive2/ として置き、
HEIC/JPG 写真は photos/<ファイル名>.jpg に変換済み、音楽は song.m4a に置くこと。
"""
import json
import os
import subprocess
import sys

W, H, FPS = 1920, 1080, 30
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"

MEDIA = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
SEG = os.path.join(OUT, "segments_v2")
os.makedirs(SEG, exist_ok=True)

D1 = "drive1"
SONY = "drive1/kikaijima sousinnyou"
MUSIC = "song.m4a"


def src(p):
    return os.path.join(MEDIA, p)


V = {
    "waves_rock": f"{SONY}/C0059.MP4",
    "waves_calm": f"{SONY}/C0056.MP4",
    "gaju39": f"{SONY}/C0039.MP4",
    "gaju40": f"{SONY}/C0040.MP4",
    "gaju41": f"{SONY}/C0041.MP4",
    "gaju42": f"{SONY}/C0042.MP4",
    "gaju43": f"{SONY}/C0043.MP4",
    "gaju44": f"{SONY}/C0044.MP4",
    "gaju46": f"{SONY}/C0046.MP4",
    "sign": f"{D1}/2226C5C9E9421A7E237C6B43B9A39DE426C7FEF6.mp4",
    "fields": f"{D1}/Video Project 4.mp4",
    "coral_wall": f"{D1}/Video Project 2 (1).mp4",
    "outer_sea": f"{D1}/Video Project 4(3).mp4",
    "inlet": f"{D1}/Video Project 4 (1).mp4",
    "road1": f"{D1}/IMG_3416.MOV",
    "road2": f"{D1}/IMG_3421.MOV",
    "cane": f"{D1}/IMG_3419.MOV",
    "sunset_grass": f"{D1}/IMG_3432.MOV",
    "sunset_beach": f"{D1}/IMG_3436.MOV",
    "sunset_rock": f"{D1}/IMG_3437.MOV",
    "sunset_rock4k": f"{D1}/IMG_3438.MOV",
    "highland": f"{D1}/IMG_3469.MOV",
    "sunset_horizon": f"{D1}/IMG_3471.MOV",
}

# ---------------------------------------------------------------------------
# タイムライン
#   wave: None なら無音。("key", ss, dB) なら波の音をその平均音量で敷く
#   cy: 縦素材を切り出す縦位置（0=上端, 1=下端）。写真は (開始, 終了) でパン
#   xf: 次のセグメントへのクロスフェード秒数
#   mark(t): 直前のセグメントの長さを調整し、切れ目を曲の t 秒に合わせる
# ---------------------------------------------------------------------------
T = []


def clip(key, ss, dur, wave=None, text=None, xf=0.6, zoom=0.0, cy=0.5):
    T.append(dict(kind="clip", src=V[key], ss=ss, dur=dur, wave=wave, text=text or [],
                  xf=xf, zoom=zoom, cy=cy))


def pic(name, dur, wave=None, text=None, xf=0.6, zoom=0.06, pan="center", cy=(0.35, 0.6)):
    T.append(dict(kind="photo", src=f"photos/{name}.jpg", ss=0, dur=dur, wave=wave,
                  text=text or [], xf=xf, zoom=zoom, pan=pan, cy=cy))


def black(dur, wave=None, text=None, xf=1.0):
    T.append(dict(kind="black", src=None, ss=0, dur=dur, wave=wave, text=text or [],
                  xf=xf, zoom=0))


def timeline_end():
    t = 0.0
    for i, s in enumerate(T):
        start = 0.0 if i == 0 else t - T[i - 1]["xf"]
        t = start + s["dur"]
    return t


def mark(t):
    """直前のセグメントの終わり（クロスフェードの中央）が曲の t 秒に来るよう伸縮する。"""
    end = timeline_end() - T[-1]["xf"] / 2
    T[-1]["dur"] = round(T[-1]["dur"] + (t - end), 3)
    assert T[-1]["dur"] > 1.5, (T[-1], t)


WAVE_HI, WAVE_MID, WAVE_LO = -24, -30, -34

# 0. イントロ（〜12.6秒）: 黒画面に波の音 → 白波
black(4.5, ("waves_rock", 0, WAVE_HI), text=[("耳を澄ませて", "lead")], xf=1.2)
clip("waves_rock", 18, 8, ("waves_rock", 18, WAVE_HI), xf=1.0)
mark(12.6)

# 1. 島へ（〜36.2秒）
pic("DSC01742", 6.5, text=[("喜界島", "title")], xf=0.8, zoom=0.06)
pic("DSC01743", 4.5, pan="right", zoom=0.05)
pic("DSC01744", 4.5, zoom=0.05)
clip("highland", 1, 5, cy=0.55)
pic("DSC01746", 5, pan="right", xf=1.0)
mark(36.2)

# 2. サトウキビの一本道（〜73.5秒）
clip("sign", 0, 6, text=[("サトウキビの一本道", "place")])
clip("road1", 0.3, 5, cy=0.55)
pic("IMG_3422", 3.5, cy=(0.5, 0.6))
clip("road2", 0.2, 4.5, cy=0.55)
clip("cane", 0, 5, cy=0.6)
clip("fields", 8, 7, zoom=0.04)
pic("IMG_3452", 3.5, cy=(0.45, 0.6))
pic("IMG_3415", 4, cy=(0.45, 0.6), xf=1.0)
mark(73.5)

# 3. 海（〜118.6秒）: 波の音あり
clip("outer_sea", 2, 7, ("waves_rock", 2, WAVE_MID))
pic("DJI_20251019025152_0016_D", 4, ("waves_rock", 9, WAVE_MID), pan="right", xf=0.5)
pic("IMG_3401", 3.5, ("waves_calm", 0, WAVE_MID), cy=(0.4, 0.6), xf=0.5)
pic("IMG_3398", 3.5, ("waves_calm", 4, WAVE_MID), cy=(0.4, 0.6), xf=0.5)
pic("IMG_3397", 3, ("waves_calm", 8, WAVE_MID), cy=(0.4, 0.6), xf=0.5)
clip("inlet", 6, 7, ("waves_calm", 11, WAVE_MID), zoom=0.03)
pic("IMG_3374", 3.5, ("waves_calm", 18, WAVE_MID), cy=(0.4, 0.6), xf=0.5)
pic("IMG_3388", 3.5, ("waves_rock", 14, WAVE_MID), cy=(0.4, 0.6), xf=0.5)
pic("IMG_3392", 3.5, ("waves_rock", 18, WAVE_MID), cy=(0.4, 0.6), xf=0.5)
pic("IMG_3498", 3, ("waves_rock", 22, WAVE_MID), cy=(0.45, 0.65), xf=0.5)
pic("IMG_3502", 3, ("waves_rock", 26, WAVE_MID), cy=(0.45, 0.65), xf=0.5)
pic("IMG_3496", 3.5, ("waves_rock", 30, WAVE_MID), cy=(0.45, 0.65), xf=1.0)
mark(118.6)

# 4. 石と森（〜184.4秒）
clip("coral_wall", 3, 6, text=[("サンゴの石垣", "place")], zoom=0.05)
pic("IMG_3363", 3.5, cy=(0.3, 0.55), xf=0.5)
pic("IMG_3366", 3, cy=(0.3, 0.55), xf=0.5)
pic("IMG_3369", 3, cy=(0.4, 0.6))
clip("gaju41", 0, 5, text=[("手久津久のガジュマル", "place")])
clip("gaju44", 0.5, 5)
clip("gaju39", 3, 6)
clip("gaju42", 1, 5)
clip("gaju43", 4, 7)
clip("gaju40", 8, 6)
clip("gaju46", 8, 6)
pic("IMG_3455", 3.5, pan="up", cy=(0.6, 0.25), xf=0.5)
pic("IMG_3453", 3, cy=(0.3, 0.5), xf=0.5)
pic("IMG_3443", 3, cy=(0.4, 0.55), xf=0.5)
pic("IMG_3442", 3, cy=(0.4, 0.55), xf=0.5)
pic("IMG_3449", 3, cy=(0.35, 0.55), xf=0.5)
pic("IMG_3447", 3.5, cy=(0.3, 0.5), xf=1.0)
mark(184.4)

# 5. 間奏（〜210秒）: 静かな部分。波の音を大きめに
clip("waves_calm", 2, 12, ("waves_calm", 2, WAVE_HI), zoom=0.03)
pic("DJI_20251019025156_0017_D", 5, ("waves_rock", 34, WAVE_HI), pan="right")
pic("IMG_3527", 4, ("waves_calm", 14, WAVE_HI), cy=(0.4, 0.6))
pic("IMG_3528", 4, ("waves_calm", 18, WAVE_HI), cy=(0.4, 0.6), xf=1.0)
mark(210.0)

# 6. 夕方・クライマックス（〜255秒）: 夕日の波打ち際の音を小さく残す
clip("sunset_beach", 0.5, 5, ("sunset_beach", 0.5, WAVE_LO), cy=0.6)
clip("sunset_grass", 0.5, 5, ("sunset_grass", 0.5, WAVE_LO), cy=0.55)
pic("IMG_3433", 3.5, ("sunset_grass", 1, WAVE_LO), cy=(0.4, 0.55), xf=0.5)
pic("IMG_3439", 3.5, ("sunset_rock", 0, WAVE_LO), cy=(0.4, 0.55), xf=0.5)
clip("sunset_rock", 0.5, 6, ("sunset_rock", 0.5, WAVE_LO), cy=0.55)
clip("sunset_rock4k", 1.5, 7, ("sunset_rock4k", 1.5, WAVE_LO), cy=0.55)
pic("IMG_3440", 3.5, ("sunset_rock4k", 8, WAVE_LO), cy=(0.4, 0.55), xf=0.5)
pic("IMG_3470", 4, text=[("百之台公園", "place")], cy=(0.45, 0.6))
pic("IMG_3472", 4, cy=(0.4, 0.55))
pic("IMG_3474", 4, cy=(0.4, 0.55))
pic("IMG_3476", 4, cy=(0.35, 0.5), xf=1.0)
mark(255.0)

# 7. アウトロ（〜曲の終わり）とクレジット
clip("sunset_horizon", 2, 10, ("sunset_horizon", 2, WAVE_MID), cy=0.5, xf=1.5)
mark(264.0)
black(13, ("waves_rock", 36, WAVE_MID),
      text=[("関西学院大学　山田ゼミ作成", "credit1"), ("音声提供　サンゴの命～喜界島～", "credit2"),
            ("制作　土岐宏大", "credit3")], xf=0)


# ---------------------------------------------------------------------------
# レンダリング
# ---------------------------------------------------------------------------
_meta = {}


def probe(path):
    if path not in _meta:
        out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json",
                              "-show_streams", path], capture_output=True, text=True, check=True).stdout
        _meta[path] = json.loads(out)["streams"]
    return _meta[path]


def vinfo(path):
    v = next(s for s in probe(path) if s["codec_type"] == "video")
    w, h = v["width"], v["height"]
    rot = 0
    for sd in v.get("side_data_list", []):
        if "rotation" in sd:
            rot = int(sd["rotation"])
    if rot in (90, -90, 270, -270):
        w, h = h, w
    return w, h, v.get("color_transfer") == "arib-std-b67"


def mean_volume(path, ss, dur):
    r = subprocess.run(["ffmpeg", "-nostdin", "-ss", str(ss), "-t", str(dur), "-i", path,
                        "-map", "0:a:0", "-af", "highpass=f=90,volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    mv = [l for l in r.stderr.splitlines() if "mean_volume" in l]
    return float(mv[0].split(":")[1].split()[0]) if mv else None


# iPhone の HLG(HDR) を SDR に変換し、他の素材と色味をそろえる
TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,"
           "tonemap=mobius:param=0.4:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
           "eq=contrast=1.07:saturation=1.15:gamma=0.96")


def fit(w, h, s, dur):
    frames = max(1, int(round(dur * FPS)))
    zoom, pan, cy = s["zoom"], s.get("pan", "center"), s["cy"]
    if w / h < 1.4:
        # 縦長: 横幅いっぱいに拡大して 16:9 に切り出す
        y0, y1 = (cy, cy) if not isinstance(cy, tuple) else cy
        ch = f"scale={W}:-2,crop={W}:{H}:0:'(ih-{H})*({y0}+({y1}-{y0})*n/{frames})'"
        if s["kind"] == "photo":
            zoom = 0.03
    else:
        ch = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    if zoom > 0:
        z = f"(1+{zoom}*on/{frames})"
        if pan == "right":
            x, y = f"(iw-iw/zoom)*on/{frames}", "(ih-ih/zoom)/2"
        else:
            x, y = "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"
        ch += f",scale={W*2}:{H*2}:flags=bicubic,zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS}"
    return ch


def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def text_filters(texts, dur):
    fs = []
    for t, style in texts:
        t = esc(t)
        if style == "title":
            a = f"if(lt(t,0.8),0,if(lt(t,1.8),t-0.8,if(lt(t,{dur-1}),1,max(0,{dur}-t))))"
            fs.append(f"drawtext=fontfile={FONT}:text='{t}':fontsize=150:fontcolor=white:"
                      f"shadowcolor=black@0.6:shadowx=4:shadowy=4:x=(w-tw)/2:y=(h-th)/2:alpha='{a}'")
        elif style == "lead":
            a = f"if(lt(t,0.6),0,if(lt(t,1.6),t-0.6,if(lt(t,{dur-1.2}),1,max(0,({dur}-t)/1.2))))"
            fs.append(f"drawtext=fontfile={FONT}:text='{t}':fontsize=56:fontcolor=white:"
                      f"x=(w-tw)/2:y=(h-th)/2:alpha='{a}'")
        elif style == "place":
            a = f"if(lt(t,0.5),0,if(lt(t,1.3),(t-0.5)/0.8,if(lt(t,{dur-0.8}),1,max(0,({dur}-t)/0.8))))"
            en = f"enable='gte(t,0.5)*lt(t,{dur-0.3})'"
            fs.append(f"drawbox=x=0:y=ih-200:w=760:h=130:color=black@0.35:t=fill:{en}")
            fs.append(f"drawbox=x=80:y=ih-170:w=6:h=70:color=white@0.9:t=fill:{en}")
            fs.append(f"drawtext=fontfile={FONT}:text='{t}':fontsize=52:fontcolor=white:"
                      f"shadowcolor=black@0.7:shadowx=2:shadowy=2:x=106:y=h-162:alpha='{a}'")
        elif style in ("credit1", "credit2", "credit3"):
            y = {"credit1": "h/2-130", "credit2": "h/2-10", "credit3": "h/2+80"}[style]
            t0 = {"credit1": 0.8, "credit2": 1.8, "credit3": 2.3}[style]
            a = f"if(lt(t,{t0}),0,if(lt(t,{t0+1}),t-{t0},if(lt(t,{dur-2}),1,max(0,({dur}-t)/2))))"
            fs.append(f"drawtext=fontfile={FONT}:text='{t}':fontsize=60:fontcolor=white:"
                      f"x=(w-tw)/2:y={y}:alpha='{a}'")
    return fs


def stabilize_trf(path, ss, dur, i):
    """手持ちのスマホ動画の手ぶれ補正用に動きを解析する（vidstab 1パス目）。"""
    trf = os.path.join(SEG, f"{i:03d}.trf")
    if not os.path.exists(trf):
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", str(ss),
                        "-t", str(dur), "-i", path, "-vf",
                        f"vidstabdetect=shakiness=6:accuracy=12:result={trf}",
                        "-f", "null", "-"], check=True)
    return trf


def render(i, s):
    out = os.path.join(SEG, f"{i:03d}.mov")
    dur = s["dur"]
    args = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y"]
    if s["kind"] == "black":
        args += ["-f", "lavfi", "-t", str(dur), "-i", f"color=black:s={W}x{H}:r={FPS}"]
        v = "[0:v]format=yuv420p"
    elif s["kind"] == "photo":
        p = src(s["src"])
        args += ["-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", p]
        from PIL import Image
        w, h = Image.open(p).size
        v = "[0:v]format=yuv420p," + fit(w, h, s, dur)
    else:
        p = src(s["src"])
        args += ["-ss", str(s["ss"]), "-t", str(dur), "-i", p]
        w, h, hlg = vinfo(p)
        pre = ""
        if hlg:
            trf = stabilize_trf(p, s["ss"], dur, i)
            # 補正後、少し拡大して端の揺れを隠す
            pre = (f"{TONEMAP},vidstabtransform=input={trf}:smoothing=20:zoom=4:"
                   f"optzoom=0:interpol=bicubic,")
        v = f"[0:v]{pre}fps={FPS},format=yuv420p," + fit(w, h, s, dur)
    tf = text_filters(s["text"], dur)
    v += ("," + ",".join(tf) if tf else "") + f",trim=0:{dur},setpts=PTS-STARTPTS,setsar=1[v]"
    fc = [v]

    if s["wave"]:
        key, ass, target = s["wave"]
        ap = src(V[key])
        mv = mean_volume(ap, ass, dur)
        g = 0.0 if mv is None else max(-10.0, min(24.0, target - mv))
        args += ["-ss", str(ass), "-t", str(dur), "-i", ap]
        fc.append(f"[1:a]highpass=f=90,afftdn=nf=-30:nr=8,equalizer=f=3500:t=q:w=1:g=2.5,"
                  f"volume={g:.2f}dB,extrastereo=m=1.25,aresample=48000,"
                  f"aformat=sample_fmts=fltp:channel_layouts=stereo,apad,atrim=0:{dur},"
                  f"asetpts=PTS-STARTPTS[a]")
    else:
        args += ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo"]
        fc.append(f"[1:a]aformat=sample_fmts=fltp:channel_layouts=stereo,atrim=0:{dur}[a]")

    args += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-r", str(FPS),
             "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
             "-c:a", "pcm_s16le", "-ar", "48000", out]
    subprocess.run(args, check=True)
    return out


def main():
    only = set(int(x) for x in os.environ.get("ONLY", "").split(",") if x)
    segs = []
    for i, s in enumerate(T):
        p = os.path.join(SEG, f"{i:03d}.mov")
        if not os.path.exists(p) or i in only or os.environ.get("FORCE"):
            print(f"[{i+1}/{len(T)}] {s['kind']} {s['src']} {s['dur']:.2f}s", flush=True)
            render(i, s)
        segs.append(p)

    args = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y"]
    for p in segs:
        args += ["-i", p]
    args += ["-i", src(MUSIC)]
    fc = []
    t = T[0]["dur"]
    vprev, aprev = "[0:v]", "[0:a]"
    for i in range(1, len(segs)):
        xf = max(T[i - 1]["xf"], 0.04)
        off = t - xf
        fc.append(f"{vprev}[{i}:v]xfade=transition=fade:duration={xf}:offset={off:.3f}[v{i}]")
        fc.append(f"{aprev}[{i}:a]acrossfade=d={xf}:c1=tri:c2=tri[a{i}]")
        vprev, aprev = f"[v{i}]", f"[a{i}]"
        t = off + T[i]["dur"]
    total = t
    m = len(segs)
    fc.append(f"{vprev}fade=t=out:st={total-1.5:.3f}:d=1.5,format=yuv420p[vout]")
    # 音楽が主役。波の音はその下に重ねる
    fc.append(f"[{m}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
              f"apad,atrim=0:{total}[mus]")
    fc.append(f"{aprev}aformat=sample_fmts=fltp:channel_layouts=stereo[amb]")
    fc.append(f"[mus][amb]amix=inputs=2:normalize=0:duration=first,"
              f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={total-3:.3f}:d=3,"
              f"aresample=48000[aout]")
    final = os.path.join(OUT, "kikai_v2.mp4")
    args += ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
             "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", "-c:a", "aac", "-b:a", "256k", final]
    subprocess.run(args, check=True)
    print(f"done: {final} ({total:.1f}s)")


if __name__ == "__main__":
    if os.environ.get("PLAN"):
        t = 0.0
        for i, s in enumerate(T):
            start = 0.0 if i == 0 else t - T[i - 1]["xf"]
            t = start + s["dur"]
            print(f"{i:3d} {start:7.2f} {s['dur']:6.2f} {s['kind']:5s} {s['src']}")
        print("total", round(t, 2))
    else:
        main()
