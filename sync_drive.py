"""Download a public-site catalog from a private Drive folder using service-account credentials."""
import datetime, json, os, pathlib, re
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

ROOT=pathlib.Path(__file__).parent
CAT=ROOT/'catalog'
IMAGES=CAT/'images'
FOLDER_ID=os.environ['DRIVE_FOLDER_ID']
creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/drive.readonly'])
api=build('drive','v3',credentials=creds,cache_discovery=False)
IMAGES.mkdir(parents=True,exist_ok=True)
entries=[]
page=None
while True:
    response=api.files().list(q=f"'{FOLDER_ID}' in parents and trashed = false",fields='nextPageToken,files(id,name,mimeType,size)',pageSize=1000,pageToken=page).execute()
    for f in response.get('files',[]):
        if f.get('mimeType') not in ('image/jpeg','image/png','image/webp'):continue
        filename=f['name']
        sku=pathlib.Path(filename).stem
        if not re.fullmatch(r'[A-Za-z0-9_-]{3,80}',sku):continue
        ext=pathlib.Path(filename).suffix.lower()
        target=IMAGES/(f['id']+ext)
        if not target.exists():
            stream=io.BytesIO()
            request=api.files().get_media(fileId=f['id'])
            downloader=MediaIoBaseDownload(stream,request)
            done=False
            while not done: _,done=downloader.next_chunk()
            target.write_bytes(stream.getvalue())
        entries.append({'sku':sku,'path':'catalog/images/'+target.name})
    page=response.get('nextPageToken')
    if not page:break
keep={x['path'].split('/')[-1] for x in entries}
for p in IMAGES.iterdir():
    if p.is_file() and p.name not in keep:p.unlink()
entries.sort(key=lambda x:x['sku'])
(CAT/'manifest.json').write_text(json.dumps({'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),'images':entries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Synced {len(entries)} images')
