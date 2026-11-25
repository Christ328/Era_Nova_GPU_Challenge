---
marp: true
theme: uncover
size: 16:9
paginate: true
style: |
  section {
    font-family: Arial, Helvetica, sans-serif;
    background: #0D1F35;
    color: white;
    padding: 48px 60px;
    justify-content: flex-start;
    text-align: left;
    overflow: hidden;
  }
  h1 {
    font-size: 3.4rem;
    font-weight: 900;
    color: white;
    margin: 0 0 10px;
    letter-spacing: -1px;
    line-height: 1.05;
  }
  h2 {
    font-size: 1.35rem;
    font-weight: 800;
    color: white;
    border-bottom: 3px solid #F4A261;
    padding-bottom: 10px;
    margin: 0 0 24px;
    display: inline-block;
  }
  h3 { font-size: 0.88rem; font-weight: 700; margin: 0 0 5px; }
  p  { font-size: 0.78rem; line-height: 1.6; margin: 0 0 6px; color: rgba(255,255,255,0.80); }
  strong { color: #F4A261; }
  section::after { font-size: 0.65rem; color: rgba(255,255,255,0.25); }

  .row  { display:flex; gap:16px; width:100%; align-items:flex-start; }
  .col  { flex:1; min-width:0; }

  .dcard {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.11);
    border-radius: 12px;
    padding: 18px 18px;
  }

  .big  { font-size:3rem; font-weight:900; line-height:1; margin:0 0 4px; }
  .gold  { color:#F4A261; }
  .teal  { color:#2E86AB; }
  .green { color:#5ECBA1; }
  .red   { color:#E07070; }
  .dim   { color:rgba(255,255,255,0.40); font-size:0.65rem; margin:3px 0 0; }

  .pill {
    display:inline-block;
    padding:3px 11px;
    border-radius:20px;
    font-size:0.68rem;
    font-weight:700;
    margin:2px 2px 0 0;
    background:rgba(46,134,171,0.22);
    color:#90CDE8;
    border:1px solid rgba(46,134,171,0.3);
  }
  .pill-g { background:rgba(22,138,98,0.22); color:#5ECBA1; border:1px solid rgba(22,138,98,0.3); }
  .pill-o { background:rgba(244,162,97,0.20); color:#F4A261; border:1px solid rgba(244,162,97,0.3); }

  .sep { width:28px; height:3px; border-radius:2px; margin:7px 0 10px; }

  .cta {
    background: linear-gradient(90deg,rgba(46,134,171,0.25),rgba(244,162,97,0.15));
    border:1px solid rgba(244,162,97,0.25);
    border-radius:10px;
    padding:12px 20px;
    text-align:center;
  }
  .cta p { color:white; font-size:0.82rem; font-weight:600; margin:0; }

  .team-row { display:flex; gap:22px; justify-content:center; margin:12px 0 20px; }
  .member   { text-align:center; flex:1; }
  .member img { width:94px; height:94px; border-radius:50%; object-fit:cover; display:block; margin:0 auto 8px; }
  .mn { font-size:0.76rem; font-weight:700; color:white; margin:0; }
  .mr { font-size:0.68rem; color:#F4A261; margin:2px 0 0; }
  .ms { font-size:0.63rem; color:rgba(255,255,255,0.40); margin:1px 0 0; }

  table { width:100%; border-collapse:collapse; font-size:0.72rem; }
  th { background:rgba(255,255,255,0.10); color:white; padding:7px 10px; text-align:left; font-weight:700; }
  td { padding:6px 10px; border-bottom:1px solid rgba(255,255,255,0.07); color:rgba(255,255,255,0.80); }
  tr:nth-child(even) td { background:rgba(255,255,255,0.03); }

  section.light {
    background: #F0F4F8;
    color: #172033;
  }
  section.light h2 { color:#1A3A5C; }
  section.light h3 { color:#1A3A5C; }
  section.light p  { color:#334155; }
  section.light::after { color:#94A3B8; }
  section.light table th { background:#1A3A5C; color:white; }
  section.light table td { color:#334155; border-bottom:1px solid #E4E7EC; }
  section.light table tr:nth-child(even) td { background:#F8FAFC; }
  .lcard {
    background:white;
    border-radius:12px;
    padding:16px 18px;
    box-shadow:0 2px 10px rgba(0,0,0,0.08);
  }
  .lcard h3 { color:#1A3A5C; }
  .lcard p  { color:#334155; }

  section.cover {
    background: #080F1A;
    justify-content: center;
    text-align: center;
  }
  .logos-bar {
    display:flex;
    justify-content:center;
    align-items:center;
    gap:50px;
    margin-bottom:28px;
  }
  .logos-bar img { height:40px; filter:brightness(0) invert(1); opacity:0.75; }
  .badge {
    display:inline-block;
    background:rgba(244,162,97,0.14);
    color:#F4A261;
    border:1px solid rgba(244,162,97,0.30);
    border-radius:20px;
    padding:4px 16px;
    font-size:0.70rem;
    font-weight:700;
    letter-spacing:2px;
    margin-bottom:16px;
  }
  .divbar {
    width:70px; height:3px;
    background:linear-gradient(90deg,#2E86AB,#F4A261);
    border-radius:2px;
    margin:14px auto;
  }
---

<!-- _class: cover -->
<!-- _paginate: false -->

<div style="position:absolute;width:520px;height:520px;top:-160px;right:-160px;border-radius:50%;background:radial-gradient(circle,rgba(46,134,171,0.15),transparent);pointer-events:none;"></div>
<div style="position:absolute;width:300px;height:300px;bottom:-80px;left:-80px;border-radius:50%;background:radial-gradient(circle,rgba(244,162,97,0.10),transparent);pointer-events:none;"></div>

<div class="logos-bar">
  <img src="epitech.png" />
  <img src="alliance_fintech.png" />
  <img src="udu.png" />
</div>

<div class="badge">GPU CHALLENGE 2026</div>

# VIGIE-TRUST

<div class="divbar"></div>

<p style="font-size:1rem;color:rgba(255,255,255,0.75);font-weight:500;margin:10px 0 6px;">
  Évaluation du risque de crédit des petits commerçants<br>
  <strong>par données alternatives et IA explicable</strong>
</p>
<p style="font-size:0.70rem;color:rgba(255,255,255,0.32);margin-top:20px;">
  Données simulées · Capacité de remboursement sans historique bancaire
</p>
<p style="margin-top:26px;font-size:0.80rem;font-weight:700;color:rgba(255,255,255,0.45);letter-spacing:3px;">ÉQUIPE ERA NOVA</p>

---

## L'exclusion financière en chiffres

<div class="row" style="margin-bottom:16px;">

<div class="dcard col" style="text-align:center;padding:22px 16px;">
<svg width="44" height="44" viewBox="0 0 44 44" fill="none" style="display:block;margin:0 auto 10px;"><circle cx="22" cy="22" r="20" stroke="#F4A261" stroke-width="1.8"/><path d="M22 6 C12 6 4 13 4 22 C4 31 12 38 22 38" stroke="#F4A261" stroke-width="2" stroke-linecap="round"/><path d="M22 6 C32 6 40 13 40 22 C40 31 32 38 22 38" stroke="rgba(244,162,97,0.25)" stroke-width="2" stroke-linecap="round"/><line x1="4" y1="22" x2="40" y2="22" stroke="#F4A261" stroke-width="1.2" stroke-dasharray="3 2"/><line x1="22" y1="6" x2="22" y2="38" stroke="#F4A261" stroke-width="1.2" stroke-dasharray="3 2"/></svg>
<p class="big gold">350M</p>
<p style="font-size:0.72rem;color:rgba(255,255,255,0.75);margin:4px 0 0;">adultes non bancarisés<br>en Afrique subsaharienne</p>
<p class="dim">World Bank, 2025</p>
</div>

<div class="dcard col" style="text-align:center;padding:22px 16px;">
<svg width="44" height="44" viewBox="0 0 44 44" fill="none" style="display:block;margin:0 auto 10px;"><rect x="6" y="6" width="32" height="32" rx="5" stroke="#2E86AB" stroke-width="1.8"/><path d="M13 30 L18 22 L23 26 L30 14" stroke="#2E86AB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="30" cy="14" r="2.5" fill="#2E86AB"/></svg>
<p class="big teal">25%</p>
<p style="font-size:0.72rem;color:rgba(255,255,255,0.75);margin:4px 0 0;">taux de bancarisation stricte<br>UEMOA 2024</p>
<p class="dim">BCEAO / Sika Finance</p>
</div>

<div class="dcard col" style="text-align:center;padding:22px 16px;">
<svg width="44" height="44" viewBox="0 0 44 44" fill="none" style="display:block;margin:0 auto 10px;"><circle cx="22" cy="22" r="20" stroke="rgba(200,80,80,0.35)" stroke-width="1.8"/><path d="M22 6 A16 16 0 0 1 38 22" stroke="#E07070" stroke-width="3" stroke-linecap="round"/><path d="M22 6 A16 16 0 1 0 38 22" stroke="rgba(200,80,80,0.18)" stroke-width="3" stroke-linecap="round"/><line x1="15" y1="15" x2="29" y2="29" stroke="#E07070" stroke-width="2.2" stroke-linecap="round"/><line x1="29" y1="15" x2="15" y2="29" stroke="#E07070" stroke-width="2.2" stroke-linecap="round"/></svg>
<p class="big red">~70%</p>
<p style="font-size:0.72rem;color:rgba(255,255,255,0.75);margin:4px 0 0;">petits commerçants refusés<br>faute d'historique bancaire</p>
<p class="dim">IFC, 2024</p>
</div>

</div>

<div class="row">
<div class="dcard col">
<div class="sep" style="background:#2E86AB;"></div>
<h3 class="teal" style="font-size:0.80rem;">Paradoxe mobile money</h3>
<p>Paiements marchands &gt; <strong>100 Mrd USD</strong> en 2024 en Afrique — mais ces flux n'ouvrent aucun accès au crédit formel.</p>
</div>
<div class="dcard col">
<div class="sep" style="background:#F4A261;"></div>
<h3 class="gold" style="font-size:0.80rem;">Contexte Bénin · PNIF 2026</h3>
<p>SNIF 2023-2027 vise <strong>85 %</strong> d'inclusion. PNIF lancé le <strong>24 nov. 2026</strong> — microcrédits en 48h pour 14 IMF partenaires.</p>
</div>
</div>

---

## La problématique

<div class="row" style="gap:18px;align-items:stretch;">

<div style="flex:1.1;display:flex;flex-direction:column;gap:14px;">

<div class="dcard">
<div style="display:flex;gap:14px;align-items:flex-start;">
<svg width="38" height="38" viewBox="0 0 38 38" fill="none" style="flex-shrink:0;margin-top:2px;"><circle cx="19" cy="19" r="17" stroke="#F4A261" stroke-width="1.6"/><circle cx="19" cy="13" r="4.5" stroke="#F4A261" stroke-width="1.8"/><path d="M9 32 C9 25 29 25 29 32" stroke="#F4A261" stroke-width="1.8" stroke-linecap="round"/><line x1="32" y1="5" x2="36" y2="1" stroke="#E07070" stroke-width="2" stroke-linecap="round"/><line x1="36" y1="5" x2="32" y2="1" stroke="#E07070" stroke-width="2" stroke-linecap="round"/></svg>
<div>
<h3 class="gold">Le commerçant invisible</h3>
<div class="sep" style="background:#F4A261;"></div>
<p>Vendeuses de marché, artisans, micro-entrepreneurs — des flux économiques <strong>réels mais invisibles</strong>. Pas de compte bancaire, pas de collatéral reconnu.</p>
</div>
</div>
</div>

<div class="dcard">
<div style="display:flex;gap:14px;align-items:flex-start;">
<svg width="38" height="38" viewBox="0 0 38 38" fill="none" style="flex-shrink:0;margin-top:2px;"><rect x="4" y="8" width="30" height="22" rx="4" stroke="#2E86AB" stroke-width="1.6"/><line x1="4" y1="16" x2="34" y2="16" stroke="#2E86AB" stroke-width="1.5"/><path d="M16 26 L19 23 L22 25 L26 20" stroke="#E07070" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
<div>
<h3 class="teal">L'impasse des modèles classiques</h3>
<div class="sep" style="background:#2E86AB;"></div>
<p>Historique bancaire de <strong>12–24 mois</strong> requis minimum. Résultat : refus systématique, recours aux usuriers, cycle de pauvreté.</p>
</div>
</div>
</div>

</div>

<div style="flex:0.9;background:linear-gradient(135deg,rgba(46,134,171,0.20),rgba(15,39,68,0.90));border:1px solid rgba(46,134,171,0.25);border-radius:14px;padding:28px 22px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;">
<svg width="50" height="50" viewBox="0 0 50 50" fill="none" style="margin-bottom:12px;"><circle cx="25" cy="25" r="23" stroke="#F4A261" stroke-width="1.6"/><path d="M18 18 C18 13 32 11 32 20 C32 25 25 26 25 30" stroke="#F4A261" stroke-width="2.4" stroke-linecap="round"/><circle cx="25" cy="36" r="2" fill="#F4A261"/></svg>
<p style="font-size:0.95rem;font-weight:800;color:#F4A261;line-height:1.4;margin-bottom:10px;">Comment évaluer la solvabilité de quelqu'un qui n'existe pas dans le système ?</p>
<p style="font-size:0.72rem;color:rgba(255,255,255,0.50);">Les données sont là — mobile money, tontines, flux de ventes — mais non exploitées.</p>
</div>

</div>

---

## Notre solution · Le profilage augmenté

<p style="font-size:0.72rem;color:rgba(255,255,255,0.40);font-style:italic;margin-bottom:18px;">Gouvernance augmentée — VIGIE-TRUST outille l'expert, il ne le remplace pas.</p>

<div class="row" style="margin-bottom:14px;">

<div class="dcard col" style="padding:18px 16px;">
<svg width="34" height="34" viewBox="0 0 34 34" fill="none" style="margin-bottom:10px;"><rect x="7" y="3" width="14" height="26" rx="4" stroke="#2E86AB" stroke-width="1.8"/><circle cx="14" cy="25" r="1.8" stroke="#2E86AB" stroke-width="1.5"/><line x1="9" y1="9" x2="19" y2="9" stroke="#2E86AB" stroke-width="1.5"/><path d="M23 11 L29 17 L23 23" stroke="#F4A261" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
<h3 class="teal">Collecte alternative</h3>
<div class="sep" style="background:#2E86AB;"></div>
<p>Transactions mobile money · régularité tontine · flux dépôts/retraits · intégration marché</p>
<div style="margin-top:10px;"><span class="pill">35+ variables</span></div>
</div>

<div class="dcard col" style="padding:18px 16px;">
<svg width="34" height="34" viewBox="0 0 34 34" fill="none" style="margin-bottom:10px;"><circle cx="17" cy="17" r="15" stroke="#F4A261" stroke-width="1.8"/><path d="M9 23 C9 14 25 14 25 23" stroke="#F4A261" stroke-width="2" stroke-linecap="round"/><circle cx="17" cy="12" r="3.5" stroke="#F4A261" stroke-width="2"/></svg>
<h3 class="gold">Profilage IA + Règles</h3>
<div class="sep" style="background:#F4A261;"></div>
<p>XGBoost GPU <strong>× 55%</strong> + 10 règles métiers contextuelles <strong>× 45%</strong></p>
<div style="margin-top:10px;"><span class="pill pill-o">Score hybride dynamique</span></div>
</div>

<div class="dcard col" style="padding:18px 16px;">
<svg width="34" height="34" viewBox="0 0 34 34" fill="none" style="margin-bottom:10px;"><rect x="4" y="10" width="8" height="14" rx="2" stroke="#5ECBA1" stroke-width="1.8"/><rect x="14" y="6" width="8" height="18" rx="2" stroke="#5ECBA1" stroke-width="1.8"/><rect x="24" y="14" width="6" height="10" rx="2" stroke="rgba(94,203,161,0.5)" stroke-width="1.8"/><line x1="4" y1="28" x2="30" y2="28" stroke="#5ECBA1" stroke-width="1.5"/></svg>
<h3 class="green">Décision expliquée SHAP</h3>
<div class="sep" style="background:#168A62;"></div>
<p>Facteurs favorables et pénalisants visibles — l'agent comprend <strong>pourquoi</strong> et peut challenger.</p>
<div style="margin-top:10px;"><span class="pill pill-g">Transparent</span></div>
</div>

</div>

<div class="cta">
<p>VIGIE-TRUST donne au chargé de crédit une <strong>vision augmentée</strong> — la décision reste humaine.</p>
</div>

---

## Les trois piliers

<div class="row" style="gap:16px;">

<div class="dcard col" style="padding:22px 18px;border-top:3px solid #2E86AB;">
<p style="font-size:3rem;font-weight:900;color:rgba(255,255,255,0.07);line-height:1;margin:0 0 6px;">01</p>
<svg width="36" height="36" viewBox="0 0 36 36" fill="none" style="margin-bottom:10px;"><rect x="3" y="3" width="30" height="30" rx="5" stroke="#2E86AB" stroke-width="1.8"/><path d="M9 26 L14 18 L18 22 L22 14 L27 9" stroke="#2E86AB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="27" cy="9" r="2.5" fill="#2E86AB"/></svg>
<h3 class="teal">Prédiction par modèle</h3>
<div class="sep" style="background:#2E86AB;"></div>
<p>XGBoost GPU Tesla T4 · <strong>700 000</strong> profils · 35+ variables alternatives</p>
<div style="margin-top:12px;"><span class="pill">AUC 0.87</span> <span class="pill">7.1× GPU</span></div>
</div>

<div class="dcard col" style="padding:22px 18px;border-top:3px solid #F4A261;">
<p style="font-size:3rem;font-weight:900;color:rgba(255,255,255,0.07);line-height:1;margin:0 0 6px;">02</p>
<svg width="36" height="36" viewBox="0 0 36 36" fill="none" style="margin-bottom:10px;"><circle cx="18" cy="18" r="15" stroke="#F4A261" stroke-width="1.8"/><path d="M10 24 C10 16 26 16 26 24" stroke="#F4A261" stroke-width="2" stroke-linecap="round"/><line x1="18" y1="7" x2="18" y2="13" stroke="#F4A261" stroke-width="2" stroke-linecap="round"/><line x1="10" y1="10" x2="14" y2="14" stroke="rgba(244,162,97,0.4)" stroke-width="1.5" stroke-linecap="round"/><line x1="26" y1="10" x2="22" y2="14" stroke="rgba(244,162,97,0.4)" stroke-width="1.5" stroke-linecap="round"/></svg>
<h3 class="gold">Convolution règles métiers</h3>
<div class="sep" style="background:#F4A261;"></div>
<p><strong>10 règles</strong> africaines — ratio survie, tontine, cohérence flux/revenu, charge remboursement</p>
<div style="margin-top:12px;"><span class="pill pill-o">Dynamique</span> <span class="pill pill-o">Score 0–100</span></div>
</div>

<div class="dcard col" style="padding:22px 18px;border-top:3px solid #168A62;">
<p style="font-size:3rem;font-weight:900;color:rgba(255,255,255,0.07);line-height:1;margin:0 0 6px;">03</p>
<svg width="36" height="36" viewBox="0 0 36 36" fill="none" style="margin-bottom:10px;"><circle cx="18" cy="18" r="15" stroke="#5ECBA1" stroke-width="1.8"/><path d="M11 18 L16 23 L25 12" stroke="#5ECBA1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
<h3 class="green">Explicabilité SHAP</h3>
<div class="sep" style="background:#168A62;"></div>
<p>Chaque décision décomposée — le chargé de crédit <strong>voit pourquoi</strong>, peut challenger et décider.</p>
<div style="margin-top:12px;"><span class="pill pill-g">Transparent</span> <span class="pill pill-g">Challengeable</span></div>
</div>

</div>

---

<!-- _class: light -->

<div style="position:absolute;top:0;left:0;width:100%;height:5px;background:linear-gradient(90deg,#0F2744,#2E86AB,#F4A261);"></div>

## Résultats du modèle

<div class="row" style="gap:18px;">

<div style="flex:1;">
<div class="row" style="gap:10px;margin-bottom:10px;">
<div class="lcard col" style="text-align:center;padding:16px 10px;border-top:3px solid #168A62;">
<svg width="30" height="30" viewBox="0 0 30 30" fill="none" style="display:block;margin:0 auto 6px;"><path d="M3 22 L9 14 L14 18 L20 9 L27 5" stroke="#168A62" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="27" cy="5" r="2.5" fill="#168A62"/></svg>
<p style="font-size:2.4rem;font-weight:900;color:#168A62;margin:0 0 2px;">0.87</p>
<p style="font-size:0.68rem;color:#667085;margin:0;">AUC-ROC · XGBoost GPU</p>
</div>
<div class="lcard col" style="text-align:center;padding:16px 10px;border-top:3px solid #2E86AB;">
<svg width="30" height="30" viewBox="0 0 30 30" fill="none" style="display:block;margin:0 auto 6px;"><path d="M15 3 L18 11 L27 11 L20 17 L23 25 L15 20 L7 25 L10 17 L3 11 L12 11 Z" stroke="#2E86AB" stroke-width="1.8" fill="none" stroke-linejoin="round"/></svg>
<p style="font-size:2.4rem;font-weight:900;color:#2E86AB;margin:0 0 2px;">7.1×</p>
<p style="font-size:0.68rem;color:#667085;margin:0;">accélération GPU vs CPU</p>
</div>
</div>
<div class="row" style="gap:10px;">
<div class="lcard col" style="text-align:center;padding:16px 10px;border-top:3px solid #F4A261;">
<svg width="30" height="30" viewBox="0 0 30 30" fill="none" style="display:block;margin:0 auto 6px;"><rect x="3" y="7" width="24" height="16" rx="4" stroke="#F4A261" stroke-width="1.8"/><line x1="3" y1="13" x2="27" y2="13" stroke="#F4A261" stroke-width="1.5"/><line x1="11" y1="7" x2="11" y2="23" stroke="#F4A261" stroke-width="1" stroke-dasharray="2 2"/></svg>
<p style="font-size:2.4rem;font-weight:900;color:#F4A261;margin:0 0 2px;">700K</p>
<p style="font-size:0.68rem;color:#667085;margin:0;">profils · 35+ variables</p>
</div>
<div class="lcard col" style="text-align:center;padding:16px 10px;border-top:3px solid #1A3A5C;">
<svg width="30" height="30" viewBox="0 0 30 30" fill="none" style="display:block;margin:0 auto 6px;"><circle cx="15" cy="15" r="12" stroke="#1A3A5C" stroke-width="2"/><path d="M15 3 A12 12 0 0 1 27 15" stroke="#1A3A5C" stroke-width="3" stroke-linecap="round"/><path d="M15 3 A12 12 0 1 0 27 15" stroke="#E4E7EC" stroke-width="3" stroke-linecap="round"/></svg>
<p style="font-size:2.4rem;font-weight:900;color:#1A3A5C;margin:0 0 2px;">80%</p>
<p style="font-size:0.68rem;color:#667085;margin:0;">précision classification</p>
</div>
</div>
</div>

<div style="flex:1.1;">
<table>
<thead><tr><th>Modèle</th><th>AUC</th><th>Temps GPU</th></tr></thead>
<tbody>
<tr><td><strong>XGBoost ✓</strong></td><td><strong>0.872</strong></td><td><strong>12.5s</strong></td></tr>
<tr><td>LightGBM</td><td>0.861</td><td>15.2s</td></tr>
<tr><td>Régression logistique</td><td>0.794</td><td>8.1s</td></tr>
<tr><td>Random Forest</td><td>0.843</td><td>41.3s</td></tr>
</tbody>
</table>
<div class="lcard" style="margin-top:14px;border-left:4px solid #F4A261;border-radius:8px;">
<h3 style="color:#1A3A5C;font-size:0.80rem;">Complexité du dataset</h3>
<p style="font-size:0.74rem;">Commerçants saisonniers, membres de tontine, dépenses irrégulières — reflète la diversité du tissu informel béninois.</p>
</div>
</div>

</div>

---

## Positionnement vs solutions existantes

<table style="margin-bottom:16px;">
<thead><tr><th>Critère</th><th>Bancaire classique</th><th>Mobile lending</th><th style="color:#F4A261;">VIGIE-TRUST</th></tr></thead>
<tbody>
<tr><td>Historique bancaire requis</td><td>Obligatoire</td><td>Partiel</td><td class="green" style="color:#5ECBA1;font-weight:700;">Non requis</td></tr>
<tr><td>Données alternatives</td><td class="red" style="color:#E07070;">Aucune</td><td>Mobile only</td><td class="green" style="color:#5ECBA1;font-weight:700;">Multi-sources</td></tr>
<tr><td>Règles métiers locales</td><td class="red" style="color:#E07070;">Aucune</td><td class="red" style="color:#E07070;">Aucune</td><td class="green" style="color:#5ECBA1;font-weight:700;">Tontine, marché…</td></tr>
<tr><td>Explicabilité SHAP</td><td class="red" style="color:#E07070;">Non</td><td class="red" style="color:#E07070;">Non</td><td class="green" style="color:#5ECBA1;font-weight:700;">Oui</td></tr>
<tr><td>Gouvernance humaine</td><td>Opaque</td><td class="red" style="color:#E07070;">Automatique</td><td style="color:#F4A261;font-weight:700;">Augmentée</td></tr>
<tr><td>Adapté secteur informel</td><td class="red" style="color:#E07070;">Non</td><td>Partiel</td><td class="green" style="color:#5ECBA1;font-weight:700;">Oui</td></tr>
</tbody>
</table>

<div class="row" style="gap:14px;">
<div class="dcard col">
<div class="sep" style="background:#E07070;"></div>
<h3 style="color:rgba(255,255,255,0.65);font-size:0.78rem;">Ce que font les autres</h3>
<p>Refus ou accord automatique sans explication — le commerçant est exclu des deux côtés.</p>
</div>
<div class="dcard col">
<div class="sep" style="background:#5ECBA1;"></div>
<h3 class="green" style="font-size:0.78rem;">Ce que fait VIGIE-TRUST</h3>
<p>Score <strong>justifié</strong>, contextuel, challengeable — l'humain reste décideur éclairé.</p>
</div>
</div>

---

## Valeur ajoutée & Innovation

<div class="row" style="gap:14px;margin-bottom:12px;">
<div class="dcard col" style="padding:16px 16px;">
<svg width="30" height="30" viewBox="0 0 30 30" fill="none" style="margin-bottom:8px;"><circle cx="15" cy="15" r="13" stroke="#F4A261" stroke-width="1.6"/><path d="M8 20 C8 13 22 10 22 18" stroke="#F4A261" stroke-width="2" stroke-linecap="round"/><circle cx="15" cy="11" r="3" stroke="#F4A261" stroke-width="1.8"/><line x1="22" y1="18" x2="26" y2="22" stroke="#F4A261" stroke-width="1.8" stroke-linecap="round"/><circle cx="27" cy="23" r="1.5" fill="#F4A261"/></svg>
<h3 class="gold" style="font-size:0.80rem;">Score hybride contextualisé</h3>
<div class="sep" style="background:#F4A261;"></div>
<p>1ère combinaison IA × règles africaines — tontine, flux mobile, marché.</p>
</div>
<div class="dcard col" style="padding:16px 16px;">
<svg width="30" height="30" viewBox="0 0 30 30" fill="none" style="margin-bottom:8px;"><rect x="4" y="8" width="7" height="14" rx="2" stroke="#2E86AB" stroke-width="1.8"/><rect x="13" y="4" width="7" height="18" rx="2" stroke="#2E86AB" stroke-width="1.8"/><rect x="22" y="12" width="5" height="10" rx="2" stroke="rgba(46,134,171,0.5)" stroke-width="1.8"/><line x1="4" y1="26" x2="27" y2="26" stroke="#2E86AB" stroke-width="1.5"/></svg>
<h3 class="teal" style="font-size:0.80rem;">Explicabilité SHAP opérationnelle</h3>
<div class="sep" style="background:#2E86AB;"></div>
<p>Chaque facteur visible — la décision devient une <strong>conversation</strong>.</p>
</div>
</div>

<div class="row" style="gap:14px;margin-bottom:14px;">
<div class="dcard col" style="padding:16px 16px;">
<svg width="30" height="30" viewBox="0 0 30 30" fill="none" style="margin-bottom:8px;"><path d="M15 3 L18 10 L26 10 L20 15 L22 23 L15 18 L8 23 L10 15 L4 10 L12 10 Z" stroke="#5ECBA1" stroke-width="1.6" fill="none" stroke-linejoin="round"/></svg>
<h3 class="green" style="font-size:0.80rem;">Infrastructure GPU démocratisée</h3>
<div class="sep" style="background:#168A62;"></div>
<p>Tesla T4 Kaggle + FastAPI + Render — stack production sans infra propriétaire.</p>
</div>
<div class="dcard col" style="padding:16px 16px;">
<svg width="30" height="30" viewBox="0 0 30 30" fill="none" style="margin-bottom:8px;"><rect x="3" y="7" width="24" height="16" rx="4" stroke="#F4A261" stroke-width="1.8"/><line x1="3" y1="13" x2="27" y2="13" stroke="#F4A261" stroke-width="1.5"/><circle cx="10" cy="10" r="1.5" fill="#F4A261"/><circle cx="15" cy="21" r="3.5" stroke="#F4A261" stroke-width="1.5"/></svg>
<h3 class="gold" style="font-size:0.80rem;">Alternative en amont du PNIF</h3>
<div class="sep" style="background:#F4A261;"></div>
<p>PNIF lancé le <strong>24 nov. 2026</strong> — VIGIE-TRUST est l'outil d'évaluation du risque manquant pour les <strong>14 IMF partenaires</strong>.</p>
</div>
</div>

<div style="background:linear-gradient(90deg,rgba(46,134,171,0.22),rgba(244,162,97,0.14));border:1px solid rgba(244,162,97,0.22);border-radius:10px;padding:12px 20px;text-align:center;">
<p style="color:#F4A261;font-size:0.86rem;font-weight:700;margin:0;font-style:italic;">Et si la prochaine révolution du crédit en Afrique ne venait pas des banques, mais des données que les commerçants génèrent déjà chaque jour ?</p>
</div>

---

<!-- _paginate: false -->

## L'équipe Era Nova

<div class="team-row">
<div class="member">
<img src="daniel.jpeg" style="border:3px solid #F4A261;" />
<p class="mn">BOCO Daniel</p>
<p class="mr">Data Scientist</p>
<p class="ms">Statistiques & Finance</p>
</div>
<div class="member">
<img src="prince.jpeg" style="border:3px solid #2E86AB;" />
<p class="mn">DJOMAMOU Prince</p>
<p class="mr">Data Engineer</p>
<p class="ms">Pipelines & Infrastructure</p>
</div>
<div class="member">
<img src="alexis.jpeg" style="border:3px solid #5ECBA1;" />
<p class="mn">DOHOU Alexis</p>
<p class="mr">Data Scientist</p>
<p class="ms">Modélisation & Analyse</p>
</div>
<div class="member">
<img src="christanel.jpg" style="border:3px solid rgba(255,255,255,0.35);" />
<p class="mn">GANGNEHESSOU Christanel</p>
<p class="mr">Développeur Web</p>
<p class="ms">Fullstack & Déploiement</p>
</div>
</div>

<div style="background:linear-gradient(135deg,rgba(46,134,171,0.18),rgba(244,162,97,0.12));border:1px solid rgba(255,255,255,0.09);border-radius:12px;padding:16px 32px;text-align:center;">
<div class="divbar"></div>
<p style="font-size:1rem;font-weight:900;color:#F4A261;margin:0 0 5px;">Merci pour votre attention</p>
<p style="font-size:0.72rem;color:rgba(255,255,255,0.50);margin:0;">GPU Challenge 2026 · Epitech Bénin · UDU Technologies · Alliance Fintech UEMOA</p>
<p style="font-size:0.65rem;color:rgba(255,255,255,0.25);margin:5px 0 0;letter-spacing:3px;">ÉQUIPE ERA NOVA · VIGIE-TRUST</p>
</div>
