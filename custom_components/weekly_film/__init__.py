"""The Weekly Film integration."""
import asyncio
import logging
import json
import re
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL, CONF_API_KEY, CONF_SCROLL_INTERVAL
from .sensor import WeeklyFilmSensor, WeeklyFilmScrollingSensor

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Weekly Film from a config entry."""
    
    coordinator = WeeklyFilmDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class WeeklyFilmDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Weekly Film data."""
    
    def __init__(self, hass, entry):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.entry = entry
        self.api_key = entry.data[CONF_API_KEY]
        self.scroll_interval = entry.options.get(CONF_SCROLL_INTERVAL, 60)
        self.film_data = []
        self.current_index = 0

    async def _async_update_data(self):
        """Fetch data from API."""
        import aiohttp
        
        url = f"https://qqlykm.cn/api/jijiangshangying/get?key={self.api_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                # 手动处理响应，忽略 Content-Type 检查
                async with session.get(url) as response:
                    if response.status == 200:
                        # 直接读取文本内容，然后手动解析 JSON
                        text = await response.text()
                        _LOGGER.debug("API response: %s", text)
                        
                        # 手动解析 JSON
                        data = json.loads(text)
                        
                        if data.get("success"):
                            self.film_data = data.get("data", [])[:25]  # 缓存25条数据
                            self.current_index = 0
                            return {
                                "film_data": self.film_data,
                                "update_time": self.get_current_time()
                            }
                        else:
                            raise Exception("API returned unsuccessful response")
                    else:
                        raise Exception(f"HTTP error: {response.status}")
        except json.JSONDecodeError as err:
            _LOGGER.error("JSON decode error: %s, response text: %s", err, text)
            raise Exception(f"JSON decode error: {err}")
        except Exception as err:
            _LOGGER.error("Error fetching film data: %s", err)
            raise

    def parse_release_date(self, release_date_str):
        """简单处理上映日期字符串，返回格式化的日期"""
        if not release_date_str:
            return "2025年01月01日", "01月01日"
        
        # 简单处理：提取日期部分，去掉后面的描述文字
        # 格式如："10月18日  本周六", "10月17日  后天", "10月24日"
        date_part = release_date_str.split()[0]  # 取第一个空格前的部分
        
        # 检查是否包含年份，如果不包含则添加2025年
        if "年" not in date_part:
            # 提取月份和日期
            match = re.search(r'(\d{1,2})月(\d{1,2})日', date_part)
            if match:
                month = match.group(1).zfill(2)
                day = match.group(2).zfill(2)
                full_date = f"2025年{month}月{day}日"
                short_date = f"{month}月{day}日"
                return full_date, short_date
        
        # 如果已经包含年份，直接使用
        return date_part, date_part

    def get_current_film(self):
        """Get current film for scrolling."""
        if not self.film_data:
            return None
            
        film = self.film_data[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.film_data)
        
        # 处理字段名匹配问题
        release_date_str = film.get("releaseDateStr", "") or film.get("releaseDate", "")
        title = film.get("title", "") or film.get("name", "未知电影")
        pic_url = film.get("picUrl", "") or film.get("picurl", "")
        film_type = film.get("type", "未分类")
        director = film.get("director", "未知导演")
        actors = film.get("actors", "暂无演员信息")
        
        # 解析上映日期
        full_date, short_date = self.parse_release_date(release_date_str)
            
        return {
            "namedate": f"{title} ({short_date})",
            "name": title,
            "type": film_type,
            "director": director,
            "actors": actors,
            "picurl": pic_url,
            "release_date": full_date,
            "poster": f'<img src="{pic_url}"/>'
        }

    def get_current_time(self):
        """Get current formatted time."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M")