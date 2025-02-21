import json
import fade
import os
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='tiktok_tracker.log'
)
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logging.getLogger('').addHandler(console)

LOGO_ART = """████████▀▀▀████
████████────▀██
████████──█▄──█
███▀▀▀██──█████
█▀──▄▄██──█████
█──█████──█████
█▄──▀▀▀──▄█████
███▄▄▄▄▄███████ TikTracker"""

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'accept-language': 'en-US,en;q=0.9',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1'
}
REQUEST_TIMEOUT = 15
SUSPICIOUS_ENGAGEMENT_THRESHOLD = 1.0
MIN_FOLLOWERS_THRESHOLD = 1000
MIN_HEARTS_THRESHOLD = 5000

@dataclass
class UserStats:
    
    friend_count: int = 0
    follower_count: int = 0
    following_count: int = 0
    heart_count: int = 0
    video_count: int = 0
    
    def calculate_engagement(self) -> float:
        
        if self.follower_count <= 0:
            return 0.0
        return (self.heart_count / self.follower_count) * 100
    
    def is_suspicious(self) -> bool:
        
        return (self.calculate_engagement() < SUSPICIOUS_ENGAGEMENT_THRESHOLD or 
                (self.follower_count < MIN_FOLLOWERS_THRESHOLD and 
                 self.heart_count < MIN_HEARTS_THRESHOLD))
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserStats':
        
        return cls(
            friend_count=data.get('friendCount', 0),
            follower_count=data.get('followerCount', 0),
            following_count=data.get('followingCount', 0),
            heart_count=data.get('heartCount', 0),
            video_count=data.get('videoCount', 0)
        )

@dataclass
class UserProfile:
    username: str = ""
    nickname: str = ""
    user_id: str = ""
    signature: str = ""
    create_time: int = 0
    region: str = ""
    language: str = ""
    avatar_url: str = ""
    verified: bool = False
    private: bool = False
    open_favorite: bool = False
    stats: UserStats = None
    
    def formatted_creation_date(self) -> str:
        return datetime.fromtimestamp(self.create_time).strftime('%d-%m-%Y %H:%M:%S')
    
    @classmethod
    def from_dict(cls, user_data: Dict, stats_data: Dict) -> 'UserProfile':
        return cls(
            username=user_data.get('uniqueId', ''),
            nickname=user_data.get('nickname', ''),
            user_id=user_data.get('id', ''),
            signature=user_data.get('signature', ''),
            create_time=user_data.get('createTime', 0),
            region=user_data.get('region', ''),
            language=user_data.get('language', ''),
            avatar_url=user_data.get('avatarLarger', ''),
            verified=user_data.get('verified', False),
            private=user_data.get('secret', False),
            open_favorite=user_data.get('openFavorite', False),
            stats=UserStats.from_dict(stats_data)
        )

class ProfilePictureTracker:
    def __init__(self, storage_file: str = 'profile_pictures.json'):
        self.storage_file = storage_file
        self.history = self._load_history()
        
    def _load_history(self) -> Dict:
        
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading profile picture history: {e}")
        return {}
    
    def _save_history(self):
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving profile picture history: {e}")
    
    def check_for_changes(self, username: str, current_url: str) -> bool:
        has_changed = username in self.history and self.history[username] != current_url
        if username not in self.history or has_changed:
            self.history[username] = current_url
            self._save_history()
        return has_changed

class TikTokAPI:
    @staticmethod
    def get_user_data(username: str) -> Optional[Dict]:
        try:
            logging.info(f"Fetching data for user: {username}")
            response = requests.get(
                f'https://www.tiktok.com/@{username}', 
                headers=HEADERS, 
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            script = soup.find('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
            
            if not script:
                logging.warning(f"Data structure not found for user: {username}")
                return None
                
            data = json.loads(script.text)
            user_data = data['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']
            logging.info(f"Successfully retrieved data for user: {username}")
            return user_data
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error while fetching user data: {e}")
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            logging.error(f"Error parsing user data: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in get_user_data: {e}")
        return None
    
    @staticmethod
    def get_related_users(user_id: str) -> List[Dict]:
        try:
            logging.info(f"Fetching related users for ID: {user_id}")
            response = requests.get(
                f'https://www.tiktok.com/node/share/discover?user_id={user_id}',
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            if data and 'user_list' in data:
                return data['user_list']
            logging.warning(f"No related users found for ID: {user_id}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error while fetching related users: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            logging.error(f"Error parsing related users data: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in get_related_users: {e}")
        return []
    
    @staticmethod
    def get_friends(username: str) -> List[Dict]:
        try:
            logging.info(f"Fetching friends for user: {username}")
            response = requests.get(
                f'https://www.tiktok.com/@{username}/following',
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Note: Selectors may change over time as tiktok updates its UI / Nota: Los selectores pueden cambiar con el tiempo ya que tiktok actualiza su UI
            user_cards = soup.select('div[data-e2e="user-card"]')
            friends = []
            
            for card in user_cards:
                username_elem = card.select_one('h3[data-e2e="user-username"]')
                nickname_elem = card.select_one('h4[data-e2e="user-nickname"]')
                
                if username_elem and nickname_elem:
                    friends.append({
                        'username': username_elem.text.strip('@'),
                        'nickname': nickname_elem.text.strip()
                    })
            
            logging.info(f"Found {len(friends)} friends for user: {username}")
            return friends
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error while fetching friends: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in get_friends: {e}")
        return []

class UI:
    @staticmethod
    def print_slowly(text: str, speed: float = 0.002):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(speed)
        print()
    
    @staticmethod
    def display_logo():
        UI.print_slowly(fade.water(LOGO_ART))
    
    @staticmethod
    def display_menu():
        options = [
            "1. Search by username",
            "2. Use your username",
            "3. View related users",
            "4. Profile History",
            "5. Exit"
        ]
        UI.display_logo()
        UI.print_slowly("\n".join(options))
        UI.print_slowly("="*50)
    
    @staticmethod
    def display_user_profile(profile: UserProfile, is_new_picture: bool):
        UI.print_slowly(f"\n{'='*50}")
        UI.print_slowly(f"Username: {profile.username}")
        UI.print_slowly(f"Nickname: {profile.nickname}")
        UI.print_slowly(f"User ID: {profile.user_id}")
        UI.print_slowly(f"Description: {profile.signature}")
        UI.print_slowly(f"Creation Date: {profile.formatted_creation_date()}")
        UI.print_slowly(f"Region: {profile.region}")
        UI.print_slowly(f"Language: {profile.language}")
        UI.print_slowly(f"Friends: {profile.stats.friend_count:,}")
        UI.print_slowly(f"Followers: {profile.stats.follower_count:,}")
        UI.print_slowly(f"Following: {profile.stats.following_count:,}")
        UI.print_slowly(f"Hearts: {profile.stats.heart_count:,}")
        UI.print_slowly(f"Videos: {profile.stats.video_count:,}")
        UI.print_slowly(f"Verified: {profile.verified}")
        UI.print_slowly(f"Private: {profile.private}")
        UI.print_slowly(f"Favorite: {profile.open_favorite}")
        UI.print_slowly(f"Engagement: {profile.stats.calculate_engagement():.2f}%")
        
        if profile.stats.is_suspicious():
            UI.print_slowly("⚠️ Suspicious or inactive account detected ⚠️")
            
        if is_new_picture:
            UI.print_slowly(f"New profile picture detected: {profile.avatar_url}")
            
        UI.print_slowly("="*50)
    
    @staticmethod
    def display_related_users(users: List[Dict]):
        if not users:
            UI.print_slowly("No related users found.")
            return
            
        UI.print_slowly("\nRelated Users:")
        for user in users:
            UI.print_slowly(f"Username: {user.get('uniqueId', 'N/A')} - Nickname: {user.get('nickname', 'N/A')}")
        UI.print_slowly("="*50)
    
    @staticmethod
    def display_friends(friends: List[Dict]):
        if not friends:
            UI.print_slowly("No friends found.")
            return
            
        UI.print_slowly("\nFriends:")
        for friend in friends:
            UI.print_slowly(f"Username: {friend['username']} - Nickname: {friend['nickname']}")
        UI.print_slowly("="*50)
    
    @staticmethod
    def display_profile_changes(changes: Dict[str, Tuple[Any, Any]]):
        if not changes:
            UI.print_slowly("No changes detected.")
            return
            
        UI.print_slowly("\nChanges Detected:")
        for key, (old_value, new_value) in changes.items():
            UI.print_slowly(f"{key}: {old_value} -> {new_value}")
        UI.print_slowly("="*50)

class TikTokTracker:
    def __init__(self):
        self.api = TikTokAPI()
        self.ui = UI()
        self.picture_tracker = ProfilePictureTracker()
        self.last_profile = None
    
    def get_username_input(self, use_system_user: bool = False) -> str:
        if use_system_user:
            return os.getlogin()
        return input("Enter username: ").strip().lstrip('@')
    
    def analyze_user(self, username: str) -> Optional[UserProfile]:
        user_data = self.api.get_user_data(username)
        if not user_data:
            self.ui.print_slowly("No user found or profile is private.")
            return None
            
        profile = UserProfile.from_dict(
            user_data.get('user', {}), 
            user_data.get('stats', {})
        )
        
        is_new_picture = self.picture_tracker.check_for_changes(
            profile.username, 
            profile.avatar_url
        )
        
        self.ui.display_user_profile(profile, is_new_picture)
        self.last_profile = profile
        return profile
    
    def check_profile_changes(self, username: str) -> Dict:
        if not self.last_profile:
            self.ui.print_slowly("No previous profile data available.")
            return {}
            
        current_data = self.api.get_user_data(username)
        if not current_data:
            self.ui.print_slowly("Could not fetch current profile data.")
            return {}
            
        current_profile = UserProfile.from_dict(
            current_data.get('user', {}),
            current_data.get('stats', {})
        )
        
        changes = {}
        for attr in ['username', 'nickname', 'signature', 'region', 'language',
                    'verified', 'private', 'open_favorite']:
            old_val = getattr(self.last_profile, attr)
            new_val = getattr(current_profile, attr)
            if old_val != new_val:
                changes[attr] = (old_val, new_val)

        if self.last_profile.stats and current_profile.stats:
            for attr in ['follower_count', 'following_count', 'heart_count', 'video_count']:
                old_val = getattr(self.last_profile.stats, attr)
                new_val = getattr(current_profile.stats, attr)
                if old_val != new_val:
                    changes[attr] = (old_val, new_val)
        
        return changes
    
    def run(self):
        while True:
            try:
                self.ui.display_menu()
                option = input("Option: ").strip()
                
                if option == '5':
                    self.ui.print_slowly("Exiting program.")
                    break
                
                if option == '1':
                    username = self.get_username_input()
                    self.analyze_user(username)
                
                elif option == '2':
                    username = self.get_username_input(use_system_user=True)
                    self.ui.print_slowly(f"Using system username: {username}")
                    self.analyze_user(username)
                
                elif option == '3':
                    username = self.get_username_input()
                    user_data = self.api.get_user_data(username)
                    if user_data and 'user' in user_data:
                        user_id = user_data['user'].get('id')
                        if user_id:
                            related_users = self.api.get_related_users(user_id)
                            self.ui.display_related_users(related_users)
                            friends = self.api.get_friends(username)
                            self.ui.display_friends(friends)
                        else:
                            self.ui.print_slowly("Could not retrieve user ID.")
                    else:
                        self.ui.print_slowly("User not found.")
                
                elif option == '4':
                    username = self.get_username_input()
                    changes = self.check_profile_changes(username)
                    self.ui.display_profile_changes(changes)
                
                else:
                    self.ui.print_slowly("Invalid option. Please try again.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                self.ui.print_slowly("\nProgram interrupted. Exiting...")
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                self.ui.print_slowly(f"An error occurred: {str(e)}")
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    tracker = TikTokTracker()
    tracker.run()
