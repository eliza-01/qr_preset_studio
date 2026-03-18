# QR Preset Studio

Локальное desktop-приложение на Python для генерации QR и сохранения пресетов.

## Что есть в MVP

- настройка итогового размера изображения
- генерация QR из ссылки
- 2 shape для body: `square`, `rounded`
- 2 shape для eye frame: `square`, `rounded`
- 2 shape для eye ball: `square`, `circle`
- цвет QR
- градиент и направление градиента
- фон изображения
- фон QR-карточки, граница, цвет, отступы, скругление
- сохранение / загрузка пресетов в JSON
- после загрузки можно сразу менять ссылку и экспортировать PNG
- экспорт PNG

## Установка

```bash
venv\Scripts\activate
python app.py
```

Для Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Пресеты

Пресеты по умолчанию сохраняются через диалог в JSON.

Пример структуры:

```json
{
  "link": "https://example.com",
  "canvas_width": 1200,
  "canvas_height": 1200,
  "canvas_background_color": "#F3F4F6",
  "background_image_path": "",
  "qr_scale_percent": 42,
  "qr_offset_x": 0,
  "qr_offset_y": 0,
  "body_shape": "square",
  "eye_frame_shape": "square",
  "eye_ball_shape": "square",
  "qr_foreground_color": "#0F172A",
  "gradient_enabled": false,
  "gradient_color": "#2563EB",
  "gradient_direction": "horizontal",
  "qr_background_enabled": true,
  "qr_background_color": "#FFFFFF",
  "qr_background_padding": 32,
  "qr_background_radius": 24,
  "qr_border_width": 4,
  "qr_border_color": "#CBD5E1"
}
```
