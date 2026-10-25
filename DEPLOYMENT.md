# Streamlit Community Cloud deployment

The application is self-contained and reads its tracked workbook and generated reports from repository-relative paths. No `/workspace` paths, external database, API keys, or font service are needed at runtime. Python packages are pinned in `requirements.txt`.

1. Sign in at https://share.streamlit.io/ using the GitHub account with access to `fastgenesys/Analysis_sheet`.
2. Choose **Create app** / **Deploy an app** and select:
   - Repository: `fastgenesys/Analysis_sheet`
   - Branch: `main`
   - Main file path: `app.py`
   - Python version in advanced settings: **3.12**
3. Connect/authorize the repository if Streamlit asks. Deploy.
4. Restrict app visibility to authorized viewers in Community Cloud sharing/security settings. The source workbook, full-data downloads, mentor names, and free-text answers are sensitive; do not enable public access without reviewing them. Keep the GitHub repository private if that material must remain private. This document does not assert the current repository visibility.
5. Use the actual `.streamlit.app` URL shown by Streamlit after deployment. No hosted URL exists until deployment succeeds.

## Readiness checks after deployment

- Default page shows 560 responses and 36 campuses.
- Select Lahore: 81 responses.
- Verify the Urdu Nastaleeq text, charts, and Excel download.
- Clear the filters and confirm that 560 responses return.
- Confirm an unauthorized/incognito session cannot access the app if private access is required.

No Streamlit or GitHub passwords/tokens should be entered into chat. Community Cloud's sign-in and repository authorization occur on its website. Updating the connected branch triggers a new deployment. Existing charts and workbook are tracked, so no build-time analysis command is required.
