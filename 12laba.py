import tkinter as tk
import os
from PIL import Image, ImageTk  # Импортируем необходимые модули из Pillow
import Traffics as tr

# Создаем главное окно приложения
root = tk.Tk()

# * Измените размер окна здесь *
root.geometry("600x700")  # Размер окна: ширина x высота
root.title("Симулятор светофора")

# Добавляем место для фото
photo_frame = tk.Frame(root, height=200, width=300)  # Область, где будет фотография
photo_frame.pack(pady=10)

label_photo = tk.Label(photo_frame)
label_photo.pack()

def DrawImage(img: str):
    global label_photo
    # Загружаем и добавляем фотографию через Pillow
    try:
        # Открываем изображение через PIL
        image_path = img
        image = Image.open(image_path)  # Загружаем изображение
        # Изменяем размер изображения под область (используем Resampling вместо ANTIALIAS)
        image = image.resize((450, 450), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)  # Конвертируем для использования в tkinter

        # Создаем виджет для отображения изображения
        label_photo.configure(image = photo)
        label_photo.image = photo  # Сохраняем ссылку на изображение, чтобы его не удалил сборщик мусора
    except Exception as e:
        print(f"Ошибка при загрузке изображения: {e}")

# Кнопка для дополнительного действия
def additional_action():
    traffic_ctrl.ChangeState([0, 1])

extra_button = tk.Button(root, text="Переключить сигнал", command=additional_action)
extra_button.pack(pady=10)

# Поле для ввода 1
entry1_label = tk.Label(root, text="Задержка красного сигнала (в сек.):")
entry1_label.pack()
entry1 = tk.Entry(root, width=30)
entry1.pack(pady=5)

# Поле для ввода 2
entry2_label = tk.Label(root, text="Задержка зеленого сигнала (в сек.):")
entry2_label.pack()
entry2 = tk.Entry(root, width=30)
entry2.pack(pady=5)

counter = tk.Label(root, text = "0", bg="gray", fg="white")

traffic_light_dr = tr.TraficLight(0, 0, 0)
traffic_light_wlk = tr.WalkTrafficLight(0, 0, 2)
traffic_ctrl = tr.TrafficCtrl([])

def UpdImage():
    dr_st = traffic_ctrl.GetState(0)
    wl_st = traffic_ctrl.GetState(1)

    if (dr_st == 0) and (wl_st == 2): DrawImage("DgWr.jpg")
    elif (dr_st == 2) and (wl_st == 0): DrawImage("DrWg.jpg")
    elif (dr_st == 1) and (wl_st == 0): DrawImage("DyWr.jpg")

def UpdText():
    t = 3 if traffic_ctrl.GetState(0) == 2 else 0
    counter.config(text=str(traffic_ctrl.GetWaitTime(0) + t))

# Кнопка подтверждения
def confirm_action():
    global traffic_light_dr
    global traffic_light_wlk
    global traffic_ctrl

    value1 = int(entry1.get())
    value2 = int(entry2.get())

    print(f"Значение из поля 1: {value1}")
    print(f"Значение из поля 2: {value2}")

    traffic_ctrl.Cancel()

    traffic_light_dr.SetRedTime(value1)
    traffic_light_dr.SetGreenTime(value2)
    traffic_light_wlk.SetRedTime(value2)
    traffic_light_wlk.SetGreenTime(value1)

    traffic_ctrl = tr.TrafficCtrl([traffic_light_dr, traffic_light_wlk])
    traffic_ctrl.AddEvent(tr.state_change, traffic_light_dr.ind, UpdImage)
    traffic_ctrl.AddEvent(tr.time_change, traffic_light_dr.ind, UpdText)
    traffic_ctrl.Start([0, 1])

    UpdImage()


confirm_button = tk.Button(root, text="Подтвердить", command=confirm_action)
confirm_button.pack(pady=10)

DrawImage('DrWg.jpg')
counter.place(x=459, y=57)

# Запуск основного цикла приложения
root.mainloop()