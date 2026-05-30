# -*- coding: utf-8 -*-
"""2ª pasada: asigna una imagen genérica por TIPO de plato a las recetas
que siguen sin foto propia, para que NINGUNA quede sin imagen."""
import json, os, re, unicodedata

APP = r"C:\Users\Rafa\recetario-romanesc"
RJSON = os.path.join(APP, "recipes.json")

def low(s):
    return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode().lower()

# orden: lo más específico primero
RULES = [
    (["sarmale"], "img_sarmale.jpg"),
    (["smoothie","shake"], "img_smoothie.jpg"),
    (["clatite","pancake","gogosi"], "img_pancakes.jpg"),
    (["mamalig","balmos","polenta"], "img_mamaliga.jpg"),
    (["cozonac"], "img_cozonac.jpg"),
    (["curry"], "img_curry.jpg"),
    (["wrap","sandwich","lipie","lipii","toast","bruschet","tartine","burger","quesadilla"], "img_wrap.jpg"),
    (["tort","prajitur","ecler","profiterol","cremsnit","papanas","amandin","negres","briosa","brioșe",
      "chec","tarta","tartă","fursec","cornulet","sarailie","baclava","desert","crema de zahar",
      "budinca","gris cu lapte","orez cu lapte","lapte de pasare","faguri","cheesecake","muffin"], "img_tort.jpg"),
    (["omleta","oua","ochiuri","jumari","frittata","scrambled"], "img_omleta.jpg"),
    (["iaurt","branza","telemea","cas ","smantana","cottage","kefir"], "img_iaurt.jpg"),
    (["peste","pește","somon","crap","scrumbie","ton","nisetru","icre","storceag","plachie","saramura",
      "macrou","hering","pastrav","creveti","fructe de mare"], "img_salmon.jpg"),
    (["paste","spaghete","lasagna","lasagne","fidea","macaroane","tagliatelle","penne","gnocchi"], "img_pasta.jpg"),
    (["orez","risotto","pilaf"], "img_orez.jpg"),
    (["hummus","naut","linte","mazare"], "img_lentil.jpg"),
    (["bol","buddha","taco","mexican","burrito","poke"], "img_buddha.jpg"),
    (["fasole","iahnie","batuta"], "img_fasole.jpg"),
    (["ciorba","bors","borș","supa","supă","zeama","zeamă","crema de","cremă de"], "img_ciorba.jpg"),
    (["salata","salată"], "img_salata.jpg"),
    (["pate","pastă de","pasta de","mujdei","guacamole","zacusca","dip","sos ","tapenade","crema de nuci"], "img_ghiveci.jpg"),
    (["ghiveci","tocana","tocanit","tochitur","ostropel","mancare de","mâncare de","ardei umplut","dovlecei umplut",
      "vinete umplut","musaca","legume","ratatouille","ciuperci"], "img_ghiveci.jpg"),
    (["brownie","mucenici","turte","poale","colaci","langosi","langoși","mere coapte","mere copt",
      "gem","dulceata","dulceață","biscuit","negresa","baclava","halva","rahat"], "img_tort.jpg"),
    (["terci","ovaz","ovăz","fulgi","porridge","granola","musli","mic dejun"], "img_pancakes.jpg"),
    (["apa","apă","limonada","limonadă","ceai","infuzat","suc","bautura","băutură"], "img_smoothie.jpg"),
    (["baton","batoane","bilute","biluțe","energizant","snack","gustare"], "img_smoothie.jpg"),
    (["cartof","cartofi","piure"], "img_ghiveci.jpg"),
    (["avocado","guacamol"], "img_salata.jpg"),
    (["murat","murături","muraturi","varza","varză","castravete"], "img_salata.jpg"),
    (["nugget","crocant","pane","snitel","șnițel"], "img_pui.jpg"),
    (["pui","curcan","gaina","găină"], "img_pui.jpg"),
    (["porc","vita","vită","friptur","muschi","mușchi","ceaf","cotlet","mici","mititei","carne","snitel","șnițel",
      "chiftel","parjoale","pârjoale","drob","rasol","gulas","vacuta","caltabos","jumari","pomana","stufat"], "img_pui.jpg"),
]

def pick(nume):
    n = low(nume)
    for kws, img in RULES:
        for kw in kws:
            if low(kw) in n:
                return img
    return None

def main():
    data = json.load(open(RJSON, encoding="utf-8"))
    assigned = none_left = 0
    for r in data:
        if r["img"] and r["img"].startswith("imgs_recipes"):
            continue
        g = pick(r["nume"])
        if g:
            r["img"] = "imgs/" + g; assigned += 1
        else:
            r["img"] = None; none_left += 1
    json.dump(data, open(RJSON, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    real = sum(1 for r in data if r["img"] and r["img"].startswith("imgs_recipes"))
    gen  = sum(1 for r in data if r["img"] and r["img"].startswith("imgs/"))
    print(f"foto propia (real): {real}")
    print(f"generica por tipo:  {gen}")
    print(f"sin imagen (placeholder de color): {none_left}")
    if none_left:
        print("--- sin imagen ---")
        for r in data:
            if not r["img"]: print("  ", r["nume"])

if __name__ == "__main__":
    main()
