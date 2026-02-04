# 🌅 Sun Set Calculator / Расчёт закатов

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</div>

## 🇬🇧 English Version

### 📌 Features

- Calculate sunset times for custom cities
- Generate text reports (`output.txt`)
- Create visual charts (PNG format)
- Adjustable weekday selection
- Time correction (hour offsets)

### 🛠 Tech Stack

```plaintext
astral 6.2.1      # Astronomical calculations
Pillow 1.10.1    # Image generation
datetime       # Built-in date handling
```

### ⚙️ Installation

```bash
git clone https://github.com/MihailPy/sun_set.git
cd sun_set
pip install -r requirements.txt
```

### 🚀 Usage

```python
# Configure in sun_set.py:
year = 2024     # Analysis year
day1 = 1        # Monday (1-7)
day2 = 5        # Friday 
```

---

## 🇷🇺 Русская версия

### 📌 Возможности

- Расчёт времени заката для городов
- Генерация текстовых отчётов (`output.txt`)
- Создание визуальных графиков (PNG)
- Настройка дней недели для анализа
- Коррекция времени (смещение часов)

### 🛠 Технологии

```plaintext
astral 6.2.1      # Астрономические расчёты
Pillow 1.10.1    # Генерация изображений
datetime       # Стандартная работа с датами
```

### ⚙️ Установка

```bash
git clone https://github.com/MihailPy/sun_set.git
cd sun_set
pip install -r requirements.txt
```

### 🚀 Использование

```python
# Настройки в sun_set.py:
year = 2024     # Год анализа
day1 = 1        # Понедельник (1-7)
day2 = 5        # Пятница
```

---

## 📸 Пример вывода / Sample Output

**Текст:**  

```plaintext
Город: Voronezh
Январь:
01  16:25   05  16:30...
```

## 📜 License / Лицензия

MIT © [MihailPy](https://github.com/MihailPy)
