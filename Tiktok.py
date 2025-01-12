import requests as r, json as j, fade as f, os as o, time as t, logging
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

art = """████████▀▀▀████
████████────▀██
████████──█▄──█
███▀▀▀██──█████
█▀──▄▄██──█████
█──█████──█████
█▄──▀▀▀──▄█████
███▄▄▄▄▄███████ wesk"""
profile_picture_history = {}

def print_slowly(text):
    [print(char, end='', flush=True) or t.sleep(0.003) for char in text]
    print()

def get_user_data(username):
    try:
        logging.info(f"Fetching data for user: {username}")
        response = r.get(f'https://www.tiktok.com/@{username}', headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
            'accept-language': 'en-GB'
        }, timeout=10)
        response.raise_for_status()
        script_content = bs(response.text, 'html.parser').find('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
        if script_content:
            logging.info("User data found.")
            return j.loads(script_content.text)['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']
        else:
            logging.warning("Expected structure not found on the page.")
    except r.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
    except (KeyError, TypeError, j.JSONDecodeError) as e:
        logging.error(f"Error processing profile data: {e}")
    return None

def get_related_users(username):
    try:
        logging.info(f"Fetching related users for: {username}")
        response = r.get(f'https://www.tiktok.com/node/share/discover?user_id={username}', headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
            'accept-language': 'en-GB'
        }, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data and 'user_list' in data:
            logging.info("Related users found.")
            return data['user_list']
        else:
            logging.warning("No related users found.")
    except r.exceptions.RequestException as e:
        logging.error(f"Request error while fetching related users: {e}")
    except (KeyError, TypeError, j.JSONDecodeError) as e:
        logging.error(f"Error processing related users data: {e}")
    return []

def get_friends(username):
    try:
        logging.info(f"Fetching friends (followers/following) for: {username}")
        response = r.get(f'https://www.tiktok.com/@{username}/following', headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
            'accept-language': 'en-GB'
        }, timeout=10)
        response.raise_for_status()
        soup = bs(response.text, 'html.parser')
        user_cards = soup.find_all('div', class_='tiktok-1egk1e7-DivItemContainer')
        friends = []
        for card in user_cards:
            username = card.find('a', class_='tiktok-1egk1e7-AnchorUsername')
            nickname = card.find('h3', class_='tiktok-1egk1e7-H3Nickname')
            if username and nickname:
                friends.append({
                    'username': username.text.strip(),
                    'nickname': nickname.text.strip()
                })
        logging.info(f"Found {len(friends)} friends.")
        return friends
    except r.exceptions.RequestException as e:
        logging.error(f"Request error while fetching friends: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while processing friends: {e}")
    return []

def display_related_users(users):
    if not users:
        print_slowly("No related users found.")
    else:
        print_slowly("\nRelated Users:")
        for user in users:
            print_slowly(f"Username: {user.get('uniqueId', 'N/A')} - Nickname: {user.get('nickname', 'N/A')}")
        print("="*50)

def display_friends(friends):
    if not friends:
        print_slowly("No friends found.")
    else:
        print_slowly("\nFriends:")
        for friend in friends:
            print_slowly(f"Username: {friend['username']} - Nickname: {friend['nickname']}")
        print("="*50)

def calculate_engagement(stats):
    try:
        return (stats.get("heartCount", 0) / stats.get("followerCount", 1)) * 100
    except ZeroDivisionError:
        logging.warning("Division by zero in engagement calculation.")
        return 0

def is_suspicious_account(stats):
    return calculate_engagement(stats) < 1 or (stats.get('followerCount', 0) < 1000 and stats.get('heartCount', 0) < 5000)

def print_menu():
    print_slowly(f.water(art + "\nWelcome!\n1. Enter username\n2. Use your username\n3. Related users\n4. Profile history\n5. Exit\n" + "="*50))

def display_user_info(user, stats):
    try:
        print_slowly(f"\n{'='*50}\nUsername: {user.get('uniqueId')}\nNickname: {user.get('nickname')}\nUser ID: {user.get('id')}\n"
                     f"Description: {user.get('signature')}\nCreation Date: {dt.fromtimestamp(user.get('createTime')).strftime('%d-%m-%Y %H:%M:%S')}\n"
                     f"Region: {user.get('region')}\nLanguage: {user.get('language')}\nFriends: {stats.get('friendCount'):,}\nFollowers: {stats.get('followerCount'):,}\n"
                     f"Following: {stats.get('followingCount'):,}\nHearts: {stats.get('heartCount'):,}\nVideos: {stats.get('videoCount'):,}\n"
                     f"Verified: {user.get('verified')}\nPrivate: {user.get('secret')}\nFavorite: {user.get('openFavorite')}\nEngagement: {calculate_engagement(stats):.2f}%")
        if is_suspicious_account(stats):
            print_slowly("Suspicious or inactive account.")
        current_picture = user.get('avatarLarger')
        if current_picture != profile_picture_history.get(user.get('uniqueId')):
            profile_picture_history[user.get('uniqueId')] = current_picture
            print_slowly(f"New profile picture: {current_picture}")
        print("="*50)
    except Exception as e:
        logging.error(f"Error displaying profile information: {e}")

def check_changes(username, old_data):
    try:
        new_data = get_user_data(username)
        return {key: (value, new_data.get(key)) for key, value in old_data.items() if new_data.get(key) != value} if new_data else None
    except Exception as e:
        logging.error(f"Error checking changes: {e}")
        return None

def main():
    old_data = {}
    while True:
        try:
            print_menu()
            option = input("Option: ").strip()
            if option == '5':
                logging.info("Exiting the program.")
                break
            username = input("Username: ").strip() if option in '13' else o.getlogin() if option == '2' else None
            if option == '3':
                if not username:
                    print_slowly("Please provide a username.")
                    continue
                related_users = get_related_users(username)
                display_related_users(related_users)
                friends = get_friends(username)
                display_friends(friends)
                continue
            if option == '4':
                changes = check_changes(username, old_data)
                if old_data and changes:
                    print_slowly("\nChanges:\n" + "\n".join(f"{key}: {value[0]} -> {value[1]}" for key, value in changes.items()))
                else:
                    print_slowly("No changes." if old_data else "No previous data.")
                continue
            data = get_user_data(username)
            if not data:
                print_slowly("No user found.")
            else:
                display_user_info(data.get('user', {}), data.get('stats', {}))
                old_data = data.get('user', {})
            input("\nPress Enter...")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

main()
