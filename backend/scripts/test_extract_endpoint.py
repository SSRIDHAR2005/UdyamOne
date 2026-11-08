import urllib.request
import uuid
import json

specimen_path = 'backend/data/kyc_documents/K02_gst_certificate.png'
with open(specimen_path, 'rb') as f:
    content = f.read()

boundary = uuid.uuid4().hex
parts = [
    f'--{boundary}\r\nContent-Disposition: form-data; name="doc_type"\r\n\r\ngst_certificate\r\n'.encode(),
    f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="K02_gst_certificate.png"\r\nContent-Type: image/png\r\n\r\n'.encode(),
    content,
    f'\r\n--{boundary}--\r\n'.encode()
]
body = b"".join(parts)

req = urllib.request.Request('http://127.0.0.1:8000/api/v1/kyc/extract-document', data=body)
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
resp = json.loads(urllib.request.urlopen(req).read().decode())
print('Status:', resp.get('status'))
print('Document Type:', resp.get('extracted_fields', {}).get('document_type'))
print('Extracted GSTIN:', resp.get('extracted_fields', {}).get('gstin'))
print('Confidence:', resp.get('confidence'))
print('Stages count:', len(resp.get('lifecycle_stages', [])))
for s in resp.get('lifecycle_stages', []):
    print(f' - Stage {s["stage_number"]}: {s["title"]} -> {s["status"]}: {s["detail"]}')

