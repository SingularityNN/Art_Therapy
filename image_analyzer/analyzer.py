import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import io
import base64

from . import config

def analyze_image(image_path):
    """
    Анализирует изображение и возвращает результаты.

    Параметры:
        image_path (str): путь к файлу изображения.

    Возвращает:
        dict: словарь с результатами:
            - 'avg_hsv': (h, s, v) средние значения по цветным пикселям.
            - 'stats_text': текстовая статистика.
            - 'distribution': список зон (Red, Green, Blue) с процентами и средними оттенками.
            - 'source_image_base64': исходное уменьшенное изображение в формате base64.
            - 'color_square_base64': квадрат среднего цвета в формате base64.
            - 'plot_base64': гистограмма распределения в формате base64.
            - 'error': сообщение об ошибке (если есть).
    """
    # Загружаем изображение
    img = cv2.imread(image_path)
    if img is None:
        return {'error': 'Не удалось загрузить изображение'}

    # Создаём уменьшенную копию для отображения
    display_img = cv2.resize(img, None, fx=config.DISPLAY_SCALE, fy=config.DISPLAY_SCALE,
                             interpolation=cv2.INTER_AREA)

    # Конвертируем BGR в HSV для анализа
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    height, width, channels = hsv_img.shape
    total_pixels_all = height * width
    ignored_pixels = 0

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

    for i in range(height):
        for j in range(width):
            h = int(hsv_img[i, j, 0])
            s = int(hsv_img[i, j, 1])
            v = int(hsv_img[i, j, 2])

            # Проверяем, является ли пиксель "цветным" (достаточно насыщенным)
            if s < config.SATURATION_THRESHOLD:
                ignored_pixels += 1
                continue

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

    total_pixels_used = count_red + count_green + count_blue

    if total_pixels_used == 0:
        return {'error': 'Нет цветных пикселей (все отброшены как белые)'}

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

    # Формируем текстовую статистику
    stats_text = (
        f"Всего пикселей: {total_pixels_all}\n"
        f"Игнорировано 'белых' пикселей (S < {config.SATURATION_THRESHOLD}): {ignored_pixels} "
        f"({ignored_pixels/total_pixels_all*100:.2f}%)\n"
        f"Учтено цветных пикселей: {total_pixels_used} ({total_pixels_used/total_pixels_all*100:.2f}%)\n"
        f"Средние значения по цветным пикселям (HSV): (H={avg_h}, S={avg_s}, V={avg_v})\n"
        f"Распределение цветных пикселей по зонам H (красный/зелёный/синий):\n"
    )
    distribution = []
    if count_red > 0:
        pct = count_red / total_pixels_used * 100
        stats_text += f"  Красный : {count_red} пикс. ({pct:.2f}%), средний H={avg_h_red}\n"
        distribution.append({'zone': 'Red', 'percentage': pct, 'avg_h': avg_h_red})
    else:
        stats_text += f"  Красный : 0 пикс. (0.00%)\n"
    if count_green > 0:
        pct = count_green / total_pixels_used * 100
        stats_text += f"  Зелёный : {count_green} пикс. ({pct:.2f}%), средний H={avg_h_green}\n"
        distribution.append({'zone': 'Green', 'percentage': pct, 'avg_h': avg_h_green})
    else:
        stats_text += f"  Зелёный : 0 пикс. (0.00%)\n"
    if count_blue > 0:
        pct = count_blue / total_pixels_used * 100
        stats_text += f"  Синий   : {count_blue} пикс. ({pct:.2f}%), средний H={avg_h_blue}\n"
        distribution.append({'zone': 'Blue', 'percentage': pct, 'avg_h': avg_h_blue})
    else:
        stats_text += f"  Синий   : 0 пикс. (0.00%)\n"

    # Функция для создания квадрата цвета
    def create_hsv_square(h, s, v):
        square = np.zeros((config.SQUARE_SIZE, config.SQUARE_SIZE, 3), dtype=np.uint8)
        square[:] = (h, s, v)
        return cv2.cvtColor(square, cv2.COLOR_HSV2BGR)

    # Квадрат со средними H,S,V всего изображения (BGR)
    color_square_bgr = create_hsv_square(avg_h, avg_s, avg_v)
    # Конвертируем в RGB для отображения
    color_square_rgb = cv2.cvtColor(color_square_bgr, cv2.COLOR_BGR2RGB)

    # Подготовка исходного изображения для отображения (BGR -> RGB)
    display_img_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)

    # --- Построение гистограммы ---
    plt.switch_backend('Agg')  # Отключаем GUI
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.canvas.manager.set_window_title('Анализ рисунка')

    # 1. Исходное изображение (верхний левый)
    axes[0, 0].imshow(display_img_rgb)
    axes[0, 0].set_title('Source Image (scaled)')
    axes[0, 0].axis('off')

    # 2. Квадрат среднего цвета (верхний правый)
    axes[0, 1].imshow(color_square_rgb)
    axes[0, 1].set_title(f'Avg Color (H={avg_h}, S={avg_s}, V={avg_v})')
    axes[0, 1].axis('off')

    # 3. Гистограмма (нижний левый)
    if distribution:
        zone_names = [d['zone'] for d in distribution]
        percentages = [d['percentage'] for d in distribution]
        # Цвета столбцов: используем оттенок из среднего H каждой зоны
        bar_colors = []
        for d in distribution:
            h_norm = d['avg_h'] / 179.0
            bar_colors.append(hsv_to_rgb([h_norm, 1.0, 1.0]))
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

    # Сохраняем график в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    # Сохраняем исходное изображение и квадрат цвета в base64
    def img_to_base64(img_rgb):
        _, buffer = cv2.imencode('.png', cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
        return base64.b64encode(buffer).decode('utf-8')

    source_img_base64 = img_to_base64(display_img_rgb)
    color_square_base64 = img_to_base64(color_square_rgb)

    # Возвращаем результат
    return {
        'avg_hsv': (avg_h, avg_s, avg_v),
        'stats_text': stats_text,
        'distribution': distribution,
        'source_image_base64': source_img_base64,
        'color_square_base64': color_square_base64,
        'plot_base64': plot_base64,
        'error': None
    }