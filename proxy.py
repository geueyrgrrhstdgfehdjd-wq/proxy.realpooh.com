import sys
import subprocess
import json
from mitmproxy import http

TARGET_HOST = "proxy.realpooh.com"
PROXY_PORT = 2026

def request(flow: http.HTTPFlow) -> None:
    try:
        # ตรวจสอบ Host เป้าหมาย
        if TARGET_HOST in flow.request.pretty_host:
            print(f"[+] Intercepted Packet to: {flow.request.url}")
            
            # ตรวจสอบว่าพาร์ทตรงตามที่ต้องการไหม
            if "api/fire" in flow.request.path or "game/action" in flow.request.path:
                if flow.request.content:
                    content_type = flow.request.headers.get("Content-Type", "")
                    
                    # เช็คว่าเป็น JSON หรือไม่
                    if "application/json" in content_type:
                        try:
                            # ถอดรหัส JSON
                            data = json.loads(flow.request.content.decode('utf-8'))
                            
                            modified = False
                            if isinstance(data, dict):
                                if "damage" in data:
                                    data["damage"] = 999999
                                    modified = True
                                if "is_headshot" in data:
                                    data["is_headshot"] = True
                                    modified = True
                                    
                                # แพ็กข้อมูลกลับถ้ามีการเปลี่ยนแปลง
                                if modified:
                                    flow.request.content = json.dumps(data).encode('utf-8')
                                    print("[!] Packet Modified: Damage set to MAX / Headshot forced!")
                                    
                        except json.JSONDecodeError as jde:
                            print(f"[-] JSON Decode Error: {jde}")
                        except Exception as inner_e:
                            print(f"[-] Inner Processing Error: {inner_e}")
                            
    except Exception as e:
        print(f"[-] Error parsing/modifying request: {e}")

def response(flow: http.HTTPFlow) -> None:
    try:
        if TARGET_HOST in flow.request.pretty_host:
            if flow.response and flow.response.content:
                # จุดจัดการ Response เพิ่มเติมถ้าต้องการ
                pass
    except Exception as e:
        print(f"[-] Error processing response: {e}")

if __name__ == "__main__":
    # เรียกสั่ง mitmdump ผ่าน CLI โดยตรงเพื่อตัดปัญหา Execution Loop
    cmd = [sys.executable, "-m", "mitmproxy.tools.main.mitmdump", "-p", str(PROXY_PORT), "-s", __file__]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[!] Stopped Proxy Server.")
