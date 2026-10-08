from inventory.client import fetch_products, format_report, low_stock

if __name__ == "__main__":
    print(format_report(low_stock(fetch_products())))
