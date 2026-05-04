# -*- coding: utf-8 -*-
"""
Python-аналог SkanerF.

Слушает COM-порт (имя берётся из SkanerF.ini, секция [Nastr], параметр ComPort)
и при сканировании штрихкода:
  1. Выводит данные в консоль.
  2. Дописывает строку с датой/временем в SkanerF.txt в текущей папке.

Параметры порта захардкодены: 9600, 8 бит, без чётности, 1 стоп-бит.
Суффикс окончания сканирования: CR (\\r).
Остановка: Ctrl+C.

Зависимости: pyserial  (pip install pyserial)
"""

import configparser
import os
import sys
from datetime import datetime

try:
    import serial
except ImportError:
    print("Не найдена библиотека 'pyserial'.")
    print("Установи её командой: pip install pyserial")
    sys.exit(1)


# --- Константы ---------------------------------------------------------------

INI_FILE = "SkanerF.ini"
OUT_FILE = "SkanerF.txt"

BAUDRATE = 9600
BYTESIZE = serial.EIGHTBITS      # 8 бит данных
PARITY = serial.PARITY_NONE      # без чётности
STOPBITS = serial.STOPBITS_ONE   # 1 стоп-бит

# Суффикс окончания сканирования: CR
TERMINATOR = b"\r"


# --- Чтение имени порта из ini -----------------------------------------------

def read_com_port_from_ini(ini_path: str) -> str:
    """Читает имя COM-порта из SkanerF.ini (секция [Nastr], ключ ComPort)."""
    if not os.path.isfile(ini_path):
        print(f"Не найден файл конфигурации: {ini_path}")
        print("Положи SkanerF.ini рядом со скриптом и пропиши в нём:")
        print("[Nastr]")
        print("ComPort=COM6")
        sys.exit(1)

    parser = configparser.ConfigParser()
    # ini SkanerF может быть в cp1251 (русские пути), читаем без падения
    try:
        parser.read(ini_path, encoding="utf-8")
    except UnicodeDecodeError:
        parser.read(ini_path, encoding="cp1251")

    if "Nastr" not in parser or "ComPort" not in parser["Nastr"]:
        print(f"В файле {ini_path} нет секции [Nastr] или параметра ComPort.")
        print("Пример корректного содержимого:")
        print("[Nastr]")
        print("ComPort=COM6")
        sys.exit(1)

    port = parser["Nastr"]["ComPort"].strip()
    if not port:
        print(f"В {ini_path} параметр ComPort пустой.")
        sys.exit(1)

    return port


# --- Чтение данных из порта по терминатору -----------------------------------

def read_until_terminator(ser: serial.Serial, terminator: bytes) -> bytes:
    """Читает байты из порта до тех пор, пока не встретится terminator.
    Возвращает данные БЕЗ терминатора. Блокирующее чтение."""
    buf = bytearray()
    while True:
        b = ser.read(1)  # таймаут не задан → блокирующее ожидание байта
        if not b:
            # на всякий случай: если read вернул пусто (например, порт закрылся)
            continue
        if b == terminator:
            return bytes(buf)
        buf += b


# --- Запись в файл -----------------------------------------------------------

def append_to_file(file_path: str, code: str) -> None:
    """Дописывает строку '<дата время> | <код>' в файл (UTF-8, append)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | {code}\n"
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(line)


# --- Главная функция ---------------------------------------------------------

def main() -> None:
    # ini-файл ищем рядом со скриптом, выходной файл — в текущей рабочей папке.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ini_path = os.path.join(script_dir, INI_FILE)

    port_name = read_com_port_from_ini(ini_path)

    print(f"Открываю порт {port_name} (9600, 8N1)...")
    try:
        ser = serial.Serial(
            port=port_name,
            baudrate=BAUDRATE,
            bytesize=BYTESIZE,
            parity=PARITY,
            stopbits=STOPBITS,
            timeout=None,  # блокирующее чтение
        )
    except serial.SerialException as e:
        # Порт занят/не существует/нет прав
        msg = str(e)
        if "PermissionError" in msg or "Access is denied" in msg or "could not open port" in msg.lower():
            print(f"Не удалось открыть {port_name}: порт занят.")
            print("Закройте SkanerF.exe и попробуйте снова.")
        else:
            print(f"Не удалось открыть {port_name}: {msg}")
        sys.exit(1)

    print(f"Порт {port_name} открыт. Жду сканирования... (Ctrl+C для выхода)")
    print()

    try:
        while True:
            data = read_until_terminator(ser, TERMINATOR)
            try:
                code = data.decode("utf-8").strip()
            except UnicodeDecodeError:
                # на случай мусора/нестандартной кодировки — fallback
                code = data.decode("utf-8", errors="replace").strip()

            if not code:
                # пустая строка — пропускаем (бывает при двойных \r или мусоре)
                continue

            print(f"Получены данные в {port_name}:")
            print(code)
            print()

            try:
                append_to_file(OUT_FILE, code)
            except OSError as e:
                print(f"[!] Не удалось записать в {OUT_FILE}: {e}")

    except KeyboardInterrupt:
        print()
        print("Остановка по Ctrl+C. Закрываю порт.")
    finally:
        try:
            ser.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
