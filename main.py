import argparse
import sys

from theater import add_show, sell_ticket, refund_ticket, show_stats, monthly_stats
from storage import VALID_TYPES


def cmd_add_show(args):
    result = add_show(
        name=args.show_name,
        date=args.date,
        time=args.time,
        show_type=args.type,
        total_seats=args.total_seats
    )
    print(result)


def cmd_sell(args):
    result = sell_ticket(
        show_name=args.show_name,
        buyer=args.buyer,
        phone=args.phone,
        qty=args.qty,
        date=args.date
    )
    print(result)


def cmd_refund(args):
    result = refund_ticket(
        show_name=args.show_name,
        phone=args.phone,
        qty=args.qty,
        date=args.date
    )
    print(result)


def cmd_show_stats(args):
    stats = show_stats(args.show_name, args.date)
    print(f"演出: {stats['name']}")
    print(f"日期: {stats['date']} {stats['time']}")
    print(f"类型: {stats['type']}")
    print(f"总座位数: {stats['total_seats']}")
    print(f"已售座位数: {stats['sold_seats']}")
    print(f"剩余座位数: {stats['remaining_seats']}")


def cmd_monthly(args):
    stats = monthly_stats(args.month)
    print(f"{args.month} 月度统计:")
    print(f"{'类型':<10}{'场次':<10}{'总售票数':<10}")
    print("-" * 30)
    for show_type in VALID_TYPES:
        s = stats[show_type]
        print(f"{show_type:<10}{s['shows']:<10}{s['tickets']:<10}")


def main():
    parser = argparse.ArgumentParser(description="剧场演出和座位票务管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    add_parser = subparsers.add_parser("add-show", help="添加演出")
    add_parser.add_argument("show_name", help="演出名称")
    add_parser.add_argument("--date", required=True, help="演出日期 (YYYY-MM-DD)")
    add_parser.add_argument("--time", required=True, help="演出时间 (HH:MM)")
    add_parser.add_argument("--type", required=True, choices=VALID_TYPES,
                            help=f"演出类型: {', '.join(VALID_TYPES)}")
    add_parser.add_argument("--total-seats", type=int, required=True, help="总座位数")
    add_parser.set_defaults(func=cmd_add_show)

    sell_parser = subparsers.add_parser("sell", help="售票")
    sell_parser.add_argument("show_name", help="演出名称")
    sell_parser.add_argument("--buyer", required=True, help="购票人姓名")
    sell_parser.add_argument("--phone", required=True, help="购票人手机号")
    sell_parser.add_argument("--qty", type=int, required=True, help="购票数量")
    sell_parser.add_argument("--date", help="演出日期 (同名演出多场时使用)")
    sell_parser.set_defaults(func=cmd_sell)

    refund_parser = subparsers.add_parser("refund", help="退票")
    refund_parser.add_argument("show_name", help="演出名称")
    refund_parser.add_argument("--phone", required=True, help="购票人手机号")
    refund_parser.add_argument("--qty", type=int, required=True, help="退票数量")
    refund_parser.add_argument("--date", help="演出日期 (同名演出多场时使用)")
    refund_parser.set_defaults(func=cmd_refund)

    stats_parser = subparsers.add_parser("show-stats", help="查看演出统计")
    stats_parser.add_argument("show_name", help="演出名称")
    stats_parser.add_argument("--date", help="演出日期 (同名演出多场时使用)")
    stats_parser.set_defaults(func=cmd_show_stats)

    monthly_parser = subparsers.add_parser("monthly", help="月度统计")
    monthly_parser.add_argument("--month", required=True, help="月份 (YYYY-MM)")
    monthly_parser.set_defaults(func=cmd_monthly)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
