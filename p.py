import requests
import json
import time
import random
import os
from datetime import datetime
import sys
from colorama import Fore, Style, init
from typing import List, Dict

# Initialize colorama
init()

# Header yang digunakan untuk semua requests
HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://palapaminiapp.bittime.com',
    'referer': 'https://palapaminiapp.bittime.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}

# Data misi yang tersedia
MISSION_DATA = {
    "available_task": [
        {"key": "isFollowX", "type": 2},
        {"key": "isJoinCommunity", "type": 3},
        {"key": "isFollowIgPalapa", "type": 6},
        {"key": "isFollowIgBittime", "type": 7},
        {"key": "isFollowXBittime", "type": 4},
        {"key": "isJoinCommunityBittime", "type": 5},
        {"key": "isFollowCatidChannel", "type": 10},
        {"key": "isPlayCatid", "type": 11},
        {"key": "isFollowPlpaChannel", "type": 12}
    ]
}

COMPLETED_MISSIONS_FILE = 'completed_missions.json'

def print_banner():
    print(Fore.WHITE + r"""
_  _ _   _ ____ ____ _    ____ _ ____ ___  ____ ____ ___ 
|\ |  \_/  |__| |__/ |    |__| | |__/ |  \ |__/ |  | |__]
| \|   |   |  | |  \ |    |  | | |  \ |__/ |  \ |__| |         
    """)
    print(Fore.GREEN + Style.BRIGHT + "Nyari Airdrop PLPA TapTap Hero")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/nyariairdrop\n")

def load_accounts() -> List[str]:
    try:
        with open('data.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(Fore.RED + "Error: File data.txt tidak ditemukan!")
        sys.exit(1)

def load_completed_missions():
    """Muat data misi yang sudah selesai dari file JSON."""
    if not os.path.exists(COMPLETED_MISSIONS_FILE):
        return {}
    with open(COMPLETED_MISSIONS_FILE, 'r') as file:
        return json.load(file)

def save_completed_missions(completed_missions):
    """Simpan data misi yang sudah selesai ke file JSON."""
    with open(COMPLETED_MISSIONS_FILE, 'w') as file:
        json.dump(completed_missions, file, indent=4)

def mark_mission_completed(username, mission_key):
    """Tandai misi sudah selesai untuk pengguna tertentu."""
    completed_missions = load_completed_missions()
    if username not in completed_missions:
        completed_missions[username] = []
    if mission_key not in completed_missions[username]:
        completed_missions[username].append(mission_key)
    save_completed_missions(completed_missions)

def is_mission_completed(username, mission_key):
    """Periksa apakah misi sudah selesai untuk pengguna tertentu."""
    completed_missions = load_completed_missions()
    return mission_key in completed_missions.get(username, [])

def login(init_data: str) -> Dict:
    try:
        url = "https://b.bittime.com/exchange-web-gateway/tg-mini-app/login"
        payload = {
            "initData": init_data,
            "username": init_data.split('username%22%3A%22')[1].split('%22')[0],
            "lang": "en"
        }
        
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(Fore.RED + f"Kesalahan saat login: {str(e)}")
        return None


def print_login_info(data: Dict, username: str):
    print(Fore.CYAN + "=" * 50)
    print(Fore.GREEN + f"👤 Pengguna: {username}")
    print(Fore.YELLOW + f"💰 Koin: {data['coin']}")
    print(Fore.BLUE + f"⚡️ Energi: {data['energy']}/{data['maxEnergy']}")
    print(Fore.MAGENTA + f"📈 Level: {data['level']}")
    
    # Status indikator dengan emoji dan warna
    status_info = []
    if data['isSignIn']:
        status_info.append(Fore.GREEN + "✅ Sudah Masuk")
    if data['isTurbo']:
        status_info.append(Fore.YELLOW + "🚀 Mode Turbo Aktif")
    if data['isFullEnergy']:
        status_info.append(Fore.BLUE + "⚡️ Energi Penuh")
    if data['isReachTodayLimit']:
        status_info.append(Fore.RED + "🚫 Batas Harian Tercapai")
        
    if status_info:
        print(Fore.WHITE + "Status: " + " | ".join(status_info))
    print(Fore.CYAN + "=" * 50)

def tap_tap(init_data: str, uid: int, energy: int) -> None:
    url = "https://b.bittime.com/exchange-web-gateway/tg-mini-app/shake"
    
    taps_needed = energy // 12  # Menghitung berapa kali tap yang dibutuhkan
    
    for i in range(taps_needed):
        if energy <= 0:  # Stop if energy is 0 or less
            print(Fore.YELLOW + "⚠️ Energi habis, menghentikan ketukan.")
            break
        
        try:
            shake_num = random.randint(69, 100)
            coin = shake_num  # Coin sama dengan shake_num
            
            payload = {
                "initData": init_data,
                "uid": uid,
                "shakeNum": shake_num,
                "coin": coin
            }
            
            response = requests.post(url, headers=HEADERS, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Update the energy with the latest data after each request
            energy = data['data'].get('energy', 0)
            
            print(Fore.GREEN + f"Ketukan ke-{i+1}: "
                  f"⚡️ Energi: {energy}, "
                  f"💰 Koin: {data['data']['coin']}")
            
            time.sleep(0.5)  # Delay kecil antara tap
            
        except Exception as e:
            print(Fore.RED + f"Kesalahan saat melakukan ketukan: {str(e)}")
            continue

def get_daily_rewards(init_data: str, uid: int) -> Dict:
    """
    Mendapatkan data hadiah harian.
    """
    url = (
        "https://b.bittime.com/exchange-web-gateway/tg-mini-app/sign-in-page"
        "?appName=Netscape&appCodeName=Mozilla&appVersion=5.0+(Windows+NT+10.0%3B+Win64%3B+x64)"
        "+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F130.0.0.0+Safari%2F537.36+Edg%2F130.0.0.0"
    )

    params = {
        "initData": init_data,
        "uid": uid
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        if data["code"] == "200":
            print(Fore.GREEN + "🎁 Data hadiah harian berhasil diambil.")
            return data["data"]
        else:
            print(Fore.RED + f"❌ Gagal mendapatkan data hadiah harian: {data['message']}")
            return None

    except Exception as e:
        print(Fore.RED + f"Kesalahan saat mengambil data hadiah harian: {str(e)}")
        return None


def claim_daily_reward(init_data: str, uid: int) -> None:
    """
    Mengambil hadiah harian dengan tipe reward_type yang selalu disetel ke 1.
    """
    url = (
        "https://b.bittime.com/exchange-web-gateway/tg-mini-app/sign-in"
        "?appName=Netscape&appCodeName=Mozilla&appVersion=5.0+(Windows+NT+10.0%3B+Win64%3B+x64)"
        "+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F130.0.0.0+Safari%2F537.36+Edg%2F130.0.0.0"
    )

    # Set reward_type to 1 for all claims
    payload = {
        "initData": init_data,
        "uid": uid,
        "type": "1"
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()


        if data["code"] == "200":
            print(Fore.GREEN + "🎉 Hadiah harian berhasil diambil.")
        else:
            print(Fore.RED + f"❌ Gagal mengambil hadiah harian: {data['message']}")

    except Exception as e:
        print(Fore.RED + f"Kesalahan saat mengambil hadiah harian: {str(e)}")

def execute_mission(init_data: str, uid: int, mission_key: str, mission_type: int) -> bool:
    """Eksekusi misi tertentu dan kembalikan status keberhasilan."""
    url = "https://b.bittime.com/exchange-web-gateway/tg-mini-app/sign-in"
    payload = {
        "initData": init_data,
        "uid": uid,
        "type": str(mission_type)
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == "200":
            print(Fore.GREEN + f"✅ Misi '{mission_key}' berhasil diselesaikan.")
            return True
        else:
            print(Fore.RED + f"❌ Misi '{mission_key}' gagal: {data.get('message')}")
            return False
    except Exception as e:
        print(Fore.RED + f"Kesalahan saat eksekusi misi '{mission_key}': {str(e)}")
        return False

def complete_all_missions(init_data: str, uid: int):
    """Selesaikan semua misi untuk pengguna, melewati misi yang sudah selesai."""
    username = init_data.split('username%22%3A%22')[1].split('%22')[0]
    
    for mission in MISSION_DATA["available_task"]:
        mission_key = mission["key"]
        mission_type = mission["type"]
        
        if is_mission_completed(username, mission_key):
            print(Fore.YELLOW + f"⚠️ Misi '{mission_key}' sudah selesai untuk {username}. Melewati.")
            continue
        
        # Eksekusi misi dan tandai sebagai selesai jika berhasil
        success = execute_mission(init_data, uid, mission_key, mission_type)
        if success:
            mark_mission_completed(username, mission_key)
        time.sleep(1)  # Penundaan opsional antara eksekusi misi

def countdown_timer(seconds: int):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\r{Fore.YELLOW}⏳ Sisa waktu: {remaining} detik")
        sys.stdout.flush()
        time.sleep(1)
    print("\n")

def main():
    while True:
        print_banner()
        accounts = load_accounts()
        total_accounts = len(accounts)
        
        print(Fore.CYAN + f"📚 Total akun ditemukan: {total_accounts}")
        
        for idx, init_data in enumerate(accounts, 1):
            print(Fore.YELLOW + f"\n📝 Memproses akun ke-{idx} dari {total_accounts}")
            
            # Login dengan username dari initData
            username = init_data.split('username%22%3A%22')[1].split('%22')[0]
            login_response = login(init_data)
            
            if not login_response:
                continue  # Skip to the next account if login failed

            if login_response['code'] == "200":
                login_data = login_response['data']
                print_login_info(login_data, username)
                
                # Mendapatkan uid dari init_data setelah login sukses
                uid = int(init_data.split('%22id%22%3A')[1].split('%2C')[0])

                # Selesaikan semua misi untuk pengguna ini
                complete_all_missions(init_data, uid)


                # Jika `isSignIn` di login_data menunjukkan hadiah sudah diambil, lewati klaim hadiah
                if login_data.get("isSignIn") == 1:
                    print(Fore.YELLOW + "✅ Hadiah harian sudah diambil untuk hari ini.")
                else:
                    # Mendapatkan data hadiah harian dan klaim jika belum diambil
                    daily_data = get_daily_rewards(init_data, uid)
                    
                    if daily_data:
                        remaining_time = daily_data["remainingTime"]
                        if remaining_time > 0:
                            print(Fore.YELLOW + f"⏳ Waktu tersisa untuk klaim hadiah berikutnya: {remaining_time} detik.")
                        elif daily_data["isSignIn"] == 0:
                            sign_in_num = daily_data["signInNum"]
                            reward_amount = daily_data["dailyRewards"][sign_in_num]
                            print(Fore.GREEN + f"💰 Hadiah hari ke-{sign_in_num + 1} adalah {reward_amount} koin.")
                            
                            # Mengklaim hadiah harian dengan tipe sesuai coinImgs
                            claim_daily_reward(init_data, uid)
                
                # Hanya lakukan tap-tap jika energi lebih dari 0
                if login_data['energy'] > 0:
                    tap_tap(init_data, uid, login_data['energy'])
                else:
                    print(Fore.YELLOW + "⚠️ Energi sudah habis, melewati tap-tap untuk akun ini.")
                
                print(Fore.YELLOW + "⏳ Menunggu 5 detik sebelum akun berikutnya...")
                time.sleep(5)
            else:
                print(Fore.RED + "❌ Gagal login!")
                continue
        
        print(Fore.CYAN + "\n✅ Semua akun telah selesai diproses!")
        print(Fore.YELLOW + "⏳ Memulai hitungan mundur 10000 detik...")
        countdown_timer(10000)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n❌ Program dihentikan oleh pengguna!")
        sys.exit(0)
