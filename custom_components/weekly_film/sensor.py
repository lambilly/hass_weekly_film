"""Sensor platform for Weekly Film integration."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

from .const import DOMAIN, NAME, CONF_SCROLL_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=NAME,
        manufacturer="Node-RED",
        model="信息查询",
    )
    
    entities = [
        WeeklyFilmSensor(coordinator, entry, device_info),
        WeeklyFilmScrollingSensor(coordinator, entry, device_info)
    ]
    
    async_add_entities(entities)

class WeeklyFilmSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Weekly Film Sensor."""
    
    def __init__(self, coordinator, entry, device_info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_film_data"
        self._attr_name = "电影数据"  # 修改实体名称
        self._attr_device_info = device_info

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("update_time", "未知")
        return "未知"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data:
            film_data = self.coordinator.data.get("film_data", [])
            return {
                "film_count": len(film_data),
                "film_list": film_data,
                "update_time": self.coordinator.data.get("update_time")
            }
        return {}

class WeeklyFilmScrollingSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Weekly Film Scrolling Sensor."""
    
    def __init__(self, coordinator, entry, device_info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_film_scrolling"
        self._attr_name = "滚动显示"  # 修改实体名称
        self._attr_device_info = device_info
        self._current_film = None
        self._remove_update_listener = None

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._start_scrolling()

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        if self._remove_update_listener:
            self._remove_update_listener()
        await super().async_will_remove_from_hass()

    def _start_scrolling(self):
        """Start the scrolling update."""
        @callback
        def _update_scrolling(now=None):
            """Update scrolling data."""
            self._current_film = self.coordinator.get_current_film()
            self.async_write_ha_state()

        # 初始更新
        _update_scrolling()
        
        # 设置定时更新
        scroll_interval = self.coordinator.scroll_interval
        self._remove_update_listener = async_track_time_interval(
            self.hass,
            _update_scrolling,
            timedelta(seconds=scroll_interval)
        )

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._current_film:
            # state 显示上映日期，格式如：2025年10月25日
            return self._current_film.get("release_date", "无数据")
        return "无数据"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self._current_film:
            return {
                "namedate": self._current_film.get("namedate"),
                "name": self._current_film.get("name"),
                "type": self._current_film.get("type"),
                "director": self._current_film.get("director"),
                "actors": self._current_film.get("actors"),
                "picurl": self._current_film.get("picurl"),
                "release_date": self._current_film.get("release_date"),  # 修改属性名
                "poster": self._current_film.get("poster")
            }
        return {}