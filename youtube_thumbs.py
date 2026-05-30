# -*- coding: utf-8 -*-
"""Rellena fotos usando miniaturas de YouTube de videos de receta.
Solo toca recetas con imagen GENERICA (imgs/) o sin imagen — nunca las que ya
tienen foto propia (imgs_recipes/), para no pisar las fotos elegidas por Rafa.
Descarta miniaturas con CARAS (OpenCV) para evitar fotos de personas.
Idempotente.
"""
import json, os, re, time, io
import numpy as np, cv2
import download_dish_images as d

APP = r"C:\Users\Rafa\recetario-romanesc"
RJSON = os.path.join(APP, "recipes.json")
IMGDIR = os.path.join(APP, "imgs_recipes")

CASC = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
def has_face(im):
    try:
        g = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
        f = CASC.detectMultiScale(g, scaleFactor=1.1, minNeighbors=6, minSize=(55, 55))
        return len(f) > 0
    except Exception:
        return True  # ante la duda, descartar

def yt_ids(q):
    try:
        r = d.S.get("https://www.youtube.com/results", params={"search_query": q},
                    timeout=25, headers={"Accept-Language": "ro-RO,ro;q=0.9"})
        seen = []
        for x in re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text):
            if x not in seen:
                seen.append(x)
        return seen
    except Exception:
        return []

def thumb(vid):
    for q in ("maxresdefault", "hqdefault"):
        im = d.fetch(f"https://img.youtube.com/vi/{vid}/{q}.jpg")
        if im and im.width >= 400:
            return im
    return None

def clean_query(nume):
    n = re.sub(r"\(.*?\)", "", nume)            # quita "(10 min)" etc
    n = re.sub(r"\s+", " ", n).strip()
    return n + " reteta"

def main():
    data = json.load(open(RJSON, encoding="utf-8"))
    targets = [r for r in data if (not r["img"]) or r["img"].startswith("imgs/")]
    print(f"objetivo (genericas/sin foto): {len(targets)}", flush=True)
    got = miss = 0
    done = 0
    for r in data:
        if not ((not r["img"]) or r["img"].startswith("imgs/")):
            continue
        done += 1
        sl = d.slug(r["nume"]); dst = os.path.join(IMGDIR, sl + ".jpg")
        if os.path.exists(dst) and os.path.getsize(dst) > 4000:
            r["img"] = "imgs_recipes/" + sl + ".jpg"; continue
        ids = yt_ids(clean_query(r["nume"]))
        chosen = None
        for vid in ids[:8]:
            im = thumb(vid)
            if not im:
                continue
            if has_face(im):
                continue
            chosen = im
            break
        if chosen:
            if chosen.width > 900:
                chosen = chosen.resize((900, int(chosen.height * 900 / chosen.width)))
            chosen.save(dst, "JPEG", quality=84)
            r["img"] = "imgs_recipes/" + sl + ".jpg"
            got += 1
        else:
            miss += 1
        if done % 15 == 0:
            print(f"  {done}/{len(targets)}  yt_ok={got} sin={miss}", flush=True)
            json.dump(data, open(RJSON, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        time.sleep(0.2)
    json.dump(data, open(RJSON, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    real = sum(1 for x in data if x["img"] and x["img"].startswith("imgs_recipes"))
    print(f"\nFIN. nuevas_yt={got} sin={miss} | total foto propia: {real}/{len(data)}", flush=True)

if __name__ == "__main__":
    main()
