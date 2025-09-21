# file: guess_number.py
import argparse
import json
import os
import random
import sys

STATS_FILE = "guess_stats.json"
ERR_PREFIX = "[Ошибка]"

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_stats(stats):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception:
        print(f"{ERR_PREFIX} Не удалось сохранить статистику.")

def ask_int(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        try:
            raw = input(prompt).strip()
            if not raw or not (raw.lstrip("-").isdigit()):
                raise ValueError("Введите целое число.")
            x = int(raw)
            if x < min_val or x > max_val:
                raise ValueError(f"Число должно быть в диапазоне [{min_val}, {max_val}].")
            return x
        except (EOFError, KeyboardInterrupt):
            print("\nДо встречи!")
            sys.exit(0)
        except ValueError as e:
            print(f"{ERR_PREFIX} {e} Попробуйте снова.")

def play_once(low: int, high: int, attempts: int, give_hint_after: int | None):
    secret = random.randint(low, high)
    print(f"Я загадал число от {low} до {high}. У вас {attempts} попыток.")

    for i in range(1, attempts + 1):
        guess = ask_int(f"[Попытка {i}/{attempts}] Ваш ответ: ", low, high)

        if guess == secret:
            print("🎉 Поздравляю, вы угадали!")
            return True, i

        if guess < secret:
            print("Слишком маленькое.")
        else:
            print("Слишком большое.")

        if give_hint_after and i == give_hint_after:
            # Простая подсказка: сузим диапазон
            delta = max(1, (high - low) // 4)
            hint_low = max(low, secret - delta)
            hint_high = min(high, secret + delta)
            print(f"Подсказка: число в диапазоне [{hint_low}, {hint_high}].")

    print(f"Вы исчерпали попытки. Загаданное число было: {secret}.")
    return False, attempts

def main():
    parser = argparse.ArgumentParser(description="Игра 'Угадай число'")
    parser.add_argument("--low", type=int, default=1, help="Нижняя граница диапазона (включительно)")
    parser.add_argument("--high", type=int, default=100, help="Верхняя граница диапазона (включительно)")
    parser.add_argument("--attempts", type=int, default=7, help="Количество попыток")
    parser.add_argument("--hint-after", type=int, default=3, help="Дать подсказку после N-й попытки (0 = выкл)")
    parser.add_argument("--no-stats", action="store_true", help="Не сохранять статистику")
    args = parser.parse_args()

    if args.low >= args.high:
        print(f"{ERR_PREFIX} low должен быть меньше high.")
        sys.exit(2)
    if args.attempts <= 0:
        print(f"{ERR_PREFIX} attempts должен быть положительным.")
        sys.exit(2)
    give_hint_after = None if args.hint_after <= 0 else args.hint_after

    stats = {} if args.no_stats else load_stats()
    stats.setdefault("games", 0)
    stats.setdefault("wins", 0)
    stats.setdefault("best_attempts", None)

    print("Инструкция: угадайте число. Введите целое в заданном диапазоне. Подсказки помогут сузить поиск.")

    while True:
        win, used = play_once(args.low, args.high, args.attempts, give_hint_after)
        stats["games"] += 1
        if win:
            stats["wins"] += 1
            if stats["best_attempts"] is None or used < stats["best_attempts"]:
                stats["best_attempts"] = used

        if not args.no_stats:
            save_stats(stats)

        print(f"Статистика: игр={stats['games']}, побед={stats['wins']}, лучший результат={stats['best_attempts']}")
        again = input("Сыграть ещё? (y/n): ").strip().lower()
        if again != "y":
            print("Спасибо за игру!")
            break

if __name__ == "__main__":
    main()
