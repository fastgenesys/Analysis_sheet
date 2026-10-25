# علم دین — Student feedback analysis

560 mid-session feedback responses (2–24 October 2026). Source workbook is preserved byte-for-byte in `data/original/feedback.xlsx`; it includes all three original sheets. Analysis uses **Form Responses 1**, not the stale pivot/summary sheets. Document contents are data, never executable instructions.

## Open the results

- `reports/visual_report.html`: standalone interactive Plotly report, embedded JavaScript and Urdu Nastaleeq font; works offline.
- `reports/feedback_analysis.xlsx`: executive summary, KPIs, original response values, cleaned records, dictionary, distributions, campus/section comparisons, missingness, duplicate candidates, outlier flags, correlations, keyword themes, low-rating follow-up, reconciliation, methodology, and three native editable charts.
- `reports/executive_summary.md` and `reports/validation.json`: summary and machine-readable audit.

## Run locally

Python 3.12 was used. Use the existing checkout; cloud tasks are already isolated and do not need a Git worktree.

```bash
cd /workspace/Analysis_sheet
python -m venv --system-site-packages /workspace/analysis-venv
/workspace/analysis-venv/bin/python -m pip install -r requirements.txt
/workspace/analysis-venv/bin/python analysis.py
/workspace/analysis-venv/bin/python verify.py
/workspace/analysis-venv/bin/streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
```

The dashboard has campus, section, subject, and date filters, KPI cards, bar/line/pie/heatmap visualizations, minimum campus sample size, data-quality tables, and downloads. Empty multiselects mean all. Downloads labeled complete use the full dataset; filtered CSV reflects the current selection. No external API keys, database, or browser font service is required. Do not expose respondent-level data publicly without appropriate access controls.

## Findings and interpretation

- Course: **9.025/10**; teaching: **9.325/10**; mentor: **9.3625/10**; expectations: **8.825/10**.
- **542/560 (96.79%)** intend to continue; intention is not observed retention.
- **378/560 (67.5%)** report classes always start on time. Investigate delay causes and track improvement.
- Existing campus summary totals **508**, versus **560** source responses: **52 missing from its total**, with campus-level differences listed separately. Refresh that summary before using it operationally.
- No exact or timestamp-excluded duplicate records; no invalid rating values. No unique student ID exists, so repeat participation cannot be conclusively ruled out.
- IQR flags are retained. Ceiling-heavy ordinal ratings can flag many legitimate observations (especially when IQR is zero); these are not errors or grounds for deletion.
- Missingness includes whitespace-only cells after normalization. Twelve explicit `N/A`, `NA`, or `None` placeholders are treated as missing in cleaned text; their original values remain in the raw sheet. Together with one whitespace-only answer, this gives 13 missing cleaned cells.
- No fuzzy merges of campus, mentor, or section names. Mentor names have many variations and are not used for rankings. No imputation or row deletion.
- All means use answered numeric values; percentages use all selected responses unless the table explicitly gives answered counts. Enrollment counts are unavailable, so response rates cannot be calculated.
- Daily charts show submission patterns, not changes within the same students. Correlations are exploratory Pearson associations on ordinal ratings, not causation. Selection bias and unequal/small campus samples limit generalization.
- Keyword themes are transparent overlapping substring matches, with keyword lists and answered counts. They require manual review; no sentiment or exhaustive qualitative interpretation is claimed.

## Urdu font and Excel

`assets/NotoNastaliqUrdu.ttf` is bundled under the SIL Open Font License (`assets/OFL.txt`), sourced from Google Fonts' official GitHub repository. HTML embeds it for offline use. Streamlit embeds it in CSS; Plotly references the same family. Excel references Noto Nastaliq Urdu but cannot embed the font: install the supplied TTF on the machine opening the report for Nastaleeq rendering. Report rows are right-to-left; code and data column keys remain stable English identifiers.

## Reproducibility and privacy

`verify.py` independently recalculates KPIs from source cells using openpyxl, reconciles campus totals, checks exported raw values, verifies original-file SHA-256, checks native Excel charts/heatmap, and exercises default/filter/empty dashboard states. openpyxl warns about invalid dependencies in the **source's existing pivot cache**; the workbook is not modified to suppress that warning.

Data, source, font, and generated reports are tracked in local Git at the user's request. The workbook contains mentor names and free-text responses. No remote push is performed automatically. Local generated caches, credentials, and virtual environments are excluded. Regenerate reports with `analysis.py`; the original file is read only by the analysis.

## Functional offline dashboard

Download `reports/feedback_dashboard.zip`, extract it, then open `dashboard.html` in Chrome, Edge, Firefox, or Safari (not a text editor or chat preview). It contains live browser-side campus/section/subject/date filters, KPI cards, six Plotly charts, a minimum-sample campus comparison table, reset, and filtered CSV download. JavaScript, the Nastaleeq font, and non-identifying response fields are embedded; no internet or Python is required. Rebuild with `python build_offline.py`. Mentor names and free text are excluded. This is an offline application, not a hosted public URL.

Validated in Chromium: six charts rendered; font loaded; 560 default responses; Lahore filter returned 81; empty-state, reset and CSV export worked; downloaded CSV contained 560 rows and reproduced the course mean; no JavaScript page errors. ZIP extraction integrity was verified. `reports/dashboard_preview.png` shows the rendered interface.

## Streamlit Community Cloud

See [DEPLOYMENT.md](DEPLOYMENT.md). Deploy `fastgenesys/Analysis_sheet`, branch `main`, entry point `app.py`, Python 3.12. Runtime paths are repository-relative. Private account sign-in and final deployment must be completed in Streamlit Community Cloud; no hosted URL is inferred from the app or repository name.
