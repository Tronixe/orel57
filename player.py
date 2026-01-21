from tkinter import *
import pygame
import os
from tkinter import ttk

pygame.mixer.init()
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # чтобы открывало картинки с кнопками на вс коде

# для работы кнопок паузы стоп плей
playing = False
paused = False
volume_visible = False
seeking = False
current_song_name = None
current_song_path = None  # запоминает какой трек играет
song_duration = 0


###получение длительности песни
def song_duration_get(song_path):
    try:
        sound = pygame.mixer.Sound(song_path)
        return sound.get_length()
    except:
        return 0


# автоматическая загрузка треков
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
            status.config(text=f'Загружено песен: {len(mp3_files)}. Выберите песню.', fg='blue')
    else:
        status.config(text='В папке нет MP3 файлов', fg='red')


###перемотка скрол баром
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
            min = int(start_time // 60)
            sec = int(start_time % 60)
            min_total = int(song_duration // 60)
            sec_total = int(song_duration % 60)
            status.config(text=f'⏩{min}:{sec:02d} / {min_total}:{sec_total:02d}', fg='blue')
        except Exception as e:
            status.config(text='❌ Ошибка перемотки', fg='red')
        seeking = False

        if playing and not paused:
            selected = song_list.curselection()
            if selected:
                song_name = song_list.get(selected[0])
                root.after(2000, lambda: status.config(text=f'▶ {song_name}', fg='green'))


###звук, полоску
def volume(value):
    volume_level = int(value) / 100
    pygame.mixer.music.set_volume(volume_level)


### функция для кнопок скипа
def start():
    global playing, paused, current_song_path
    selected = song_list.curselection()
    if not selected:
        return
    song_name = song_list.get(selected[0])
    song_path = os.path.join(music_folder, song_name)
    try:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        playing = True
        paused = False
        current_song_path = song_path
        status.config(text=f'▶ {song_name}', fg='green')
        btnplay_pause.config(image=img2)
    except:
        status.config(text='Ошибка', fg='red')

    ##вправо скип


def right():
    if song_list.size() > 0:  # количество песен в папке
        number_song = song_list.curselection()
        if number_song:
            index_before = (number_song[0] + 1) % song_list.size()
            song_list.selection_clear(0, END)  # убирает выделения в списке и выделяют предыдущий трек
            song_list.selection_set(index_before)  #
            song_list.see(index_before)
            start()


###влево скип
def left():
    if song_list.size() > 0:  # количество песен в папке
        number_song = song_list.curselection()
        if number_song:
            index_before = (number_song[0] - 1) % song_list.size()
            song_list.selection_clear(0, END)  # убирает выделения в списке и выделяют предыдущий трек
            song_list.selection_set(index_before)  #
            song_list.see(index_before)  #
            start()


###плей/пауз кнопка
def play_pause():
    global playing, paused, current_song_path, current_song_name, song_duration
    selected = song_list.curselection()
    if not selected:
        return
    song_name = song_list.get(selected[0])
    song_path = os.path.join(music_folder, song_name)
    new_song = (song_path != current_song_path)
    if new_song or (not playing and not paused):  # надо воспроизвести 1 раз с самого начала
        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            playing = True
            paused = False
            current_song_path = song_path
            current_song_name = song_name
            song_duration = song_duration_get(song_path)
            seek_bar.set(0)
            status.config(text=f'▶ {song_name}', fg='green')
            btnplay_pause.config(image=img2)
        except:
            pass
    elif playing and not paused and not new_song:  # нужно поставить на паузу
        pygame.mixer.music.pause()
        paused = True
        btnplay_pause.config(image=img1)
    elif paused and playing and not new_song:  # на паузу надо продолжить
        pygame.mixer.music.unpause()
        paused = False
        btnplay_pause.config(image=img2)


###загрузка песен###
music_folder = "music"


def load_songs():
    song_list.delete(0, END)
    for file in os.listdir(music_folder):
        if file.endswith('.mp3'):
            song_list.insert(END, file)


root = Tk()
root.title('орловский плеер')
root.geometry('1280x770')




#### фон фон фон фонофнф
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
    ####текст
    canvas.create_text(640, 50, text='🎵Mutesound🎵 ',
                       font=('Arial', 24, 'bold'),
                       fill='#424242')

    ####прямоугольник для треков
    canvas.create_rectangle(930, 20, 1250, 220,
                            fill='white',
                            outline='#bdbdbd',
                            width=2)

    # прямоугольник для кнопок
    canvas.create_rectangle(50, 550, 800, 700,
                            fill='white',
                            outline='#bdbdbd',
                            width=2,
                            stipple='gray50')
    canvas.create_text(400, 300, text='♫', font=('Arial', 100), fill='#e0e0e0')
    canvas.create_text(900, 400, text='♪', font=('Arial', 80), fill='#f0f0f0')
    canvas.create_rectangle(65, 605, 280, 635,
                            fill='#f8f9fa',
                            outline='#f8f9fa')
    canvas.create_text(70, 610,
                       text='Тут будет ваш трек',
                       font=('TimesNewRoman', 16, 'bold'),
                       fill='#ff9800',
                       anchor='nw')


create_beautiful_background()
status = Label(root,
               text='Тут будет ваш трек',
               font=('TimesNewRoman', 16, 'bold'),
               fg='#ff9800',
               bg='#f8f9fa')  # тот же цвет что у фона

status.place(x=70, y=610)


###ползунок громкости + все для громкости
volume_scale = Scale(root, from_=100, to_=0, orient=VERTICAL, command=volume, bg = 'white' )
volume_scale.set(70)
volume_scale.place_forget()  # cкрыт изначально

volume_icon = Label(root, text='🔊', font=('TimesNewRoman', 20))
volume_icon.place(x=735, y=645)
volume_icon.bind('<Enter>', lambda e: volume_scale.place(x=732, y=545))
volume_scale.bind('<Leave>', lambda e: volume_scale.place_forget())

###выбор треков###
song_list = Listbox(root,width=52,height=12)
song_list.place(x=932,y=21)

###КНОПКИ###
img1 = PhotoImage(file="resume.png").subsample(x=9, y=9)
img2 = PhotoImage(file="pause.png").subsample(x=9, y=9)
img3 = PhotoImage(file="left.png").subsample(x=17, y=17)
img4 = PhotoImage(file="right.png").subsample(x=17, y=17)
img5 = PhotoImage(file="stop.png").subsample(x=30, y=30)
img6 = PhotoImage(file="load.png").subsample(x=30, y=30)
btnplay_pause = Button(root, image=img1, command=play_pause)
btnplay_pause.place(x=600, y=645)
btn_load = Button(root, image=img6, command=load_songs)
btn_load.place(x=70, y=655)
btn_left = Button(root, image=img3, command=left)
btn_left.place(x=525, y=650)
btn_right = Button(root, image=img4, command=right)
btn_right.place(x=660, y=650)

###орловские лейблы
status = Label(root, text='Тут будет ваш трек', fg='#8B0000', font=('TimesNewRoman', 16, 'bold'), bg = '#e8f5e8')
status.place(x=70, y=610)

###перемотка трека
seek_bar = Scale(root, from_=0, to=100, orient=HORIZONTAL, command=seek, bg = '#e8f5e8')
seek_bar.place_forget()
status.bind('<Enter>', lambda e: seek_bar.place(x=70, y=570))
seek_bar.bind('<Leave>', lambda e: seek_bar.place_forget())




root.after(100, load_songs)



mainloop()

