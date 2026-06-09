# Rack And Ride — Export du contenu actuel (audit)

> Photographie de l'existant au moment de l'extraction (API Admin, lecture seule).
> Sert de base à la rédaction optimisée (voir `02-optimise.md`).
> **Aucune donnée Shopify n'a été modifiée.**

Catalogue : **17 produits** · **7 collections**. Langue source : EN.

---

## 🔎 Anomalies repérées (à corriger dans l'optimisation)

1. **Meta title / meta description manquants** sur ~9 produits (champ SEO vide) → à rédiger (4 langues).
2. **`product_type` incohérent** : « Surfboard Wall Mount », « Skateboard Wall Mount » (singulier), « Skateboard Wall Mounts » (pluriel), « Home Decoration », « Road Bike Wall Mount ». À **uniformiser**.
3. **Mauvais rangement** :
   - `surfboard-wall-mount-black-tinted` (« Black Surfboard Wall Rack ») → `product_type` = **Skateboard** ❌ (c'est un support **surf** noir). Sa **meta title dit « Skateboard »** ❌.
   - `skateboard-rack` & les black-tinted → type « Skateboard Wall Mounts » (pluriel) vs les autres au singulier.
4. **Dimensions douteuses** : `floating-flower-pot-shelf` (1 pot) **et** `triple-floating-flowerpots-shelf` (3 pots) ont la **même largeur 42 cm** → à vérifier (le 1-pot devrait être plus court).
5. **Dimensions dupliquées** : présentes à la fois dans `key_features` (texte) **et** `product_details` (structuré) → on les sortira dans un champ dédié `custom.dimensions` et on retire la ligne des `key_features`.
6. **Incohérences de wording** : bike = « Oak padding » alors que les autres = « Cork padding » ; titres FR/EN mélangés (« Patere »).
7. **Collections** : descriptions + meta **déjà bonnes** ✅ ; **aucune FAQ** (gros gain SEO à ajouter) ; `seo_intro`/`seo_body`/`faq` (metafields) vides → le thème retombe sur la description (OK).

---

## PRODUITS

> Format : Titre · handle · type · statut · **Meta title** · **Meta desc** · Short description · Points forts (key_features) · Dimensions/Matière (product_details).

### Surf

**Vertical Surfboard Rack** · `vertical-surfboard-rack` · type: Surfboard Wall Mount · ACTIVE
- Meta title: « Vertical Surfboard Rack - Stylish & Durable Surfboard Display »
- Meta desc: « Organize and display your surfboard with our Vertical Surfboard Rack. Made from solid oak with cork padding, it’s durable, stylish, and fits all surfboard sizes. »
- Short: idem meta desc
- Points forts: Quick & easy install (kit complet) · Eco-treated solid oak (cire d'abeille + huile de lin) · Ultra-secure hold · Anti-scratch cork padding · Universal compatibility (cruisers→longboards) · Elegant wall décor · 100% recyclable packaging · **Dimensions 50.5 × 10.3 × 2.2 cm**
- product_details: H 2.2 / L 50.5 / P 10.3 cm · Oak · Natural · France

**Surfboard Wall Rack** · `surfboard-wall-mount` · type: Surfboard Wall Mount · ACTIVE
- Meta title: « Surfboard Wall Mount – Durable Oak Rack for Secure & Stylish Storage »
- Meta desc: « Surfboard wall mount in solid oak. Durable, eco-friendly, and secure storage with cork protection. Fits all surfboards and adds style to your home. »
- Short: idem
- Points forts: install · solid oak · secure hold · **cork anti-scratch** · shortboards→longboards · décor · recyclable · Gironde France · **Dimensions 22.5 × 11.4 × 2.2 cm**
- product_details: H 2.2 / L 22.5 / P 11.4 · Oak · Natural · France

**Black Surfboard Wall Rack** · `surfboard-wall-mount-black-tinted` · type: **Skateboard Wall Mounts ❌** · ACTIVE
- Meta title: « Black Vertical Skateboard Wall Rack – Stylish & Durable » **❌ (dit Skateboard)**
- Meta desc: « Black Oak Surfboard Wall Rack in solid oak. Durable, eco-friendly… »
- Short: « Surfboard wall mount in solid oak… »
- Points forts: idem surf · **Dimensions 22.5 × 11.4 × 2.2 cm**
- product_details: Oak · **Black** · France
- ⚠️ À reclasser en **Surf** ; corriger meta title.

### Skate

**Vertical Skateboard Wall Mount** · `vertical-skateboard-wall-mount` · type: Skateboard Wall Mount · ACTIVE
- Meta title: « Vertical Skateboard Wall Mount – Stylish & Durable Skateboard Mount »
- Meta desc: « Vertical Wall Skateboard Rack – Secure, stylish storage for all skateboards… »
- Points forts (riches) : install · all wall types (anchors drywall/concrete/stone) · eco oak · secure · universal · décor · recyclable · Gironde · **Dimensions 35.7 × 10 × 2.2 cm**

**Black Vertical Skateboard Wall Mount** · `vertical-skateboard-wall-mount-black-tinted` · type: Skateboard Wall Mounts · ACTIVE
- Meta title: « Black Vertical Skateboard Wall Mount – Stylish & Durable » · Meta desc OK
- **Dimensions 35.7 × 10 × 2.2 cm** · Black

**Double Vertical Skateboard Wall Mount** · `double-vertical-skateboard-wall-mount` · type: Skateboard Wall Mount · ACTIVE
- Meta: **MANQUANT** ❌ · Short OK · **Dimensions 71 × 10 × 2.2 cm**

**Skateboard Wall Mount** · `skateboard-rack` · type: Skateboard Wall Mounts · ACTIVE
- Meta: **MANQUANT** ❌ · Short « 45-degree Skateboard Wall Mount… » · **Dimensions 17.6 × 9.3 × 2.2 cm**

**Simple Skateboard & Boardsport Rack** · `simple-boardsport-rack` · type: Skateboard Wall Mount · ACTIVE
- Meta: **MANQUANT** ❌ · Short (skate/snow/kite/wake) · **Dimensions 20.3 × 10 × 2.2 cm**

**Double Skateboard & Boardsport Rack** · `double-boardsport-rack` · type: Skateboard Wall Mount · ACTIVE
- Meta: **MANQUANT** ❌ · **Dimensions 31.8 × 10 × 2.2 cm**

**Triple Skateboard & Boardsport Rack** · `triple-boardsport-rack` · type: Skateboard Wall Mount · ACTIVE
- Meta: **MANQUANT** ❌ · **Dimensions 46.8 × 10 × 2.2 cm**

### Snowboard

**Vertical Snowboard Wall Mount** · `vertical-snowboard-wall-mount` · type: Snowboard Wall Mount · ACTIVE
- Meta title: « Vertical Snowboard Wall Mount – Stylish & Durable » · Meta desc **MANQUANT** ❌
- **Dimensions (tailles)** S 29.5 / M 31.5 / L 33 / XL 35 cm × 5 × 2.2 cm

### Skis

**Vertical Ski Wall Mount** · `vertical-ski-wall-mount` · type: Skis Wall Mount · ACTIVE
- Meta title: « Vertical Ski Wall Mount – Stylish & Durable » · Meta desc **MANQUANT** ❌
- **Dimensions (tailles)** S 30 / M 33 / L 36 / XL 38 cm × 5 × 2.2 cm

### Vélo

**Road Bike Wall Mount** · `road-bike-wall-mount` · type: Road Bike Wall Mount · ACTIVE
- Meta: **MANQUANT** ❌ · Short « Discover the TUB-RACK… »
- Points forts: install · secure · **« Oak padding » (incohérent vs cork)** · décor · recyclable · Gironde · **Dimensions 32.5 × 5 × 3 cm** · **largeur cintre max 55 cm**
- product_details: Steel/Oak · Black · France

### Déco

**Patere** · `patere` · type: Home Decoration · ACTIVE
- Meta: **MANQUANT** ❌ · Titre à revoir (« Patère » / « Oak coat hook »)
- **Dimensions 14.3 × 2.3 × 6.3 cm** (H × l × P) · Oak · France

**Floating Flowerpot Shelf - 1 Pot** · `floating-flower-pot-shelf` · type: Home Decoration · ACTIVE
- Meta: **MANQUANT** ❌ · **Dimensions 42 × 11.5 × 2.2 cm** ⚠️ (= identique au 3 pots ?) · pot Ø 7 × 7

**Floating Flowerpots Shelf - 2 Pots** · `double-floating-flowerpots-shelf` · type: Home Decoration · ACTIVE
- Titre : double espace « Shelf  - 2 » à nettoyer · Meta: **MANQUANT** ❌ · **Dimensions 28 × 11.5 × 2.2 cm** · pot Ø 7 × 7

**Floating Flowerpot Shelf - 3 Pots** · `triple-floating-flowerpots-shelf` · type: Home Decoration · ACTIVE
- Meta: **MANQUANT** ❌ · **Dimensions 42 × 11.5 × 2.2 cm** · pot Ø 7 × 7

---

## COLLECTIONS (déjà bien dotées en SEO ✅)

> Chaque collection a déjà une **description riche (HTML, H3/H4 + paragraphes)** + **meta title/desc**. Manque : **FAQ** (à créer). `seo_intro/seo_body/faq` (metafields) = vides.

| Collection | handle | produits | Meta title | FAQ |
|---|---|---|---|---|
| Surfboard Wall Mounts | `surfboard-wall-mount` | 3 | « Surfboard Racks & Wall Mounts \| Stylish & Secure Oak Storage » | ❌ |
| Skateboard Wall Mounts | `skateboard-wall-mounts` | 7 | « Skateboard Racks And Wall Mounts \| Stylish & Secure Oak Storage » | ❌ |
| Snowboard Wall Mounts | `snowboard-wall-mounts` | 4 | « Snowboard Racks and Wall Mounts \| Stylish & Secure Oak Storage » | ❌ |
| Skis Wall Mounts | `skis-wall-mounts` | 1 | « Skis Racks and Wall Mounts \| Stylish & Secure Oak Storage » | ❌ |
| Bike Racks | `bike-racks` | 1 | « Bike Racks \| Stylish & Secure Oak Storage \| Rack And Ride » | ❌ |
| Wake & Kite Racks | `kitesurf-racks` | 3 | « Wake & Kite Racks \| Stylish & Secure Oak Storage \| Rack And Ride » | ❌ |
| Home Deco | `deco` | 4 | « Home Deco \| Stylish & Minimalist Oak Deco \| Rack And Ride » | ❌ |

**Descriptions collections** : déjà rédigées (chêne massif, fait main Gironde/Landes, cire d'abeille + huile de chanvre, éco, design). Ton cohérent. → on **harmonise légèrement** (terminologie : « huile de lin » sur produits vs « huile de chanvre » sur collections ⚠️ à trancher) et on **ajoute la FAQ + meta par langue**.

> ⚠️ **Incohérence finition** : produits disent **« beeswax + linseed oil » (huile de lin)** ; collections disent **« beeswax + hemp oil » (huile de chanvre)**. À **trancher** (cf. CLAUDE.md = cire d'abeille + **huile de lin**). Je m'aligne sur **huile de lin** sauf indication contraire.
