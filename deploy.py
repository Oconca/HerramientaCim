import os, zipfile, time
try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests

USERNAME = "xaviergarzonr"
TOKEN = "0e079104753539fda8a34e762c3f2dd612dd227f"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# Create zip
print("Zipping files...")
with zipfile.ZipFile('oconca.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in root or '.git' in root or 'venv' in root or 'env' in root:
            continue
        for file in files:
            if file in ['oconca.zip', 'deploy.py', 'oconca.db-journal'] or file.endswith('.pyc') or file.startswith('~$'):
                continue
            path = os.path.join(root, file)
            zf.write(path, arcname=os.path.relpath(path, '.'))

print("Uploading zip...")
with open('oconca.zip', 'rb') as f:
    res = requests.post(f"{API_BASE}/files/path/home/{USERNAME}/oconca.zip", headers=HEADERS, files={"content": f})
    print("Upload status:", res.status_code)

print("Setting up webapp...")
requests.delete(f"{API_BASE}/webapps/{USERNAME}.pythonanywhere.com/", headers=HEADERS)

payload = {
    "domain_name": f"{USERNAME}.pythonanywhere.com",
    "python_version": "3.10"
}
res = requests.post(f"{API_BASE}/webapps/", headers=HEADERS, data=payload)
print("Create WebApp status:", res.status_code)

# Set virtualenv
res = requests.patch(f"{API_BASE}/webapps/{USERNAME}.pythonanywhere.com/", headers=HEADERS, json={"virtualenv_path": f"/home/{USERNAME}/oconca/venv"})
print("Set virtualenv status:", res.status_code)

print("Writing WSGI config...")
wsgi_code = f"""
import sys
import os

path = '/home/{USERNAME}/oconca'
if path not in sys.path:
    sys.path.append(path)

# Ensure database runs smoothly in WSGI mode without permission failures
os.chdir(path)

from app import app as fastapi_app
from a2wsgi import ASGIMiddleware

application = ASGIMiddleware(fastapi_app)
"""
res = requests.post(f"{API_BASE}/files/path/var/www/{USERNAME.replace('.','_')}_pythonanywhere_com_wsgi.py", headers=HEADERS, files={"content": ("wsgi.py", wsgi_code)})
print("Write WSGI status:", res.status_code)

print("Creating console to unzip and install...")
res = requests.post(f"{API_BASE}/consoles/", headers=HEADERS, json={"executable": "bash"})
if res.status_code in [200, 201]:
    console_id = res.json()["id"]
    
    def send_command(cmd):
        print(f"Executing: {cmd}")
        requests.post(f"{API_BASE}/consoles/{console_id}/send_input/", headers=HEADERS, json={"input": cmd + "\\n"})
        time.sleep(3.5)

    send_command("rm -rf oconca && mkdir -p oconca")
    send_command("unzip -o oconca.zip -d oconca")
    send_command("cd oconca")
    send_command("python3 -m venv venv")
    send_command("source venv/bin/activate")
    send_command("pip install -r requirements.txt")
    print("Pinging python process to test...")
    send_command(f"curl -s -X POST {API_BASE}/webapps/{USERNAME}.pythonanywhere.com/reload/ -H 'Authorization: Token {TOKEN}'")
    
    print("Console task dispatched. Give the server roughly 2-3 minutes to download your requirements in the background!")
else:
    print("Failed to create console:", res.text)
