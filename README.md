# 🏋️ Viktspårare - Weight Tracker

En modern och användarvänlig desktop-applikation för att spåra din viktresa med avancerade grafer, prediktioner och analyser. Perfekt för alla som vill ha en vetenskaplig approach till vikthantering!

![Viktspårare Screenshot](screenshot.png)

## ✨ Funktioner

### 📊 Visualisering och Grafer
- **Interaktiv viktgraf** med zoom och panorering
- **Prediktionsmodeller** som visar framtida viktutveckling:
  - Linjär regression
  - Exponentiell utjämning
  - Viktad glidande medelvärde (WMA)
- **Optimal viktförlust-guide** (0.5-0.75% av vikten per vecka)
- **Anpassningsbara markeringar**:
  - Helgmarkeringar för att se mönster
  - Specifika veckodagar (perfekt för fastedagar, träningsdagar etc.)
  - Anpassade händelser med färger och etiketter

### 📈 Statistik och Analys
- BMI-beräkning (Body Mass Index)
- Veckovis viktförändring i kg och procent
- Total viktförändring sedan start
- Min/max/medelvikt
- Vetenskapligt baserade rekommendationer

### 📝 Datahantering
- Sorterbar historik (klicka på kolumnrubriker för att sortera)
- Enkel viktinmatning med datumväljare
- JSON-baserad lokal datalagring
- Export/import möjligheter

### 🎨 Användarvänligt Gränssnitt
- Modern flik-baserad design
- Automatisk sparning av inställningar
- Intuitiva kontroller
- Responsiv layout

## 🚀 Installation

### Krav
- **Python 3.7 eller högre**
- **Windows, macOS eller Linux**

### Steg-för-steg Guide

#### 1. Installera Python
Om du inte har Python installerat:

**Windows:**
1. Gå till [python.org/downloads](https://www.python.org/downloads/)
2. Ladda ner den senaste versionen
3. **VIKTIGT:** Kryssa i "Add Python to PATH" under installationen!
4. Kör installationsfilen

**macOS:**
```bash
# Använd Homebrew (rekommenderat)
brew install python3

# Eller ladda ner från python.org
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip
```

#### 2. Ladda ner Viktspåraren

**Alternativ A: Med Git (rekommenderat)**
```bash
git clone https://github.com/DITTANVÄNDARNAMN/viktspårare.git
cd viktspårare
```

**Alternativ B: Ladda ner ZIP**
1. Klicka på den gröna "Code"-knappen högst upp på sidan
2. Välj "Download ZIP"
3. Packa upp ZIP-filen
4. Öppna mappen i terminalen/kommandotolken

#### 3. Installera Beroenden

Öppna terminal/kommandotolk i projektmappen och kör:

```bash
pip install -r requirements.txt
```

**Om du får felmeddelande på Linux**, prova:
```bash
pip install -r requirements.txt --break-system-packages
```

**Om du får felmeddelande om pip**, prova:
```bash
python -m pip install -r requirements.txt
```

#### 4. Starta Applikationen

```bash
python weight_tracker.py
```

**På vissa system kan du behöva använda:**
```bash
python3 weight_tracker.py
```

## 📖 Användarguide

### Lägga till vikt
1. Öppna fliken **"Lägg till vikt"**
2. Välj datum (standard är dagens datum)
3. Ange din vikt i kg
4. (Valfritt) Lägg till anteckningar
5. Klicka på **"Lägg till vikt"**

### Visa graf och statistik
1. Gå till fliken **"Graf & Analys"**
2. Se din viktgraf med automatiska prediktioner
3. Statistik visas till vänster med all relevant information

### Anpassa grafen
1. Öppna fliken **"Grafanpassning"**
2. **Helgmarkering:** Kryssa i för att se helger markerade i grafen
3. **Veckodagar:** Markera specifika dagar (t.ex. måndagar för fastedagar)
4. **Anpassade händelser:** Lägg till viktiga datum som påverkat din vikt
   - Klicka "Lägg till händelse"
   - Välj datum, skriv etikett och välj färg
   - Händelsen visas nu i grafen
5. Alla ändringar **sparas automatiskt**!

### Historik
1. Gå till fliken **"Historik"**
2. Se alla dina viktmätningar
3. **Klicka på kolumnrubriker** för att sortera (datum, vikt, etc.)
4. Ta bort poster med "Ta bort"-knappen

### Profilinställningar
1. Öppna fliken **"Profilinställningar"**
2. Ange din längd för korrekt BMI-beräkning
3. Se din målvikt och rekommenderad veckoförändring

## 📊 Förstå Prediktionerna

Applikationen använder tre olika modeller för att förutsäga framtida viktförändringar:

- **Linjär trend (blå linje):** Enkel linjär projektion baserat på din historiska data
- **Exponentiell utjämning (orange linje):** Ger mer vikt åt nyare mätningar
- **Optimal viktförlust (grön/röd zon):** Visar den vetenskapligt rekommenderade viktförlusten (0.5-0.75% av din vikt per vecka)

### Varför 0.5-0.75% per vecka?
Detta är den hastighet som forskning visar är optimal för:
- Hållbar viktminskning
- Minimera muskelbortfall
- Undvika metabolisk anpassning
- Långsiktig framgång

För en person på 100 kg innebär det 0.5-0.75 kg per vecka, medan för någon på 70 kg är det 0.35-0.53 kg per vecka.

## 🛠️ Felsökning

### "ModuleNotFoundError: No module named 'PyQt5'"
**Lösning:** Installera beroendena igen:
```bash
pip install -r requirements.txt
```

### "ModuleNotFoundError: No module named 'scipy'"
**Lösning:** Installera scipy:
```bash
pip install scipy
```

### Applikationen startar inte
1. Kontrollera att du har Python 3.7 eller högre: `python --version`
2. Kontrollera att alla beroenden är installerade: `pip list`
3. Försök ta bort `weight_data.json` och `weight_settings.json` om de finns

### Grafen visas inte
1. Kontrollera att matplotlib och scipy är installerade
2. Prova att lägga till minst 3 viktmätningar med olika datum

### "Permission denied" på Linux
**Lösning:** Lägg till execution-rättigheter:
```bash
chmod +x weight_tracker.py
```

## 📁 Filstruktur

```
viktspårare/
│
├── weight_tracker.py          # Huvudprogrammet
├── requirements.txt           # Python-beroenden
├── README.md                  # Denna fil
│
├── weight_data.json          # Din viktdata (skapas automatiskt)
├── weight_settings.json      # Dina inställningar (skapas automatiskt)
├── profile_data.json         # Din profil (skapas automatiskt)
└── vis_settings.json         # Visualiseringsinställningar (skapas automatiskt)
```

## 🔒 Integritet och Datasäkerhet

- **All data lagras lokalt** på din dator - inget skickas till internet
- **Inga konton eller inloggningar** krävs
- **Du äger din data** - JSON-filerna kan kopieras, säkerhetskopieras eller exporteras när som helst
- **Öppen källkod** - du kan granska all kod själv

## 🤝 Bidra

Bidrag är välkomna! Om du vill hjälpa till:

1. Forka projektet
2. Skapa en feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit dina ändringar (`git commit -m 'Add some AmazingFeature'`)
4. Push till branchen (`git push origin feature/AmazingFeature`)
5. Öppna en Pull Request

### Idéer för framtida funktioner
- Export till Excel/CSV
- Fler prediktionsmodeller
- Mål-viktfunktion med nedräkning
- Träningsdagbok integration
- Mått-spårning (midja, höfter etc.)
- Mobil app (iOS/Android)

## 📜 Licens

Detta projekt är licensierat under MIT License - se [LICENSE](LICENSE) filen för detaljer.

## 👨‍💻 Författare

**Din Name** - [GitHub](https://github.com/DITTANVÄNDARNAMN)

## 🙏 Erkännanden

- PyQt5 för det fantastiska GUI-ramverket
- Matplotlib för grafer och visualisering
- NumPy och SciPy för matematiska beräkningar
- Alla som bidragit med feedback och förbättringsförslag!

## 📞 Support

Om du har frågor eller problem:
- Öppna en [Issue](https://github.com/DITTANVÄNDARNAMN/viktspårare/issues) på GitHub
- Läs igenom [Felsökning](#-felsökning)-sektionen ovan

## ⭐ Gilla projektet?

Om du tycker om Viktspåraren, ge gärna projektet en stjärna på GitHub! Det hjälper andra att hitta det.

---

**OBS:** Denna applikation är ett verktyg för personlig viktspårning och ersätter inte professionell medicinsk rådgivning. Konsultera alltid en läkare eller dietist för personlig hälsorådgivning.
