# 🎯 TikTok Hashtag Alert Bot

Bot Telegram tự động theo dõi TikToker và gửi thông báo khi họ đăng bài mới kèm hashtag.

## ✨ Tính năng

- 🔔 **Tự động theo dõi**: Theo dõi nhiều TikToker cùng lúc
- 📱 **Thông báo Telegram**: Nhận alert ngay khi có bài viết mới
- 🏷️ **Theo dõi hashtag**: Hiển thị tất cả hashtag trong bài viết
- 💾 **Lưu trữ lịch sử**: Không bị duplicate alert
- ⚙️ **Tùy chỉnh**: Cấu hình interval monitoring

## 🏗️ Kiến trúc

```
hashtag-alert/
├── config/                 # Configuration
│   ├── __init__.py
│   └── settings.py        # Environment settings
├── src/
│   ├── database/          # Supabase integration
│   │   ├── __init__.py
│   │   ├── schema.sql     # Database schema
│   │   └── supabase_client.py
│   ├── tiktok/            # TikTok scraping
│   │   ├── __init__.py
│   │   └── scraper.py     # TikTokApi + yt-dlp
│   ├── bot/               # Telegram bot
│   │   ├── __init__.py
│   │   ├── handlers.py    # Command handlers
│   │   └── telegram_bot.py
│   └── scheduler/         # Monitoring scheduler
│       ├── __init__.py
│       ├── monitor.py     # Monitoring logic
│       └── scheduler.py   # APScheduler
├── .env                   # Environment variables
├── .env.example           # Environment template
├── .gitignore
├── requirements.txt
└── main.py               # Entry point
```

## 📋 Yêu cầu hệ thống

- Python 3.10+
- Supabase account
- Telegram Bot Token
- VPS hoặc máy chạy 24/7

## 🚀 Cài đặt

### 1. Clone và setup môi trường

```bash
cd c:\Dương\hashtag-alert

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
.\venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Cài đặt Playwright browser (cần cho TikTokApi)
playwright install chromium
```

### 2. Tạo Telegram Bot

1. Mở Telegram và tìm [@BotFather](https://t.me/botfather)
2. Gửi `/newbot`
3. Làm theo hướng dẫn để đặt tên bot
4. Copy **Bot Token** (dạng: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 3. Setup Supabase

1. Tạo account tại [supabase.com](https://supabase.com)
2. Tạo project mới
3. Vào **SQL Editor** và chạy script từ `src/database/schema.sql`
4. Lấy credentials:
   - **URL**: Settings → API → Project URL
   - **Key**: Settings → API → anon/service_role key

### 4. Cấu hình môi trường

```bash
# Copy file template
cp .env.example .env

# Chỉnh sửa .env với thông tin của bạn
notepad .env
```

Điền thông tin vào `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key_here
MONITOR_INTERVAL_MINUTES=10
```

### 5. Chạy bot

```bash
python main.py
```

## 📱 Sử dụng

### Các lệnh Telegram

- `/start` - Bắt đầu sử dụng bot
- `/add <username>` - Thêm TikToker vào danh sách theo dõi
- `/remove <username>` - Xóa TikToker
- `/list` - Xem danh sách đang theo dõi
- `/help` - Hướng dẫn

### Ví dụ

```
/add khaby.lame
/add charlidamelio
/list
/remove khaby.lame
```

## 🖥️ Deployment lên VPS

### Systemd Service (Linux)

Tạo file `/etc/systemd/system/hashtag-alert.service`:

```ini
[Unit]
Description=TikTok Hashtag Alert Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/hashtag-alert
Environment="PATH=/path/to/hashtag-alert/venv/bin"
ExecStart=/path/to/hashtag-alert/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Kích hoạt service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hashtag-alert
sudo systemctl start hashtag-alert

# Kiểm tra status
sudo systemctl status hashtag-alert

# Xem logs
sudo journalctl -u hashtag-alert -f
```

### PM2 (Cross-platform)

```bash
# Cài đặt PM2
npm install -g pm2

# Start bot
pm2 start main.py --name hashtag-alert --interpreter python

# Setup auto-start
pm2 startup
pm2 save

# Xem logs
pm2 logs hashtag-alert
```

## ⚙️ Cấu hình

Các biến môi trường trong `.env`:

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `TELEGRAM_BOT_TOKEN` | Token từ BotFather | Bắt buộc |
| `SUPABASE_URL` | URL Supabase project | Bắt buộc |
| `SUPABASE_KEY` | Supabase API key | Bắt buộc |
| `MONITOR_INTERVAL_MINUTES` | Interval check posts (phút) | `10` |
| `MAX_POSTS_PER_CHECK` | Số post tối đa mỗi lần check | `5` |
| `LOG_LEVEL` | Log level (DEBUG/INFO/WARNING) | `INFO` |
| `TIKTOK_REQUEST_DELAY` | Delay giữa các request (giây) | `2` |
| `TIKTOK_MAX_RETRIES` | Số lần retry khi lỗi | `3` |

## 🐛 Troubleshooting

### Bot không nhận được thông báo

- Kiểm tra logs: `tail -f bot.log`
- Đảm bảo MONITOR_INTERVAL_MINUTES đủ lớn (>= 5 phút)
- Kiểm tra TikToker có đăng bài mới chưa

### Lỗi TikTok API

TikTok thường xuyên thay đổi security measures. Nếu gặp lỗi:

1. Kiểm tra update mới nhất của `TikTokApi`:
   ```bash
   pip install --upgrade TikTokApi
   ```
2. Bot sẽ tự động fallback sang yt-dlp
3. Update yt-dlp:
   ```bash
   pip install --upgrade yt-dlp
   ```

### Database errors

- Kiểm tra Supabase credentials
- Đảm bảo đã chạy `schema.sql`
- Kiểm tra Supabase dashboard xem tables đã tồn tại chưa

## 📊 Database Schema

Xem chi tiết trong `src/database/schema.sql`

**Tables:**
- `tracked_creators` - Danh sách TikToker
- `posts` - Lịch sử bài viết
- `bot_users` - Người dùng Telegram

## 🔒 Bảo mật

- **Không commit `.env`** vào git
- Sử dụng **service_role key** của Supabase (không phải anon key) để có full quyền
- Chạy bot dưới user có quyền hạn chế trên VPS

## 📝 License

MIT License - Tự do sử dụng và chỉnh sửa

## 🤝 Đóng góp

Mọi contribution đều được hoan nghênh!

## 📞 Support

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs
2. Đọc phần Troubleshooting
3. Tạo issue mô tả chi tiết lỗi

---

**Lưu ý**: Bot này sử dụng unofficial TikTok API, có thể ngừng hoạt động khi TikTok update security. Cần maintain và update thường xuyên.
