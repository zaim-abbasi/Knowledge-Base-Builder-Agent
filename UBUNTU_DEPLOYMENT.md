# Ubuntu Server Deployment Guide
## Knowledge Base Builder Agent

This guide will help you deploy your Knowledge Base Builder Agent to your own Ubuntu server.

---

## Prerequisites

1. **Ubuntu Server** (20.04 LTS or 22.04 LTS recommended)
2. **SSH access** to your server
3. **Domain name** (optional, but recommended) or IP address
4. **Basic Linux command knowledge**

---

## Step 1: Initial Server Setup

### 1.1 Connect to Your Server

```bash
ssh username@your-server-ip
# or
ssh username@your-domain.com
```

### 1.2 Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.3 Install Python and Required Tools

```bash
sudo apt install -y python3 python3-pip python3-venv git nginx
```

---

## Step 2: Set Up Application Directory

### 2.1 Create Application User (Recommended)

```bash
sudo adduser --disabled-password --gecos "" knowledgebuilder
sudo su - knowledgebuilder
```

### 2.2 Create Application Directory

```bash
mkdir -p ~/knowledge-builder-agent
cd ~/knowledge-builder-agent
```

### 2.3 Clone or Upload Your Code

**Option A: Using Git (Recommended)**
```bash
git clone https://github.com/yourusername/your-repo-name.git .
# or if repo is private, use SSH key
```

**Option B: Upload via SCP**
```bash
# From your local machine
scp -r "Knowledge Builder"/* username@your-server-ip:~/knowledge-builder-agent/
```

---

## Step 3: Set Up Python Environment

### 3.1 Create Virtual Environment

```bash
cd ~/knowledge-builder-agent
python3 -m venv venv
source venv/bin/activate
```

### 3.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

---

## Step 4: Test Locally

### 4.1 Test the Application

```bash
# Still in virtual environment
python api_server.py
```

### 4.2 Test in Another Terminal

```bash
curl http://localhost:5000/health
```

If it works, stop the server (Ctrl+C) and proceed.

---

## Step 5: Configure Gunicorn

### 5.1 Create Gunicorn Configuration

Create `gunicorn_config.py`:

```python
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

### 5.2 Test Gunicorn

```bash
source venv/bin/activate
gunicorn -c gunicorn_config.py api_server:app
```

Test: `curl http://localhost:5000/health`

---

## Step 6: Set Up Systemd Service

### 6.1 Create Service File

```bash
sudo nano /etc/systemd/system/knowledge-builder-agent.service
```

### 6.2 Add This Content:

```ini
[Unit]
Description=Knowledge Base Builder Agent
After=network.target

[Service]
User=knowledgebuilder
Group=knowledgebuilder
WorkingDirectory=/home/knowledgebuilder/knowledge-builder-agent
Environment="PATH=/home/knowledgebuilder/knowledge-builder-agent/venv/bin"
ExecStart=/home/knowledgebuilder/knowledge-builder-agent/venv/bin/gunicorn -c gunicorn_config.py api_server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Important:** Replace `knowledgebuilder` with your actual username if different.

### 6.3 Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable knowledge-builder-agent
sudo systemctl start knowledge-builder-agent
sudo systemctl status knowledge-builder-agent
```

### 6.4 Check Logs

```bash
sudo journalctl -u knowledge-builder-agent -f
```

---

## Step 7: Configure Nginx Reverse Proxy

### 7.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/knowledge-builder-agent
```

### 7.2 Add This Content:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 7.3 Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/knowledge-builder-agent /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

---

## Step 8: Set Up SSL with Let's Encrypt (Recommended)

### 8.1 Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 8.2 Get SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com
```

Follow the prompts. Certbot will automatically configure Nginx for HTTPS.

### 8.3 Auto-Renewal (Automatic)

Certbot sets up auto-renewal automatically. Test it:

```bash
sudo certbot renew --dry-run
```

---

## Step 9: Configure Firewall

### 9.1 Set Up UFW

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## Step 10: Test Deployment

### 10.1 Test Health Check

```bash
curl http://your-domain.com/health
# or
curl https://your-domain.com/health
```

### 10.2 Test Wiki Update

```bash
curl -X POST https://your-domain.com/message \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-001",
    "agent_name": "KnowledgeBaseBuilderAgent",
    "intent": "update_wiki",
    "input": {
      "text": "# Test Wiki\n\nTest entry.",
      "metadata": {"update_mode": "overwrite"}
    },
    "context": {
      "user_id": "test_user",
      "timestamp": "2025-01-21T10:00:00Z"
    }
  }'
```

---

## Step 11: Update Supervisor Registry

Update your Supervisor's agent registry with:

```json
{
  "name": "KnowledgeBaseBuilderAgent",
  "description": "Updates team wiki from daily work interactions",
  "intents": ["update_wiki"],
  "type": "http",
  "endpoint": "https://your-domain.com/message",
  "healthcheck": "https://your-domain.com/health",
  "timeout_ms": 10000
}
```

**Important:** Replace `your-domain.com` with your actual domain or IP.

---

## Step 12: Set Up LTM Directory Permissions

```bash
cd ~/knowledge-builder-agent
chmod 755 LTM
chmod 644 LTM/*.json 2>/dev/null || true
```

---

## Useful Commands

### Check Service Status

```bash
sudo systemctl status knowledge-builder-agent
```

### View Logs

```bash
# Service logs
sudo journalctl -u knowledge-builder-agent -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Service

```bash
sudo systemctl restart knowledge-builder-agent
```

### Reload Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Update Code

```bash
cd ~/knowledge-builder-agent
source venv/bin/activate
git pull  # if using Git
# or upload new files
sudo systemctl restart knowledge-builder-agent
```

---

## Troubleshooting

### Issue: Service Won't Start

**Check:**
```bash
sudo journalctl -u knowledge-builder-agent -n 50
```

**Common fixes:**
- Check file paths in service file
- Verify virtual environment path
- Check Python version compatibility
- Ensure all dependencies installed

### Issue: 502 Bad Gateway

**Check:**
1. Is Gunicorn running?
   ```bash
   sudo systemctl status knowledge-builder-agent
   ```
2. Check Gunicorn logs
3. Verify Nginx proxy_pass URL matches Gunicorn bind address

### Issue: Permission Denied

**Fix:**
```bash
sudo chown -R knowledgebuilder:knowledgebuilder ~/knowledge-builder-agent
chmod 755 ~/knowledge-builder-agent
chmod 755 ~/knowledge-builder-agent/LTM
```

### Issue: Port Already in Use

**Check:**
```bash
sudo netstat -tlnp | grep 5000
```

**Fix:** Kill the process or change port in gunicorn_config.py

### Issue: LTM Files Not Persisting

**Fix:**
```bash
chmod 755 LTM
chmod 644 LTM/*.json
```

---

## Security Best Practices

1. **Keep System Updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Use SSH Keys** (disable password auth):
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart sshd
   ```

3. **Set Up Fail2Ban:**
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

4. **Regular Backups:**
   ```bash
   # Backup LTM files
   tar -czf backup-$(date +%Y%m%d).tar.gz LTM/
   ```

5. **Monitor Logs:**
   ```bash
   # Set up log rotation
   sudo nano /etc/logrotate.d/knowledge-builder-agent
   ```

---

## Production Checklist

- [ ] Server updated and secured
- [ ] Application deployed and tested
- [ ] Gunicorn service running
- [ ] Nginx configured and tested
- [ ] SSL certificate installed (HTTPS)
- [ ] Firewall configured
- [ ] Service auto-starts on boot
- [ ] Logs accessible
- [ ] LTM directory permissions correct
- [ ] Supervisor registry updated
- [ ] End-to-end integration tested

---

## Next Steps

1. ✅ Deploy to Ubuntu server
2. ✅ Test all endpoints
3. ✅ Update Supervisor registry
4. ✅ Test integration with Supervisor
5. ✅ Monitor logs and performance
6. ✅ Set up backups

---

## Support

- **Gunicorn Docs:** https://docs.gunicorn.org
- **Nginx Docs:** https://nginx.org/en/docs/
- **Systemd Docs:** https://www.freedesktop.org/software/systemd/man/systemd.service.html

Your agent should now be live at: `https://your-domain.com` 🚀

