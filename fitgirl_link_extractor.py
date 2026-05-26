import os, re, requests
from bs4 import BeautifulSoup
from datetime import datetime
from colorama import Fore, Style

class console:
    def __init__(self) -> None:
        self.colors = {"green": Fore.GREEN, "red": Fore.RED, "yellow": Fore.YELLOW, "blue": Fore.BLUE, "magenta": Fore.MAGENTA, "cyan": Fore.CYAN, "white": Fore.WHITE, "black": Fore.BLACK, "reset": Style.RESET_ALL, "lightblack": Fore.LIGHTBLACK_EX, "lightred": Fore.LIGHTRED_EX, "lightgreen": Fore.LIGHTGREEN_EX, "lightyellow": Fore.LIGHTYELLOW_EX, "lightblue": Fore.LIGHTBLUE_EX, "lightmagenta": Fore.LIGHTMAGENTA_EX, "lightcyan": Fore.LIGHTCYAN_EX, "lightwhite": Fore.LIGHTWHITE_EX}

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def timestamp(self):
        return datetime.now().strftime("%H:%M:%S")
    
    def success(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightgreen']}SUCC {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightgreen']}{obj}{self.colors['white']} {self.colors['reset']}")

    def error(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightred']}ERRR {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightred']}{obj}{self.colors['white']} {self.colors['reset']}")

    def done(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightmagenta']}DONE {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightmagenta']}{obj}{self.colors['white']} {self.colors['reset']}")

    def warning(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightyellow']}WARN {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightyellow']}{obj}{self.colors['white']} {self.colors['reset']}")

    def info(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightblue']}INFO {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightblue']}{obj}{self.colors['white']} {self.colors['reset']}")

    def custom(self, message, obj, color):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors[color.upper()]}{color.upper()} {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors[color.upper()]}{obj}{self.colors['white']} {self.colors['reset']}")

    def input(self, message):
        return input(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightcyan']}INPUT   {self.colors['lightblack']}• {self.colors['white']}{message}{self.colors['reset']}")

log = console()
log.clear()

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.5',
    'referer': 'https://fitgirl-repacks.site/',
    'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

def save_to_output(download_url, output_file='output.txt'):
    with open(output_file, 'a') as file:
        file.write(download_url + '\n')

# --- STEP 1: Get Game Link and Scrape for Base URLs ---
url = log.input("Enter Fitgirl Game Link : ")
try:
    r = requests.get(url, headers=headers)
    r.raise_for_status()
except requests.exceptions.RequestException as e:
    log.error("HTTP request failed", f"{url} ({e})")
    raise SystemExit(1)

soup = BeautifulSoup(r.text, "html.parser")

links = [
    a["href"]
    for dlinks_div in soup.find_all("div", class_="dlinks")
    for a in dlinks_div.find_all("a", href=True)
    if a["href"].startswith("https://fuckingfast.co/")
]

if not links:
    log.error("No Matching URLs Found", "Retry..")
    raise SystemExit(1)
else:
    log.info("Matching URLs Found", len(links))

# --- STEP 2: Process Each Link for Direct Downloads ---
for link in links:
    log.info(f"Started Processing", f"{link[:30]}...{link[-15:]}" if len(link) > 45 else link)
    
    try:
        response = requests.get(link, headers=headers)
        
        if response.status_code != 200:
            log.error(f"Failed To Fetch Page", response.status_code)
            continue

        fsoup = BeautifulSoup(response.text, 'html.parser')
        script_tags = fsoup.find_all('script')
        download_function = None
        
        for script in script_tags:
            if script.text and 'function download' in script.text:
                download_function = script.text
                break

        if download_function:
            match = re.search(r'window\.open\(["\'](https?://[^\s"\'\)]+)', download_function)
            if match:
                download_url = match.group(1)
                log.info(f"Found Download Url", f"{download_url[:50]}...")
                
                try:
                    save_to_output(download_url)
                    log.success("Successfully saved to output.txt", "")
                except Exception as e:
                    log.error(f"Failed To Save Link", str(e))
            else:
                log.error("No Download Url Found", "Regex failed to match")
        else:
            log.error("Download Function Not Found", "Check script logic")

    except requests.exceptions.RequestException as e:
        log.error("Network Error Fetching Link", str(e))

log.done("All links processed.", "Check output.txt")