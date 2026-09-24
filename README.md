# ⚡ py-warcraft-td: Element Tower Defense (Warcraft III Adaptation)

Eine moderne, native Python-Desktop-Adaption der legendären Warcraft III Custom Map **Element TD** (Element Tower Defense), kombiniert mit freiem Labyrinth-Bauen (**Mazing** via dynamischer A\*-Pfadsuche).

---

## 🌟 Hauptfeatures & Spielmechaniken

### 1. Der 6-Elemente-Vorteilskreis
Jeder Turm und jeder Gegner gehört einem bestimmten Element an. Der Kreis der Elemente bestimmt den ausgeteilten Schaden:
$$\text{Licht} \rightarrow \text{Dunkelheit} \rightarrow \text{Wasser} \rightarrow \text{Feuer} \rightarrow \text{Natur} \rightarrow \text{Erde} \rightarrow \text{Licht}$$

- **Überlegenes Element (200% Schaden):** Das angreifende Element schlägt das Ziel im Kreis (z. B. Licht gegen Dunkelheit, Feuer gegen Natur).
- **Unterlegenes Element (50% Schaden):** Das angreifende Element ist schwach gegen seinen Konter (z. B. Dunkelheit gegen Licht, Natur gegen Feuer).
- **Neutral (100% Schaden):** Nicht benachbarte Elemente oder physische Angriffe (Pfeil / Kanone).

### 2. Freies Labyrinth-Bauen (Mazing) & Fliegende Einheiten
- **Bodeneinheiten:** Suchen mithilfe von dynamischer **A\*-Wegfindung** in Echtzeit den kürzesten Pfad durch das von dir errichtete Turmlabyrinth.
- **Wegblockierungs-Schutz:** Türme können nicht platziert werden, wenn sie den Weg von Start zu Ziel komplett versperren oder aktive Einheiten einsperren würden.
- **Fliegende Einheiten:** Fliegen schnurgerade quer über die Karte und ignorieren Mauern! Nur Türme mit Luftabwehrfähigkeit können sie abschießen.
- **Leak-Respawn:** Einheiten, die das Ziel erreichen, ziehen Leben ab (1 Leben bzw. 3 bei Bossen) und **erscheinen am Startpunkt mit ihren verbleibenden Lebenspunkten erneut**, sodass du weiterhin die Chance hast, sie für ihr Gold zu besiegen!

### 3. Das vollständige Kompendium aller 43 Türme
- **Starter-Türme (Stufe 1–3):**
  - **Pfeilturm:** Hohe Angriffsgeschwindigkeit gegen Boden und Luft.
  - **Kanonenturm:** Massiver Flächenschaden gegen Bodengruppen.
- **6 Basis-Elementartürme (Stufe 1–3):**
  - `Licht`: Extremer Sofort-Laserstrahl mit großer Reichweite (Boden & Luft).
  - `Dunkelheit`: Gewaltiger Seelenkugel-Einzelschaden (Boden & Luft).
  - `Wasser`: Spritzende Gezeitenwellen mit Flächen-Verlangsamung.
  - `Feuer`: Explosive Feuerbälle mit Flächenbrand über Zeit (Boden & Luft).
  - `Natur`: Ätzende Giftsporen mit anhaltendem Toxin.
  - `Erde`: Tektonische Schockwellen mit Betäubung und Rüstungsbrecher.
- **15 Dual-Elementartürme (Alle 2er-Kombinationen):**
  1. *Täuschung (Licht + Dunkelheit):* Phantom-Kritische Treffer mit hohem DPS.
  2. *Eis (Licht + Wasser):* 50% Frostverlangsamung im Radius.
  3. *Elektrizität (Licht + Feuer):* Kettenblitz springt auf 4 Feinde über.
  4. *Sonne (Licht + Natur):* Solarer Strahl mit Rüstungsdurchdringung.
  5. *Quark / Gold (Licht + Erde):* Subatomare Impulse mit +3 Extragold pro Kill.
  6. *Dunst (Dunkelheit + Wasser):* Giftiger Miasmanebel mit Flächen-Slow.
  7. *Verdammnis (Dunkelheit + Feuer):* Todesfluch mit massiver Explosion.
  8. *Gift (Dunkelheit + Natur):* Aggressives Gift über 5 Sekunden.
  9. *Eisen / Schmiede (Dunkelheit + Erde):* Zerschlägt Rüstung (+35% erlittener Schaden).
  10. *Dampf (Wasser + Feuer):* Extrem schnelle Dampfprojektile.
  11. *Geysir (Wasser + Natur):* Kochende Wasserfontänen mit Splash.
  12. *Schlamm (Wasser + Erde):* Zäher Matsch hemmt Bewegung um 45%.
  13. *Verbrennung (Feuer + Natur):* Napalmboden entzündet alles.
  14. *Magma (Feuer + Erde):* Glühendes Lavagestein mit riesigem Krater.
  15. *Wurzeln (Natur + Erde):* Umschlingende Ranken mit Festhalte-Effekt.
- **20 Triple-Elementartürme (Alle 20 3er-Kombinationen):**
  - *Oblivion, Pure Laser, Life, Eclipse, Prisma, Wellspring, Polar, Solar Flare, Forge, Gaia, Abyssal, Plague, Mire, Corrosion, Meteor, Rot, Biohazard, Obsidian, Tsunami, Juggernaut.*

### 4. Elementarwächter & Beschwörungs-Altar
- Alle 5 Wellen (Welle 5, 10, 15, 20 ...) erhältst du einen **Wächter-Beschwörungstoken**.
- Klicke auf den **Wächter-Altar** oben im HUD, um einen Elementarwächter deiner Wahl (Licht, Schatten, Wasser, Flammen, Natur, Erde) in die Arena zu rufen.
- Besiegst du den Wächter-Boss, erhältst du **+1 Essenz** dieses Elements, wodurch du neue Grundstufen und Hybridtürme freischaltest!
- *Alternative:* Tausche den Token gegen eine dauerhafte **Erhöhung deiner Zinsrate um +0.5%** ein!

### 5. Das Zinseszins-System
- Alle **15 Sekunden** schüttet die Bank **2.0% Zinsen** auf dein ungenutztes Gold aus.
- Sparsamkeit und strategisches Haushalten werden mit exponentiellem Zinseszins belohnt!

### 6. Prozedurale Audio-Synthese (NumPy & Pygame Mixer)
- Keine externen Audio-Dateien nötig: Alle 18 Soundeffekte (Laser, Donner, Blitze, Frost, Münzen, Fanfaren) werden in Echtzeit mathematisch synthetisiert.

---

## 🕹️ Steuerung & Tastenkürzel

| Taste / Aktion | Funktion |
| :--- | :--- |
| **Linksklick** | Turm auswählen, bauen, inspizieren oder Menü bedienen |
| **Rechtsklick / Esc** | Turm-Platzierung abbrechen / Turmauswahl aufheben |
| **Leertaste (`Space`)** | Spiel pausieren / fortsetzen |
| **`1`, `2`, `3`** | Spielgeschwindigkeit (1x, 2x, 4x) |
| **`U`** | Ausgewählten platzierten Turm aufwerten (Upgrade) |
| **`S`** | Ausgewählten platzierten Turm verkaufen (Sell, 80% Rückerstattung) |

---

## 🚀 Spiel starten

### Voraussetzungen
- Python $\ge$ 3.12 (oder Python 3.14)
- [`uv`](https://github.com/astral-sh/uv) (empfohlen) oder Standard-`pip`

### Starten mit `uv`:
```bash
# Spiel direkt starten
uv run py-warcraft-td

# Schnelles 20-Wellen-Spiel direkt starten
uv run py-warcraft-td --quick --difficulty Hard

# Tests ausführen
uv run pytest
```
