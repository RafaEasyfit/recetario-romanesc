# -*- coding: utf-8 -*-
"""Descarga una foto real de COMIDA (Openverse, licencia abierta) para cada receta
sin foto propia. Busca con contexto de comida y valida que el resultado sea comida;
si no hay coincidencia clara, NO pone foto (se rellena luego con genérica).
Idempotente: si ya existe imgs_recipes/<slug>.jpg no la vuelve a bajar.
"""
import json, os, re, time, unicodedata, io
import requests, urllib3
from PIL import Image
urllib3.disable_warnings()

APP = r"C:\Users\Rafa\recetario-romanesc"
RJSON = os.path.join(APP, "recipes.json")
IMGDIR = os.path.join(APP, "imgs_recipes")
os.makedirs(IMGDIR, exist_ok=True)

S = requests.Session(); S.verify = False
S.headers.update({"User-Agent": "recetario-romanesc/1.0 (personal recipe app)"})

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()

def low(s):
    return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode().lower()

FILLER = {"light","usor","usoara","usoare","rapid","rapida","rapide","reteta","retete",
          "traditional","traditionala","traditionale","dietetic","dietetica","dietetice",
          "proteic","proteica","proteice","sanatos","sanatoasa","sanatoase","clasic","clasica",
          "simplu","simpla","de","post","la","cuptor","tava","gratar","casa","mod","stil",
          "fara","crocant","crocanta","cremos","cremoasa","aromat",
          "bunica","bunicii","mamei","taranesc","taraneasca","taranesti","ardelenesc","ardeleneasca",
          "ardelenesti","moldovenesc","moldoveneasca","banatean","oltenesc","transilvanean","verde","rosu"}

# tipo de plato -> UNA palabra de contexto de comida en INGLÉS (Openverse/Flickr usan inglés)
TYPE = [
    (["sarmale"], "food"),
    (["smoothie","shake"], "smoothie"),
    (["clatite","clătite","pancake","gogosi"], "pancakes"),
    (["mamalig","mămălig","balmos","polenta"], "polenta"),
    (["tort","prajitur","prăjitur","ecler","profiterol","cremsnit","papanas","papanaș","amandin",
      "negres","briosa","chec","tarta","tartă","fursec","cornulet","sarailie","baclava","savarin",
      "budinca","cheesecake","muffin","desert","cozonac","faguri"], "dessert"),
    (["omleta","omletă","oua","ouă","ochiuri","jumari","frittata"], "eggs"),
    (["iaurt","branza","brânză","telemea","smantana","smântână","cottage","kefir"], "cheese"),
    (["peste","pește","somon","crap","scrumbie","ton","nisetru","icre","storceag","plachie",
      "saramura","macrou","hering","pastrav","creveti"], "fish"),
    (["paste","spaghete","lasagna","lasagne","fidea","macaroane","penne","gnocchi"], "pasta"),
    (["orez","risotto","pilaf"], "rice"),
    (["hummus","naut","năut","linte","mazare","mazăre"], "food"),
    (["fasole","iahnie"], "beans"),
    (["bol","buddha","taco","mexican","burrito","poke"], "food"),
    (["ciorba","ciorbă","bors","borș","supa","supă","zeama","zeamă"], "soup"),
    (["salata","salată"], "salad"),
    (["wrap","sandwich","lipie","lipii","toast","bruschet","tartine","burger","quesadilla"], "sandwich"),
    (["pate","pastă de","pasta de","mujdei","guacamole","zacusca","dip","tapenade"], "food"),
    (["ghiveci","tocana","tocăniț","tocanit","tochitur","ostropel","mancare","mâncare","ardei umplut",
      "dovlecei","vinete","musaca","legume","ciuperci","ratatouille"], "food"),
    (["pui","curcan","gaina","găină"], "chicken"),
    (["porc","vita","vită","friptur","muschi","mușchi","ceaf","cotlet","mici","mititei","carne",
      "snitel","șnițel","chiftel","parjoale","drob","rasol","gulas","caltabos","pomana","stufat"], "meat"),
]
def food_ctx(nume):
    n = low(nume)
    for kws, ctx in TYPE:
        for kw in kws:
            if low(kw) in n:
                return ctx
    return "food"

# palabras que confirman que el resultado ES comida
FOOD_WORDS = {"food","dish","meal","soup","salad","dessert","cake","sweet","meat","chicken","beef",
 "pork","fish","seafood","recipe","cuisine","cooking","cook","vegetable","veggie","pasta","rice",
 "bread","cheese","dairy","egg","fruit","breakfast","lunch","dinner","snack","pancake","pie","stew",
 "dumpling","sauce","dip","spread","drink","smoothie","vegan","vegetarian","homemade","kitchen","eat",
 "tasty","delicious","gastronom","mancare","reteta","romanian","moldovan","baking","baked","bake","grill",
 "roast","fried","fry","plate","bowl","dough","cream","yogurt","yoghurt","bean","legume","tomato","potato",
 "salmon","tuna","soup","polenta","wrap","sandwich","brunch","appetizer","cabbage","mushroom","lentil",
 "chickpea","pizza","pastry","donut","doughnut","pudding","custard","jam","honey","nuts","seeds","oat"}

# palabras que indican que NO es comida (rechazo aunque cuele una palabra de comida)
NEG_WORDS = {"auditori","auditorium","signature","portrait","building","church","temple","monument",
 "conference","meeting","politician","president","mayor","minister","stadium","museum","statue",
 "painting","sculpture","logo","map","flag","street","city","skyline","landscape","mountain","beach",
 "car","vehicle","aircraft","airplane","train","bridge","castle","cathedral","palace","wedding","funeral",
 "concert","band","actor","singer","celebrity","award","ceremony","graduation","office","desk","computer",
 "phone","football","soccer","basketball","tennis","racing","military","soldier","weapon","coin","stamp",
 "banknote","document","book cover","poster","movie","film","tv series","cartoon","anime","manga",
 "presiden","politic","diplomac","embassy","parliament","senate","congress","official","summit",
 "ceremoni","mesa president","acte de","speech","interview","press","protest","election","campaign",
 "uniform","general","army","navy","police","hospital","school","university","library"}

def is_food(res):
    txt = low(res.get("title") or "")
    tags = " ".join(low(t.get("name","")) for t in (res.get("tags") or []))
    blob = txt + " " + tags
    if any(w in blob for w in NEG_WORDS):
        return False
    return any(w in blob for w in FOOD_WORDS)

def queries(nume):
    base = low(nume); base = re.sub(r"[^a-z0-9 ]+"," ",base); base = re.sub(r"\s+"," ",base).strip()
    ctx = food_ctx(nume)
    qs = []
    words = [w for w in base.split() if w not in FILLER]
    name = " ".join(words)
    cut = re.split(r"\bcu\b", base)[0].strip()
    cw = [w for w in cut.split() if w not in FILLER]
    cutname = " ".join(cw)
    def add(q):
        if q and q not in qs and len(q) >= 3: qs.append(q)
    add(name + " " + ctx)      # nombre + 1 palabra contexto (desambigua)
    add(name)                  # nombre solo (suele ser el más fiel; is_food filtra no-comida)
    if cutname != name:
        add(cutname + " " + ctx)   # plato base (antes de 'cu') + contexto
        add(cutname)
    return qs

def search(q):
    try:
        r = S.get("https://api.openverse.org/v1/images/",
                  params={"q": q, "page_size": 6, "mature": "false"}, timeout=25)
        if r.status_code == 429: time.sleep(5); return []
        return r.json().get("results", [])
    except Exception:
        return []

def fetch(url):
    try:
        r = S.get(url, timeout=25)
        if r.status_code != 200 or len(r.content) < 4000: return None
        im = Image.open(io.BytesIO(r.content)).convert("RGB")
        if im.width < 350 or im.height < 250: return None
        if im.width > 900: im = im.resize((900, int(im.height*900/im.width)), Image.LANCZOS)
        return im
    except Exception:
        return None

def main():
    data = json.load(open(RJSON, encoding="utf-8"))
    targets = [r for r in data if (not r["img"]) or r["img"].startswith("imgs/")]
    print(f"objetivo: {len(targets)} recetas sin foto propia", flush=True)
    got = miss = skip = 0
    done = 0
    for r in data:
        if not ((not r["img"]) or r["img"].startswith("imgs/")):
            continue
        sl = slug(r["nume"]); dst = os.path.join(IMGDIR, sl + ".jpg")
        if os.path.exists(dst) and os.path.getsize(dst) > 4000:
            r["img"] = "imgs_recipes/" + sl + ".jpg"; skip += 1; done += 1; continue
        found = False
        for q in queries(r["nume"]):
            for res in search(q):
                if not is_food(res):      # rechaza personas/lugares/abstracto
                    continue
                im = fetch(res.get("url"))
                if im:
                    im.save(dst, "JPEG", quality=80, optimize=True)
                    r["img"] = "imgs_recipes/" + sl + ".jpg"; found = True; got += 1; break
            if found: break
            time.sleep(0.25)
        if not found: miss += 1
        done += 1
        if done % 20 == 0:
            print(f"  {done}/{len(targets)}  ok={got} sin_match={miss} ya={skip}", flush=True)
            json.dump(data, open(RJSON,"w",encoding="utf-8"), ensure_ascii=False, separators=(",",":"))
    json.dump(data, open(RJSON, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    real = sum(1 for x in data if x["img"] and x["img"].startswith("imgs_recipes"))
    print(f"\nFIN. nuevas={got} sin_match={miss} ya={skip} | total foto propia: {real}/{len(data)}")

if __name__ == "__main__":
    main()
