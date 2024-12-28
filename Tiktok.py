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
            Slow(fade.water("\n[ERROR] No data found in the response, check the username.\n"))
            return None

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        Slow(fade.water(f"\n[ERROR] {str(e)}\n"))
        return None

def get_own_username():
    user_name = os.getlogin()
    return user_name

def calculate_engagement_rate(stats):
    likes = stats.get("heartCount", 0)
    followers = stats.get("followerCount", 0)
    if followers == 0:
        return 0
    return (likes / followers) * 100

def print_menu():
    print(fade.water(ascii_art))
    print(fade.water("Welcome to the TikTok User Info Tool!"))
    print(fade.water("\nSelect an option:\n"))
    print(fade.water("1. Enter TikTok username manually"))
    print(fade.water("2. Use your own username"))
    print(fade.water("3. Search related users"))
    print(fade.water("4. View profile change history"))
    print(fade.water("5. Exit"))
    print(fade.water("\n" + "=" * 50))

def print_user_info(user_data, stats):
    print(fade.water("\n" + "=" * 50))
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
    print(fade.water("\n" + "=" * 50))

def search_related_users(username):

    url = f'https://www.tiktok.com/@{username}/followers'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        users = []
#test 
        related_users = soup.find_all('a', {'class': 'some-class-to-identify-users'})
        for user in related_users:
            users.append(user.get('href'))
        return users
    return []

def track_profile_changes(username, old_data):
   #this is a test
    new_data = get_tiktok_user_info(username)
    if new_data is None:
        return None
    
    changes = {}
    for key, value in old_data.items():
        if new_data.get(key) != value:
            changes[key] = (value, new_data.get(key))
    
    return changes

def main():
    old_user_data = {}  
    
    while True:
        print_menu()
        
        option = input(fade.water("\nEnter your choice (1/2/3/4/5): ")).strip().lower()
        
        if option == '1':
            username = input(fade.water("Enter the TikTok username: ")).strip()
        elif option == '2':
            username = get_own_username()
            print(fade.water(f"Using your own username: {username}"))
        elif option == '3':
            username = input(fade.water("Enter the tiktok username to find related users: ")).strip()
            related_users = search_related_users(username)
            if related_users:
                Slow(fade.water("\nRelated users found:"))
                for user in related_users:
                    Slow(fade.water(user))
            else:
                Slow(fade.water("\nNo related users found."))
            continue
        elif option == '4':
            username = input(fade.water("Enter the tiktok username to view profile changes: ")).strip()
            if old_user_data:
                changes = track_profile_changes(username, old_user_data)
                if changes:
                    Slow(fade.water("\nProfile changes detected:"))
                    for key, (old_value, new_value) in changes.items():
                        Slow(fade.water(f"{key}: {old_value} -> {new_value}"))
                else:
                    Slow(fade.water("\nNo changes detected in the profile."))
            else:
                Slow(fade.water("\nNo previous data to compare."))
            continue
        elif option == '5':
            Slow(fade.water("\nExiting..."))
            break
        else:
            Slow(fade.water("\n[ERROR] Invalid option.\n"))
            continue
        
        if not username:
            Slow(fade.water("\n[ERROR] Username cannot be empty.\n"))
            continue
        
        data = get_tiktok_user_info(username)
        
        if data is None:
            Slow(fade.water(f"\n[ERROR] No user found with the username '{username}'.\n"))  
        else:
            user_data = data.get('user', {})
            stats = data.get('stats', {})
            Slow(fade.water("\nTikTok User Information:"))
            print_user_info(user_data, stats)
            
            #this is a test
            old_user_data = user_data
        
        input(fade.water("\n[x] Press Enter to return to the menu..."))

if __name__ == "__main__":
    main()

