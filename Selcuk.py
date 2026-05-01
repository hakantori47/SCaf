import requests
import re
import urllib3
import warnings
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

class M3UGenerator:
    def __init__(self):
        self.m3u_content = "#EXTM3U\n"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8'
        })
    
    def get_html(self, url):
        try:
            response = self.session.get(url, timeout=20, verify=False, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except:
            return None
    
    def find_active_domain(self):
        try:
            with open("last_working_domain.txt", "r") as f:
                last_domain = f.read().strip()
                if self.test_domain(last_domain):
                    return last_domain
        except:
            pass
        
        proxy_services = [
            "https://cors-proxy.fringe.zone/",
            "https://api.allorigins.win/raw?url=",
            "https://cors-anywhere.herokuapp.com/",
            "https://proxy.cors.sh/",
            "https://cors-proxy.htmldriven.com/?url="
        ]
        
        domains_to_test = [
            "selcuksportshd.is",
            "selcuksportshd.xyz", 
            "selcukspor.live",
            "selcuksporhd.live"
        ]
        
        search_sources = [
            "https://www.google.com/search?q=selcuksportshd+canli+mac+izle",
            "https://selcukspor.live/",
            "https://selcuksporhd.net/"
        ]
        
        for source in search_sources:
            html = self.get_html(source)
            if html:
                new_domains = re.findall(r'(?:https?://)?(?:www\.)?(selcuksportshd[a-zA-Z0-9]*\.(?:xyz|is|live|net))', html)
                for domain in new_domains:
                    test_url = f"https://www.{domain}"
                    if self.test_domain(test_url):
                        self.cache_domain(test_url)
                        return test_url
        
        for proxy in proxy_services:
            for domain in domains_to_test:
                try:
                    if "allorigins" in proxy or "cors.sh" in proxy:
                        test_url = f"{proxy}{domain}"
                    else:
                        test_url = f"{proxy}https://{domain}"
                    
                    html = self.get_html(test_url)
                    if html and ('player' in html.lower() or 'm3u8' in html or 'data-url' in html):
                        real_domain = self.extract_real_domain(html, domain)
                        if real_domain:
                            self.cache_domain(real_domain)
                            return real_domain
                except:
                    continue
        
        known_domains = [
            "https://www.selcuksportshdf60ed33068.xyz/",
            "https://www.selcuksportshd.is/",
            "https://www.selcuksportshd.xyz/",
            "https://www.selcuksportshd.live/",
            "https://selcukspor.live/"
        ]
        
        for domain in known_domains:
            if self.test_domain(domain):
                self.cache_domain(domain)
                return domain
        
        return None
    
    def test_domain(self, url):
        try:
            response = self.session.get(url, timeout=10, verify=False, allow_redirects=True)
            if response.status_code == 200:
                content = response.text.lower()
                if 'player' in content or 'm3u8' in content or 'data-url' in content:
                    return True
                if 'selcukspor' in content and ('canli' in content or 'mac' in content):
                    return True
            return False
        except:
            return False
    
    def extract_real_domain(self, html, original_domain):
        patterns = [
            r'https?://(?:www\.)?([a-zA-Z0-9-]+\.(?:xyz|is|live|net|com))/',
            r'data-url="(https?://[^"]+)"',
            r'href="(https?://[^"]*selcuksport[^"]*)"'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if match.startswith('http'):
                    domain = match
                else:
                    domain = f"https://www.{match}"
                
                if 'selcuksport' in domain and domain != original_domain:
                    if self.test_domain(domain):
                        return domain
        return None
    
    def cache_domain(self, domain):
        try:
            with open("last_working_domain.txt", "w") as f:
                f.write(domain)
        except:
            pass
    
    def selcuksports_streams(self):
        active_domain = self.find_active_domain()
        if not active_domain:
            print("HATA: Aktif domain bulunamadi!")
            return False
        
        channel_ids = [
            "selcukbeinsports1", "selcukbeinsports2", "selcukbeinsports3",
            "selcukbeinsports4", "selcukbeinsports5", "selcukbeinsportsmax1",
            "selcukbeinsportsmax2", "selcukssport", "selcukssport2",
            "selcuksmartspor", "selcuksmartspor2", "selcuktivibuspor1",
            "selcuktivibuspor2", "selcuktivibuspor3", "selcuktivibuspor4",
            "sssplus1", "sssplus2", "selcukobs1", 
            "selcuktabiispor1", "selcuktabiispor2", 
            "selcuktabiispor3", "selcuktabiispor4", 
            "selcuktabiispor5"
        ]
        
        html = self.get_html(active_domain)
        if not html:
            print("HATA: Ana sayfa acilamadi!")
            return False
        
        player_links = re.findall(r'(?:data-url|href)=["\'](https?://[^"\']+player[^"\']+\.php[^"\']*)["\']', html)
        
        if not player_links:
            player_links = re.findall(r'(https?://[^"\'\s]+(?:player|embed|video|canli)[^"\'\s]*\.php[^"\'\s]*)', html)
        
        base_stream_url = None
        
        for player_url in player_links[:5]:
            html_player = self.get_html(player_url)
            if html_player:
                patterns = [
                    r'this\.baseStreamUrl\s*=\s*[\'"]([^\'"]+)[\'"]',
                    r'baseStreamUrl:\s*[\'"]([^\'"]+)[\'"]',
                    r'streamUrl\s*=\s*[\'"]([^\'"]+\.m3u8)[\'"]',
                    r'source:\s*[\'"]([^\'"]+\.m3u8)[\'"]',
                    r'(https?://[^\s\'"]+\.m3u8)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, html_player)
                    if match:
                        base_stream_url = match.group(1)
                        if '/playlist.m3u8' in base_stream_url:
                            base_stream_url = base_stream_url.replace('/playlist.m3u8', '')
                        if not base_stream_url.endswith('/'):
                            base_stream_url += '/'
                        break
                
                if base_stream_url:
                    break
        
        if not base_stream_url:
            print("HATA: Stream URL bulunamadi!")
            return False
        
        for cid in channel_ids:
            stream_url = base_stream_url + cid + "/playlist.m3u8"
            clean_name = re.sub(r'^selcuk', '', cid, flags=re.IGNORECASE)
            clean_name = clean_name.upper() + " HD"
            channel_name = "TR:" + clean_name
            
            self.m3u_content += f'#EXTINF:-1 tvg-id="" tvg-name="{channel_name}" tvg-logo="https://i.hizliresim.com/b6xqz10.jpg" group-title="TURKIYE",{channel_name}\n'
            self.m3u_content += f'#EXTVLCOPT:http-referrer={active_domain}\n'
            self.m3u_content += f'{stream_url}\n'
        
        return True
    
    def save_m3u(self, filename="DeaTHLesS-Selcuksport.m3u"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.m3u_content)
            print("DeaTHLesS-Selcuksport.m3u oluşturuldu")
            return True
        except Exception as e:
            print(f"HATA: Dosya kaydedilemedi - {str(e)}")
            return False

def main():
    generator = M3UGenerator()
    success = generator.selcuksports_streams()
    if success:
        generator.save_m3u()
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
