from tkinter import *
import pygame
import os
import re

pygame.mixer.init()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Глобальные переменные
playing = False
paused = False
volume_visible = False
seeking = False
current_song_name = None
current_song_path = None
song_duration = 0
lyrics = []
current_lyrics_index = 0

### караоке ###
def toggle_karaoke():
    if karaoke_frame.winfo_ismapped():
        karaoke_frame.place_forget()
        toggle_karaoke_btn.config(text="🎤 Показать караоке")
    else:
        karaoke_frame.place(x=300, y=100, width=600, height=350)
        toggle_karaoke_btn.config(text="🎤 Скрыть караоке")

def load_lyrics(song_name):
    global lyrics, current_lyrics_index
    lyrics = []
    current_lyrics_index = 0
    
    clean_name = song_name
    if clean_name.endswith('.mp3'):
        clean_name = clean_name[:-4]
    
    possible_files = [
        os.path.join("lyrics", f"{clean_name}.lrc"),
        os.path.join("lyrics", f"{clean_name}.txt"),
        os.path.join("lyrics", f"{clean_name.lower()}.lrc"),
    ]
    
    if ' - ' in clean_name:
        song_only = clean_name.split(' - ')[-1].strip()
        possible_files.append(os.path.join("lyrics", f"{song_only}.lrc"))
    
    lrc_content = None
    for file_path in possible_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lrc_content = f.read()
                break
            except:
                continue
    
    if not lrc_content:
        karaoke_text.config(state='normal')
        karaoke_text.delete('1.0', END)
        karaoke_text.insert('1.0', f"Текст песни '{clean_name}' не найден")
        karaoke_text.config(state='disabled')
        karaoke_current.config(text=f"{clean_name}", fg="#9E9E9E")
        karaoke_next.config(text="Текст не найден", fg="#B71C1C")
        return
    
    parse_lrc_content(lrc_content)
    display_lyrics_text(lrc_content, clean_name)
    karaoke_current.config(text=f"🎵 {clean_name}", fg="#4CAF50")
    karaoke_next.config(text="Нажмите Play", fg="#757575")

def parse_lrc_content(lrc_content):
    global lyrics
    lyrics = []
    
    for line in lrc_content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        match = re.match(r'\[(\d+):(\d+\.?\d*)\](.*)', line)
        if match:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            text = match.group(3).strip()
            time_sec = minutes * 60 + seconds
            
            if text and not text.startswith('['):
                lyrics.append((time_sec, text))
    
    lyrics.sort(key=lambda x: x[0])
    if not lyrics:
        lyrics.append((0, "Текст без тайминга"))

def display_lyrics_text(lrc_content, song_name):
    karaoke_text.config(state='normal')
    karaoke_text.delete('1.0', END)
    karaoke_text.insert('1.0', f"🎤 {song_name}\n{'='*40}\n\n")
    
    lines = lrc_content.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('[ti:') and not line.startswith('[ar:') and not line.startswith('[al:'):
            clean_line = re.sub(r'\[\d+:\d+\.?\d*\]', '', line)
            if clean_line.strip():
                karaoke_text.insert(END, clean_line + '\n')
    
    karaoke_text.config(state='disabled')

def highlight_current_line(text):
    if not text:
        return
    
    karaoke_text.config(state='normal')
    karaoke_text.tag_remove("highlight", "1.0", END)
    
    content = karaoke_text.get("1.0", END)
    lines = content.split('\n')
    clean_search_text = text.strip().lower()
    
    for i, line in enumerate(lines):
        clean_line = line.strip().lower()
        if clean_search_text in clean_line:
            start_index = f"{i+1}.0"
            end_index = f"{i+1}.end"
            karaoke_text.tag_add("highlight", start_index, end_index)
            karaoke_text.tag_config("highlight", background="#E3F2FD", foreground="#1565C0", font=('Arial', 12, 'bold'))
            karaoke_text.see(start_index)
            break
    
    karaoke_text.config(state='disabled')

def update_karaoke():
    global current_lyrics_index
    
    if playing and not paused and not seeking:
        try:
            current_time = pygame.mixer.music.get_pos() / 1000
            
            if lyrics:
                found = False
                for i in range(len(lyrics)):
                    time_sec, text = lyrics[i]
                    next_time = lyrics[i+1][0] if i+1 < len(lyrics) else float('inf')
                    if time_sec <= current_time < next_time:
                        if i != current_lyrics_index:
                            current_lyrics_index = i
                            karaoke_current.config(text=text, fg="#FF5722")
                            if i+1 < len(lyrics):
                                karaoke_next.config(text=lyrics[i+1][1], fg="#757575")
                            else:
                                karaoke_next.config(text="Конец", fg="#9E9E9E")
                            highlight_current_line(text)
                        found = True
                        break
                
                if not found and current_time < lyrics[0][0]:
                    karaoke_current.config(text="▶ Начало...", fg="#4CAF50")
                    karaoke_next.config(text=lyrics[0][1] if lyrics else "", fg="#757575")
            else:
                karaoke_current.config(text="🎵 Играет музыка", fg="#2196F3")
                karaoke_next.config(text="Нет текста", fg="#9E9E9E")
                
        except:
            pass
    
    root.after(100, update_karaoke)

def on_song_select(event):
    selected = song_list.curselection()
    if selected:
        song_name = song_list.get(selected[0])
        load_lyrics(song_name)
        status.config(text=f'Выбрано: {song_name}', fg='blue')

### функции дефолтные ###
def song_duration_get(song_path):
    try:
        sound = pygame.mixer.Sound(song_path)
        return sound.get_length()
    except:
        return 0

def load_songs():
    song_list.delete(0, END)
    if not os.path.exists(music_folder):
        os.makedirs(music_folder)
        status.config(text=f'Создана папка {music_folder}. Добавьте MP3 файлы.', fg='blue')
        return
    
    mp3_files = [f for f in os.listdir(music_folder) if f.lower().endswith('.mp3')]
    if mp3_files:
        for file in sorted(mp3_files):
            song_list.insert(END, file)
        if mp3_files:
            song_list.selection_set(0)
            status.config(text=f'Загружено песен: {len(mp3_files)}', fg='blue')
    else:
        status.config(text='В папке нет MP3 файлов', fg='red')

def seek(a):
    global seeking
    if playing or paused:
        seeking = True
        position = seek_bar.get()
        try:
            if song_duration > 0:
                start_time = (position / 100) * song_duration
            else:
                start_time = position * 3
            pygame.mixer.music.stop()
            pygame.mixer.music.load(current_song_path)
            pygame.mixer.music.play(start=start_time)
            if paused:
                pygame.mixer.music.pause()
            min = int(start_time // 60)
            sec = int(start_time % 60)
            min_total = int(song_duration // 60)
            sec_total = int(song_duration % 60)
            status.config(text=f'⏩{min}:{sec:02d} / {min_total}:{sec_total:02d}', fg='blue')
        except:
            status.config(text='❌ Ошибка перемотки', fg='red')
        seeking = False
        
        if playing and not paused:
            selected = song_list.curselection()
            if selected:
                song_name = song_list.get(selected[0])
                root.after(2000, lambda: status.config(text=f'▶ {song_name}', fg='green'))

def volume(value):
    volume_level = int(value) / 100
    pygame.mixer.music.set_volume(volume_level)

def start():
    global playing, paused, current_song_path, current_song_name, song_duration
    selected = song_list.curselection()
    if not selected:
        return
    current_song_name = song_list.get(selected[0])
    current_song_path = os.path.join(music_folder, current_song_name)
    try:
        pygame.mixer.music.load(current_song_path)
        pygame.mixer.music.play()
        playing = True
        paused = False
        song_duration = song_duration_get(current_song_path)
        seek_bar.set(0)
        status.config(text=f'▶ {current_song_name}', fg='green')
        btnplay_pause.config(image=img2)
        load_lyrics(current_song_name)
    except:
        status.config(text='Ошибка', fg='red')

def right():
    if song_list.size() > 0:
        number_song = song_list.curselection()
        if number_song:
            index_before = (number_song[0] + 1) % song_list.size()
            song_list.selection_clear(0, END)
            song_list.selection_set(index_before)
            song_list.see(index_before)
            start()

def left():
    if song_list.size() > 0:
        number_song = song_list.curselection()
        if number_song:
            index_before = (number_song[0] - 1) % song_list.size()
            song_list.selection_clear(0, END)
            song_list.selection_set(index_before)
            song_list.see(index_before)
            start()

def play_pause():
    global playing, paused, current_song_path, current_song_name, song_duration
    selected = song_list.curselection()
    if not selected:
        return
    current_song_name = song_list.get(selected[0])
    song_path = os.path.join(music_folder, current_song_name)
    new_song = (song_path != current_song_path)
    if new_song or (not playing and not paused):
        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            playing = True
            paused = False
            current_song_path = song_path
            song_duration = song_duration_get(song_path)
            seek_bar.set(0)
            status.config(text=f'▶ {current_song_name}', fg='green')
            btnplay_pause.config(image=img2)
            load_lyrics(current_song_name)
        except:
            status.config(text='Ошибка', fg='red')
    elif playing and not paused and not new_song:
        pygame.mixer.music.pause()
        paused = True
        btnplay_pause.config(image=img1)
        status.config(text=f'⏸ {current_song_name}', fg='orange')
    elif paused and playing and not new_song:
        pygame.mixer.music.unpause()
        paused = False
        btnplay_pause.config(image=img2)
        status.config(text=f'▶ {current_song_name}', fg='green')

### окно ###
music_folder = "music"
root = Tk()
root.title('MuteSound - Плеер с караоке')
root.geometry('1280x770')
root.configure(bg='white')

canvas = Canvas(root, width=1280, height=770, bg='white', highlightthickness=0)
canvas.place(x=0, y=0)

def create_beautiful_background():
    canvas.create_rectangle(0, 0, 1280, 770, fill='#f8f9fa', outline='')
    colors = ['#e3f2fd', '#f3e5f5', '#e8f5e8', '#fff3e0']
    for i, (x, y) in enumerate([(100, 100), (1180, 100), (100, 670), (1180, 670)]):
        canvas.create_oval(x - 150, y - 150, x + 150, y + 150, fill=colors[i % 4], outline='', width=0)
    for i in range(5):
        y = 200 + i * 100
        canvas.create_line(0, y, 1280, y, fill='#e0e0e0', width=1, dash=(4, 4))
    canvas.create_text(640, 50, text='🎵MuteSound🎵', font=('Arial', 24, 'bold'), fill='#424242')
    canvas.create_rectangle(930, 20, 1250, 220, fill='white', outline='#bdbdbd', width=2)
    canvas.create_rectangle(50, 550, 800, 700, fill='white', outline='#bdbdbd', width=2, stipple='gray50')
    canvas.create_text(400, 300, text='♫', font=('Arial', 100), fill='#e0e0e0')
    canvas.create_text(900, 400, text='♪', font=('Arial', 80), fill='#f0f0f0')
    canvas.create_rectangle(65, 605, 280, 635, fill='#f8f9fa', outline='#f8f9fa')

create_beautiful_background()

### кнопки караоке ###
karaoke_frame = Frame(root, bg='white', relief=RAISED, borderwidth=2)
karaoke_frame.place(x=300, y=100, width=600, height=350)
karaoke_frame.place_forget()

karaoke_title = Label(karaoke_frame, text="🎤 КАРАОКЕ", font=('Arial', 18, 'bold'), fg='#D32F2F', bg='white')
karaoke_title.pack(pady=10)

karaoke_current = Label(karaoke_frame, text="Выберите песню", font=('Arial', 24, 'bold'), fg='#FF5722', bg='white', height=2)
karaoke_current.pack(pady=10)

karaoke_next = Label(karaoke_frame, text="", font=('Arial', 16), fg='#757575', bg='white')
karaoke_next.pack()

text_frame = Frame(karaoke_frame, bg='white')
text_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

scrollbar = Scrollbar(text_frame)
scrollbar.pack(side=RIGHT, fill=Y)

karaoke_text = Text(text_frame, height=8, width=50, yscrollcommand=scrollbar.set, font=('Arial', 11), bg='#FAFAFA', wrap=WORD)
karaoke_text.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=karaoke_text.yview)

toggle_karaoke_btn = Button(root, text="🎤 Показать караоке", font=('Arial', 12), command=toggle_karaoke, bg='#4CAF50', fg='white', activebackground='#45a049')
toggle_karaoke_btn.place(x=300, y=460)

### бейзовые виджеты ###
status = Label(root, text='Тут будет ваш трек', font=('TimesNewRoman', 16, 'bold'), fg='#ff9800', bg='#f8f9fa')
status.place(x=70, y=610)

volume_scale = Scale(root, from_=100, to_=0, orient=VERTICAL, command=volume, bg='white')
volume_scale.set(70)
volume_scale.place_forget()

volume_icon = Label(root, text='🔊', font=('TimesNewRoman', 20))
volume_icon.place(x=735, y=645)
volume_icon.bind('<Enter>', lambda e: volume_scale.place(x=732, y=545))
volume_scale.bind('<Leave>', lambda e: volume_scale.place_forget())

song_list = Listbox(root, width=52, height=12)
song_list.place(x=932, y=21)
song_list.bind('<<ListboxSelect>>', on_song_select)

try:
    img1 = PhotoImage(file="resume.png").subsample(x=9, y=9)
    img2 = PhotoImage(file="pause.png").subsample(x=9, y=9)
    img3 = PhotoImage(file="left.png").subsample(x=17, y=17)
    img4 = PhotoImage(file="right.png").subsample(x=17, y=17)
    img6 = PhotoImage(file="load.png").subsample(x=30, y=30)
except:
    img1 = img2 = img3 = img4 = img6 = None

if img1:
    btnplay_pause = Button(root, image=img1, command=play_pause)
else:
    btnplay_pause = Button(root, text='▶/⏸', command=play_pause)
btnplay_pause.place(x=600, y=645)

if img6:
    btn_load = Button(root, image=img6, command=load_songs)
else:
    btn_load = Button(root, text='📁', command=load_songs)
btn_load.place(x=70, y=655)

if img3:
    btn_left = Button(root, image=img3, command=left)
else:
    btn_left = Button(root, text='⏮', command=left)
btn_left.place(x=525, y=650)

if img4:
    btn_right = Button(root, image=img4, command=right)
else:
    btn_right = Button(root, text='⏭', command=right)
btn_right.place(x=660, y=650)

status = Label(root, text='Тут будет ваш трек', fg='#8B0000', font=('TimesNewRoman', 16, 'bold'), bg='#e8f5e8')
status.place(x=70, y=610)

seek_bar = Scale(root, from_=0, to=100, orient=HORIZONTAL, command=seek, bg='#e8f5e8')
seek_bar.place_forget()
status.bind('<Enter>', lambda e: seek_bar.place(x=70, y=570))
seek_bar.bind('<Leave>', lambda e: seek_bar.place_forget())

root.after(100, load_songs)
update_karaoke()

def load_first_song():
    if song_list.size() > 0:
        song_list.selection_set(0)
        song_name = song_list.get(0)
        load_lyrics(song_name)

root.after(200, load_first_song)

mainloop() ### енто делал арсений аддьятулин
