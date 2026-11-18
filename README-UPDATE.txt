DANON Product Finder - update instructions

1. Replace the root index.html and sync_drive.py files in GitHub.
2. Edit .github/workflows/sync-catalog.yml and replace the pip install line with:
   python -m pip install google-api-python-client google-auth Pillow
3. Commit all changes to main.
4. GitHub Actions > Sync Danon Images > Run workflow.
5. Confirm catalog/manifest.json contains version: 2 and features arrays.
6. Hard-refresh the website on mobile and test with known matches and nonmatches.

Notes:
- This is a fast, conservative pixel-descriptor heuristic, not semantic AI recognition.
- The distance threshold (0.085) is an initial heuristic and must be calibrated.
- The 20-second target is not a guaranteed SLA on every phone/network.
- Public GitHub Pages exposes catalog images and descriptors to the public.
- The existing sync script reads only direct children of DRIVE_FOLDER_ID, not subfolders.
