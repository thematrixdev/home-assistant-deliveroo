"""Constants for the Deliveroo HK integration."""

from datetime import timedelta

DOMAIN = "deliveroohk"
CONF_TOKEN = "token"

SCAN_INTERVAL = timedelta(minutes=5)

API_ENDPOINT = "https://api.hk.deliveroo.com/consumer/order-history/v1/orders"
API_ORDER_STATUS_ENDPOINT = "https://api.hk.deliveroo.com/consumer/v2-6/consumer_order_statuses/{id}"

DEFAULT_TIMEZONE = "Asia/Hong_Kong"
