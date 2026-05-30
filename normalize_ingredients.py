# -*- coding: utf-8 -*-
"""Normaliza el FORMATO de los ingredientes (sin tocar cantidades):
- espacio entre numero y unidad: 130g -> 130 g
- espacios multiples -> uno
- recorta espacios sobrantes
NO une lineas ni cambia numeros (eso es mas delicado; se hace aparte)."""
import json, re

APP = r"C:\Users\Rafa\recetario-romanesc\recipes.json"

def fix(line):
    s = line
    # 130g -> 130 g  (numero pegado a unidad)
    s = re.sub(r"(\d)\s*(kg|g|gr|ml|l)\b", r"\1 \2", s)
    # quitar doble espacio que pudiera quedar
    s = re.sub(r"[ \t]{2,}", " ", s).strip()
    return s

def main():
    data = json.load(open(APP, encoding="utf-8"))
    changed_lines = 0
    changed_recipes = 0
    examples = []
    for r in data:
        ch = False
        new = []
        for i in r.get("ing", []):
            f = fix(i)
            if f != i:
                changed_lines += 1; ch = True
                if len(examples) < 12: examples.append((i, f))
            new.append(f)
        r["ing"] = new
        if ch: changed_recipes += 1
    json.dump(data, open(APP, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"recetas tocadas: {changed_recipes} | lineas corregidas: {changed_lines}")
    print("--- ejemplos ---")
    for a, b in examples:
        print(f"   '{a}'  ->  '{b}'")

if __name__ == "__main__":
    main()
