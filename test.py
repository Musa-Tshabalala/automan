import subprocess, os

def to_int(pick):
    try:
        number = int(pick)
        return number - 1
    except Exception:
        return -1
    
def clear():
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True)


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

    chosen_type = input('Choose:\n')
    pick = to_int(chosen_type)

torr_type = types[pick]

id = ''
while not id.startswith('tt') or len(id) < 5:
    clear()
    id = input('Enter Valid ID (ttxxxxxx):\n')

title = ''

while not title or len(title) <= 2:
    clear()
    title = input(f'Enter the name of the {torr_type}:\n').strip()

y = ''

while not y or len(y) != 4:
    clear()
    y = input(f'What year was this {torr_type} released?\n')

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
    print('Database entry...')