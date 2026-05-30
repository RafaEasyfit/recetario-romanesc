# 🍃 Rețetar Sănătos Românesc

Aplicación web (PWA) con **492 recetas saludables rumanas**: tradicionales, internacionales,
de ayuno (post), de fiestas y rápidas (10 min). Instalable en Android e iOS como una app nativa,
funciona sin conexión y se usa desde cualquier dispositivo con un solo enlace.

## 📲 Cómo usarla

Abre el enlace de GitHub Pages en el móvil:

**https://RafaEasyfit.github.io/recetario-romanesc/**

- **Android (Chrome):** menú ⋮ → *Añadir a pantalla de inicio* (o sale solo un aviso).
- **iPhone (Safari):** botón Compartir → *Añadir a pantalla de inicio*.

Una vez instalada se abre a pantalla completa, como una app, y guarda las recetas para usarlas
sin internet.

## ✨ Funciones

- 🔍 Buscador instantáneo por nombre **o ingrediente**.
- 🏷️ Filtros por categoría (Tradiționale, Internaționale, De Post, Sărbători, Rapide).
- ⭐ Favoritos (se guardan en el dispositivo).
- 📄 Cada receta: foto, kcal, tiempo, porciones, macros (proteínas/grasas/carbos),
  ingredientes y pasos de preparación.

## 🗂️ Estructura

```
index.html              · interfaz
styles.css              · estilos
app.js                  · lógica (búsqueda, filtros, favoritos, detalle)
recipes.json            · las 492 recetas (datos)
manifest.webmanifest    · configuración PWA
sw.js                   · service worker (modo sin conexión)
icons/                  · iconos de la app
imgs_recipes/           · fotos reales de recetas
imgs/                   · imágenes genéricas por categoría
```

## 🔄 Actualizar las recetas

Los datos salen de `all_recipes_ro_v3.json` (carpeta de trabajo) y se regeneran con
`build_app_data.py`, que limpia, ordena, empareja fotos y crea `recipes.json`.
Tras regenerar, sube los cambios a GitHub y GitHub Pages se actualiza solo.

> Si cambias `sw.js` o quieres forzar la actualización en un móvil ya instalado,
> sube la versión de caché (`retetar-v1` → `retetar-v2`) en `sw.js`.

---
Generado con datos propios · 492 recetas · 192 fotos
