#!/usr/bin/env python3
"""喜界島まとめ動画 仮編集（歌・BGMなし、環境音のみ）をビルドする。

使い方:
    python3 scripts/build_rough.py <素材ディレクトリ> <出力ディレクトリ>

素材ディレクトリには Google Drive の2フォルダを drive1/ drive2/ として置き、
HEIC/JPG 写真は photos/<ファイル名>.jpg に変換済みであること。
"""
import json
import os
import subprocess
import sys

W, H, FPS = 1920, 1080, 30
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"

MEDIA = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
SEG = os.path.join(OUT, "segments")
os.makedirs(SEG, exist_ok=True)

D1 = "drive1"
SONY = "drive1/kikaijima sousinnyou"


def src(p):
    return os.path.join(MEDIA, p)


# 素材の短縮名
V = {
    "waves_rock": f"{SONY}/C0059.MP4",
    "waves_calm": f"{SONY}/C0056.MP4",
    "gaju39": f"{SONY}/C0039.MP4",
    "gaju40": f"{SONY}/C0040.MP4",
    "gaju41": f"{SONY}/C0041.MP4",
    "gaju43": f"{SONY}/C0043.MP4",
    "gaju45": f"{SONY}/C0045.MP4",
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


def photo(name):
    return f"photos/{name}.jpg"


# ---------------------------------------------------------------------------
# タイムライン
#   kind: "clip"（動画） / "photo"（写真） / "black"（黒画面）
#   audio: None なら素材自身の音。("key", ss) なら別素材の音を環境音として敷く
#   gain: 環境音の目標平均音量 (dBFS)
#   text: 画面に出す文字 [(文字, スタイル)]
#   xf: 次のセグメントへのクロスフェード秒数
# ---------------------------------------------------------------------------
T = []


def clip(key, ss, dur, audio=None, gain=-24, text=None, xf=0.6, zoom=0.0):
    T.append(dict(kind="clip", src=V[key], ss=ss, dur=dur, audio=audio, gain=gain,
                  text=text or [], xf=xf, zoom=zoom))


def pic(name, dur, audio, gain=-26, text=None, xf=0.6, zoom=0.07, pan="center"):
    T.append(dict(kind="photo", src=photo(name), ss=0, dur=dur, audio=audio, gain=gain,
                  text=text or [], xf=xf, zoom=zoom, pan=pan))


def black(dur, audio, gain=-26, text=None, xf=1.0):
    T.append(dict(kind="black", src=None, ss=0, dur=dur, audio=audio, gain=gain,
                  text=text or [], xf=xf, zoom=0))


# 0. フック: 黒画面に波の音だけ → 白波
black(4.0, ("waves_rock", 0), gain=-24, text=[("耳を澄ませて", "lead")], xf=1.2)
clip("waves_rock", 20, 7, gain=-21, xf=1.0)

# 1. 島へ
pic("DSC01742", 6, ("waves_calm", 0), text=[("喜界島", "title")], xf=0.8, zoom=0.06)
pic("DSC01744", 4.5, ("waves_calm", 6), xf=0.6, pan="right")
clip("highland", 0.5, 7, gain=-24, xf=1.0)

# 2. サトウキビの一本道
clip("sign", 0, 6, audio=("cane", 0), text=[("サトウキビの一本道", "place")], xf=0.6)
clip("road1", 0, 6, xf=0.6)
pic("IMG_3414", 3.5, ("road2", 0), xf=0.5)
clip("cane", 0, 6.5, xf=0.6)
clip("fields", 8, 7, audio=("road1", 1), xf=0.6, zoom=0.04)
pic("IMG_3452", 3.5, ("cane", 1.5), xf=1.0)

# 3. 海
clip("outer_sea", 2, 7, audio=("waves_rock", 2), gain=-22,
     text=[("阿伝", "place")], xf=0.6)
pic("DJI_20251019025152_0016_D", 4, ("waves_rock", 9), gain=-22, xf=0.5, pan="right")
pic("IMG_3401", 3.5, ("waves_calm", 0), xf=0.5)
pic("IMG_3398", 3.5, ("waves_calm", 4), xf=0.5)
clip("inlet", 6, 7, audio=("waves_calm", 8), xf=0.6, zoom=0.03)
pic("IMG_3374", 3.5, ("waves_calm", 15), xf=0.5)
pic("IMG_3388", 3.5, ("waves_calm", 18), xf=0.5)
pic("IMG_3392", 3.5, ("waves_rock", 14), xf=0.5)
pic("IMG_3498", 3, ("waves_rock", 18), gain=-23, xf=0.5)
pic("IMG_3502", 3, ("waves_rock", 22), xf=1.0)

# 4. 石と森
clip("coral_wall", 3, 6, audio=("gaju41", 0), gain=-27,
     text=[("サンゴの石垣", "place")], xf=0.6, zoom=0.05)
pic("IMG_3363", 3.5, ("gaju40", 0), gain=-27, xf=0.5)
pic("IMG_3366", 3, ("gaju40", 4), gain=-27, xf=0.6)
clip("gaju41", 0, 5, gain=-25, text=[("手久津久のガジュマル", "place")], xf=0.6)
clip("gaju39", 3, 6, gain=-25, xf=0.6)
clip("gaju43", 4, 7, gain=-25, xf=0.6)
clip("gaju46", 8, 6, gain=-25, xf=0.6)
pic("IMG_3455", 3.5, ("gaju45", 0), gain=-25, xf=0.5, pan="up")
pic("IMG_3443", 3, ("gaju45", 4), gain=-26, xf=0.5)
pic("IMG_3449", 3, ("gaju45", 8), gain=-26, xf=1.0)

# 5. 夕方
clip("sunset_beach", 0.5, 6, xf=0.6)
clip("sunset_grass", 0.5, 5.5, xf=0.6)
pic("IMG_3439", 3.5, ("sunset_rock", 0), xf=0.6)
clip("sunset_rock", 0.5, 7, xf=0.6)
clip("sunset_rock4k", 1.5, 8, xf=0.8)
pic("IMG_3470", 4, ("sunset_horizon", 0), text=[("百之台公園", "place")], xf=0.6)
pic("IMG_3472", 4, ("sunset_horizon", 4), xf=0.6)
pic("IMG_3476", 4, ("sunset_horizon", 8), xf=1.0)

# 6. 締め
clip("sunset_horizon", 3, 12, xf=1.2)
clip("waves_calm", 5, 8, gain=-25, xf=1.5)

# 7. エンディング（クレジット）
black(8, ("waves_calm", 13), gain=-28,
      text=[("関西学院大学　山田ゼミ作成", "credit1"), ("音声提供　○○", "credit2")], xf=0)


# ---------------------------------------------------------------------------
# セグメントのレンダリング
# ---------------------------------------------------------------------------
_meta_cache = {}


def probe(path):
    if path not in _meta_cache:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", path],
            capture_output=True, text=True, check=True).stdout
        _meta_cache[path] = json.loads(out)["streams"]
    return _meta_cache[path]


def vinfo(path):
    v = next(s for s in probe(path) if s["codec_type"] == "video")
    w, h = v["width"], v["height"]
    rot = 0
    for sd in v.get("side_data_list", []):
        if "rotation" in sd:
            rot = int(sd["rotation"])
    if rot in (90, -90, 270, -270):
        w, h = h, w
    hlg = v.get("color_transfer") == "arib-std-b67"
    return w, h, hlg


def has_audio(path):
    return any(s["codec_type"] == "audio" for s in probe(path))


_vol_cache = {}


def mean_volume(path, ss, dur):
    k = (path, ss, dur)
    if k not in _vol_cache:
        r = subprocess.run(
            ["ffmpeg", "-nostdin", "-ss", str(ss), "-t", str(dur), "-i", path,
             "-map", "0:a:0", "-af", "highpass=f=80,volumedetect", "-f", "null", "-"],
            capture_output=True, text=True)
        mv = [l for l in r.stderr.splitlines() if "mean_volume" in l]
        _vol_cache[k] = float(mv[0].split(":")[1].split()[0]) if mv else None
    return _vol_cache[k]


TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,"
           "tonemap=mobius:param=0.4:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def fit_filters(w, h, zoom, dur, pan="center"):
    """入力 [in] を 1920x1080 にし、縦長はぼかし背景を敷き、ゆっくりズームする。"""
    frames = int(round(dur * FPS))
    if w / h < 1.4:  # 縦長・正方形に近い素材
        fg_h = H
        chain = (
            f"split[a][b];"
            f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"boxblur=40:3,eq=brightness=-0.08:saturation=0.9[bg];"
            f"[b]scale=-2:{fg_h}[fg];[bg][fg]overlay=(W-w)/2:0"
        )
    else:
        chain = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    if zoom > 0:
        # 2倍に拡大してから zoompan で動かす（整数丸めによるガタつきを抑える）
        z = f"(1+{zoom}*on/{frames})"
        if pan == "right":
            x = f"(iw-iw/zoom)*on/{frames}"
            y = "(ih-ih/zoom)/2"
        elif pan == "up":
            x = "(iw-iw/zoom)/2"
            y = f"(ih-ih/zoom)*(1-on/{frames})"
        else:
            x, y = "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"
        chain += (f",scale={W*2}:{H*2}:flags=bicubic,"
                  f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS}")
    return chain


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
            fs.append(f"drawbox=x=0:y=ih-200:w=760:h=130:color=black@0.35:t=fill:enable='gte(t,0.5)*lt(t,{dur-0.3})'")
            fs.append(f"drawbox=x=80:y=ih-170:w=6:h=70:color=white@0.9:t=fill:enable='gte(t,0.5)*lt(t,{dur-0.3})'")
            fs.append(f"drawtext=fontfile={FONT}:text='{t}':fontsize=52:fontcolor=white:"
                      f"shadowcolor=black@0.7:shadowx=2:shadowy=2:x=106:y=h-162:alpha='{a}'")
        elif style in ("credit1", "credit2"):
            y = "h/2-80" if style == "credit1" else "h/2+30"
            t0 = 0.8 if style == "credit1" else 1.8
            a = f"if(lt(t,{t0}),0,if(lt(t,{t0+1}),t-{t0},if(lt(t,{dur-1.5}),1,max(0,({dur}-t)/1.5))))"
            fs.append(f"drawtext=fontfile={FONT}:text='{t}':fontsize=60:fontcolor=white:"
                      f"x=(w-tw)/2:y={y}:alpha='{a}'")
    return fs


def audio_chain(path, ss, dur, gain):
    mv = mean_volume(path, ss, dur)
    g = 0.0 if mv is None else max(-10.0, min(24.0, gain - mv))
    # 環境音を立たせる: 風の低音をカット、軽いノイズ除去、高域の存在感を少し上げ、広げる
    return (f"highpass=f=90,afftdn=nf=-30:nr=8,equalizer=f=3500:t=q:w=1:g=2.5,"
            f"volume={g:.2f}dB,extrastereo=m=1.25,"
            f"aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"apad,atrim=0:{dur},asetpts=PTS-STARTPTS")


def render(i, s):
    out = os.path.join(SEG, f"{i:03d}.mp4")
    dur = s["dur"]
    args = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y"]
    fc = []
    # 映像入力
    if s["kind"] == "black":
        args += ["-f", "lavfi", "-t", str(dur), "-i", f"color=black:s={W}x{H}:r={FPS}"]
        vchain = "[0:v]format=yuv420p"
    elif s["kind"] == "photo":
        p = src(s["src"])
        args += ["-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", p]
        from PIL import Image
        w, h = Image.open(p).size
        vchain = "[0:v]format=yuv420p," + fit_filters(w, h, s["zoom"], dur, s.get("pan", "center"))
    else:
        p = src(s["src"])
        args += ["-ss", str(s["ss"]), "-t", str(dur), "-i", p]
        w, h, hlg = vinfo(p)
        pre = (TONEMAP + ",") if hlg else ""
        vchain = (f"[0:v]{pre}fps={FPS},format=yuv420p,"
                  + fit_filters(w, h, s["zoom"], dur))
    tf = text_filters(s["text"], dur)
    vchain += ("," + ",".join(tf) if tf else "") + f",trim=0:{dur},setpts=PTS-STARTPTS,setsar=1[v]"
    fc.append(vchain)

    # 音声入力
    if s["audio"] is None and s["kind"] == "clip" and has_audio(src(s["src"])):
        apath, ass = src(s["src"]), s["ss"]
        fc.append(f"[0:a]{audio_chain(apath, ass, dur, s['gain'])}[a]")
    elif s["audio"] is not None:
        key, ass = s["audio"]
        apath = src(V[key])
        args += ["-ss", str(ass), "-t", str(dur), "-i", apath]
        fc.append(f"[1:a]{audio_chain(apath, ass, dur, s['gain'])}[a]")
    else:
        args += ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo"]
        fc.append(f"[1:a]atrim=0:{dur}[a]")

    args += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
             "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "17",
             "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", out.replace(".mp4", ".mov")]
    subprocess.run(args, check=True)
    return out.replace(".mp4", ".mov")


def main():
    only = set(int(x) for x in os.environ.get("ONLY", "").split(",") if x)
    segs = []
    for i, s in enumerate(T):
        p = os.path.join(SEG, f"{i:03d}.mov")
        if not os.path.exists(p) or (only and i in only) or os.environ.get("FORCE"):
            print(f"[{i+1}/{len(T)}] {s['kind']} {s['src']}", flush=True)
            render(i, s)
        segs.append(p)

    # クロスフェードでつなぐ
    args = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y"]
    for p in segs:
        args += ["-i", p]
    fc = []
    t = T[0]["dur"]
    vprev, aprev = "[0:v]", "[0:a]"
    for i in range(1, len(segs)):
        xf = T[i - 1]["xf"]
        if xf <= 0:
            xf = 0.04
        off = t - xf
        fc.append(f"{vprev}[{i}:v]xfade=transition=fade:duration={xf}:offset={off:.3f}[v{i}]")
        fc.append(f"{aprev}[{i}:a]acrossfade=d={xf}:c1=tri:c2=tri[a{i}]")
        vprev, aprev = f"[v{i}]", f"[a{i}]"
        t = off + T[i]["dur"]
    total = t
    fc.append(f"{vprev}fade=t=out:st={total-1.0:.3f}:d=1.0,format=yuv420p[vout]")
    fc.append(f"{aprev}loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st={total-2.5:.3f}:d=2.5,"
              f"aresample=48000[aout]")
    final = os.path.join(OUT, "kikai_rough_v1.mp4")
    args += ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
             "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", "-c:a", "aac", "-b:a", "256k", final]
    subprocess.run(args, check=True)
    print(f"done: {final} ({total:.1f}s)")


if __name__ == "__main__":
    main()
