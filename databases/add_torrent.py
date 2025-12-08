from core.db import DB
from dotenv import load_dotenv
import os, subprocess
load_dotenv()

db_name = os.getenv('TORRENT_DB')
db_pass = os.getenv('DBPASS')
db_user = os.getenv('DBUSER')

def to_int(pick):
    try:
        number = int(pick)
        return number - 1
    except Exception:
        return -1
    
def clear():
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True)

with DB(db_name, db_pass, db_user, 'localhost') as torr:
    print('What type of show are you adding?\n')
    types = ['movie', 'series']
    for i, type in enumerate(types, start=1):
        print(f'{i}. {type.title()}')

    chosen_type = input('\nChoose:\n')
    pick = to_int(chosen_type)
    torr_type = None

    while not pick in range(len(types)):
        clear()
        print('Please enter valid option\n')
        for i, type in enumerate(types, start=1):
            print(f'{i}. {type.title()}')

        chosen_type = input('\nChoose:\n')
        pick = to_int(chosen_type)

    torr_type = types[pick]

    id = ''
    while not id.startswith('tt') or len(id) < 7:
        clear()
        id = input(f'Enter valid ID for the {torr_type} (ttxxxxxx):\n').strip()
        
    title = ''

    while not title or len(title) <= 2:
        clear()
        title = input(f'Enter the name of the {torr_type}:\n').strip()

    y = ''

    while not y or len(y) != 4:
        clear()
        y = input(f'What year was this {torr_type} released?\n').strip()
        try:
            int(y)
        except Exception:
            y = ''

    e = 0
    s = 0

    if torr_type == 'series':
        while s <= 0:
            clear()
            s = input('What season would you like to download?\n')
            try:
                s = int(s)
            except TypeError:
                s = 0
        
        s = str(s)

        while e <= 1:
            clear()
            e = input('How many episodes does this season have?\n')
            try:
                e = int(e)
            except TypeError:
                e = 0

        e = str(e)
    clear()

    print(
        f'Type: {torr_type}\nTitle: {title}\nYear: {y}\nId: {id}\nSeason: {s}\nEpisodes: {e}\n'
    )

    confirm = input('\nPlease confirm details (y/n)\n')

    if confirm.lower() == 'y' or confirm.lower() == 'yes':
        entry = torr.execute(
            """
            INSERT INTO torrents (id, type, title, y, s, max_e)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (id, torr_type, title, y, s, e)
        )

        if entry == 'INSERT 0 1':
            print('Your entry has been recorded')
        else:
            print('Your entry was successfull:', entry)
    else:
        clear()
        print('Upload unsuccessfull, start again!')



    




    

