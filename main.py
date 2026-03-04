import cv2
import numpy as np
import math

square_size = 300
SATURATION_THRESHOLD = 30  # пиксели с насыщенностью ниже этого считаются "белыми" и игнорируются
IMG_SRC = 'image2.jpg'
DISPLAY_SCALE = 0.25        # коэффициент уменьшения исходного изображения для отображения

# Переменные для сумм H, S, V (только для не-белых)
all_h = 0
all_s = 0
all_v = 0

# Счётчики пикселей в каждой цветовой зоне (не-белые)
count_red = 0
count_green = 0
count_blue = 0

# Для красной зоны используем векторное усреднение
sum_cos_red = 0.0
sum_sin_red = 0.0

# Для зелёной и синей зон — обычная сумма
sum_h_green = 0
sum_h_blue = 0

# Загружаем изображение
img = cv2.imread(IMG_SRC)
if img is None:
    print("Image load failed")
    exit()

# Создаём уменьшенную копию для отображения
display_img = cv2.resize(img, None, fx=DISPLAY_SCALE, fy=DISPLAY_SCALE, interpolation=cv2.INTER_AREA)

# Конвертируем BGR в HSV для анализа
hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

height, width, channels = hsv_img.shape

total_pixels_all = height * width
ignored_pixels = 0  # счётчик отброшенных "белых" пикселей

for i in range(height):
    for j in range(width):
        h = int(hsv_img[i, j, 0])
        s = int(hsv_img[i, j, 1])
        v = int(hsv_img[i, j, 2])

        # Проверяем, является ли пиксель "цветным" (достаточно насыщенным)
        if s < SATURATION_THRESHOLD:
            ignored_pixels += 1
            continue   # пропускаем белые/серые пиксели

        # Общие суммы для средних по всем не-белым пикселям
        all_h += h
        all_s += s
        all_v += v

        # Распределение по диапазонам оттенка
        if (0 <= h < 30) or (150 <= h < 180):      # красная зона
            count_red += 1
            angle = h * 2   # h (0-179) -> угол (0-358)
            rad = math.radians(angle)
            sum_cos_red += math.cos(rad)
            sum_sin_red += math.sin(rad)
        elif 30 <= h < 90:                          # зелёная зона
            count_green += 1
            sum_h_green += h
        elif 90 <= h < 150:                          # синяя зона
            count_blue += 1
            sum_h_blue += h
        # Пиксели с h в других диапазонах не попадают (h всегда 0-179)

total_pixels_used = count_red + count_green + count_blue   # количество учтённых пикселей

if total_pixels_used == 0:
    print("Нет цветных пикселей (все отброшены как белые).")
    # Можно установить средние в 0 и завершить или показать что-то
    avg_h = avg_s = avg_v = 0
    avg_h_red = avg_h_green = avg_h_blue = 0
else:
    # Средние по всем учтённым пикселям
    avg_h = all_h // total_pixels_used
    avg_s = all_s // total_pixels_used
    avg_v = all_v // total_pixels_used

    # Средний оттенок для красной зоны (циклическое усреднение)
    if count_red > 0:
        mean_cos = sum_cos_red / count_red
        mean_sin = sum_sin_red / count_red
        avg_angle_rad = math.atan2(mean_sin, mean_cos)
        avg_angle_deg = math.degrees(avg_angle_rad) % 360
        avg_h_red = int(round(avg_angle_deg / 2))       # обратно в шкалу 0–179
    else:
        avg_h_red = 0   # можно задать другое значение, например, 0

    # Средний оттенок для зелёной зоны
    avg_h_green = (sum_h_green // count_green) if count_green > 0 else 0
    # Средний оттенок для синей зоны
    avg_h_blue = (sum_h_blue // count_blue) if count_blue > 0 else 0


def create_hsv_square(h, s, v):
    square = np.zeros((square_size, square_size, 3), dtype=np.uint8)
    square[:] = (h, s, v)
    return cv2.cvtColor(square, cv2.COLOR_HSV2BGR)

# Квадраты для отображения (используем средние значения)
color_square_avg = create_hsv_square(avg_h, avg_s, avg_v)

# Если в какой-то зоне нет пикселей, квадрат будет с H=0 (красный), что может ввести в заблуждение,
# но мы оставим так, можно потом заменить на серый, если нужно.
color_square_red = create_hsv_square(avg_h_red, 255, 255)
color_square_green = create_hsv_square(avg_h_green, 255, 255)
color_square_blue = create_hsv_square(avg_h_blue, 255, 255)

cv2.imshow('HSV_mix (avg H,S,V)', color_square_avg)
cv2.imshow('Red zone (avg H)', color_square_red)
cv2.imshow('Green zone (avg H)', color_square_green)
cv2.imshow('Blue zone (avg H)', color_square_blue)
cv2.imshow(f"Source image (scaled by {DISPLAY_SCALE})", display_img)   # ← показываем уменьшенную версию

print(f"Всего пикселей: {total_pixels_all}")
print(f"Игнорировано 'белых' пикселей (S < {SATURATION_THRESHOLD}): {ignored_pixels} ({ignored_pixels/total_pixels_all*100:.2f}%)")
print(f"Учтено цветных пикселей: {total_pixels_used} ({total_pixels_used/total_pixels_all*100:.2f}%)")
print(f"Средние значения по цветным пикселям (HSV): (H={avg_h}, S={avg_s}, V={avg_v})")
print(f"Распределение цветных пикселей по зонам H (красный/зелёный/синий):")
if total_pixels_used > 0:
    print(f"  Красный : {count_red} пикс. ({count_red/total_pixels_used*100:.2f}%), средний H={avg_h_red}")
    print(f"  Зелёный : {count_green} пикс. ({count_green/total_pixels_used*100:.2f}%), средний H={avg_h_green}")
    print(f"  Синий   : {count_blue} пикс. ({count_blue/total_pixels_used*100:.2f}%), средний H={avg_h_blue}")
else:
    print("  Нет цветных пикселей для анализа.")

cv2.waitKey(0)
cv2.destroyAllWindows()
