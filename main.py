import cv2
import numpy as np

all_r = 0
all_g = 0
all_b = 0

stat_r = 0
stat_g = 0
stat_b = 0


# Загружаем изображение (по умолчанию в цвете)
img = cv2.imread('image2.jpg')

# Проверяем, загрузилось ли изображение
if img is None:
    print("Ошибка: Не удалось загрузить изображение. Проверьте путь к файлу.")
else:
    print(f"Изображение загружено! Размер: {img.shape}")



height, width, channels = img.shape

for i in range(height):
    for j in range(width):
        #bgr!!!
        all_b += int(img[i, j, 0])
        all_g += int(img[i, j, 1])
        all_r += int(img[i, j, 2])

        max_color = max(int(img[i, j, 0]), int(img[i, j, 1]), int(img[i, j, 2]))
        if max_color == int(img[i, j, 0]):
            stat_b += 1
        elif max_color == int(img[i, j, 1]):
            stat_g += 1
        elif max_color == int(img[i, j, 2]):
            stat_r += 1

total_pixels = height * width
avg_r = all_r // total_pixels
avg_g = all_g // total_pixels
avg_b = all_b // total_pixels

square_size=200

color_square = np.zeros((square_size, square_size, 3), dtype=np.uint8)
# Заливаем квадрат средним цветом (в формате BGR для OpenCV)
color_square[:] = (avg_b, avg_g, avg_r)

color_square_r = np.zeros((square_size, square_size, 3), dtype=np.uint8)
color_square_r[:] = (0, 0, avg_r)

color_square_g = np.zeros((square_size, square_size, 3), dtype=np.uint8)
color_square_g[:] = (0, avg_g, 0)

color_square_b = np.zeros((square_size, square_size, 3), dtype=np.uint8)
color_square_b[:] = (avg_b, 0, 0)

cv2.imshow('Цвет', color_square)
cv2.imshow('Красный', color_square_r)
cv2.imshow('Синий', color_square_b)
cv2.imshow('Зелёный', color_square_g)
cv2.imshow('Мое изображение', img)


print(f"Средние значения (RGB): ({avg_r}, {avg_g}, {avg_b})")

print(f"соотношение пикселей цветов красных/зелёных/синих: ({((stat_r/total_pixels)*100):.2f}%, {((stat_g/total_pixels)*100):.2f}%, {((stat_b/total_pixels)*100):.2f}%)")
cv2.waitKey(0)
cv2.destroyAllWindows()