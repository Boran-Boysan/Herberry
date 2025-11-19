"""Fiyat donusum fonksiyonlari"""

def to_tl(cents):
    """Cents'i TL'ye cevir"""
    return cents / 100 if cents else 0


def to_cents(tl):
    """TL'yi cents'e cevir"""
    return int(tl * 100)


def format_price(cents):
    """Fiyati formatla: 2550 -> "25.50 TL" """
    return f"{to_tl(cents):.2f} TL"