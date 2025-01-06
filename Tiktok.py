import requests as r, json as j, fade as f, os as o, time as t
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt

a = """████████▀▀▀████
████████────▀██
████████──█▄──█
███▀▀▀██──█████
█▀──▄▄██──█████
█──█████──█████
█▄──▀▀▀──▄█████
███▄▄▄▄▄███████ sssolus"""
profile_picture_history = {}

def p(x): [print(c, end='', flush=True) or t.sleep(0.003) for c in x]; print()
def d(u): 
    try:
        res = r.get(f'https://www.tiktok.com/@{u}', headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
            'accept-language': 'en-GB'}, timeout=10)
        res.raise_for_status()
        sc = bs(res.text, 'html.parser').find('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
        return j.loads(sc.text)['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo'] if sc else None
    except: return None

def c(s): return (s.get("heartCount", 0) / s.get("followerCount", 1)) * 100
def f_acc(s): return c(s) < 1 or (s.get('followerCount', 0) < 1000 and s.get('heartCount', 0) < 5000)
def i(): p(f.water(a + "\nWelcome!\n1. Enter username\n2. Use your username\n3. Related users\n4. Profile history\n5. Exit\n" + "="*50))
def p_i(u, s):
    p(f"\n{'='*50}\nUsername: {u.get('uniqueId')}\nNickname: {u.get('nickname')}\nUser ID: {u.get('id')}\n"
      f"Description: {u.get('signature')}\nCreation Date: {dt.fromtimestamp(u.get('createTime')).strftime('%d-%m-%Y %H:%M:%S')}\n"
      f"Region: {u.get('region')}\nLanguage: {u.get('language')}\nFriends: {s.get('friendCount'):,}\nFollowers: {s.get('followerCount'):,}\n"
      f"Following: {s.get('followingCount'):,}\nHearts: {s.get('heartCount'):,}\nVideos: {s.get('videoCount'):,}\n"
      f"Verified: {u.get('verified')}\nPrivate: {u.get('secret')}\nFavorite: {u.get('openFavorite')}\nEngagement: {c(s):.2f}%")
    if f_acc(s): p("Suspicious or inactive account.")
    curr_pic = u.get('avatarLarger')
    if curr_pic != profile_picture_history.get(u.get('uniqueId')):
        profile_picture_history[u.get('uniqueId')] = curr_pic
        p(f"New profile picture: {curr_pic}")
    print("="*50)

def t_c(u, o_d): n_d = d(u); return {k: (v, n_d.get(k)) for k, v in o_d.items() if n_d.get(k) != v} if n_d else None

def main():
    o_d = {}
    while True:
        i(); op = input("Option: ").strip()
        u = input("Username: ").strip() if op in '13' else o.getlogin() if op == '2' else None
        if op == '5': break
        if op == '4':
            chgs = t_c(u, o_d)
            p("\nChanges:\n" + "\n".join(f"{k}: {v[0]} -> {v[1]}" for k, v in chgs.items()) if chgs else "No changes.") if o_d else p("No previous data.")
            continue
        data = d(u)
        p("No user found.") if not data else p_i(data.get('user', {}), data.get('stats', {}))
        o_d = data.get('user', {}) if data else o_d
        input("\nPress Enter...")
main()
