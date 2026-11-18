# DANON Product Finder

Static, Hebrew, mobile-friendly product lookup. Staff only see one photo button and up to five candidate SKUs. Results are **visual candidates, not verified identification**.

## Publish
Upload the **contents** of this directory to the root of your public GitHub repository. Keep GitHub Pages set to `main` / `(root)`.

## Daily sync setup
1. Create a Google Cloud project, enable Google Drive API, and create a service account with a JSON key. Do not commit the key to GitHub.
2. Share the **Danon Images** Google Drive folder with the service account email as **Viewer**.
3. In GitHub repository Settings > Secrets and variables > Actions > New repository secret, add:
   - `GOOGLE_SERVICE_ACCOUNT_JSON`: full contents of the JSON key file.
   - `DRIVE_FOLDER_ID`: `1_GDcbzpphhFi91QqHSZ6Eetz1_2dsmx4`
4. In Actions > Sync Danon Images > Run workflow, run the first sync. Afterwards it is scheduled daily at 03:15 UTC (05:15 Israel standard time, 06:15 daylight saving time). GitHub schedules may run late or be skipped; monitor workflow status.
5. Confirm `catalog/manifest.json` contains entries and the site displays the count.

## Security and limits
The repository and downloaded catalog images are **public**. Never upload private inventory, credentials, or restricted product images. GitHub Pages has limits and is not an SLA. A service-account setup may be restricted by Google Workspace policy. Large image catalogs may cause slow first searches and significant mobile data use. This version uses simple image pixel similarity, **not semantic AI**; photo-angle/background changes can make it inaccurate. Validate against actual branch photos before operational use. For production-grade matching, replace the image feature extractor with a tested vision embedding model and precompute catalog embeddings in the sync workflow.
