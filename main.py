
import requests
import re
import datetime

# --- AYARLAR ---
OUTPUT_FILE = "Sporcafe.m3u"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

# Senin verdiğin güncel link
START_URL = "https://www.sporcafe-4a2fb1f79d.xyz/"

CHANNELS = [
    {"id": "bein1", "source_id": "sbeinsports-1", "name": "BeIN Sports 1", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/5rhmw31628798883.png", "group": "SPORCAFE"},
    {"id": "bein2", "source_id": "sbeinsports-2", "name": "BeIN Sports 2", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/7uv6x71628799003.png", "group": "SPORCAFE"},
    {"id": "bein3", "source_id": "sbeinsports-3", "name": "BeIN Sports 3", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/u3117i1628798857.png", "group": "SPORCAFE"},
    {"id": "bein4", "source_id": "sbeinsports-4", "name": "BeIN Sports 4", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/2ktmcp1628798841.png", "group": "SPORCAFE"},
    {"id": "bein5", "source_id": "sbeinsports-5", "name": "BeIN Sports 5", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/BeIn_Sports_5_US.png", "group": "SPORCAFE"},
    {"id": "beinmax1", "source_id": "sbeinsportsmax-1", "name": "BeIN Sports Max 1", "logo": "https://assets.bein.com/mena/sites/3/2015/06/beIN_SPORTS_MAX1_DIGITAL_Mono.png", "group": "SPORCAFE"},
    {"id": "beinmax2", "source_id": "sbeinsportsmax-2", "name": "BeIN Sports Max 2", "logo": "http://tvprofil.com/img/kanali-logo/beIN_Sports_MAX_2_TR_logo_v2.png?1734011568", "group": "SPORCAFE"},
    {"id": "tivibu1", "source_id": "stivibuspor-1", "name": "Tivibu Spor 1", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/qadnsi1642604437.png", "group": "SPORCAFE"},
    {"id": "tivibu2", "source_id": "stivibuspor-2", "name": "Tivibu Spor 2", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/kuasdm1642604455.png", "group": "SPORCAFE"},
    {"id": "ssport1", "source_id": "sssport", "name": "S Sport 1", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923239.png", "group": "SPORCAFE"},
    {"id": "ssport2", "source_id": "sssport2", "name": "S Sport 2", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923321.png", "group": "SPORCAFE"},
    {"id": "smart1", "source_id": "ssmartspor", "name": "Smart Spor 1", "logo": "https://dsmart-static-v2.ercdn.net//resize-width/1920/content/p/el/11909/Thumbnail.png", "group": "SPORCAFE"},
    {"id": "aspor", "source_id": "saspor", "name": "A Spor", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/9d28401f-2d4e-4862-85e2-69773f6f45f4.png", "group": "SPORCAFE"},
    {"id": "tr1", "source_id": "strt-1", "name": "TRT 1", "logo": "https://upload.wikimedia.org/wikipedia/commons/0/05/TRT_1_logo_2021.svg", "group": "SPORCAFE"},
]

def get_active_info():
    print(f"[*] Ana site taranıyor: {START_URL}")
    try:
        res = requests.get(START_URL, headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        html = res.text
        
        # Yayın domainini bul (uxsyplayer domaini)
        stream_match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', html)
        stream_domain = f"https://{stream_match.group(1)}" if stream_match else None
        
        return html, START_URL, stream_domain
    except Exception as e:
        print(f"[!] Hata: {e}")
        return None, None, None

def extract_base_url(html):
    match = re.search(r'this\.adsBaseUrl\s*=\s*[\'"]([^\'"]+)', html)
    return match.group(1) if match else None

def fetch_links():
    html, referer, stream_domain = get_active_info()
    if not stream_domain:
        print("[!] Yayın domaini bulunamadı.")
        return []

    print(f"[+] Yayın Domaini: {stream_domain}")
    found_links = []

    for ch in CHANNELS:
        full_url = f"{stream_domain}/index.php?id={ch['source_id']}"
        try:
            r = requests.get(full_url, headers={**HEADERS, "Referer": referer}, timeout=5)
            r.encoding = 'utf-8'
            base = extract_base_url(r.text)
            if base:
                stream_url = f"{base}{ch['source_id']}/playlist.m3u8"
                found_links.append((ch, stream_url))
                print(f" [OK] {ch['name']} bulundu.")
        except:
            continue
    return found_links, referer

def save_m3u(links, referer):
    if not links:
        print("[!] Kaydedilecek yayın bulunamadı.")
        return

    content = "#EXTM3U\n"
    content += f"# Guncelleme: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    for ch, url in links:
        content += f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}\n'
        content += f"#EXTVLCOPT:http-referrer={referer}\n"
        content += f"{url}\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n[SUCCESS] {len(links)} kanal {OUTPUT_FILE} dosyasına kaydedildi.")

if __name__ == "__main__":
    links, referer = fetch_links()
    save_m3u(links, referer)
