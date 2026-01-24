# 🚀 Snabbstart - Viktspåraren

## För Nybörjare (Windows)

### Steg 1: Installera Python
1. Gå till https://www.python.org/downloads/
2. Klicka på den gula "Download Python" knappen
3. Kör installationsfilen
4. **VIKTIGT:** Kryssa i "Add Python to PATH" längst ner!
5. Klicka "Install Now"

### Steg 2: Ladda ner Viktspåraren
1. Klicka på den gröna "Code" knappen högst upp på denna sida
2. Välj "Download ZIP"
3. Packa upp ZIP-filen där du vill ha programmet

### Steg 3: Installera Beroenden
1. Öppna den uppackade mappen
2. Håll inne `Shift` och högerklicka i mappen
3. Välj "Open PowerShell window here" eller "Öppna kommandotolken här"
4. Skriv: `pip install -r requirements.txt`
5. Tryck Enter och vänta tills allt är klart

### Steg 4: Starta Programmet
**Alternativ A:** Dubbelklicka på `start.bat`

**Alternativ B:** I PowerShell/Kommandotolken, skriv:
```
python weight_tracker.py
```

---

## För Mac-användare

### Steg 1: Installera Homebrew (om du inte har det)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Steg 2: Installera Python
```bash
brew install python3
```

### Steg 3: Ladda ner och installera
```bash
# Ladda ner med Git
git clone https://github.com/DITTANVÄNDARNAMN/viktspårare.git
cd viktspårare

# Installera beroenden
pip3 install -r requirements.txt

# Starta programmet
python3 weight_tracker.py
```

---

## För Linux-användare

### Ubuntu/Debian
```bash
# Installera Python och pip
sudo apt update
sudo apt install python3 python3-pip

# Ladda ner projektet
git clone https://github.com/DITTANVÄNDARNAMN/viktspårare.git
cd viktspårare

# Installera beroenden
pip3 install -r requirements.txt --break-system-packages

# Starta programmet
python3 weight_tracker.py
```

### Fedora
```bash
# Installera Python och pip
sudo dnf install python3 python3-pip

# Ladda ner projektet
git clone https://github.com/DITTANVÄNDARNAMN/viktspårare.git
cd viktspårare

# Installera beroenden
pip3 install -r requirements.txt

# Starta programmet
python3 weight_tracker.py
```

---

## ❓ Vanliga Problem

### "python is not recognized as an internal or external command"
**Lösning:** Python är inte i PATH. Installera om Python och kryssa i "Add Python to PATH"

### "No module named 'PyQt5'"
**Lösning:** Kör `pip install -r requirements.txt` igen

### Programmet startar inte
**Lösning:** Ta bort filerna `weight_data.json` och `weight_settings.json` om de finns

---

## 💡 Tips
- Första gången du startar programmet skapas automatiskt datafiler
- All data lagras lokalt på din dator
- Du kan säkerhetskopiera dina `.json` filer för att spara din vikthistorik

---

## 📖 Mer Hjälp
Läs den fullständiga [README.md](README.md) för detaljerad information!
