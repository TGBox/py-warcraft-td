# ⚡ py-warcraft-td: Element Tower Defense (Warcraft III Adaptation)

Eine moderne, native Python-Desktop-Adaption der legendären Warcraft III Custom Map **Element TD** (Element Tower Defense), kombiniert mit freiem Labyrinth-Bauen (**Mazing** via dynamischer A\*-Pfadsuche), prozeduralen Sprites und Vektor-Icons sowie nativer Unterstützung für **1920x1080 (16:9 Full HD)** und **2560x1080 (21:9 Ultrawide)** inkl. **Vollbildmodus**.

---

## 🌟 Grafische Neuerungen & Visuelle Highlights

### 🎨 Prozedural generierte Sprites (Pixel-Art / WC3-Stil)

- **Gegner & Bosse:**
  - Jede Gegner-Kategorie besitzt ein individuelles, dynamisch skaliertes Modell:
    - *Bosse & Elementarwächter:* Gewaltige Basaltpanzer, pulsierende Elementarauren, goldene Kronen und leuchtende Kerne.
    - *Flugeinheiten:* Große Schwingen mit Flügelschlag-Animation und realistischem Bodenschatten.
    - *Schnelle Läufer (Wölfe / Raptoren):* Stromlinienförmiger Körper mit Geschwindigkeitsstreifen und Kämmen.
    - *Tanks / Schwere Brecher:* Wuchtige Felsenschultern, Eisenpanzerung und Zwillingsaugen.
    - *Schwarm-Kriecher:* Kompakte Mehrbeiner-Insektoiden.
- **Türme:**
  - Mehrschichtige Steinfundamente, Rumpfverzierungen und elementare Runenböden.
  - Pfeilturm mit Holzarmbrust und Pfeilspitze; Kanonenturm mit genieteter Eisenhaubitze.
  - Elementartürme mit schwebenden Kristallkernen, Spuren und orbitalen Elementarkugeln bei Dual- und Triple-Kombinationen.
  - Goldene Stufen-Indikatoren (Pips) für Tier 1 bis Tier 3.

### 🛡️ Gestochen scharfe Vektor-Icons (Keine Vierecke / Tofu-Boxen mehr!)

- Alle Schriftart-Emojis wurden durch ein eigenes Vektor-Icon-System ersetzt:
  - **Währung:** Geprägte Goldmünze mit Glanzkante.
  - **Leben:** Rubinrotes Herz mit Lichtreflex.
  - **Kampf & Altar:** Gekreuzte Silberklingen mit Goldknauf.
  - **Flugeinheiten:** Ausgebreitete Adlerschwingen.
  - **Schloss:** Messing-Vorhängeschloss für noch gesperrte Elementkombinationen.
  - **Element-Abzeichen:** Eigene Symbole für Licht (Sonne/Stern), Dunkelheit (Mondsichel), Wasser (Tropfen), Feuer (Flamme), Natur (Smaragdblatt) und Erde (Gebirgsgipfel).
  - **UI-Steuerung:** Eigene Icons für Play, Pause, Fast-Forward, Upgrade-Pfeil und Schließen-Kreuz.

---

## 🖥️ Auflösungen & Vollbildmodus

Das Spiel passt seine Benutzeroberfläche und das Spielfeld dynamisch an:

- **1920 x 1080 (16:9 Full HD):** 26 Spalten x 17 Zeilen Spielfeld mit 48px Zellgröße und 588px Sidebar.
- **2560 x 1080 (21:9 Ultrawide):** 34 Spalten x 17 Zeilen Spielfeld mit 48px Zellgröße und 828px breiter Sidebar mit **zweispaltigen Turmkarten**!
- **1360 x 768 (Fenstermodus):** Kompaktes Fenster-Layout.
- **Vollbild (Fullscreen):** Jederzeit im Spiel mit **`F11`** (oder über den Button in der oberen Leiste) umschaltbar!

---

## 🌟 Spielmechaniken

### 1. Der 6-Elemente-Vorteilskreis

$$\text{Licht} \rightarrow \text{Dunkelheit} \rightarrow \text{Wasser} \rightarrow \text{Feuer} \rightarrow \text{Natur} \rightarrow \text{Erde} \rightarrow \text{Licht}$$

- **Überlegen (200% Schaden):** Das angreifende Element schlägt das Ziel im Kreis.
- **Unterlegen (50% Schaden):** Das Ziel resistiert dem Angriff.
- **Neutral (100% Schaden):** Physischer Schaden oder nicht benachbarte Elemente.

### 2. Freies Labyrinth-Bauen (Mazing) & Fliegende Einheiten

- **Bodeneinheiten:** Berechnen in Echtzeit den kürzesten Weg via **A\*-Pfadsuche** um errichtete Türme.
- **Wegblockierungs-Schutz:** Verhindert das vollständige Zubauen des Durchgangs.
- **Flugeinheiten:** Nehmen die direkte Luftlinie quer über die Karte (nur von Luftabwehr treffbar).
- **Leak-Respawn:** Durchgebrochene Monster ziehen Leben ab und **erscheinen am Start mit ihren Rest-HP erneut**, sodass du weiterhin die Chance auf das Kopfgeld hast!

### 3. Das vollständige 43-Turm-Kompendium

- **Starter:** Pfeilturm (Boden/Luft), Kanonenturm (Fläche Boden).
- **6 Basis-Elementartürme (Stufe 1–3):** Licht, Dunkelheit, Wasser, Feuer, Natur, Erde.
- **15 Dual-Türme:** Täuschung, Eis, Elektrizität, Sonne, Quark (Gold), Dunst, Verdammnis, Gift, Eisen, Dampf, Geysir, Schlamm, Verbrennung, Magma, Wurzeln.
- **20 Triple-Türme:** Oblivion, Pure Laser, Life, Eclipse, Prisma, Wellspring, Polar, Solar Flare, Forge, Gaia, Abyssal, Plague, Mire, Corrosion, Meteor, Rot, Biohazard, Obsidian, Tsunami, Juggernaut.

### 4. Elementarwächter & Beschwörungs-Altar

- Alle 5 Wellen erhältst du einen **Beschwörungstoken**.
- Rufe im **Wächter-Altar** einen Elementarwächter deiner Wahl heraus.
- Bei Sieg erhältst du **+1 Essenz** dieses Elements für neue Turmstufen und Kombinationen!
- *Alternative:* Tausche den Token gegen dauerhafte **+0.5% Zinsen** ein.

### 5. Zinsen & Wirtschaft

- Alle **15 Sekunden** erhältst du **2.0% Zinsen** auf dein nicht ausgegebenes Gold.

---

## 🕹️ Steuerung & Tastenkürzel

| Taste / Aktion | Funktion |
| :--- | :--- |
| **`F11`** | **Vollbildmodus aktivieren / deaktivieren** |
| **`X` / `Entf`** | **Löschen- / Radierer-Modus umschalten** (Türme einzeln oder mit gedrückter Maustaste abreißen) |
| **Linksklick** | Turm auswählen, bauen, inspizieren, abreißen oder Menüs bedienen |
| **Gedrückt halten & Ziehen (im Löschmodus)** | **Radierer:** Zieht über mehrere Türme, um sie blitzschnell ohne Abfrage zu verkaufen! |
| **Rechtsklick / Esc** | Bauen abbrechen / Löschmodus beenden / Turmauswahl aufheben |
| **Leertaste (`Space`)** | Spiel pausieren / fortsetzen |
| **`1`, `2`, `3`** | Spielgeschwindigkeit (1x, 2x, 4x) |
| **`U`** | Ausgewählten Turm verbessern (Upgrade) |
| **`S`** | Ausgewählten Turm verkaufen (80% Rückerstattung) |

---

## 🚀 Spiel starten

### Starten mit `uv`

```bash
# Spiel standardmäßig auf 1920x1080 starten
uv run py-warcraft-td

# Direkt im Vollbildmodus starten
uv run py-warcraft-td --fullscreen

# Auf 2560x1080 (21:9 Ultrawide) starten
uv run py-warcraft-td --ultrawide

# 21:9 Ultrawide im Vollbildmodus
uv run py-warcraft-td --ultrawide --fullscreen

# Schnelles 20-Wellen-Spiel starten
uv run py-warcraft-td --quick --difficulty Hard

# Tests ausführen
uv run pytest
```
