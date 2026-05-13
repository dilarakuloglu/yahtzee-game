## full house a tekrar bir bak 

CATEGORIES = [
    "ones", "twos", "threes", "fours", "fives", "sixes",
    "three_of_a_kind", "four_of_a_kind", "full_house",
    "small_straight", "large_straight", "yahtzee", "chance"
]

CATEGORY_NAMES = {
    "ones": "Birler (1'ler)",
    "twos": "İkiler (2'ler)",
    "threes": "Üçler (3'ler)",
    "fours": "Dörder (4'ler)",
    "fives": "Beşler (5'ler)",
    "sixes": "Altılar (6'lar)",
    "three_of_a_kind": "3'lü Dizi",
    "four_of_a_kind": "4'lü Dizi",
    "full_house": "Full House",
    "small_straight": "Küçük Seri",
    "large_straight": "Büyük Seri",
    "yahtzee": "YAHTZEE!",
    "chance": "Şans"
}

UPPER_CATEGORIES = CATEGORIES[:6]
LOWER_CATEGORIES = CATEGORIES[6:]

BONUS_THRESHOLD = 63
BONUS_SCORE = 35


def calculate_score(category, dice):
    """Verilen zarlarla kategori puanını hesaplar."""
    counts = [dice.count(i) for i in range(1, 7)]
    total = sum(dice)

    if category == "ones":   return dice.count(1)
    if category == "twos":   return dice.count(2) * 2
    if category == "threes": return dice.count(3) * 3
    if category == "fours":  return dice.count(4) * 4
    if category == "fives":  return dice.count(5) * 5
    if category == "sixes":  return dice.count(6) * 6

    if category == "three_of_a_kind":
        return total if max(counts) >= 3 else 0
    if category == "four_of_a_kind":
        return total if max(counts) >= 4 else 0
    if category == "full_house":
        return 25 if (3 in counts and 2 in counts) else 0
    if category == "small_straight":
        s = set(dice)
        if {1,2,3,4}.issubset(s) or {2,3,4,5}.issubset(s) or {3,4,5,6}.issubset(s):
            return 30
        return 0
    if category == "large_straight":
        return 40 if set(dice) in ({1,2,3,4,5}, {2,3,4,5,6}) else 0
    if category == "yahtzee":
        return 50 if max(counts) == 5 else 0
    if category == "chance":
        return total
    return 0


def calculate_total(scores):
    """Bir oyuncunun toplam puanını hesaplar (bonus dahil)."""
    upper = sum(scores.get(c, 0) for c in UPPER_CATEGORIES)
    bonus = BONUS_SCORE if upper >= BONUS_THRESHOLD and all(c in scores for c in UPPER_CATEGORIES) else 0
    lower = sum(scores.get(c, 0) for c in LOWER_CATEGORIES)
    return upper + bonus + lower
