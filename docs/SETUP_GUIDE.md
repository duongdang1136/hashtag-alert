# 📖 Setup Guide - TikTok Hashtag Alert Bot

Hướng dẫn chi tiết từng bước để setup bot.

## 📑 Mục lục

1. [Tạo Telegram Bot](#1-tạo-telegram-bot)
2. [Setup Supabase Database](#2-setup-supabase-database)
3. [Cấu hình Local](#3-cấu-hình-local)
4. [Deploy lên VPS](#4-deploy-lên-vps)

---

## 1. Tạo Telegram Bot

### Bước 1: Mở BotFather

1. Mở Telegram
2. Tìm kiếm `@BotFather` hoặc truy cập https://t.me/botfather
3. Click **Start**

### Bước 2: Tạo Bot mới

Gửi lệnh:
```
/newbot
```

BotFather sẽ hỏi:

**1. Bot name** (tên hiển thị):
```
TikTok Hashtag Alert
```

**2. Bot username** (phải unique và kết thúc bằng `bot`):
```
your_tiktok_alert_bot
```

### Bước 3: Lưu Bot Token

BotFather sẽ trả về token dạng:
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

⚠️ **Lưu token này cẩn thận!** Không chia sẻ với ai.

### Bước 4: Tùy chỉnh Bot (Optional)

```
/setdescription - Mô tả bot
/setabouttext - Thông tin About
/setuserpic - Upload avatar cho bot
```

---

## 2. Setup Supabase Database

### Bước 1: Tạo Supabase Account

1. Truy cập https://supabase.com
2. Click **Start your project**
3. Đăng ký với GitHub hoặc email

### Bước 2: Tạo Project mới

1. Click **New Project**
2. Điền thông tin:
   - **Name**: `tiktok-hashtag-alert`
   - **Database Password**: Tạo password mạnh (lưu lại)
   - **Region**: Chọn gần VPS của bạn nhất
3. Click **Create new project**

⏳ Đợi 2-3 phút để Supabase setup database.

### Bước 3: Chạy Database Schema

1. Vào project vừa tạo
2. Mở **SQL Editor** (menu bên trái)
3. Click **New query**
4. Copy toàn bộ nội dung từ file `src/database/schema.sql`
5. Paste vào editor
6. Click **Run** hoặc nhấn `Ctrl+Enter`

✅ Bạn sẽ thấy thông báo "Success" và 3 tables được tạo:
- `tracked_creators`
- `posts`
- `bot_users`

### Bước 4: Lấy API Credentials

1. Click **Settings** → **API** (menu bên trái)
2. Lưu 2 thông tin sau:

**Project URL**:
```
https://abcdefghijk.supabase.co
```

**API Key** - Chọn `anon` hoặc `service_role`:
- `anon`: Dùng cho production (có giới hạn)
- `service_role`: Full quyền (recommended cho bot)

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 3. Cấu hình Local

### Bước 1: Clone hoặc tải code

```bash
cd c:\Dương\hashtag-alert
```

### Bước 2: Tạo Virtual Environment

```bash
# Tạo venv
python -m venv venv

# Kích hoạt (Windows)
.\venv\Scripts\activate

# Kích hoạt (Linux/Mac)
source venv/bin/activate
```

### Bước 3: Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### Bước 4: Cài đặt Playwright Browser

TikTokApi cần Playwright để chạy:

```bash
playwright install chromium
```

### Bước 5: Tạo file `.env`

```bash
# Copy template
cp .env.example .env

# Chỉnh sửa
notepad .env  # Windows
nano .env     # Linux
```

Điền thông tin:

```env
# Telegram Bot Token từ BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Supabase credentials
SUPABASE_URL=https://abcdefghijk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Monitoring settings
MONITOR_INTERVAL_MINUTES=10
MAX_POSTS_PER_CHECK=5

# Logging
LOG_LEVEL=INFO
```

### Bước 6: Test chạy

```bash
python main.py
```

Bạn sẽ thấy:
```
2026-02-09 14:00:00 - INFO - Supabase client initialized
2026-02-09 14:00:00 - INFO - Telegram bot setup complete
2026-02-09 14:00:00 - INFO - 🚀 TikTok Hashtag Alert Bot is running!
```

### Bước 7: Test trên Telegram

1. Mở Telegram và tìm bot của bạn
2. Gửi `/start`
3. Bot sẽ trả lời với welcome message
4. Thử `/add <tiktok_username>`

---

## 4. Deploy lên VPS

### Chuẩn bị VPS

**Yêu cầu tối thiểu:**
- OS: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- RAM: 512MB+
- Storage: 2GB+
- Python 3.10+

### A. Deploy với Systemd (Linux)

#### Bước 1: Upload code lên VPS

```bash
# Từ máy local
scp -r c:\Dương\hashtag-alert user@your-vps-ip:/home/user/

# Hoặc dùng git
ssh user@your-vps-ip
cd ~
git clone https://github.com/yourusername/hashtag-alert.git
cd hashtag-alert
```

#### Bước 2: Setup trên VPS

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Cài Python và dependencies
sudo apt install python3 python3-pip python3-venv -y

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt
playwright install chromium
playwright install-deps  # Cài system dependencies cho Playwright
```

#### Bước 3: Tạo `.env` file

```bash
nano .env
```

Paste configuration và save (`Ctrl+X`, `Y`, `Enter`)

#### Bước 4: Tạo Systemd Service

```bash
sudo nano /etc/systemd/system/hashtag-alert.service
```

Paste nội dung sau (thay `your_username` và đường dẫn):

```ini
[Unit]
Description=TikTok Hashtag Alert Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/hashtag-alert
Environment="PATH=/home/your_username/hashtag-alert/venv/bin"
ExecStart=/home/your_username/hashtag-alert/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/your_username/hashtag-alert/bot.log
StandardError=append:/home/your_username/hashtag-alert/error.log

[Install]
WantedBy=multi-user.target
```

#### Bước 5: Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable hashtag-alert

# Start service
sudo systemctl start hashtag-alert

# Kiểm tra status
sudo systemctl status hashtag-alert
```

#### Bước 6: Xem Logs

```bash
# Real-time logs
sudo journalctl -u hashtag-alert -f

# Hoặc từ file
tail -f ~/hashtag-alert/bot.log
```

### B. Deploy với PM2 (Cross-platform)

PM2 hoạt động trên Windows, Linux, Mac.

#### Bước 1: Cài Node.js và PM2

```bash
# Linux
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

# Windows
# Download và cài Node.js từ https://nodejs.org
npm install -g pm2
```

#### Bước 2: Start với PM2

```bash
cd /path/to/hashtag-alert

# Activate venv trước
source venv/bin/activate  # Linux
.\venv\Scripts\activate   # Windows

# Start với PM2
pm2 start main.py --name hashtag-alert --interpreter python
```

#### Bước 3: Setup Auto-start

```bash
# Generate startup script
pm2 startup

# Copy và chạy lệnh mà PM2 suggest

# Save process list
pm2 save
```

#### Bước 4: Quản lý PM2

```bash
# Xem logs
pm2 logs hashtag-alert

# Restart
pm2 restart hashtag-alert

# Stop
pm2 stop hashtag-alert

# Delete
pm2 delete hashtag-alert

# List processes
pm2 list
```

### C. Deploy với Docker (Advanced)

Tạo `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium && \
    playwright install-deps

COPY . .

CMD ["python", "main.py"]
```

Tạo `docker-compose.yml`:

```yaml
version: '3.8'

services:
  bot:
    build: .
    restart: always
    env_file:
      - .env
    volumes:
      - ./bot.log:/app/bot.log
```

Chạy:

```bash
docker-compose up -d
```

---

## 🔧 Troubleshooting

### Bot không start

```bash
# Kiểm tra .env file
cat .env

# Test import
python -c "from config.settings import settings; settings.validate()"
```

### Playwright errors

```bash
# Cài lại browsers
playwright install chromium
playwright install-deps
```

### Permission denied

```bash
# Fix ownership
sudo chown -R your_username:your_username /path/to/hashtag-alert

# Fix permissions
chmod +x main.py
```

---

**✅ Hoàn tất!** Bot của bạn đã sẵn sàng hoạt động 24/7 trên VPS.
