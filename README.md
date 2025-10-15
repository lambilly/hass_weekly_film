# 每周电影 Home Assistant 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

这是一个用于 Home Assistant 的自定义集成，可以获取内地即将上映的电影信息，并以滚动方式展示。

## 功能特点

- 🎬 获取内地即将上映的电影信息
- ⏰ 24小时自动更新数据
- 🔄 可配置的滚动显示（默认每分钟切换一部电影）
- 📱 支持中文本地化界面
- 🖼️ 显示电影海报和详细信息
- 📊 两个实体：数据实体和滚动显示实体

## 安装

### 通过 HACS 安装（推荐）

1. 确保已安装 [HACS](https://hacs.xyz/)
2. 在 HACS 中点击「集成」
3. 点击右下角「+ 浏览并下载存储库」
4. 搜索「每周电影」或添加自定义存储库：
   - 存储库：`https://github.com/lambilly/hass_weekly_film`
   - 类别：集成
5. 下载「每周电影」集成
6. 重启 Home Assistant

### 手动安装

1. 将 `weekly_film` 文件夹复制到 `custom_components` 目录
2. 重启 Home Assistant
3. 在集成界面添加「每周电影」

## 配置

### 初始配置

1. 在 Home Assistant 中进入「配置」->「设备与服务」
2. 点击「+ 添加集成」
3. 搜索「每周电影」
4. 输入以下信息：
   - **API Key**: 从冷言数据申请（见下文）
   - **滚动间隔**: 电影切换间隔（秒），默认60秒

### API Key 申请

1. 访问 [冷言数据](https://qqlykm.cn/)
2. 注册账号并登录
3. 在API市场中找到「内地即将上映的电影」免费API
4. 申请获取 API Key
5. 将获得的 API Key 填入集成配置中

### 选项配置

集成安装后，可以在集成选项中进行配置：
- **滚动间隔**: 调整电影信息切换的频率

## 生成的实体

集成会创建一个设备，包含两个实体：

### 1. 每周电影数据
- **状态**: 最后更新时间
- **属性**:
  - `film_count`: 电影数量
  - `film_list`: 完整的电影列表
  - `update_time`: 更新时间

### 2. 每周电影滚动显示
- **状态**: 当前显示的电影名称和日期
- **属性**:
  - `name`: 电影名称
  - `type`: 电影类型
  - `director`: 导演
  - `actors`: 主演
  - `picurl`: 海报图片URL
  - `releasedatestr`: 上映日期
  - `poster`: HTML格式的海报图片

## 使用示例

### Lovelace 卡片配置

```yaml
type: entities
entities:
  - entity: sensor.weekly_film_scrolling
    name: 即将上映
    secondary_info: last-changed
```
## 故障排除
### 常见问题
1.	API 错误: 检查 API Key 是否正确，确保申请的是「内地即将上映的电影」API
2.	无数据显示: 确认网络连接正常，API服务可用
3.	滚动不工作: 检查滚动间隔设置，重启集成

## 日志调试
如需查看详细日志，在 configuration.yaml 中添加：

```yaml
logger:
  default: info
  logs:
    custom_components.weekly_film: debug
```
## 支持
如遇问题，请：
1.	查看 Home Assistant 日志
2.	确认 API Key 有效
3.	检查网络连接

## 许可证
MIT License

## 贡献
欢迎提交 Issue 和 Pull Request！
