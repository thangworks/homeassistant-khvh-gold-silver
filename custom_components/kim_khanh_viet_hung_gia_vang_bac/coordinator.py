"""Data coordinator for Kim Khanh Viet Hung - Gia Vang Bac."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import re
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import utcnow

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class PriceRow:
    """Parsed price row."""

    group: str
    name: str
    buy: int | None
    sell: int | None
    exchange: int | None


def _clean_text(value: str) -> str:
    """Remove HTML tags and normalize spaces."""
    text = re.sub(r"<[^>]+>", " ", value, flags=re.IGNORECASE)
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _parse_price(value: str) -> int | None:
    """Parse Vietnamese formatted price like 17.600.000đ."""
    digits = re.sub(r"[^0-9]", "", value)
    if not digits:
        return None
    return int(digits)


def parse_kimkhanh_table(html: str) -> list[PriceRow]:
    """Parse table values from Kim Khanh website.

    Works with imperfect HTML by reading `th` and `td` tokens in sequence.
    """
    tokens = re.findall(r"<(th|td)\b[^>]*>(.*?)</(?:th|td)>", html, flags=re.IGNORECASE | re.DOTALL)
    rows: list[PriceRow] = []
    current_group = ""

    i = 0
    while i < len(tokens):
        tag = tokens[i][0].lower()
        raw = tokens[i][1]

        if tag == "th":
            if i + 3 < len(tokens) and all(tokens[i + j][0].lower() == "th" for j in range(4)):
                current_group = _clean_text(raw)
                i += 4
                continue
            i += 1
            continue

        if tag == "td" and i + 3 < len(tokens) and all(tokens[i + j][0].lower() == "td" for j in range(4)):
            name = _clean_text(tokens[i][1])
            buy = _parse_price(tokens[i + 1][1])
            sell = _parse_price(tokens[i + 2][1])
            exchange = _parse_price(tokens[i + 3][1])

            if name:
                rows.append(
                    PriceRow(
                        group=current_group or "Khác",
                        name=name,
                        buy=buy,
                        sell=sell,
                        exchange=exchange,
                    )
                )
            i += 4
            continue

        i += 1

    return rows


class KimKhanhPriceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch and store Kim Khanh prices."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        url: str,
        update_interval,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Kim Khanh Viet Hung Price Coordinator",
            update_interval=update_interval,
            config_entry=entry,
        )
        self.url = url

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from website and parse rows."""
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(self.url, timeout=30) as response:
                response.raise_for_status()
                html = await response.text()
        except Exception as err:
            raise UpdateFailed(f"Error fetching {self.url}: {err}") from err

        rows = parse_kimkhanh_table(html)
        if not rows:
            raise UpdateFailed("No rows parsed from source table")

        fetched_at = utcnow().isoformat()
        return {
            "rows": rows,
            "fetched_at": fetched_at,
            "source_url": self.url,
        }
