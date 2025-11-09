# RouterDown - Automatic Network Monitor & Router Recovery

A Python-based network monitoring tool that detects internet connectivity issues and automatically resets your router when needed. Perfect for diagnosing and recovering from router failures in home networks.

## The Problem

Routers sometimes hang or lose internet connectivity, requiring a manual reset. This tool solves that by:

1. **Continuously monitoring** your internet connection
2. **Detecting** when your router loses internet access (even if local network still works)
3. **Automatically resetting** your router via Home Assistant webhook
4. **Logging** all outages and recovery events for diagnostics

## How It Works

The script runs continuously on a machine in your internal network and:

- Pings Google's DNS server (8.8.8.8) every 30 seconds to verify internet connectivity
- If connection fails 3 times in a row, it triggers a router reset via Home Assistant webhook
- Waits 2 minutes after reset for router to come back online
- Logs all connection state changes with timestamps
- Tracks downtime duration for each outage

## Requirements

- Python 3.x
- `requests` library
- Home Assistant with a configured webhook for router control
- A machine on your network that stays running (Raspberry Pi, NAS, always-on PC, etc.)

## Setup

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Configure Home Assistant Webhook

You'll need a Home Assistant automation that can power cycle your router. The webhook URL in `main.py` needs to be updated to match your setup:

```python
URL_FOR_WEBHOOK = 'https://192.168.1.116:8123/api/webhook/YOUR_WEBHOOK_ID'
```

Replace with your Home Assistant IP and webhook ID.

### 3. Adjust Monitoring Parameters (Optional)

Edit the constants at the top of `main.py` to customize behavior:

```python
SLEEP_WHILE_OFFLINE = 60          # Check every 60 seconds when offline
SLEEP_WHILE_ONLINE = 30           # Check every 30 seconds when online
SLEEP_AFTER_RESET = 120           # Wait 2 minutes after resetting router
NUMBER_OF_FAILED_PINGS_TO_RESET = 3   # Reset after 3 consecutive failures
MAX_NUMBER_OF_RESETS = 3          # Max resets per outage (prevents loops)
```

### 4. Run the Monitor

```bash
python main.py
```

The script will:
- Check if internet is available
- Start monitoring once connection is acquired
- Run indefinitely until you stop it (Ctrl+C)

## Running with Docker (Recommended for Raspberry Pi)

Docker provides an easier way to run this on your Raspberry Pi without worrying about Python dependencies.

### 1. Quick Start with Docker Compose

Edit `docker-compose.yml` to configure your Home Assistant details:

```yaml
environment:
  - HA_HOST=192.168.1.116          # Your Home Assistant IP
  - HA_PORT=8123                    # Your Home Assistant port
  - HA_WEBHOOK_ID=your-webhook-id  # Your webhook ID
  - HA_USE_HTTPS=true              # true or false
```

Then run:

```bash
docker-compose up -d
```

Logs will be saved to `./logs/networkinfo.log` on your host machine.

### 2. View Logs

```bash
# View real-time logs
docker-compose logs -f

# View log file
cat logs/networkinfo.log
```

### 3. Stop/Restart

```bash
# Stop the container
docker-compose down

# Restart after config changes
docker-compose restart

# Update and rebuild
docker-compose up -d --build
```

### 4. Alternative: Using .env File

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
HA_HOST=192.168.1.116
HA_PORT=8123
HA_WEBHOOK_ID=your-webhook-id-here
HA_USE_HTTPS=true
```

Update `docker-compose.yml` to use the .env file:

```yaml
services:
  routerdown:
    build: .
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    network_mode: "host"
    restart: unless-stopped
```

### 5. Manual Docker Build (without docker-compose)

```bash
# Build the image
docker build -t routerdown .

# Run the container
docker run -d \
  --name routerdown \
  --restart unless-stopped \
  --network host \
  -e HA_HOST=192.168.1.116 \
  -e HA_PORT=8123 \
  -e HA_WEBHOOK_ID=your-webhook-id \
  -e HA_USE_HTTPS=true \
  -v $(pwd)/logs:/app/logs \
  routerdown

# View logs
docker logs -f routerdown
```

## Running Without Docker

### Run as Background Service (systemd)

For Linux/Raspberry Pi, create a systemd service to run this automatically:

```ini
[Unit]
Description=Router Network Monitor
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/routerdown
ExecStart=/usr/bin/python3 /path/to/routerdown/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Save as `/etc/systemd/system/routerdown.service`, then:

```bash
sudo systemctl enable routerdown
sudo systemctl start routerdown
```

## Monitoring Logs

All events are logged to `networkinfo.log` in the same directory:

```
15-Oct-24 17:10:49 - CONNECTION ACQUIRED
15-Oct-24 17:10:49 - connection acquired at: 2024-10-15 17:10:49
15-Oct-24 17:10:49 - monitoring started at: 2024-10-15 17:10:49
15-Oct-24 17:45:32 - disconnected at: 2024-10-15 17:45:32
15-Oct-24 17:47:15 - RESETTING ROUTER NOW
15-Oct-24 17:49:42 - connected again: 2024-10-15 17:49:42
15-Oct-24 17:49:42 - connection was unavailable for: 0:04:10
```

This helps you:
- Track when outages occur
- See how long each outage lasted
- Determine if router resets are helping
- Identify patterns (time of day, frequency)

## How Connection Testing Works

Instead of ICMP ping (which often requires admin/root privileges), this tool:

1. Opens a TCP connection to Google's public DNS server (8.8.8.8) on port 53
2. Uses a 3-second timeout
3. Returns success if connection is established, failure otherwise

This method:
- Works without elevated privileges
- Tests actual internet connectivity (not just local network)
- Is more reliable than DNS queries which might be cached

## Troubleshooting

**Script says "CONNECTION NOT ACQUIRED" and waits forever**
- Check that your internet is actually working
- Verify you can reach 8.8.8.8 from your network
- Check firewall rules aren't blocking outbound connections to port 53

**Router isn't resetting**
- Verify the webhook URL is correct
- Check Home Assistant logs for webhook errors
- Test the webhook manually with `curl -X POST <webhook-url>`
- Check that SSL certificate issues aren't blocking requests (script uses `verify=False`)

**Too many/few resets happening**
- Adjust `NUMBER_OF_FAILED_PINGS_TO_RESET` (increase to be more patient)
- Adjust `SLEEP_WHILE_OFFLINE` (longer = fewer checks when offline)
- Check `MAX_NUMBER_OF_RESETS` to prevent reset loops

## License

This is a personal network monitoring tool. Use and modify as needed for your home network.
