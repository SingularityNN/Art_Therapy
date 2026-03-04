import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb

square_size = 300
SATURATION_THRESHOLD = 30  # пиксели с насыщенностью ниже этого считаются "белыми" и игнорируются
IMG_SRC = 'art/art_zaitseva_38f_1.jpeg'
DISPLAY_SCALE = 0.5        # коэффициент уменьшения исходного изображения для отображения

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
        avg_h_red = 0

    # Средний оттенок для зелёной зоны
    avg_h_green = (sum_h_green // count_green) if count_green > 0 else 0
    # Средний оттенок для синей зоны
    avg_h_blue = (sum_h_blue // count_blue) if count_blue > 0 else 0

def create_hsv_square(h, s, v):
    square = np.zeros((square_size, square_size, 3), dtype=np.uint8)
    square[:] = (h, s, v)
    return cv2.cvtColor(square, cv2.COLOR_HSV2BGR)

# Квадрат со средними H,S,V всего изображения (BGR)
color_square_avg_bgr = create_hsv_square(avg_h, avg_s, avg_v)
# Конвертируем в RGB для отображения в matplotlib
color_square_avg_rgb = cv2.cvtColor(color_square_avg_bgr, cv2.COLOR_BGR2RGB)

# Подготовка исходного изображения для matplotlib (BGR -> RGB)
display_img_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)

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

# --- Построение комбинированного окна matplotlib ---
if total_pixels_used > 0:
    # Формируем текстовую статистику
    stats_text = f"Всего пикселей: {total_pixels_all}\n"
    stats_text += f"Игнорировано 'белых' пикселей (S < {SATURATION_THRESHOLD}): {ignored_pixels} ({ignored_pixels/total_pixels_all*100:.2f}%)\n"
    stats_text += f"Учтено цветных пикселей: {total_pixels_used} ({total_pixels_used/total_pixels_all*100:.2f}%)\n"
    stats_text += f"Средние значения по цветным пикселям (HSV): (H={avg_h}, S={avg_s}, V={avg_v})\n"
    stats_text += f"Распределение цветных пикселей по зонам H (красный/зелёный/синий):\n"
    if count_red > 0:
        stats_text += f"  Красный : {count_red} пикс. ({count_red/total_pixels_used*100:.2f}%), средний H={avg_h_red}\n"
    else:
        stats_text += f"  Красный : 0 пикс. (0.00%)\n"
    if count_green > 0:
        stats_text += f"  Зелёный : {count_green} пикс. ({count_green/total_pixels_used*100:.2f}%), средний H={avg_h_green}\n"
    else:
        stats_text += f"  Зелёный : 0 пикс. (0.00%)\n"
    if count_blue > 0:
        stats_text += f"  Синий   : {count_blue} пикс. ({count_blue/total_pixels_used*100:.2f}%), средний H={avg_h_blue}\n"
    else:
        stats_text += f"  Синий   : 0 пикс. (0.00%)\n"

    # Собираем данные для зон, в которых есть пиксели (для гистограммы)
    zone_names = []
    percentages = []
    bar_colors = []

    if count_red > 0:
        zone_names.append('Red')
        percentages.append(count_red / total_pixels_used * 100)
        h_norm = avg_h_red / 179.0
        bar_colors.append(hsv_to_rgb([h_norm, 1.0, 1.0]))

    if count_green > 0:
        zone_names.append('Green')
        percentages.append(count_green / total_pixels_used * 100)
        h_norm = avg_h_green / 179.0
        bar_colors.append(hsv_to_rgb([h_norm, 1.0, 1.0]))

    if count_blue > 0:
        zone_names.append('Blue')
        percentages.append(count_blue / total_pixels_used * 100)
        h_norm = avg_h_blue / 179.0
        bar_colors.append(hsv_to_rgb([h_norm, 1.0, 1.0]))

    # Создаём фигуру 2×2
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.canvas.manager.set_window_title('Анализ рисунка')

    # 1. Исходное изображение (верхний левый)
    axes[0, 0].imshow(display_img_rgb)
    axes[0, 0].set_title('Source Image (scaled)')
    axes[0, 0].axis('off')

    # 2. Квадрат среднего цвета (верхний правый)
    axes[0, 1].imshow(color_square_avg_rgb)
    axes[0, 1].set_title(f'Avg Color (H={avg_h}, S={avg_s}, V={avg_v})')
    axes[0, 1].axis('off')

    # 3. Гистограмма (нижний левый)
    if zone_names:
        bars = axes[1, 0].bar(zone_names, percentages, color=bar_colors, edgecolor='black')
        axes[1, 0].set_ylabel('Процент цветных пикселей')
        axes[1, 0].set_title('Распределение по зонам оттенка')
        axes[1, 0].set_ylim(0, 100)
        axes[1, 0].grid(axis='y', linestyle='--', alpha=0.7)
        for bar, p in zip(bars, percentages):
            height = bar.get_height()
            axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + 1,
                            f'{p:.1f}%', ha='center', va='bottom', fontsize=9)
    else:
        axes[1, 0].text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=axes[1, 0].transAxes)
        axes[1, 0].set_title('Распределение по зонам оттенка')
        axes[1, 0].axis('off')

    # 4. Текстовая статистика (нижний правый)
    axes[1, 1].axis('off')
    axes[1, 1].text(0.05, 0.95, stats_text, transform=axes[1, 1].transAxes,
                    fontsize=10, verticalalignment='top', family='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.show()
else:
    print("Недостаточно данных для построения визуализации.")