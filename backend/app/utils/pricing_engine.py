from typing import Optional

def estimate(year: int, make: str, model: str, miles: Optional[int], base_price: Optional[float]):
    miles = miles or 0
    age = max(0, 2025 - (year or 2020))
    cond_factor = 1 - min(0.4, (miles / 200_000) * 0.4)
    base = (base_price or 20000) * cond_factor
    rarity = 1.15 if make and make.lower() in {"porsche","ferrari","aston martin","lotus","alfa romeo"} else 1.0
    season = 1.05
    target_sale_low = round(base * rarity * season * 0.95, 2)
    target_sale_high = round(base * rarity * season * 1.10, 2)
    est_recon = 1500 + age * 150 + (0 if miles < 60_000 else 1000)
    target_buy_high = round(target_sale_low * 0.78 - est_recon, 2)
    target_buy_low  = round(target_sale_low * 0.62 - est_recon, 2)
    min_profit = round(target_sale_low - (target_buy_high + est_recon), 2)
    max_profit = round(target_sale_high - (target_buy_low + est_recon), 2)
    return {
        "target_sale_low": target_sale_low,
        "target_sale_high": target_sale_high,
        "target_buy_low": max(0, target_buy_low),
        "target_buy_high": max(0, target_buy_high),
        "est_recon_cost": round(est_recon, 2),
        "est_profit_range": (min_profit, max_profit)
    }
