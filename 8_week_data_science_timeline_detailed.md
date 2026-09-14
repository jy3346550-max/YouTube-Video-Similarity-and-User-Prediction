# 8-Week Data Science Portfolio & Internship Prep Timeline (Detailed)

**Goal:** Ship the YouTube similarity/recommender project, build a second complementary project, close the SQL/BI skill gap, earn 1-2 certifications, and leave with internship-ready application materials.

**Time budget assumption:** ~12-15 hrs/week alongside coursework. Weeks are built to survive a bad exam week — if something slips, protect Weeks 5 and 8 (project completion + application week) above all else.

**How to use this doc:** Each week has (1) a rationale, (2) a day-by-day breakdown, (3) specific tools/resources named, (4) a concrete deliverable you can point to, and (5) a "definition of done" checklist so you're not guessing whether you can move on.

---

## Week 1 — Foundations: SQL, Tableau Basics, Project Infrastructure

**Rationale:** Everything downstream (feature engineering, dashboards, the eventual "likelihood" model) depends on being fluent enough in SQL and Tableau that they're not a bottleneck later. Front-loading this now means Weeks 2-8 are about the *project*, not about learning syntax mid-build.

| Day | Task | Detail |
|---|---|---|
| 1 | Enroll + start Google Data Analytics or Advanced Data Analytics Professional Certificate (Coursera) | If you already know spreadsheets/basic stats, audit/skip ahead — don't grind through material you've outgrown. Set a target of finishing ~40% of the specialization by end of Week 1. |
| 2 | SQL fundamentals refresh | SELECT, WHERE, JOIN (inner/left/right), GROUP BY, HAVING, aggregate functions (COUNT, SUM, AVG). Use **Mode Analytics' free SQL tutorial** — it's built around realistic business questions, not toy syntax drills. |
| 3 | SQL practice set #1 | Pull the **Kaggle "Trending YouTube Video Statistics"** dataset, load it into SQLite or Postgres, write 10 queries answering real questions ("which category has highest median views," "top 5 channels by trending frequency"). This dataset does double duty — you'll reuse it in Week 6 potentially. |
| 4 | SQL practice set #2 (intermediate) | Window functions (`ROW_NUMBER`, `RANK`, `LAG`/`LEAD`), CTEs, subqueries. Do 5-10 problems on **StrataScratch** (filter to "Data Analyst" tagged, real company questions) or **LeetCode SQL** (Medium difficulty). |
| 5 | Tableau Public setup | Install, connect to the YouTube trending CSV, build: (1) a bar chart of views by category, (2) a time series of trending duration, (3) a simple dashboard combining both with a filter. This is also your first pass toward the Tableau Desktop Specialist cert. |
| 6 | Project infrastructure | Create a Google Cloud project, enable **YouTube Data API v3**, generate an API key, set daily quota alerts (default quota is 10,000 units/day — metadata calls cost ~1-5 units each, so budget accordingly). Set up OAuth consent screen (you'll need it eventually if you ever pull live watch-history-adjacent data, though the main history pull will be via Takeout). |
| 7 | Dev environment | Create a virtual environment. Install: `google-api-python-client`, `pandas`, `numpy`, `scikit-learn`, `sentence-transformers`, `youtube-transcript-api`, `sqlalchemy`, `streamlit`. Initialize a GitHub repo now — commit early, commit often, so your contribution graph and commit history tell a real story later. |

**Resources:**
- Mode SQL Tutorial: mode.com/sql-tutorial
- StrataScratch: stratascratch.com
- Kaggle YouTube dataset: search "Trending YouTube Video Statistics"
- YouTube Data API docs: developers.google.com/youtube/v3

**Definition of done:**
- [ ] Can write a query with a JOIN + GROUP BY + window function without looking up syntax
- [ ] Have a working Tableau Public profile with at least one published dashboard
- [ ] Have a valid, tested YouTube API key that successfully returns data for a test video ID
- [ ] GitHub repo initialized with a real (even if sparse) README

---

## Week 2 — Video Similarity Engine: Data Collection & Pipeline

**Rationale:** Good similarity scoring is 80% about having clean, well-structured input data. Rushing this step is the single most common way these projects go sideways later.

| Day | Task | Detail |
|---|---|---|
| 1 | Schema design (do this on paper/Notion first, not in code) | Decide your feature categories: **text** (title, description, tags, transcript), **categorical** (category ID, channel ID, default language), **numeric** (duration in seconds, publish date, view/like/comment counts). Write out exactly what table(s) you need before writing a single query. |
| 2-3 | Build the collection pipeline | Use `search.list` to pull seed videos across 4-6 categories you personally care about (this matters — you'll be manually sanity-checking similarity later, so pick topics you actually understand). Then `videos.list` for full metadata on each (this is where duration, stats, and tags live — `search.list` alone doesn't give you everything). Target 300-500 videos. |
| 4 | Add transcript collection | Use `youtube-transcript-api`. Build a fallback path: if no captions exist, mark the row and proceed without transcript features for that video rather than crashing the pipeline — expect roughly 10-30% of videos to lack usable captions. |
| 5 | Persist to a real database | Use SQLite for local dev (Postgres if you want extra practice matching real job stacks). Design at least 2 normalized tables: `videos` and `channels` (don't flatten channel info into every video row — this is your chance to practice normalization, a common interview topic). |
| 6 | Data quality pass | Check for duplicates, null transcripts, videos with missing stats (some older/unlisted videos return partial data), encoding issues in non-English titles. Write a short data-quality report — this becomes a section in your README later and is a very real data science skill (most real data is dirty). |
| 7 | SQL/Tableau maintenance block | 30-45 min of SQL practice on StrataScratch/LeetCode. Don't let Week 1's momentum die. |

**Definition of done:**
- [ ] A queryable database with 300+ videos, each with text + categorical + numeric fields populated
- [ ] Transcript coverage documented (e.g., "72% of videos had usable transcripts")
- [ ] A written (even 1-paragraph) data quality summary

---

## Week 3 — Feature Engineering & Similarity Scoring

**Rationale:** This is the technical core of Project 1 and the part interviewers will ask the most questions about. Build the simple version first — resist jumping straight to embeddings.

| Day | Task | Detail |
|---|---|---|
| 1 | Baseline text similarity: TF-IDF | Use `sklearn.feature_extraction.text.TfidfVectorizer` on titles + descriptions (concatenated or weighted separately). Compute cosine similarity. This is your baseline — cheap, fast, explainable, and a good thing to say in an interview ("I started with TF-IDF before reaching for embeddings, to have an interpretable baseline"). |
| 2 | Upgrade: sentence embeddings | Use `sentence-transformers` (`all-MiniLM-L6-v2` is small and fast enough to run locally). Embed titles, descriptions, and transcripts separately, then decide how to combine them (concatenation vs. weighted average vs. treating each as a separate similarity signal). |
| 3 | Categorical + numeric features | One-hot encode category ID and channel ID (careful: channel ID as one-hot will get very sparse with 300+ unique channels — consider whether to use it at all, or bucket by subscriber tier if you pull channel stats). Normalize numeric features (duration, view count — probably log-transform view count, it's heavily skewed). |
| 4 | Combine into a single similarity function | Decide on a weighting scheme: e.g., `similarity = 0.5*text_sim + 0.3*category_match + 0.2*numeric_sim`. Try 2-3 different weightings and see which produces results that match your intuition. |
| 5 | Build an evaluation set | Manually label ~20-30 video pairs as "similar" / "somewhat similar" / "not similar" based on your own judgment. This is your ground truth — without it, you're just guessing whether the model works. |
| 6 | Evaluate against your labels | Check: does the similarity score rank your "similar" pairs higher than your "not similar" pairs? Compute something simple like a rank correlation or just eyeball a sorted list. Document where it fails (e.g., "two cooking videos in different languages score low despite being genuinely similar in content"). |
| 7 | Write the technical section of your README | Explain the approach, the weighting decisions, and the failure cases. This kind of honest limitations section is what separates a portfolio project from a toy script in an interviewer's eyes. |

**Definition of done:**
- [ ] A `similarity(video_a_id, video_b_id) -> float` function that runs end to end
- [ ] A hand-labeled evaluation set of 20-30 pairs
- [ ] A documented comparison of at least 2 approaches (TF-IDF vs. embeddings) with reasoning for which you kept

---

## Week 4 — Watch History Analyzer & Dashboard

**Rationale:** This is where the project becomes personal and demoable — a dashboard about your own YouTube habits is something you can actually show people, not just describe.

| Day | Task | Detail |
|---|---|---|
| 1 | Export your watch history | Google Takeout → select YouTube and YouTube Music → History → request export in JSON format (much easier to parse than the HTML export). |
| 2 | Parse the export | Extract video ID (from the URL), watched timestamp, and video title from each entry. Expect several hundred to several thousand entries depending on your history length — this is good practice handling a dataset an order of magnitude bigger than Week 2's. |
| 3 | Enrich with your metadata pipeline | For each watched video, pull it through the same pipeline from Weeks 2-3 (or query it if already in your DB; otherwise hit the API fresh — expect this to eat meaningfully into your daily quota, so batch it and monitor usage). |
| 4 | Build the taste profile | Compute: category distribution (%), channel diversity (unique channels / total watches), average video duration watched, watch frequency by day-of-week/hour, a recency-weighted "current interest" vector (weight recent watches higher than old ones — e.g., exponential decay). |
| 5-6 | Build the Tableau dashboard | At minimum: a category breakdown chart, a watch-frequency-over-time chart, a top-channels chart, and one interactive filter (e.g., filter by date range or category). Publish to Tableau Public — this alone is a shareable, standalone artifact for your resume/LinkedIn. |
| 7 | Write this section's README + reflect | Document any privacy considerations you handled (e.g., not committing your raw personal watch history to a public GitHub repo — use a `.gitignore` and note in the README that this runs on the user's own Takeout export). |

**Important note on privacy/scope:** YouTube's API terms restrict pulling *other users'* watch history without their explicit OAuth consent — this is why the design runs on your own Takeout export rather than trying to scrape or query arbitrary users' histories. If you want the tool to work for other people eventually, the honest path is: they run the script on their own Takeout export locally, or you build an OAuth flow where they explicitly grant your app access to their own account (this is a heavier lift — mention it as "future work" rather than building it now).

**Definition of done:**
- [ ] A working history-to-profile pipeline
- [ ] A published Tableau Public dashboard
- [ ] A brief written note on the privacy/scope decision (interviewers like seeing you thought about this unprompted)

---

## Week 5 — Likelihood Model, App Wrapper, and Ship Project 1

**Rationale:** This is where "similarity" becomes "prediction" — the actual applied ML step, and where Project 1 gets finished and shipped rather than left 90% done (a common trap).

| Day | Task | Detail |
|---|---|---|
| 1 | Frame the ML problem | Label = 1 if watched, 0 if not. Positive examples: your actual watch history. Negative examples: sample videos from your broader collection (Week 2's 300-500) that you *didn't* watch — this needs care, since random negatives will make the problem too easy (obviously-unwatched-because-obviously-different videos). Try to include some "hard negatives" — videos similar to your taste but not actually watched. |
| 2 | Feature set for the model | Combine: similarity-to-taste-profile score (from Week 4's profile), the video's own raw features (category, duration, view count), and maybe recency of similar watches. |
| 3 | Baseline model | Logistic regression via `sklearn`. Do a proper train/test split (or better, time-based split — train on earlier watches, test on later ones, since this mimics the real prediction task and avoids leakage). |
| 4 | Evaluation | Use precision, recall, F1, and ROC-AUC — **not accuracy**, since "not watched" will vastly outnumber "watched" and accuracy will be misleadingly high on a model that just predicts "no" every time. Plot a confusion matrix. |
| 5 | Try one stronger model (optional, time-permitting) | Random forest or gradient boosting (`XGBoost`/`LightGBM`). Compare against the logistic regression baseline — if it's not meaningfully better, that's a legitimate and interview-worthy finding ("the baseline was competitive, so I kept the simpler model for interpretability"). |
| 6 | Build the Streamlit app | Two modes: (1) paste two video URLs → similarity %, (2) upload a Takeout export (or use a pre-loaded demo profile) → ranked list of "videos you're likely to watch" from a candidate pool. Keep the UI simple — function over form. |
| 7 | Finalize README + push everything to GitHub | Structure: Problem → Approach → Data → Methods → Results (with actual numbers/charts) → Limitations → Future work → How to run it. Add a GIF or screenshot of the app in action — READMEs with visuals get read far more than walls of text. |

**Definition of done:**
- [ ] A trained model with documented precision/recall/AUC numbers
- [ ] A working, demoable Streamlit app
- [ ] A polished README with screenshots
- [ ] Project pinned on your GitHub profile

**Also due this week:** Take the Google Data Analytics (or Advanced Data Analytics) cert exam if you haven't finished it yet — you should be close to done by now given Week 1's head start.

---

## Week 6 — Project 2, Part 1: Scope & Build

Choose the direction that best matches the internships you're actually targeting. Both are detailed below — pick one, don't try to do both.

### Option A: End-to-End Data Engineering Pipeline
*Best if you're leaning data engineering or "data analyst with SQL/pipeline emphasis."*

| Day | Task |
|---|---|
| 1 | Pick a data source with a real API or regularly-updating dataset (options: a public weather API, a finance API like Alpha Vantage, or a Kaggle dataset simulating daily updates) |
| 2-3 | Build the extraction layer — pull raw data, handle pagination/rate limits/failures gracefully (retry logic matters here) |
| 3-4 | Build the transform layer — cleaning, deduplication, type casting, handling nulls, joining reference tables |
| 4-5 | Load into a database (Postgres recommended for extra practice beyond SQLite) with a proper schema |
| 5-6 | Add orchestration — even a simple cron job counts, but if you want the resume line, set up a basic **Apache Airflow** DAG running locally |
| 7 | First-pass validation: does a fresh run actually update the database correctly without manual intervention? |

### Option B: A/B Testing & Experimentation Project
*Best if you're leaning classic data analyst/data scientist roles — this one is genuinely underused by other applicants and stands out more than another ML project.*

| Day | Task |
|---|---|
| 1 | Find a dataset (Kaggle has several marketing/product A/B test datasets — search "AB Test," "Cookie Cats," or "Marketing A/B Testing") |
| 2 | Frame the business question properly: what's the hypothesis, what's the success metric, what's the minimum detectable effect you care about |
| 3 | Do a power analysis *before* looking at results (this ordering matters — it shows you understand experimental design, not just p-hacking after the fact) |
| 4-5 | Run the statistical test (t-test, chi-squared, or Mann-Whitney depending on the metric type) and check assumptions (normality, variance, sample size) |
| 6 | Check for common pitfalls: novelty effects, sample ratio mismatch, multiple comparisons if you're testing several metrics |
| 7 | Draft a business-facing recommendation memo — not just "p < 0.05," but "here's what I'd tell a product manager to do and why" |

**Definition of done (either option):**
- [ ] A working end-to-end version 1, even if rough
- [ ] Clear documentation of the design decisions made *before* seeing results (this is what makes it credible)

---

## Week 7 — Project 2, Part 2: Depth, Dashboard, Certification

| Day | Task |
|---|---|
| 1-2 | **Option A:** Add monitoring/logging, handle edge cases from Week 6's rough version, add tests. **Option B:** Add a secondary analysis (segment the effect by user type/platform/cohort — does the effect hold everywhere or only in some segments?) |
| 3-4 | Build the visualization layer in Tableau — for Option A, a dashboard showing pipeline health/data freshness/key metrics over time; for Option B, a dashboard showing the experiment results with confidence intervals clearly displayed |
| 5-6 | Study for the **Tableau Desktop Specialist** exam (it's a proctored, ~1 hour, 30-multiple-choice-question exam covering connecting to data, basic chart types, calculated fields, and dashboard design — review the official exam guide from Tableau's site and do 1-2 practice dashboards outside your project data to build speed) |
| 6 | Take the Tableau Desktop Specialist exam |
| 7 | Write Project 2's README following the same structure as Project 1's |

**Definition of done:**
- [ ] Project 2 complete with a working dashboard
- [ ] Tableau Desktop Specialist certification earned
- [ ] README written

---

## Week 8 — Polish, Portfolio, and Start Applying

| Day | Task | Detail |
|---|---|---|
| 1 | Polish both READMEs | Read them as if you're a stranger seeing the repo for the first time — is it obvious what the project does, why it matters, and how to run it within 30 seconds of landing on the page? |
| 2 | Clean commit history (optional but nice) | Doesn't need to be obsessive, but a repo with one giant "final commit" looks worse than one showing incremental progress |
| 3 | Build/update a simple portfolio page | A single page linking: GitHub repos, both Tableau dashboards, resume PDF, and a short 2-3 sentence blurb per project. A free GitHub Pages site or Notion page is enough — don't over-invest in this relative to the projects themselves |
| 4 | Rewrite resume bullets | Use concrete numbers wherever possible. See templates below. |
| 5 | Update LinkedIn + tailor 2-3 resume versions | One leaning data analyst, one leaning data scientist, one leaning data engineer — same base content, different emphasis and top bullets |
| 6 | Do 1-2 mock interviews | Practice: (a) a SQL whiteboarding-style question, (b) "walk me through a project," (c) "how did you handle [specific tradeoff]" |
| 7 | Start applying | Target 5-10 quality applications this week rather than mass-applying — tailor at least the resume top section to each role type |

### Resume bullet templates (fill in your real numbers)

- "Built an end-to-end video recommendation pipeline in Python, collecting and processing 500+ YouTube videos via the YouTube Data API and engineering text (TF-IDF, sentence embeddings) and metadata features to compute content similarity."
- "Designed and trained a logistic regression model predicting watch likelihood from a personal watch history dataset, achieving [X] ROC-AUC on a time-based holdout split."
- "Built a Tableau Public dashboard visualizing [X hundred/thousand] historical watch events, surfacing category and channel-diversity trends."
- "Ran an A/B test analysis on [dataset], including power analysis and segment-level effect testing, and produced a business recommendation memo."
- "Wrote 50+ SQL queries across window functions, CTEs, and multi-table joins to answer analytical questions on a [X]-row dataset."

**Definition of done:**
- [ ] Two complete, polished, publicly viewable projects
- [ ] Portfolio page live
- [ ] Resume tailored into 2-3 versions
- [ ] At least 5 applications submitted

---

## Running threads across all 8 weeks (don't let these slip)

- **SQL practice:** 20-30 min, minimum 3x/week, every single week — this compounds more than any individual project and is the single most common technical screen for these internships
- **LeetCode (general):** keep your existing habit going, lighter during heavy build weeks (2, 3, 5)
- **Weekly reflection (Sundays, 10 min):** write 3-4 sentences on what worked, what didn't, and what surprised you. This becomes real interview material later ("tell me about a time you had to change your approach")

---

## Certification & tooling summary

| Item | Timing | Format/Cost | Notes |
|---|---|---|---|
| Google Data Analytics (or Advanced Data Analytics) Professional Certificate | Weeks 1-5, background | Coursera subscription (~$49/month, often 7-day free trial); self-paced | Skip/audit modules you already know — don't grind material below your level |
| Tableau Desktop Specialist | Week 7 | ~$100 exam fee, proctored, ~1 hour, 30 MCQs | Review the official exam guide on Tableau's site before scheduling |
| SQL fluency | Ongoing | Free (Mode tutorial, StrataScratch free tier, LeetCode free tier) | No formal cert needed — fluency demonstrated via projects + live screens is what actually gets checked |
| (Optional, later) Azure Data Scientist Associate or AWS Certified Data Analytics | After this 8-week sprint | Paid, proctored | Only worth it once you're specifically interviewing for cloud-heavy data engineering roles — not needed for this sprint |

---

## Appendix: Suggested repo structure (for both projects)

```
project-name/
├── README.md              (problem, approach, results, how to run)
├── requirements.txt
├── data/                  (small sample data only — never commit personal watch history)
│   └── .gitkeep
├── src/
│   ├── collect.py         (data collection/API calls)
│   ├── features.py        (feature engineering)
│   ├── model.py           (training/evaluation)
│   └── app.py             (Streamlit app)
├── notebooks/             (exploratory work — fine to be messier here)
│   └── eda.ipynb
└── .gitignore             (exclude data/, .env, personal exports)
```

Keeping personal watch history data out of the public repo (via `.gitignore`) and mentioning this explicitly in your README is a small detail that signals real engineering judgment to anyone reviewing your code.
