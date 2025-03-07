import os
import sys
import requests
import datetime
import pytz
import time
from colorama import init, Fore, Style

init(autoreset=True)

# Global variables
url_claim = 'https://elb.seeddao.org/api/v1/seed/claim'
url_balance = 'https://elb.seeddao.org/api/v1/profile/balance'
url_checkin = 'https://elb.seeddao.org/api/v1/login-bonuses'
url_upgrade_storage = 'https://elb.seeddao.org/api/v1/seed/storage-size/upgrade'
url_upgrade_mining = 'https://elb.seeddao.org/api/v1/seed/mining-speed/upgrade'
url_get_profile = 'https://elb.seeddao.org/api/v1/profile'

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-ID,en-US;q=0.9,en;q=0.8,id;q=0.7',
    'content-length': '0',
    'dnt': '1',
    'origin': 'https://cf.seeddao.org',
    'priority': 'u=1, i',
    'referer': 'https://cf.seeddao.org/',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'telegram-data': 'tokens',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

# Function to print the welcome message
def print_welcome_message():
    print(r"""
 ___  __  __  ____  __  __  ____    ____   __    _  _  ____    ____  _____  ____ 
/ __)(  )(  )(  _ \(  )(  )(  _ \  (_  _) /__\  ( \( )(_  _)  (  _ \(  _  )(_  _)
\__ \ )(__)(  ) _ < )(__)(  )   /    )(  /(__)\  )  (  _)(_    ) _ < )(_)(   )(  
(___/(______)(____/(______)(_)\_)   (__)(__)(__)(_)\_)(____)  (____/(_____) (__) 

              """)
    print(Fore.GREEN + Style.BRIGHT + "SeedBOT by Altaff")
    print(Fore.GREEN + Style.BRIGHT + "Update Link: https://github.com/altaffoc/seed")
    print(Fore.GREEN + Style.BRIGHT + "Free Testing DWYOR")

# Function to load credentials from a file
def load_credentials():
    try:
        with open('query.txt', 'r') as file:
            tokens = file.read().strip().split('\n')
        return tokens
    except FileNotFoundError:
        print("File tokens.txt tidak ditemukan.")
        return []
    except Exception as e:
        print(f"Terjadi kesalahan saat memuat token: {str(e)}")
        return []

# Function to check the worm status
def check_worm():
    response = requests.get('https://elb.seeddao.org/api/v1/worms', headers=headers)
    if response.status_code == 200:
        worm_data = response.json()['data']
        next_refresh = worm_data['next_refresh']
        is_caught = worm_data['is_caught']

        next_refresh_dt = datetime.datetime.fromisoformat(next_refresh[:-1] + '+00:00')
        now_utc = datetime.datetime.now(pytz.utc)

        time_diff_seconds = (next_refresh_dt - now_utc).total_seconds()
        hours = int(time_diff_seconds // 3600)
        minutes = int((time_diff_seconds % 3600) // 60)

        print(f"{Fore.GREEN+Style.BRIGHT}[ Worms ]: Next in {hours} jam {minutes} menit - Status: {'Caught' if is_caught else 'Available'}")

        return worm_data
    else:
        print(f"{Fore.RED+Style.BRIGHT}[ Worms ]: Gagal mendapatkan data worm.")
        return None

# Function to catch the worm
def catch_worm():
    worm_data = check_worm()
    if worm_data and not worm_data['is_caught']:
        response = requests.post('https://elb.seeddao.org/api/v1/worms/catch', headers=headers)
        if response.status_code == 200:
            print(f"{Fore.GREEN+Style.BRIGHT}[ Worms ]: Berhasil menangkap")
        elif response.status_code == 400:
            print(f"{Fore.RED+Style.BRIGHT}[ Worms ]: Sudah terangkap")
        elif response.status_code == 404:
            print(f"{Fore.RED+Style.BRIGHT}[ Worms ]: Worm tidak ditemukan")
        else:
            print(f"{Fore.RED+Style.BRIGHT}[ Worms ]: Gagal menangkap worm, status code: {response.status_code}")
    else:
        print(f"{Fore.RED+Style.BRIGHT}[ Worms ]: Worm tidak tersedia atau sudah tertangkap.")

# Function to get profile information
def get_profile():
    response = requests.get(url_get_profile, headers=headers)
    if response.status_code == 200:
        profile_data = response.json()
        name = profile_data['data']['name']
        print(f"{Fore.CYAN+Style.BRIGHT}:::::::::::::: [ Tuyul | {name} ] ::::::::::::::")

        upgrades = {}
        for upgrade in profile_data['data']['upgrades']:
            upgrade_type = upgrade['upgrade_type']
            upgrade_level = upgrade['upgrade_level']
            if upgrade_type in upgrades:
                if upgrade_level > upgrades[upgrade_type]:
                    upgrades[upgrade_type] = upgrade_level
            else:
                upgrades[upgrade_type] = upgrade_level

        for upgrade_type, level in upgrades.items():
            print(f"{Fore.BLUE+Style.BRIGHT}[ {upgrade_type.capitalize()} Level ]: {level + 1}")
    else:
        print(f"Gagal mendapatkan data, status code: {response.status_code}")
        return None

# Function to check account balance
def check_balance():
    response = requests.get(url_balance, headers=headers)
    if response.status_code == 200:
        balance_data = response.json()
        print(f"{Fore.YELLOW+Style.BRIGHT}[ Balance ]: {balance_data['data'] / 1000000000}")
        return True
    else:
        print(f"{Fore.RED+Style.BRIGHT}[ Balance ]: Gagal masa ora | {response.status_code}")
        return False

# Function to perform daily check-in
def cekin_daily():
    response = requests.post(url_checkin, headers=headers)
    if response.status_code == 200:
        data = response.json()
        day = data.get('data', {}).get('no', '')
        print(f"{Fore.GREEN+Style.BRIGHT}[ Check-in ]: Joss Check-in berhasil | Day {day}")
    else:
        data = response.json()
        if data.get('message') == 'already claimed for today':
            print(f"{Fore.RED+Style.BRIGHT}[ Check-in ]: Hari dah check in bang jangan maruk")
        else:
            print(f"{Fore.RED+Style.BRIGHT}[ Check-in ]: Gagal lah masa kagak | {data}")

# Function to upgrade storage
def upgrade_storage(confirm):
    if confirm.lower() == 'y':
        response = requests.post(url_upgrade_storage, headers=headers)
        if response.status_code == 200:
            return '[ Upgrade storage ]: Joss Berhasil'
        else:
            return '[ Upgrade storage ]: Balancenya kurang banyak'
    else:
        return None

# Function to upgrade mining
def upgrade_mining(confirm):
    if confirm.lower() == 'y':
        response = requests.post(url_upgrade_mining, headers=headers)
        if response.status_code == 200:
            return '[ Upgrade mining ]: Joss Berhasil'
        else:
            return '[ Upgrade mining ]: Balancenya kurang banyak'
    else:
        return None

# Function to fetch and complete tasks
def get_tasks():
    response = requests.get('https://elb.seeddao.org/api/v1/tasks/progresses', headers=headers)
    tasks = response.json()['data']
    for task in tasks:
        if task['task_user'] is None or not task['task_user']['completed']:
            complete_task(task['id'], task['name'])

# Function to mark a task as completed
def complete_task(task_id, task_name):
    response = requests.post(f'https://elb.seeddao.org/api/v1/tasks/{task_id}', headers=headers)
    if response.status_code == 200:
        print(f"{Fore.GREEN+Style.BRIGHT}[ Tasks ]: Joss Tugas {task_name} selesai.")
    else:
        print(f"{Fore.RED+Style.BRIGHT}[ Tasks ]: Gagal ngerjain tugas sabar yak!! {task_name}, status code: {response.status_code}")

# Function to clear console screen
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to verify password
def verify_password():
    password = input("Masukin password dulu bang: ")
    # Replace 'YOUR_PASSWORD' with your actual password
    if password == 'suburtani':
        return True
    else:
        print("Salah password bang. Baleni meneh.")
        return False

# Main function to run the script
def main():
    print_welcome_message()
    
    # Verify password before proceeding
    if not verify_password():
        return
    
    tokens = load_credentials()

    confirm_storage = input("Auto upgrade penyimpanan? (y/n): ")
    confirm_mining = input("Auto upgrade mining? (y/n): ")
    confirm_task = input("Auto Selesein Task? (y/n): ")

    while True:
        try:
            hasil_upgrade_storage = upgrade_storage(confirm_storage)
            hasil_upgrade_mining = upgrade_mining(confirm_mining)

            for index, token in enumerate(tokens):
                headers['telegram-data'] = token
                profile_info = get_profile()
                if profile_info:
                    print(f"Memproses untuk token ke {profile_info['data']['name']}")

                if hasil_upgrade_storage:
                    print(hasil_upgrade_storage)
                    time.sleep(1)
                if hasil_upgrade_mining:
                    print(hasil_upgrade_mining)
                    time.sleep(1)

                if check_balance():
                    response = requests.post(url_claim, headers=headers)
                    if response.status_code == 200:
                        print(f"{Fore.GREEN+Style.BRIGHT}[ Claim ]: Joss Claim berhasil")
                    elif response.status_code == 400:
                        response_data = response.json()
                        print(f"{Fore.RED+Style.BRIGHT}[ Claim ]: Belum waktunya claim bang")
                    else:
                        print(f"Terjadi kesalahan, status code: {response.status_code}")

                    cekin_daily()
                    if confirm_task.lower() == 'y':
                        get_tasks()

            for i in range(30, 0, -1):
                sys.stdout.write(f"\r{Fore.CYAN+Style.BRIGHT}:::::::::::: Selesai, tunggu {i} detik.. ::::::::::::")
                sys.stdout.flush()
                time.sleep(1)
            print()

        except Exception as e:
            print(f"Terjadi kesalahan utama: {str(e)}")

if __name__ == "__main__":
    main()
