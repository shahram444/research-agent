# 🔬 Research Agent
### AI-Powered Academic Paper Discovery & Analysis Tool

A powerful desktop application that helps researchers find papers, analyze PDFs, and verify citations using AI (Claude or ChatGPT).

---

## ✨ Features

### 🔍 Feature 1: Paper Finder
**Search for academic papers online using AI**

| What it does | How it helps |
|--------------|--------------|
| Searches Google Scholar, arXiv, PubMed, etc. | Find relevant papers fast |
| Returns title, authors, year, journal | Get complete citation info |
| Provides paper summaries | Understand papers without reading |
| Shows relevance to your query | Know why each paper matters |
| Includes direct links | Access papers immediately |

**Example Query:**
```
pore-scale numerical simulation anaerobic oxidation methane AOM reactive transport
```

**Example Output:**
```
[1] Pore-Scale Modeling of Anaerobic Methane Oxidation in Marine Sediments
    Authors: Smith, J., Johnson, K., Lee, M.
    Year: 2023
    Journal: Water Resources Research
    
    Summary: This study develops a pore-scale reactive transport model
    for AOM processes in marine sediments using lattice Boltzmann methods...
    
    Relevance: Directly addresses numerical simulation of AOM at pore scale
    with reactive transport framework similar to your research approach.
    
    Link: https://doi.org/10.1029/2023WR034567
```

---

### 📁 Feature 2: Local Paper Analyzer
**Ask questions about your own PDF papers**

| What it does | How it helps |
|--------------|--------------|
| Reads PDFs from any folder | Use your existing paper collection |
| Understands paper content | AI reads and comprehends papers |
| Answers any question | Get insights without re-reading |
| Cites specific papers | Know which paper said what |
| Compares across papers | Find agreements/disagreements |

**Example Questions You Can Ask:**
```
What oxygen penetration depths are reported in these papers?
```
```
Which papers use lattice Boltzmann methods and what are their findings?
```
```
Compare the Damköhler numbers used across these studies
```
```
What are the main limitations mentioned in these papers?
```
```
Find all data about biofilm thickness measurements
```

---

### ✓ Feature 3: Citation Verifier
**Check if your citations actually support your claims**

| What it does | How it helps |
|--------------|--------------|
| Reads your paragraph | Understands your claims |
| Analyzes cited papers | Checks original sources |
| Verifies each claim | Confirms support exists |
| Provides evidence | Shows exact supporting text |
| Suggests improvements | Strengthens your writing |

**Example Use:**
```
Your paragraph:
"According to Smith et al. (2022), oxygen penetration depth in marine 
sediments typically ranges from 2-5mm under normal conditions."

AI Response:
✓ SUPPORTED
Evidence from Smith2022.pdf, page 12: "Oxygen penetration depths 
measured between 1.8 and 5.2 mm across all sampling sites..."
```
---

## 📋 Requirements

- **Python 3.8+** (Download: https://www.python.org/downloads/)
- **API Key** (choose one):
  - Claude: https://console.anthropic.com
  - ChatGPT: https://platform.openai.com/api-keys

---

## 🚀 Installation (Step-by-Step)

### Step 1: Install Python
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or newer
3. Run installer
4. ✅ **CHECK "Add Python to PATH"** during installation
5. Click Install

### Step 2: Create Project Folder
Open **Command Prompt** (Windows) or **Terminal** (Mac/Linux):

**Windows:**
```cmd
mkdir C:\ResearchAgent
cd C:\ResearchAgent
```

**Mac/Linux:**
```bash
mkdir ~/ResearchAgent
cd ~/ResearchAgent
```

### Step 3: Download the Script
1. Download `research_agent_gui.py` from the provided files
2. Save it to `C:\ResearchAgent\` (or `~/ResearchAgent/` on Mac)

### Step 4: Install Required Packages
```cmd
pip install anthropic openai pymupdf rich
```

You should see:
```
Successfully installed anthropic-0.75.0 openai-1.x.x pymupdf-1.x.x rich-13.x.x
```

### Step 5: Get Your API Key

**Option A: Claude (Anthropic) - Recommended**
1. Go to https://console.anthropic.com
2. Sign up / Log in
3. Click "Get API Key"
4. Add $5 credits (lasts a long time)
5. Create new key
6. Copy the key (starts with `sk-ant-...`)

**Option B: ChatGPT (OpenAI)**
1. Go to https://platform.openai.com/api-keys
2. Sign up / Log in
3. Create new key
4. Copy the key (starts with `sk-...`)

### Step 6: Set Your API Key

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```
or
```cmd
set OPENAI_API_KEY=sk-your-openai-key-here
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```
or
```bash
export OPENAI_API_KEY="sk-your-openai-key-here"
```

### Step 7: Run the Application
```cmd
cd C:\ResearchAgent
python research_agent_gui.py
```

🎉 **The GUI window should open!**

---

## 📖 How to Use

### 🔍 Using Paper Finder

1. Click **"🔍 Paper Finder"** tab
2. Type your search query:
   ```
   pore-scale numerical simulation anaerobic oxidation methane AOM
   ```
3. Click **"🔍 Search Papers"**
4. Wait 15-30 seconds
5. View results with titles, authors, summaries, and links

**Good Search Queries:**
| Topic | Query |
|-------|-------|
| AOM modeling | `pore-scale numerical simulation anaerobic oxidation methane` |
| Biofilm transport | `lattice Boltzmann biofilm reactive transport porous media` |
| Oxygen dynamics | `oxygen penetration depth sediment pore-scale modeling` |
| Carbonate microbes | `micro-CT carbonate microbial distribution sulfate methane` |

---

### 📁 Using Local Paper Analyzer

1. Click **"📁 Local Paper Analyzer"** tab
2. Click **"Browse..."** button
3. Select folder containing your PDF papers
4. Click **"Load"**
5. You'll see: `Loaded X papers`
6. Type your question:
   ```
   What methods do these papers use for pore-scale simulation?
   ```
7. Click **"🔬 Analyze Papers"**
8. Wait 30-60 seconds (depends on number of papers)
9. Read the detailed analysis with citations

**Example Questions:**
```
What are the key findings about oxygen consumption rates?
```
```
Summarize the modeling approaches used in each paper
```
```
Find specific numerical values for diffusion coefficients
```
```
Compare how different papers handle boundary conditions
```

---

### ✓ Using Citation Verifier

1. **First:** Load papers in the Analyzer tab
2. Click **"✓ Citation Verifier"** tab
3. Paste your paragraph:
   ```
   According to Smith et al. (2022), the oxygen penetration 
   depth in marine sediments typically ranges from 2-5 mm. 
   This finding is consistent with Johnson (2021) who reported
   similar values using pore-scale modeling approaches.
   ```
4. Optionally edit "What to Verify":
   ```
   Check if the numerical values I cite are accurate
   ```
5. Click **"✓ Verify Citations"**
6. View results showing:
   - Overall verdict (SUPPORTED / PARTIALLY SUPPORTED / NOT SUPPORTED)
   - Claim-by-claim analysis
   - Evidence from papers
   - Recommendations

---

### ⚙️ Settings Tab

1. **Choose Provider:**
   - ○ Claude (Anthropic) - Has web search, better for research
   - ○ ChatGPT (OpenAI) - Alternative option

2. **Enter API Key:**
   - Paste your key
   - Click "💾 Save & Connect"
   - Should show: ✓ Connected to Claude!

---

## 💡 Tips for Best Results

### Paper Finder Tips:
| Do ✅ | Don't ❌ |
|-------|---------|
| Use specific terms: `lattice Boltzmann AOM` | Vague queries: `modeling` |
| Include method names | Single word searches |
| Add field-specific terms | Generic descriptions |

### Analyzer Tips:
| Do ✅ | Don't ❌ |
|-------|---------|
| Ask specific questions | Ask vague questions |
| Limit to 10 papers at a time | Load 50+ papers |
| Use clear language | Use ambiguous terms |

### Verifier Tips:
| Do ✅ | Don't ❌ |
|-------|---------|
| Include full paragraph with context | Single sentences |
| Name the papers you're citing | Forget to load the PDFs |
| Be specific about what to verify | Vague verification requests |

---

## ⚠️ Troubleshooting

### "No module named 'anthropic'"
```cmd
pip install anthropic openai pymupdf rich
```

### "API Key not found"
Set it in Command Prompt before running:
```cmd
set ANTHROPIC_API_KEY=your-key-here
python research_agent_gui.py
```

Or enter it in the Settings tab.

### "File not found"
Make sure you're in the right folder:
```cmd
cd C:\ResearchAgent
dir
```
You should see `research_agent_gui.py` listed.

### GUI doesn't open
Install tkinter:
```cmd
# Windows: Usually included
# Ubuntu/Debian:
sudo apt-get install python3-tk
# Mac: Usually included
```

### Takes too long
- Reduce number of papers (move some out of folder)
- Use shorter queries
- Check internet connection

---

## 💰 API Costs

| Provider | Cost | Notes |
|----------|------|-------|
| Claude | ~$0.01-0.10 per query | Web search included |
| ChatGPT | ~$0.01-0.05 per query | No web search |

$5 credit typically lasts for 50-500 queries depending on paper sizes.

---

## 📁 Files Included

| File | Description |
|------|-------------|
| `research_agent_gui.py` | Main GUI application |
| `research_agent_cli.py` | Command-line version |
| `README.md` | This documentation |

---

## 🔧 Command Line Version

If you prefer terminal:
```cmd
python research_agent_cli.py
```

Commands:
```
folder <path>      Set papers folder
list               List loaded papers  
find <query>       Search papers online
analyze <question> Analyze local papers
verify             Verify citations
quit               Exit
```

---

## 📄 License

MIT License - Free to use and modify for your research!

---

Made with ❤️ for researchers
