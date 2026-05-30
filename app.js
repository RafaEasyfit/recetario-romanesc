'use strict';

const CATS = [
  { key: 'Rețete Tradiționale',     short: 'Tradiționale',  color: 'var(--c-trad)',  emoji: '🥘' },
  { key: 'Rețete Internaționale',   short: 'Internaționale',color: 'var(--c-int)',   emoji: '🌍' },
  { key: 'Rețete de Post',          short: 'De Post',       color: 'var(--c-post)',  emoji: '🥗' },
  { key: 'Sărbători Sănătoase',     short: 'Sărbători',     color: 'var(--c-sarb)',  emoji: '🎄' },
  { key: 'Rețete Rapide (10 min)',  short: 'Rapide 10min',  color: 'var(--c-rapid)', emoji: '⚡' },
  { key: 'Alte Rețete',             short: 'Altele',        color: 'var(--c-alt)',   emoji: '🍴' },
];
const catInfo = k => CATS.find(c => c.key === k) || CATS[CATS.length - 1];

let RECIPES = [];
let filterCat = 'all';      // 'all' | 'fav' | category key
let query = '';

const FAV_KEY = 'reteta_favs';
const favs = new Set(JSON.parse(localStorage.getItem(FAV_KEY) || '[]'));
const saveFavs = () => localStorage.setItem(FAV_KEY, JSON.stringify([...favs]));

const $ = id => document.getElementById(id);
const norm = s => (s || '').toLowerCase()
  .normalize('NFD').replace(/[̀-ͯ]/g, '');

// ---------- carga ----------
fetch('recipes.json')
  .then(r => r.json())
  .then(data => {
    RECIPES = data.map(r => ({ ...r, _s: norm(r.nume + ' ' + r.ing.join(' ')) }));
    buildChips();
    route();
  })
  .catch(() => { $('list').innerHTML = '<p class="empty">Eroare la încărcarea rețetelor.</p>'; });

// ---------- chips ----------
function buildChips() {
  const counts = {};
  RECIPES.forEach(r => counts[r.cat] = (counts[r.cat] || 0) + 1);
  const chips = $('chips');
  const mk = (key, label, n) =>
    `<button class="chip" data-cat="${key}">${label}${n != null ? `<span class="n">${n}</span>` : ''}</button>`;
  let html = mk('all', 'Toate', RECIPES.length);
  html += mk('fav', '★ Favorite', favs.size || '');
  CATS.forEach(c => { if (counts[c.key]) html += mk(c.key, c.emoji + ' ' + c.short, counts[c.key]); });
  chips.innerHTML = html;
  chips.querySelectorAll('.chip').forEach(b => b.onclick = () => {
    filterCat = b.dataset.cat;
    setActiveChip();
    render();
  });
  setActiveChip();
}
function setActiveChip() {
  document.querySelectorAll('.chip').forEach(b =>
    b.classList.toggle('active', b.dataset.cat === filterCat));
}

// ---------- render lista ----------
function render() {
  const q = norm(query);
  let items = RECIPES;
  if (filterCat === 'fav') items = items.filter(r => favs.has(r.id));
  else if (filterCat !== 'all') items = items.filter(r => r.cat === filterCat);
  if (q) items = items.filter(r => r._s.includes(q));

  $('empty').hidden = items.length > 0;
  $('count').textContent = items.length + (items.length === 1 ? ' rețetă' : ' rețete');

  $('list').innerHTML = items.map(cardHTML).join('');
  $('list').querySelectorAll('.card').forEach(c =>
    c.onclick = () => openDetail(+c.dataset.id));
}

function imgBlock(r, cls) {
  const ci = catInfo(r.cat);
  if (r.img) return `<img class="card-img" loading="lazy" src="${r.img}" alt="">`;
  return `<div class="card-ph" style="background:${ci.color}">${ci.emoji}</div>`;
}
function cardHTML(r) {
  const meta = [];
  if (r.timp) meta.push('⏱ ' + r.timp);
  if (r.portii) meta.push('🍽 ' + r.portii);
  return `<article class="card" data-id="${r.id}">
    ${imgBlock(r)}
    ${r.kcal ? `<span class="kcal-badge">${r.kcal} kcal</span>` : ''}
    ${favs.has(r.id) ? '<span class="fav-mark">★</span>' : ''}
    <div class="card-body">
      <div class="card-name">${esc(r.nume)}</div>
      <div class="card-meta">${meta.join('<span></span>')}</div>
    </div>
  </article>`;
}

// ---------- detalle ----------
function openDetail(id) {
  if (location.hash !== '#r=' + id) { location.hash = 'r=' + id; }
  showDetail(id);
}
function showDetail(id) {
  const r = RECIPES.find(x => x.id === id);
  if (!r) { closeDetail(); return; }
  const ci = catInfo(r.cat);

  const hero = $('detailHero');
  if (r.img) {
    hero.style.background = `center/cover no-repeat url("${r.img}")`;
    hero.innerHTML = '';
  } else {
    hero.style.background = ci.color;
    hero.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;font-size:80px">${ci.emoji}</div>`;
  }

  $('detailCat').textContent = ci.emoji + ' ' + ci.short;
  $('detailCat').style.background = ci.color;
  $('detailName').textContent = r.nume;

  const badges = [];
  if (r.kcal) badges.push(`<span class="badge"><b>${r.kcal}</b> kcal</span>`);
  if (r.timp) badges.push(`<span class="badge">⏱ ${esc(r.timp)}</span>`);
  if (r.portii) badges.push(`<span class="badge">🍽 ${r.portii} porții</span>`);
  if (r.dif) badges.push(`<span class="badge">📊 ${esc(r.dif)}</span>`);
  $('detailBadges').innerHTML = badges.join('');

  const nutri = [['Proteine', r.prot], ['Grăsimi', r.gras], ['Carbo', r.carb]];
  if (r.prot != null || r.gras != null || r.carb != null) {
    $('detailNutri').style.display = '';
    $('detailNutri').innerHTML =
      `<div class="n-box"><div class="n-val">${r.kcal || '–'}</div><div class="n-lab">kcal</div></div>` +
      nutri.map(([l, v]) => `<div class="n-box"><div class="n-val">${v != null ? v + 'g' : '–'}</div><div class="n-lab">${l}</div></div>`).join('');
  } else $('detailNutri').style.display = 'none';

  $('detailDesc').textContent = r.desc || '';
  $('detailDesc').style.display = r.desc ? '' : 'none';
  $('detailIng').innerHTML = r.ing.map(i => `<li>${esc(i)}</li>`).join('');
  $('detailPasi').innerHTML = r.pasi.map(p => `<li>${esc(p)}</li>`).join('');

  const favBtn = $('fav');
  const setFav = () => { favBtn.textContent = favs.has(id) ? '★' : '☆'; favBtn.classList.toggle('on', favs.has(id)); };
  setFav();
  favBtn.onclick = () => {
    favs.has(id) ? favs.delete(id) : favs.add(id);
    saveFavs(); setFav(); buildChips();
  };

  $('detail').hidden = false;
  $('detail').scrollTop = 0;
  document.body.style.overflow = 'hidden';
}
function closeDetail() {
  $('detail').hidden = true;
  document.body.style.overflow = '';
  render();
}
$('back').onclick = () => { history.back(); };

// ---------- routing ----------
function route() {
  const m = location.hash.match(/r=(\d+)/);
  if (m) showDetail(+m[1]);
  else { closeDetail(); }
}
window.addEventListener('hashchange', route);

// ---------- búsqueda ----------
let t;
$('search').addEventListener('input', e => {
  query = e.target.value;
  $('clearSearch').classList.toggle('show', !!query);
  clearTimeout(t); t = setTimeout(render, 120);
});
$('clearSearch').onclick = () => {
  query = ''; $('search').value = ''; $('clearSearch').classList.remove('show'); render();
};

// ---------- util ----------
function esc(s) { return (s + '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

// ---------- PWA ----------
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
let deferredPrompt;
window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault(); deferredPrompt = e; showInstall();
});
function showInstall() {
  if (localStorage.getItem('install_dismissed')) return;
  let el = $('installHint');
  if (!el) {
    el = document.createElement('div'); el.id = 'installHint';
    el.innerHTML = '📲 Instalează aplicația pe telefon <button id="instBtn">Instalează</button><button class="x" id="instX">✕</button>';
    document.body.appendChild(el);
    $('instBtn').onclick = async () => { el.style.display = 'none'; if (deferredPrompt) { deferredPrompt.prompt(); deferredPrompt = null; } };
    $('instX').onclick = () => { el.style.display = 'none'; localStorage.setItem('install_dismissed', '1'); };
  }
  el.style.display = 'flex';
}
