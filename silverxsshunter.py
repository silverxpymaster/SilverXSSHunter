import os
import time
import logging
import random
import urllib3
import argparse
import requests
import re
from base64 import b64encode, b64decode
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from urllib.parse import urlsplit, parse_qs, urlencode, urlunsplit
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from threading import Lock
from colorama import Fore
from termcolor import colored

print(colored(r"""
  ___ _ _           __  _____ ___ _  _          _           
 / __(_) |_ _____ _ \ \/ / __/ __| || |_  _ _ _| |_ ___ _ _ 
 \__ \ | \ V / -_) '_>  <\__ \__ \ __ | || | ' \  _/ -_) '_|
 |___/_|_|\_/\___|_|/_/\_\___/___/_||_|\_,_|_||_\__\___|_|  

                  Author: SilverX   TG: t.me/silverxvip

""","yellow"))

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger('WDM').setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

driver_pool = Queue()
driver_lock = Lock()

def silverdetect_waf(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5, verify=False)
        wafler = {
            "Cloudflare": "cloudflare",
            "Akamai": "akamai",
            "Sucuri": "sucuri",
            "Imperva": "imperva|incapsula",
            "F5 Big-IP": "big-ip|f5",
            "AWS WAF": "aws|amazon",
            "Barracuda": "barracuda",
            "Citrix": "citrix|netscaler",
            "DenyAll": "denyall",
            "Fortinet": "fortigate|fortinet",
            "Palo Alto": "paloalto|panw",
            "Radware": "radware",
            "Edgecast": "edgecast",
            "ChinaCache": "chinacache",
            "DDoS-Guard": "ddos-guard",
            "StackPath": "stackpath",
            "HyperFilter": "hyperfilter",
            "ArvanCloud": "arvancloud",
            "Safe3": "safe3",
            "Beluga CDN": "belugacdn",
            "Yundun": "yundun",
            "Yunsuo": "yunsuo",
            "BaShield": "bashield",
            "Bluedon": "bluedon"
        }
        
        for waf, pattern in wafler.items():
            if re.search(pattern, response.headers.get("Server", ""), re.I) or re.search(pattern, response.text, re.I):
                print(Fore.CYAN + f"[i] WAF aşkar edildi: {waf}")
                return waf
        
        print(Fore.CYAN + "[i] WAF tapılmadi")
        return None
    except requests.exceptions.RequestException:
        print(Fore.RED + "[!] Sayta qoşulmaq mümkün olmadi")
        return None

def base64(string, encode=False):
    if encode:
        return b64encode(string.encode('utf-8')).decode('utf-8')
    else:
        return b64decode(string.encode('utf-8')).decode('utf-8') if re.match(r'^[A-Za-z0-9+\/=]+$', string) and (len(string) % 4) == 0 else string

def yukle_user_agents(useragent_fayl):
    try:
        with open(useragent_fayl, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(Fore.RED + f"[!] User-Agentləri yükləmə xətasi: {e}")
        os._exit(0)

def yukle_payloadlar(payload_fayl):
    try:
        with open(payload_fayl, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(Fore.RED + f"[!] Payloadları yükləmə xətasi: {e}")
        os._exit(0)

def yarada_payload_url(url, payload):
    url_kombinasiyalari = []
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    
    if not scheme:
        scheme = 'http'
    
    query_params = parse_qs(query_string, keep_blank_values=True)

    if query_string:
        split_url = query_string.split("=", 1)
        if len(split_url) > 1:
            key = split_url[0]
            modified_params = query_params.copy()
            modified_params[key] = [payload]
            modified_query_string = urlencode(modified_params, doseq=True)
            modified_url = urlunsplit((scheme, netloc, path, modified_query_string, fragment))
            url_kombinasiyalari.append(modified_url)
    
    return url_kombinasiyalari

def yarat_driver(user_agents, proxy):
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--disable-gpu")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")

    user_agent = random.choice(user_agents)
    firefox_options.set_preference("general.useragent.override", user_agent)

    if proxy:
        firefox_options.set_preference("network.proxy.type", 1)
        firefox_options.set_preference("network.proxy.http", proxy.split(":")[0])
        firefox_options.set_preference("network.proxy.http_port", int(proxy.split(":")[1]))
        firefox_options.set_preference("network.proxy.ssl", proxy.split(":")[0])
        firefox_options.set_preference("network.proxy.ssl_port", int(proxy.split(":")[1]))

    logging.disable(logging.CRITICAL)
    
    service = Service("/usr/local/bin/geckodriver")
    return webdriver.Firefox(service=service, options=firefox_options)

def elde_et_driver(user_agents):
    try:
        return driver_pool.get_nowait()
    except:
        with driver_lock:
            return yarat_driver(user_agents)

def qaytar_driver(driver):
    driver_pool.put(driver)

def yoxla_zaiflik(url, payload, zaif_url, gozleme, payload_sayisi, user_agents, proxy, post_data=None):
    driver = yarat_driver(user_agents, proxy)
    proxies = {"http": proxy, "https": proxy} if proxy else None

    try:
        if post_data:
            modified_data = {k: payload for k in post_data.keys()}
            response = requests.post(url, data=modified_data, headers={"User-Agent": random.choice(user_agents)}, verify=False, proxies=proxies)
            if payload in response.text:
                print(Fore.GREEN + f"[+] XSS tapıldı: {url} - Data: {modified_data}")
                zaif_url.append(url)
        else:
            payload_url = yarada_payload_url(url, payload)
            if not payload_url:
                return
            for pu in payload_url:
                try:
                    driver.get(pu)
                    try:
                        alert = WebDriverWait(driver, gozleme).until(EC.alert_is_present())
                        alert_text = alert.text
                        if alert_text:
                            print(Fore.GREEN + f"Zeif Url Tapildi: {pu} - Alert Mətni: {alert_text}")
                            zaif_url.append(pu)
                            alert.accept()
                    except TimeoutException:
                        pass
                except UnexpectedAlertPresentException:
                    pass
    finally:
        driver.quit()
    
    payload_sayisi[0] += 1
    print(Fore.YELLOW + f"[i] {payload_sayisi[0]} payload yoxlanildi.", end="\r")

def yukle_user_agents(useragent_fayl=None):
    default_user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
    ]
    
    if useragent_fayl:
        try:
            with open(useragent_fayl, "r") as file:
                return [line.strip() for line in file if line.strip()]
        except Exception as e:
            print(Fore.RED + f"[!] User-Agentleri yükleme xetasi: {e}")
            return default_user_agents
    else:
        return default_user_agents


def icra_et_yoxlama(urls, payload_fayl, gozleme, cixti_fayl, useragent_fayl, post_data=None):
    payloadlar = yukle_payloadlar(payload_fayl)
    zaif_url = []
    payload_sayisi = [0]

    user_agents = yukle_user_agents(useragent_fayl)

    for _ in range(3):
        driver_pool.put(yarat_driver(user_agents))
    
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            for url in urls:
                for payload in payloadlar:
                    futures.append(executor.submit(yoxla_zaiflik, url, payload, zaif_url, gozleme, payload_sayisi, user_agents, post_data))
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(Fore.RED + f"[!] Yoxlama zamani xeta: {e}")
    finally:
        while not driver_pool.empty():
            driver = driver_pool.get()
            driver.quit()

        if cixti_fayl:
            with open(cixti_fayl, "w") as f:
                for v_url in zaif_url:
                    f.write(v_url + "\n")

        print(Fore.YELLOW + f"\n[i] {payload_sayisi[0]} payload yoxlanildi")
        return zaif_url

def esas():
    parser = argparse.ArgumentParser(description="SilverXSSHunter - Avtomatik XSS Skanner")
    parser.add_argument("-u", "--url", help="Skan üçün hədəf URL")
    parser.add_argument("-t", "--targets", help="Birdən çox hədəf ucun icinde url-ler olan txt fayl yolu daxil edin")
    parser.add_argument("-p", "--payload", required=True, help="Payload faylının yolu")
    parser.add_argument("--wait", type=float, default=0.5, help="Alert gözləmə vaxtı (standart: 0.5s)")
    parser.add_argument("-a", "--useragent", help="User-Agent-ləri goturecek fayl yolu")
    parser.add_argument("--data", help="POST istəkləri üçün göndəriləcək məlumat (məsələn: 'username=silver&password=silver')")
    parser.add_argument("--proxy", help="İstifadə ediləcək proxy server (məsələn: 127.0.0.1:8080)")
    parser.add_argument("--encode", action="store_true", help="Payloadları base64 ilə kodla")    
    parser.add_argument("-o", "--output", help="Neticeni saxlamaq ucun cixis fayli (.txt formatinda)")
    args = parser.parse_args()

    urls = []
    if args.url:
        urls.append(args.url)
    if args.targets:
        try:
            with open(args.targets, "r") as file:
                urls.extend([line.strip() for line in file if line.strip()])
        except Exception as e:
            print(Fore.RED + f"[!] Hədəflər faylını oxuma xətası: {e}")
            os._exit(0)

    for url in urls:
        waf_name = silverdetect_waf(url)
        if waf_name:
            print(Fore.YELLOW + f"[!] {url} - {waf_name} WAF aktivdir.")
        else:
            print(Fore.BLUE + f"[+] {url} - WAF yoxdur və skan üçün uyğun ola bilər.")

    print(Fore.YELLOW + "\n[i] Skan başlanir...\n")

    user_agents = yukle_user_agents(args.useragent)
    
    zaif_url = []
    payload_sayisi = [0]

    payloadlar = yukle_payloadlar(args.payload)
    
    if args.encode:
        payloadlar = [base64(payload, encode=True) for payload in payloadlar]
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        for url in urls:
            for payload in payloadlar:
                futures.append(executor.submit(yoxla_zaiflik, url, payload, zaif_url, args.wait, payload_sayisi, user_agents, args.proxy))
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(Fore.RED + f"[!] Yoxlama zamanı xəta: {e}")

    if args.output:
        with open(args.output, "w") as f:
            for v_url in zaif_url:
                f.write(v_url + "\n")

    print(Fore.YELLOW + f"\n[i] Skan bitdi. {len(zaif_url)} zəiflik tapıldı.")

if __name__ == "__main__":
    try:
        esas()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Skan istifadəçi tərəfindən dayandirildi")
    except Exception as e:
        print(Fore.RED + f"[!] Proqramda xəta baş verdi: {e}")
    finally:
        print(Fore.YELLOW + "[i] Proqram bağlanir")
