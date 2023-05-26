import tkinter as tk
import vk_api
import random
import threading
import time



class StatusUpdater:
    def __init__(self, access_token, console, status, interval=10):
        self.access_token = access_token
        self.console = console
        self.status = status
        self.interval = interval  # изменяем interval на количество секунд
        self.stop_flag = False

    def start(self):
        # Создаем объект VK
        vk_session = vk_api.VkApi(token=self.access_token)
        vk = vk_session.get_api()

        # Проверяем корректность токена
        try:
            vk.users.get(user_ids=1)
            self.status.set("Токен проверен и верен!")
        except vk_api.exceptions.ApiError:
            self.status.set("Неправильный токен")
            return

        # Бесконечный цикл для обновления статуса каждые self.interval секунд
        while True:
            self.update_status(vk)
            time.sleep(self.interval)

            # Проверяем флаг остановки цикла
            if self.stop_flag:
                break

        # Сбрасываем флаги
        self.stop_flag = False

    def stop(self):
        # Устанавливаем флаг остановки цикла
        self.stop_flag = True

    def update_status(self, vk):
        # Создаем список случайных смайликов
        smileys = ['😊', '😄', '😋', '😚', '😍', '😻', '🥰', '😎', '😇', '🤩', '🤔', '😴', '😜', '🤯', '😇', '😉', '🤤', '🙃', '👀', '👍', '👌', '🤙', '🤘', '🥳', '😳', '💩', '🤷‍♂️', '🤷‍♀️', '🙈']

        # Выбираем случайный смайлик из списка и обновляем статус
        random_smiley = random.choice(smileys)
        old_status = vk.status.get()['text']
        vk.status.set(text=random_smiley)
        new_status = vk.status.get()['text']
        self.console.insert(tk.END, f'Status updated: {old_status} -> {new_status}\n')

    def delete_status(self, vk):
        vk.status.set()

    def set_interval(self, interval):
        self.interval = interval


# ... Остальной код

def start_cycle():
    # Получаем access token и интервал цикла в секундах
    access_token = token_entry.get().strip()
    interval = int(interval_entry.get().strip())

    # Создаем объект StatusUpdater и запускаем в новом потоке
    global status_updater  # сохраняем ссылку на объект в глобальной переменной
    status_updater = StatusUpdater(access_token, console, status, interval)
    thread = threading.Thread(target=status_updater.start)
    thread.daemon = True
    thread.start()

def stop_cycle():
    # Останавливаем цикл
    if status_updater:
        status_updater.stop()
        console.insert(tk.END, 'Цикл остановлен\n')

def delete_status():
    # Получаем access token
    access_token = token_entry.get().strip()

    # Создаем объект VK
    vk_session = vk_api.VkApi(token=access_token)
    vk = vk_session.get_api()

    # Удаляем статус
    vk.status.set()

    # Выводим сообщение в консоль
    console.insert(tk.END, 'Статус удален\n')

def set_cycle_interval():
    # Создаем диалоговое окно для ввода интервала цикла в секундах
    dialog = CycleIntervalDialog(root)
    interval = dialog.show()

    # Устанавливаем новый интервал для объекта StatusUpdater
    if status_updater and interval is not None:
        status_updater.set_interval(interval)
        console.insert(tk.END, f'Интервал цикла установлен на {interval} секунд\n')

class CycleIntervalDialog:
    def __init__(self, parent):
        self.parent = parent
        self.top = tk.Toplevel(parent)
        self.top.title('Настройка цикла')
        self.top.geometry("200x100")
        self.top.transient(parent)
        self.top.grab_set()

        self.label = tk.Label(self.top, text='Интервал цикла (секунды):')  # изменяем label
        self.label.pack(padx=10, pady=10)

        self.entry = tk.Entry(self.top, width=10)
        self.entry.pack(padx=10, pady=5)

        self.unit_label = tk.Label(self.top, text='sec')  # добавляем unit_label
        self.unit_label.pack(padx=10, pady=5)

        self.ok_button = tk.Button(self.top, text='OK', command=self.ok)
        self.ok_button.pack(padx=10, pady=5)

    def ok(self):
        try:
            interval = int(self.entry.get())
            self.top.destroy()
            self.result = interval
        except ValueError:
            self.label.config(text='Неправильный формат числа')

    def show(self):
        self.result = None
        self.parent.wait_window(self.top)
        return self.result

# Создаем графическое окно
root = tk.Tk()
root.title('Смена статуса VK')
root.geometry("500x500")

# Создаем элементы интерфейса
token_label = tk.Label(root, text='Введите access token:')
token_entry = tk.Entry(root, width=50)
interval_label = tk.Label(root, text='Интервал цикла (секунды):')
interval_entry = tk.Entry(root, width=10)
start_button = tk.Button(root, text='Начать цикл', command=start_cycle)
stop_button = tk.Button(root, text='Остановить цикл', command=stop_cycle)
delete_button = tk.Button(root, text='Удалить статус', command=delete_status)
set_interval_button = tk.Button(root, text='Настроить цикл', command=set_cycle_interval)
status = tk.StringVar()
status.set("Введите токен и интервал цикла и нажмите 'Начать цикл'")  # добавляем интервал цикла
status_label = tk.Label(root, textvariable=status)

# Создаем консольный виджет
console_label = tk.Label(root, text='Консоль:')
console = tk.Text(root, width=50, height=10)

# Размещаем элементы интерфейса
token_label.grid(row=0, column=0, padx=10, pady=10)
token_entry.grid(row=0, column=1, padx=10, pady=10)
interval_label.grid(row=1, column=0, padx=10, pady=10)
interval_entry.grid(row=1, column=1, padx=10, pady=10)
start_button.grid(row=2, column=0, padx=10, pady=10)
stop_button.grid(row=2, column=1, padx=10, pady=10)
delete_button.grid(row=3, column=0, padx=10, pady=10)
set_interval_button.grid(row=3, column=1, padx=10, pady=10)
status_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
console_label.grid(row=5, column=0, padx=10, pady=10)
console.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Инициализируем переменную status_updater
status_updater = None

# Запускаем цикл обработки событий
root.mainloop() 