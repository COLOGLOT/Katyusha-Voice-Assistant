import speech_recognition as sr
import pyttsx3
import datetime
import subprocess
import random
import os
import sys
import glob
import webbrowser
import platform
import pygame
import tkinter as tk
from tkinter import ttk, scrolledtext, PhotoImage
from PIL import Image, ImageTk
import threading
import time

# Инициализация speech_recognition
r = sr.Recognizer()

# Инициализация pygame
pygame.mixer.init()

# Папка с MP3 файлами (укажите свой путь)
AUDIO_DIR = "audio"  # Создайте папку "audio" рядом со скриптом и поместите туда MP3 файлы

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Голосовой помощник")
        self.root.geometry("800x600")
        self.root.configure(bg="#308014")
        self.root.resizable(True, True)
        
        # Устанавливаем иконку приложения
        try:
            self.root.iconbitmap("icon.ico")  # Замените на путь к вашей иконке
        except:
            pass
        
        # Создаем стиль
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#308014")
        self.style.configure("TButton", 
                            background="#3498DB", 
                            foreground="#FFFFFF", 
                            font=("Arial", 12, "bold"),
                            padding=10)
        self.style.map("TButton", 
                      background=[("active", "#2980B9"), ("pressed", "#1F618D")])
        self.style.configure("TLabel", 
                            background="#308014", 
                            foreground="#ECF0F1", 
                            font=("Arial", 12))
        
        # Создаем основной фрейм
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        self.title_label = ttk.Label(self.main_frame, 
                                    text="Голосовой помощник Катюша", 
                                    font=("Arial", 24, "bold"),
                                    foreground="#ECF0F1")
        self.title_label.pack(pady=10)
        
        # Изображение помощника
        try:
            self.assistant_image = Image.open("assistant.png")  # Замените на путь к вашему изображению
            self.assistant_image = self.assistant_image.resize((200, 200), Image.LANCZOS)
            self.assistant_photo = ImageTk.PhotoImage(self.assistant_image)
            self.image_label = ttk.Label(self.main_frame, image=self.assistant_photo, background="#2C3E50")
            self.image_label.pack(pady=10)
        except:
            # Если изображение не найдено, создаем заглушку
            self.image_frame = ttk.Frame(self.main_frame, width=150, height=150)
            self.image_frame.pack(pady=10)
        
        # Текстовое поле для вывода сообщений
        self.text_frame = ttk.Frame(self.main_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.text_area = scrolledtext.ScrolledText(self.text_frame, 
                                                 wrap=tk.WORD, 
                                                 width=60, 
                                                 height=10, 
                                                 font=("Arial", 11),
                                                 bg="#34495E",
                                                 fg="#ECF0F1")
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)
        
        # Статус распознавания
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        self.status_label = ttk.Label(self.main_frame, 
                                     textvariable=self.status_var,
                                     font=("Arial", 10, "italic"),
                                     foreground="#BDC3C7")
        self.status_label.pack(pady=5)
        
        # Кнопки управления
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        self.listen_button = ttk.Button(self.button_frame, 
                                       text="Слушать", 
                                       command=self.start_listening)
        self.listen_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.stop_button = ttk.Button(self.button_frame, 
                                     text="Стоп", 
                                     command=self.stop_assistant)
        self.stop_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.help_button = ttk.Button(self.button_frame, 
                                     text="Команды", 
                                     command=self.show_help)
        self.help_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Инициализация переменных
        self.listening = False
        self.listen_thread = None
        
        # Добавляем приветствие
        self.update_text("Голосовой помощник Катюша запущен. Нажмите 'Слушать' для начала работы.")
    
    def update_text(self, message):
        """Обновляет текстовое поле с сообщениями"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, f"{message}\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
    
    def start_listening(self):
        """Запускает процесс прослушивания в отдельном потоке"""
        if not self.listening:
            self.listening = True
            self.status_var.set("Слушаю...")
            self.listen_button.config(state=tk.DISABLED)
            self.listen_thread = threading.Thread(target=self.listen_commands)
            self.listen_thread.daemon = True
            self.listen_thread.start()
    
    def stop_assistant(self):
        """Останавливает помощника"""
        self.listening = False
        self.status_var.set("Остановлен")
        self.listen_button.config(state=tk.NORMAL)
        self.update_text("Помощник остановлен.")
    
    def show_help(self):
        """Показывает справку по командам"""
        help_text = """
        Доступные команды:
        - "расскажи анекдот" или "рассмеши меня" - рассказать анекдот
        - "открой диспетчер задач" - открыть диспетчер задач
        - "закрой диспетчер задач" - закрыть диспетчер задач
        - "включи [название песни]" - воспроизвести музыку
        - "открой ворд" - открыть Microsoft Word
        - "открой погоду" - открыть прогноз погоды
        - "закрой Microsoft" - закрыть Microsoft
        - "открой цоя" или "найти группу на рукаве" - найти музыку Цоя
        - "выход", "пока" или "до свидания" - завершить работу
        """
        self.update_text(help_text)
    
    def listen_commands(self):
        """Слушает команды пользователя и обрабатывает их"""
        play_audio("hello.mp3")
        self.update_text("Привет! Я ваш голосовой помощник Катюша. Что вы хотите?")
        
        while self.listening:
            command = self.listen()
            if not command or not self.listening:
                continue
                
            self.update_text(f"Вы сказали: {command}")
            
            if "сколько времени" in command or "который час" in command:
                self.tell_time()
            elif "расскажи анекдот" in command or "рассмеши меня" in command:
                self.tell_joke()
            elif "открой диспетчер задач" in command or "открыть диспетчер задач" in command:
                self.open_task_manager()
            elif "закрой диспетчер задач" in command or "закрыть диспетчер задач" in command:
                self.close_task_manager()
            elif "включи" in command:
                song_name = command.replace("включи", "").strip()
                if song_name:
                    self.play_music(song_name)
                else:
                    play_audio("which_song.mp3")
                    self.update_text("Какую песню вы хотите включить?")
            elif "открой ворд" in command or "открыть ворд" in command:
                self.open_word_2007()
            elif "открой погоду" in command or "покажи погоду" in command:
                self.open_yandex_weather()
            elif "закрой Microsoft" in command or "закрыть Microsoft" in command or "закрой microsoft " in command or "закрыть microsoft " in command:
                self.close_microsoft_edge()
            elif "открой цоя" in command or "найти цоя" in command or "открой группу на рукаве" in command or "найти группу на рукаве" in command:
                self.open_microsoft_edge_and_search_music("цой группа на рукаве")
            elif "выход" in command or "завершить работу" in command or "пока" in command or "до свидания" in command:
                play_audio("goodbye.mp3")
                self.update_text("До свидания! Было приятно пообщаться.")
                self.stop_assistant()
                break
            elif command:  # Если была распознана команда, но она не обработана
                play_audio("unknown_command.mp3")
                self.update_text("Я не знаю, как это сделать. Попробуйте другую команду.")
        
        self.status_var.set("Готов к работе")
        self.listen_button.config(state=tk.NORMAL)
    
    def listen(self):
        """Слушает команды пользователя и возвращает текст."""
        try:
            with sr.Microphone() as source:
                self.status_var.set("Слушаю...")
                self.update_text("Слушаю...")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
    
            try:
                command = r.recognize_google(audio, language="ru-RU").lower()
                return command
            except sr.UnknownValueError:
                self.update_text("Я не поняла, что вы сказали.")
                return ""
            except sr.RequestError as e:
                self.update_text(f"Не удалось получить результаты от сервиса распознавания речи; {e}")
                return ""
        except Exception as e:
            self.update_text(f"Ошибка при прослушивании: {e}")
            return ""
    
    # Далее идут методы для выполнения команд
    def tell_time(self):
        now = datetime.datetime.now()
        self.update_text(f"Сейчас {now.hour}:{now.minute:02}")
        play_audio("time_is.mp3")
    
    def tell_joke(self):
        jokes = [
            "Что такое искусственный интеллект? Это когда компьютер делает ошибки с большей уверенностью, чем люди.",
        ]
        self.update_text(random.choice(jokes))
        play_audio("joke.mp3")
    
    def open_task_manager(self):
        try:
            subprocess.Popen(['taskmgr.exe'])
            self.update_text("Открываю диспетчер задач.")
            play_audio("opening_task_manager.mp3")
        except FileNotFoundError:
            self.update_text("Я не могу найти диспетчер задач.")
            play_audio("task_manager_not_found.mp3")
        except Exception as e:
            self.update_text(f"Произошла ошибка при открытии диспетчера задач: {e}")
            play_audio("task_manager_error.mp3")
    
    def close_task_manager(self):
        try:
            subprocess.Popen(['taskkill', '/IM', 'taskmgr.exe', '/F'])
            self.update_text("Закрываю диспетчер задач.")
            play_audio("closing_task_manager.mp3")
        except Exception as e:
            self.update_text(f"Произошла ошибка при закрытии диспетчера задач: {e}")
            play_audio("task_manager_error1.mp3")
    
    def play_music(self, song_name):
        music_dir = os.path.expanduser("D:\ДИМА ШКОЛА\Рабочий стол\музыка быстрого доступа")
        try:
            song_path = find_song(song_name, music_dir)
            if song_path:
                try:
                    os.startfile(song_path)
                    self.update_text(f"Включаю {song_name}.")
                    play_audio("playing.mp3")
                except Exception as e:
                    self.update_text(f"Не удалось открыть файл: {e}")
                    play_audio("file_error.mp3")
            else:
                self.update_text(f"Не могу найти песню {song_name}.")
                play_audio("song_not_found.mp3")
        except FileNotFoundError:
            self.update_text("Не найдена папка с музыкой.")
            play_audio("music_folder_not_found.mp3")
        except Exception as e:
            self.update_text(f"Произошла общая ошибка: {e}")
            play_audio("general_error.mp3")
    
    def open_word_2007(self):
        try:
            word_path = r"C:\Program Files (x86)\Microsoft Office\Office12\WINWORD.EXE"
            subprocess.Popen([word_path])
            self.update_text("Открываю Microsoft Office Word 2007.")
            play_audio("opening_word.mp3")
        except FileNotFoundError:
            self.update_text("Не могу найти Microsoft Office Word 2007. Убедитесь, что он установлен и путь указан верно.")
            play_audio("word_not_found.mp3")
        except Exception as e:
            self.update_text(f"Произошла ошибка при открытии Microsoft Office Word 2007: {e}")
            play_audio("general_error.mp3")
    
    def open_yandex_weather(self):
        url = "https://yandex.ru/pogoda/urga?lat=55.713557&lon=84.933869"
        try:
            webbrowser.open_new_tab(url)
            self.update_text("Открываю погоду в Яндекс.")
            play_audio("opening_weather.mp3")
        except Exception as e:
            self.update_text(f"Произошла ошибка при открытии ссылки: {e}")
            play_audio("link_error.mp3")
    
    def close_microsoft_edge(self):
        try:
            subprocess.Popen(['taskkill', '/IM', 'msedge.exe', '/F'])
            self.update_text("Закрываю Microsoft Edge.")
            play_audio("closing_edge.mp3")
        except Exception as e:
            self.update_text(f"Произошла ошибка при закрытии Microsoft Edge: {e}")
            play_audio("edge_error.mp3")
    
    def open_microsoft_edge_and_search_music(self, music_query):
        try:
            search_url = f"https://yandex.ru/search/?text={music_query}"
            system = platform.system()
            
            if system == "Windows":
                edge_path = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
                subprocess.Popen([edge_path, search_url])
            elif system == "Darwin":  # macOS
                subprocess.Popen(['open', '-a', 'Microsoft Edge', search_url])
            elif system == "Linux":
                subprocess.Popen(['microsoft-edge', search_url])
            
            self.update_text(f"Открываю Microsoft Edge и ищу {music_query}.")
            play_audio("opening_edge_searching.mp3")
            
            # Ждем немного, чтобы Edge успел загрузить результаты поиска
            time.sleep(5)
            
            import requests
            from bs4 import BeautifulSoup
            
            try:
                response = requests.get(search_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                first_result = soup.find('li', class_='serp-item')
                if first_result:
                    link = first_result.find('a')
                    if link:
                        first_url = link['href']
                        webbrowser.open_new_tab(first_url)
                        self.update_text("Открываю первый сайт из результатов поиска.")
                        play_audio("opening_first_site.mp3")
                    else:
                        self.update_text("Не удалось найти ссылку на первом сайте.")
                        play_audio("cant_find_link.mp3")
                else:
                    self.update_text("Не удалось найти первый результат поиска.")
                    play_audio("cant_find_result.mp3")
            except requests.exceptions.RequestException as e:
                self.update_text(f"Ошибка при получении результатов поиска: {e}")
                play_audio("search_error.mp3")
            except Exception as e:
                self.update_text(f"Произошла ошибка: {e}")
                play_audio("cant_open_first_site.mp3")
        except FileNotFoundError:
            self.update_text("Не могу найти Microsoft Edge.")
            play_audio("edge_not_found.mp3")
        except Exception as e:
            self.update_text(f"Произошла ошибка при открытии Microsoft Edge и поиске музыки: {e}")
            play_audio("general_error1.mp3")


def play_audio(filename):
    """Воспроизводит MP3 файл."""
    try:
        filepath = os.path.join(AUDIO_DIR, filename)
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # Ждем окончания воспроизведения
            pygame.time.Clock().tick(10)
    except FileNotFoundError:
        print(f"Файл {filename} не найден!")
    except pygame.error as e:
        print(f"Ошибка воспроизведения: {e}")


def find_song(song_name, music_dir):
    """Ищет музыкальный файл, игнорируя регистр и расширение."""
    pattern = os.path.join(music_dir, f"*{song_name}*.*")
    files = glob.glob(pattern)
    if files:
        return files[0]
    else:
        return None


def main():
    """Основная функция запуска приложения."""
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
