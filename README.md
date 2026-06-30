# 🎮 Indie Games on Twitch — 2025
> **Do indie games punch above their weight on Twitch?**  [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://steam-twitch-analysis-2025.streamlit.app/)
> An end-to-end data analysis pipeline crossing Steam catalog metadata with Twitch viewership data for the top 1,000 most-watched games of 2025.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?logo=plotly)](https://plotly.com)
[![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas)](https://pandas.pydata.org)

---

## 📖 About

This project analyzes whether indie games compete with AAA titles on Twitch using a dataset built from multiple sources.

The pipeline combines Steam metadata, Twitch statistics, and manually curated non-Steam titles to produce a fair comparison between indie and non-indie games. The final result is an interactive Streamlit dashboard with insights into watch hours, streamer reach, platform coverage, pricing, review scores, and game release trends.

**Highlights**

- End-to-end ETL pipeline
- Twitch API integration
- Selenium web scraping
- Data cleaning & fuzzy matching
- Interactive Streamlit dashboard
- Reproducible data analysis

---

## 📌 Project Overview

This project investigates the performance of indie games on Twitch in 2025, measured by watch hours, number of streamers, and peak viewership. The analysis combines two primary data sources:

- **Steam API** — game metadata (genre, price, release date, user review scores) snapshot from March 2025
- **SullyGnome** — Twitch viewership statistics for the top 1,000 most-watched games across the full year 2025

The core challenge: Steam's catalog does not include the largest Twitch titles (League of Legends, Fortnite, VALORANT, all Nintendo IP). A Steam-only join would structurally undercount non-indie viewership and inflate indie share. This was solved by **manually classifying and adding ~150 non-Steam titles** with their SullyGnome data, making the comparison fair.

---

## 🔍 Key Findings

| Finding | Detail |
|---------|--------|
| **Watch-hour gap** | Non-indie games average **~7–9× more** watch hours per title than indie — driven by IP recognition and marketing budgets, not audience preference |
| **Breakout effect** | The top indie game (Rust) outperformed **70%+ of all non-indie titles** in the dataset |
| **2025 launches** | Titles like R.E.P.O., Schedule I, and Peak entered the top 1,000 within weeks of launch, averaging competitively against 2025 non-indie releases |
| **Steam blind spot** | Only ~50% of Twitch watch hours come from Steam-available games — any Steam-only analysis misses half the picture |
| **Streamer reach** | Several indie games (R.E.P.O., Phasmophobia, Among Us) attract more unique streamers than many AAA titles, indicating strong discoverability |
| **Review score ≠ viewership** | High Steam review scores correlate weakly with watch hours — viral gameplay and social media moment matter more than critical reception |

---

## 🗂️ Project Structure

```text
steam-twitch-analysis/
│
├── notebooks/
│   ├── 01_twitch_data.py
│   ├── 02_sullygnome_scraper.py
│   ├── 03_analysis_final.py
│   └── 04_missing_games.py
│
├── data/
│   ├── disponibilidade_steam.csv
│   ├── indie_final.csv
│   ├── naoindie_final.csv
│   ├── sullygnome_top2000.csv
│   └── twitch_top_games.csv
│
├── assets/
├── app.py
├── game_utils.py
├── requirements.txt
└── README.md
```
> **Note:** The original Steam catalog snapshot (~447 MB) is intentionally excluded from this repository because it exceeds GitHub's file size limit. The processed datasets included here are sufficient to reproduce the analysis and dashboard.

---

## 🔄 Data Pipeline

```text
                 Steam API
                     │
                     ▼
        Steam Catalog Snapshot
                     │
                     │
                     ├──────────────────────────┐
                     │                          │
                     ▼                          ▼
          Data Cleaning              SullyGnome Scraper
      (Normalization & Reviews)      (Top 1,000 Games)
                     │                          │
                     └──────────────┬───────────┘
                                    ▼
                           Merge & Deduplication
                                    ▼
                     Manual Classification (Steam /
                        Non-Steam / Indie / AAA)
                                    ▼
                       Processed Analysis Datasets
                                    ▼
                         Interactive Streamlit App

```
## ⚙️ Methodology
The project follows a complete ETL (Extract, Transform, Load) workflow, combining data from multiple sources, cleaning inconsistencies, enriching missing information, and producing reproducible datasets for analysis and visualization.

### Data Collection
- **Twitch API** (`01_twitch_data.py`): OAuth2 authentication, paginated requests to `/helix/games/top`
- **SullyGnome** (`02_sullygnome_scraper.py`): Selenium + ChromeDriver scraper with anti-bot mitigations, extracting watch hours, stream time, peak viewers, and streamer count for the top 1,000 games of 2025

### Data Processing (`03_analysis_final.py`)
1. **Name normalisation** (`game_utils.py`): strips Unicode symbols (™, ®, ©), converts Roman numerals, handles known SullyGnome aliases (e.g. `METAL GEAR SOLID Δ` → `Metal Gear Solid Delta`)
2. **Inner join** between Steam catalog and Twitch data on normalised game names
3. **Manual enrichment**: ~150 titles not on Steam (Riot, Epic, Nintendo, Blizzard, Activision) added with SullyGnome data to avoid undercounting non-indie viewership
4. **Deduplication**: two-pass dedup — first by exact name, then by special-character-stripped key to catch cases like `Rocket League` vs `Rocket League®`
5. **Review score backfill**: Steam's March 2025 snapshot predates several major 2025 launches; review scores for post-snapshot titles (Peak, Hollow Knight: Silksong, Megabonk, CloverPit, etc.) were manually verified and added from current Steam store pages
6. **Classification**: indie flag from Steam genre tags, with manual corrections for edge cases (Rocket League → non-indie post Epic acquisition; Fall Guys → non-indie post Epic acquisition)

### Platform Coverage Analysis (`04_missing_games.py`)
- Classifies all 1,000 SullyGnome titles into: On Steam / Not on Steam / Non-Game Content / Unclassified
- Keyword-based classification with `rapidfuzz` fuzzy matching for ambiguous cases
- Produces `disponibilidade_steam.csv` used in the dashboard's platform coverage section

---

## 📸 Dashboard Preview

> Dashboard screenshots will be added soon.

---

## 📊 Dashboard Sections

| Section | What It Shows |
|---------|--------------|
| **Key Findings** | 6 data-driven insight cards with computed metrics |
| **Top 20 Most Watched** | Side-by-side indie vs non-indie ranking by watch hours |
| **Game Type Breakdown** | Avg and total watch hours by type (Single Player / Multiplayer / MMO) |
| **Price Range Analysis** | Watch performance by price tier — FTP caveat explicitly noted |
| **Top 15 by Streamers** | Content creator reach, indie vs non-indie |
| **2025 vs Legacy** | Cohort comparison with partial-year caveat |
| **Review Score vs Viewership** | Steam positive % bucketed against watch hours and streamer count |
| **Platform Coverage** | Donut chart: what share of Twitch watch hours comes from Steam games |
| **Opportunity Index** | Peak viewers ÷ streamers ratio — identifies under-served niches for new creators |
| **Explore** | Interactive filterable table of the full dataset |

---

## 🚀 Running Locally

### Prerequisites
```bash
Python 3.11+
Chrome + ChromeDriver (for scraper only)
```

### Setup

```bash
git clone https://github.com/Danjunq87/steam-twitch-analysis.git
cd steam-twitch-analysis
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

After the installation, you can either:

- Run the complete data pipeline to regenerate all datasets.
- Use the processed datasets already included in the repository to launch the dashboard immediately.

> **Note:** The raw Steam catalog snapshot is intentionally excluded from this repository because it exceeds GitHub's file size limit.

### Environment Variables (scraper + Twitch API only)
Create a `.env` file in the project root:
```
TWITCH_CLIENT_ID=your_client_id
TWITCH_CLIENT_SECRET=your_client_secret
```

### Run the Pipeline
```bash
# Step 1 — collect Twitch data (optional if using provided CSVs)
python notebooks/02_sullygnome_scraper.py

# Step 2 — run analysis and generate datasets
python notebooks/03_analysis_final.py

# Step 3 — classify Steam coverage
python notebooks/04_missing_games.py

# Step 4 — launch dashboard
streamlit run app.py
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.11** | Core language |
| **Pandas** | Data wrangling, joins, aggregations |
| **Selenium + ChromeDriver** | Web scraping (SullyGnome) |
| **Requests** | Twitch API calls |
| **rapidfuzz** | Fuzzy string matching for game name resolution |
| **Plotly** | Interactive charts |
| **Streamlit** | Dashboard framework |
| **python-dotenv** | Environment variable management |

---

## ⚠️ Limitations

- **Steam snapshot is from March 2025** — games released after that date were added manually and may have incomplete metadata (estimated owners, peak CCU)
- **Indie classification** follows Steam's own genre tagging, which is self-reported by developers and not always consistent
- **SullyGnome data** reflects Twitch watch hours, not actual player counts — a game can have low viewership and a large player base (or vice versa)
- **Non-Steam titles** were classified manually — a keyword-based heuristic, not an exhaustive API lookup
- **Review scores for 41 indie titles** remain missing — either no Steam page, insufficient reviews, or too new for inclusion in the snapshot

---

## 🚀 Future Improvements

Possible future enhancements include:

- Integration with the SteamSpy API for richer ownership estimates.
- Automated Steam Store scraping for review score updates.
- Time-series analysis of Twitch viewership trends.
- Machine learning models to predict breakout indie titles.
- Deployment of the Streamlit dashboard to Streamlit Community Cloud.
- Automated data pipeline using GitHub Actions.

---

## 👤 Author

**Daniel Silva Junqueira**

Aspiring Data Analyst with a focus on Python, SQL, data visualization, and ETL pipelines.

- GitHub: https://github.com/Danjunq87
- LinkedIn: https://www.linkedin.com/in/daniel-silva-junqueira-105261b5/

---

*Data sources: [Steam Store API](https://store.steampowered.com/api/) · [SullyGnome](https://sullygnome.com) · [Twitch API](https://dev.twitch.tv/docs/api/)*
