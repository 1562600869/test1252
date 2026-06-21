from storage import VALID_TYPES, atomic_transaction, load_data


def _find_show(data, name, date=None):
    for show in data["shows"]:
        if show["name"] == name and (date is None or show["date"] == date):
            return show
    return None


def _sold_seats(show):
    return sum(order["qty"] for order in show["orders"])


def _remaining_seats(show):
    return show["total_seats"] - _sold_seats(show)


def add_show(name, date, time, show_type, total_seats):
    if show_type not in VALID_TYPES:
        raise ValueError(f"无效的演出类型，必须是: {', '.join(VALID_TYPES)}")
    if total_seats <= 0:
        raise ValueError("总座位数必须大于0")

    @atomic_transaction
    def _add(data):
        existing = _find_show(data, name, date)
        if existing:
            raise ValueError(f"演出 '{name}' 在 {date} 已存在")
        data["shows"].append({
            "name": name,
            "date": date,
            "time": time,
            "type": show_type,
            "total_seats": total_seats,
            "orders": []
        })
        return f"已添加演出: {name} ({date} {time}) - {show_type}, 共{total_seats}座"

    return _add()


def sell_ticket(show_name, buyer, phone, qty, date=None):
    if qty <= 0:
        raise ValueError("购票数量必须大于0")

    @atomic_transaction
    def _sell(data):
        show = _find_show(data, show_name, date)
        if not show:
            raise ValueError(f"未找到演出: {show_name}" + (f" ({date})" if date else ""))

        remaining = _remaining_seats(show)
        if qty > remaining:
            raise ValueError(f"剩余座位不足，当前剩余 {remaining} 座")

        show["orders"].append({
            "buyer": buyer,
            "phone": phone,
            "qty": qty
        })
        return f"售票成功: {buyer} ({phone}) 购买了 {qty} 张票，剩余 {remaining - qty} 座"

    return _sell()


def refund_ticket(show_name, phone, qty, date=None):
    if qty <= 0:
        raise ValueError("退票数量必须大于0")

    @atomic_transaction
    def _refund(data):
        show = _find_show(data, show_name, date)
        if not show:
            raise ValueError(f"未找到演出: {show_name}" + (f" ({date})" if date else ""))

        buyer_orders = [o for o in show["orders"] if o["phone"] == phone]
        buyer_total = sum(o["qty"] for o in buyer_orders)
        if qty > buyer_total:
            raise ValueError(f"该手机号已购票数为 {buyer_total}，退票数量不能超过已购票数")

        remaining_to_refund = qty
        for order in list(show["orders"]):
            if remaining_to_refund <= 0:
                break
            if order["phone"] == phone:
                if order["qty"] <= remaining_to_refund:
                    remaining_to_refund -= order["qty"]
                    show["orders"].remove(order)
                else:
                    order["qty"] -= remaining_to_refund
                    remaining_to_refund = 0

        return f"退票成功: 退还 {qty} 张票，剩余 {_remaining_seats(show)} 座"

    return _refund()


def show_stats(show_name, date=None):
    data = load_data()
    show = _find_show(data, show_name, date)
    if not show:
        raise ValueError(f"未找到演出: {show_name}" + (f" ({date})" if date else ""))

    sold = _sold_seats(show)
    remaining = _remaining_seats(show)
    return {
        "name": show["name"],
        "date": show["date"],
        "time": show["time"],
        "type": show["type"],
        "total_seats": show["total_seats"],
        "sold_seats": sold,
        "remaining_seats": remaining
    }


def monthly_stats(month):
    data = load_data()
    stats = {}
    for show_type in VALID_TYPES:
        stats[show_type] = {"shows": 0, "tickets": 0}

    for show in data["shows"]:
        if show["date"].startswith(month):
            show_type = show["type"]
            stats[show_type]["shows"] += 1
            stats[show_type]["tickets"] += _sold_seats(show)

    return stats
