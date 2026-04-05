def process_cart(items, coupon=None):
    if not items:
        return None

    total = 0
    has_invalid = False

    for item in items:
        if item["price"] < 0 or item["quantity"] < 1:
            has_invalid = True
            continue
        total += item["price"] * item["quantity"]

    if has_invalid:
        return {"total": total, "warning": "Some items were skipped"}

    if coupon == "SAVE10":
        total *= 0.90
    elif coupon == "SAVE20":
        total *= 0.80

    return {"total": round(total, 2)}