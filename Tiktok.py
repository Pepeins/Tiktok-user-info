import requests
import json
from datetime import datetime
import fade
import time
import os
from bs4 import BeautifulSoup

ascii_art = """
████████▀▀▀████
████████────▀██
████████──█▄──█
███▀▀▀██──█████
█▀──▄▄██──█████
█──█████──█████
█▄──▀▀▀──▄█████
███▄▄▄▄▄███████ Made by sssolus
"""

def Slow(text):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(0.003)
    print()

def get_tiktok_user_info(username) -> dict:
    url = f'https://www.tiktok.com/@{username}'
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
        'accept-language': 'en-GB'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10) 
        response.raise_for_status()  
        
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
        
        if script:
            data:dict = json.loads(script.text)['__DEFAULT_SCOPE__']['webapp.user-detail']
            return data.get('userInfo')
        else:
            Slow(fade.water("Error: No data found in the response."))
            return None

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        Slow(fade.water(f"Error occurred: {str(e)}"))
        return None

def get_own_username():
    user_name = os.getlogin()
    return user_name

def calculate_engagement_rate(stats):
    """Calcula la tasa de interacción del usuario."""
    likes = stats.get("heartCount", 0)
    followers = stats.get("followerCount", 0)
    if followers == 0:
        return 0
    return (likes / followers) * 100

def print_menu():
    """Imprime un menú con las opciones disponibles."""
    print(fade.water(ascii_art))
    print(fade.water("Welcome to the TikTok User Info Tool!"))
    print(fade.water("Select an option:"))
    print(fade.water("1. Enter TikTok username manually"))
    print(fade.water("2. Use your own username"))
    print(fade.water("3. Exit"))

def print_user_info(user_data, stats):
    """Muestra la información del usuario de forma estructurada y atractiva."""
    Slow(fade.water(f"Username: {user_data.get('uniqueId')}"))
    Slow(fade.water(f"Nickname: {user_data.get('nickname')}"))
    Slow(fade.water(f"User ID: {user_data.get('id')}"))
    Slow(fade.water(f"Description: {user_data.get('signature')}"))
    Slow(fade.water(f"Creation Date: {datetime.fromtimestamp(user_data.get('createTime')).strftime('%d-%m-%Y at %H:%M:%S')}"))
    Slow(fade.water(f"Region: {user_data.get('region')}"))
    Slow(fade.water(f"Language: {user_data.get('language')}"))
    Slow(fade.water(f"Friends: {stats.get('friendCount'):,}"))
    Slow(fade.water(f"Followers: {stats.get('followerCount'):,}"))
    Slow(fade.water(f"Following: {stats.get('followingCount'):,}"))
    Slow(fade.water(f"Hearts: {stats.get('heartCount'):,}"))
    Slow(fade.water(f"Videos: {stats.get('videoCount'):,}"))
    Slow(fade.water(f"Verified: {user_data.get('verified')}"))
    Slow(fade.water(f"Private Account: {user_data.get('secret')}"))
    Slow(fade.water(f"Open favorite: {user_data.get('openFavorite')}"))
    
    engagement_rate = calculate_engagement_rate(stats)
    Slow(fade.water(f"Engagement Rate: {engagement_rate:.2f}%"))

def main():
    while True:
        print_menu()
        
        option = input(fade.water("Enter your choice (1/2/3): ")).strip().lower()
        
        if option == '1':
            username = input(fade.water("Enter the TikTok username: ")).strip()
        elif option == '2':
            username = get_own_username()
            print(fade.water(f"Using your own username: {username}"))
        elif option == '3':
            Slow(fade.water("Exiting..."))
            break
        else:
            Slow(fade.water("Invalid option. Please try again."))
            continue
        
        if not username:
            Slow(fade.water("Username cannot be empty."))
            continue
        
        data = get_tiktok_user_info(username)
        
        if data is None:
            Slow(fade.water(f"Error: No user found with the username '{username}'."))  
        else:
            user_data = data.get('user', {})
            stats = data.get('stats', {})
            Slow(fade.water("TikTok User Information:"))
            print_user_info(user_data, stats)
        
        input(fade.water("[x] Press Enter to return to the menu..."))

if __name__ == "__main__":
    main()
