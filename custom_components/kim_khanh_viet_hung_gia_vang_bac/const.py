"""Constants for Kim Khanh Viet Hung - Gia Vang Bac integration."""

from datetime import timedelta

DOMAIN = "kim_khanh_viet_hung_gia_vang_bac"
DEFAULT_NAME = "KHVH Gold Silver Prices"
DEFAULT_URL = "https://kimkhanhviethung.vn/tra-cuu-gia-vang.html"
DEFAULT_SCAN_INTERVAL = timedelta(hours=1)

CONF_URL = "url"
CONF_SCAN_INTERVAL_HOURS = "scan_interval_hours"

COORDINATOR = "coordinator"
ATTR_GROUP = "group"
ATTR_LAST_FETCH = "last_fetch"
ATTR_SOURCE_URL = "source_url"

SERVICE_REFRESH_PRICES = "refresh_prices"
