
import sys
import argparse
from typing import List, Tuple

# --------- Поліноміальний ролінг-хеш (64-бітове циклічне переповнення) ---------
def poly_hash(s: str, base: int = 911382323) -> int:
    h = 0
    for ch in s:
        h = (h * base + (ord(ch) - 96)) & 0xFFFFFFFFFFFFFFFF  # очікуються символи 'a'..'z'
    return h

# --------- Хеш-таблиця з окремими ланцюжками (separate chaining) ---------
class StringSet:
    def __init__(self, init_pow: int = 20):
        # місткість має бути степенем двійки для маскування
        self.capacity = 1 << init_pow  # типово 1 048 576 бакетів
        self.mask = self.capacity - 1
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0

    def _idx(self, h: int) -> int:
        return h & self.mask

    def _rehash(self, new_cap_pow: int):
        new_cap = 1 << new_cap_pow
        new_mask = new_cap - 1
        new_buckets = [[] for _ in range(new_cap)]
        for bucket in self.buckets:
            for h, s in bucket:
                new_buckets[h & new_mask].append((h, s))
        self.capacity = new_cap
        self.mask = new_mask
        self.buckets = new_buckets

    def _maybe_resize(self):
        # поріг коефіцієнта заповнення 0.75
        if self.size * 4 >= self.capacity * 3:
            self._rehash((self.capacity.bit_length()))  # подвоїти місткість

    def add(self, s: str) -> bool:
        h = poly_hash(s)
        b = self._idx(h)
        bucket = self.buckets[b]
        for _, x in bucket:
            if x == s:
                return False  # вже існує
        bucket.append((h, s))
        self.size += 1
        self._maybe_resize()
        return True

    def discard(self, s: str) -> bool:
        h = poly_hash(s)
        b = self._idx(h)
        bucket = self.buckets[b]
        for i, (_, x) in enumerate(bucket):
            if x == s:
                bucket.pop(i)
                self.size -= 1
                return True
        return False

    def contains(self, s: str) -> bool:
        h = poly_hash(s)
        b = self._idx(h)
        for _, x in self.buckets[b]:
            if x == s:
                return True
        return False

    def __iter__(self):
        for bucket in self.buckets:
            for _, s in bucket:
                yield s

# --------- Варіанти ---------
def variant_groupdups(stdin: List[str]) -> None:
    data = [line.strip() for line in stdin if line.strip()]
    if not data:
        return
    try:
        n = int(data[0])
        strings = data[1:1+n]
    except ValueError:
        # if N not provided, treat all lines as strings
        strings = data
    from collections import Counter
    cnt = Counter(strings)
    for s, c in cnt.items():
        if c > 1:
            print(f"{s} {c}")

def is_palin(s: str) -> bool:
    return s == s[::-1]

def variant_palin(stdin: List[str]) -> None:
    data = [line.strip() for line in stdin if line.strip()]
    try:
        n = int(data[0])
        strings = data[1:1+n]
    except ValueError:
        strings = data
    from collections import Counter
    cnt = Counter(strings)
    for s, c in cnt.items():
        if is_palin(s):
            print(f"{s} {c}")

def z_function(s: str) -> List[int]:
    n = len(s)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > r:
            l, r = i, i + z[i] - 1
    z[0] = n
    return z

def variant_z(stdin: List[str]) -> None:
    # читаємо один рядок
    for line in stdin:
        s = line.strip()
        if s:
            print(" ".join(map(str, z_function(s))))
            return

# --------- Основний режим (ops) ---------
def run_ops(stdin, store_path: str = None):
    ss = StringSet()
    # початкове завантаження зі сховища файлу
    if store_path:
        try:
            with open(store_path, "r", encoding="utf-8") as f:
                for line in f:
                    w = line.strip().lower()
                    if w:
                        ss.add(w)
        except FileNotFoundError:
            pass
    for line in stdin:
        line = line.strip()
        if not line: 
            continue
        if line == ".":
            break
        if len(line) < 2:
            continue
        op = line[0]
        # підтримуємо формати "+ слово" та "+слово"
        s = line[1:].strip()
        # нормалізуємо до малих літер
        s = s.lower()
        changed = False
        if op == '+':
            changed = ss.add(s)
        elif op == '-':
            changed = ss.discard(s)
        elif op == '?':
            print("yes" if ss.contains(s) else "no")
        elif op == 'p':
            print("yes" if is_palin(s) else "no")
        # ігноруємо невідомі операції
        # синхронізація зі сховищем після зміни
        if store_path and changed:
            words_sorted = sorted(set(ss))
            with open(store_path, "w", encoding="utf-8") as f:
                for w in words_sorted:
                    f.write(f"{w}\n")

def main():
    parser = argparse.ArgumentParser(description="Lab 2: Polynomial hash applications")
    parser.add_argument("mode", nargs="?", default="ops",
                        choices=["ops", "groupdups", "palin", "z"],
                        help="ops (default): + s / - s / ? s / p s until '.'; groupdups: count duplicates; palin: palindromes; z: Z-function")
    parser.add_argument("--store", "-f", dest="store", default=None,
                        help="шлях до файлу для збереження слів у режимі ops")
    args = parser.parse_args()
    data = sys.stdin
    if args.mode == "ops":
        run_ops(data, args.store)
    elif args.mode == "groupdups":
        variant_groupdups(data)
    elif args.mode == "palin":
        variant_palin(data)
    else:
        variant_z(data)

if __name__ == "__main__":
    main()

