import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import io
import base64
from . import config

def make_json_serializable(obj):
    """Рекурсивно преобразует numpy-типы в стандартные Python типы (int, float, list)."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    else:
        return obj


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
            - 'ignored_white_pixels': процент игнорированных белых пикселей
            - 'avg_hue': средний оттенок на рисунке
            - 'avg_saturation': средняя насыщенность пикселей
            - 'avg_brightness': средняя яркость пикселей
            - 'red_percent': процент пикселей красного диапазона
            - 'green_percent': процент пикселей зеленого диапазона
            - 'blue_percent': процент пикселей синего диапазона
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
    height, width, _ = hsv_img.shape
    total_pixels_all = height * width

    # ========== НАЧАЛО ВЕКТОРИЗОВАННОГО УЧАСТКА (вместо циклов) ==========
    # Извлекаем каналы H, S, V как целочисленные массивы (int16 для H 0-179)
    H = hsv_img[:, :, 0].astype(np.int16)
    S = hsv_img[:, :, 1].astype(np.int16)
    V = hsv_img[:, :, 2].astype(np.int16)

    # Маска "цветных" пикселей (не белых, насыщенность выше порога)
    color_mask = (S >= config.SATURATION_THRESHOLD)
    total_colored = np.sum(color_mask)
    ignored_pixels = total_pixels_all - total_colored

    if total_colored == 0:
        return {'error': 'Нет цветных пикселей (все отброшены как белые)'}

    # Общие суммы и средние по всем цветным пикселям
    all_h = np.sum(H[color_mask])
    all_s = np.sum(S[color_mask])
    all_v = np.sum(V[color_mask])

    avg_h = all_h // total_colored
    avg_s = all_s // total_colored
    avg_v = all_v // total_colored

    # Маски для цветовых зон (только среди цветных пикселей)
    red_mask   = color_mask & ((H < 30) | (H >= 150))
    green_mask = color_mask & ((H >= 30) & (H < 90))
    blue_mask  = color_mask & ((H >= 90) & (H < 150))

    count_red   = np.sum(red_mask)
    count_green = np.sum(green_mask)
    count_blue  = np.sum(blue_mask)

    # --- Средний оттенок для красной зоны (циклическое усреднение) ---
    if count_red > 0:
        h_red = H[red_mask].astype(np.float64)
        angles = h_red * 2                     # перевод в градусы 0..358
        rad = np.radians(angles)
        mean_cos = np.mean(np.cos(rad))
        mean_sin = np.mean(np.sin(rad))
        avg_angle_rad = math.atan2(mean_sin, mean_cos)
        avg_angle_deg = math.degrees(avg_angle_rad) % 360
        avg_h_red = int(round(avg_angle_deg / 2))
    else:
        avg_h_red = 0

    # --- Средний оттенок для зелёной зоны (целочисленное среднее) ---
    if count_green > 0:
        avg_h_green = int(np.sum(H[green_mask]) // count_green)
    else:
        avg_h_green = 0

    # --- Средний оттенок для синей зоны ---
    if count_blue > 0:
        avg_h_blue = int(np.sum(H[blue_mask]) // count_blue)
    else:
        avg_h_blue = 0

    total_pixels_used = total_colored  # для совместимости с оригиналом

    # ========== КОНЕЦ ВЕКТОРИЗОВАННОГО УЧАСТКА ==========

    # Формируем текстовую статистику (без изменений)
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

    # Функция для создания квадрата цвета (без изменений)
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

    # --- Построение гистограммы (без изменений) ---
    plt.switch_backend('Agg')
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.canvas.manager.set_window_title('Анализ рисунка')

    axes[0, 0].imshow(display_img_rgb)
    axes[0, 0].set_title('Исходное изображение')
    axes[0, 0].axis('off')

    axes[0, 1].imshow(color_square_rgb)
    axes[0, 1].set_title(f'Средний цвет по изображению (H={avg_h}, S={avg_s}, V={avg_v})')
    axes[0, 1].axis('off')

    if distribution:
        zone_names = [d['zone'] for d in distribution]
        percentages = [d['percentage'] for d in distribution]
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

    axes[1, 1].axis('off')
    axes[1, 1].text(0.05, 0.95, stats_text, transform=axes[1, 1].transAxes,
                    fontsize=10, verticalalignment='top', family='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    def img_to_base64(img_rgb):
        _, buffer = cv2.imencode('.png', cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
        return base64.b64encode(buffer).decode('utf-8')

    source_img_base64 = img_to_base64(display_img_rgb)
    color_square_base64 = img_to_base64(color_square_rgb)

    # Возвращаем результат
    result = {
        'avg_hsv': (avg_h, avg_s, avg_v),
        'stats_text': stats_text,
        'distribution': distribution,
        'source_image_base64': source_img_base64,
        'color_square_base64': color_square_base64,
        'plot_base64': plot_base64,
        'error': None,
        'ignored_white_pixels': ignored_pixels / total_pixels_all * 100,
        'avg_hue': avg_h,
        'avg_saturation': avg_s,
        'avg_brightness': avg_v,
        'red_percent': count_red / total_pixels_used * 100,
        'green_percent': count_green / total_pixels_used * 100,
        'blue_percent': count_blue / total_pixels_used * 100,
    }

    # Преобразуем все numpy-типы в стандартные Python-типы
    result = make_json_serializable(result)
    return result