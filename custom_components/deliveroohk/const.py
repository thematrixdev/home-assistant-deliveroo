"""Constants for the Deliveroo HK integration."""

from datetime import timedelta

DOMAIN = "deliveroohk"
CONF_TOKEN = "token"
CONF_LOCALE = "locale"

# Locale options
LOCALE_TC = "Traditional Chinese"
LOCALE_EN = "English"

# Language headers
LANG_TC = "zh"
LANG_EN = "en"

# Update intervals
SCAN_INTERVAL = timedelta(minutes=1)  # Default interval for checking orders
ACTIVE_ORDER_SCAN_INTERVAL = timedelta(seconds=30)  # Interval when order is active

API_ENDPOINT = "https://api.hk.deliveroo.com/consumer/order-history/v1/orders"
API_ORDER_STATUS_ENDPOINT = "https://api.hk.deliveroo.com/consumer/v2-6/consumer_order_statuses/{id}"

DEFAULT_TIMEZONE = "Asia/Hong_Kong"
