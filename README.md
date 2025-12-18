# Home Network Monitor

A full-stack network monitoring solution that tracks ping latency to multiple hosts with a real-time dashboard.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Node](https://img.shields.io/badge/node-18%2B-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start (Docker)](#quick-start-with-docker-recommended)
- [Manual Installation](#manual-installation)
- [Configuration](#configuration)
- [Usage](#running-the-application)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## ✨ Features

- **Real-time Monitoring**: Automatically pings configured hosts at set intervals (default: 60 seconds)
- **120-Day Data Retention**: Stores ping history for up to 120 days
- **Interactive Dashboard**: React-based frontend with real-time charts and status cards
- **Multiple Time Ranges**: View latency data from 1 hour to 120 days
- **Multi-Host Support**: Monitor multiple hosts simultaneously
- **Statistics**: Track average latency, uptime percentage, and success rates
- **Automatic Cleanup**: Daily job removes old data to maintain storage efficiency

## Architecture

### Backend (Python + FastAPI)
- **FastAPI**: High-performance REST API
- **SQLite**: Lightweight database with optimized indexes
- **APScheduler**: Periodic ping execution and cleanup jobs
- **pythonping**: Cross-platform ICMP ping implementation

### Frontend (React + TypeScript)
- **Vite**: Modern build tool with fast hot module replacement
- **Chart.js**: High-performance time-series charting
- **SWR**: Data fetching with automatic revalidation
- **Responsive Design**: Works on desktop and mobile devices

## 📸 Screenshots

**Dashboard Overview**
- Real-time status cards showing host availability and latency
- Interactive charts with multiple time ranges (1h to 120 days)
- Detailed statistics including average latency, min/max, and uptime percentage

## 🚀 Prerequisites

### Option 1: Docker (Recommended) ⭐
- **Docker** 20.10 or higher (includes Docker Compose v2)

### Option 2: Manual Installation
- **Python** 3.8 or higher
- **Node.js** 18 or higher
- **npm** or yarn

## 🐳 Quick Start with Docker (Recommended)

The easiest and fastest way to get started.

> **Note:** This guide uses the modern `docker compose` command (Docker Compose v2). If you see errors with `docker-compose` (hyphenated), make sure you're using `docker compose` (space) instead. Docker Compose v2 comes bundled with Docker 20.10+.

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd home-network-monitor
```

### Step 2: (Optional) Customize Monitored Hosts
Edit `docker-compose.yml` and modify the `MONITORED_HOSTS` environment variable:
```yaml
- MONITORED_HOSTS=router.local,8.8.8.8,1.1.1.1,192.168.1.1
```

### Step 3: Start the Application
```bash
docker compose up -d
```

That's it! The application is now running.

### Step 4: Access the Application

Open your browser and navigate to:
- **📊 Dashboard**: http://localhost
- **🔧 API Docs**: http://localhost:8000/docs
- **💚 Health Check**: http://localhost:8000/health

### Viewing Logs
```bash
# View all logs
docker compose logs -f

# View only backend logs
docker compose logs -f backend

# View only frontend logs
docker compose logs -f frontend
```

### Stopping the Application
```bash
# Stop containers (keeps data)
docker compose down

# Stop and remove all data
docker compose down -v
```

### 🔧 Docker Configuration Options

Edit `docker-compose.yml` to customize these settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `MONITORED_HOSTS` | Comma-separated list of hosts to ping | `router.local,8.8.8.8,1.1.1.1` |
| `PING_INTERVAL` | Seconds between pings | `60` |
| `PING_TIMEOUT` | Ping timeout in seconds | `5` |
| `PING_RETRIES` | Number of retry attempts | `2` |
| `RETENTION_DAYS` | Days to keep ping data | `120` |
| `CLEANUP_HOUR` | Hour to run daily cleanup (0-23) | `2` |

**Example customization:**
```yaml
environment:
  - MONITORED_HOSTS=192.168.1.1,192.168.1.254,google.com,1.1.1.1
  - PING_INTERVAL=30
  - RETENTION_DAYS=90
```

### 🎯 Common Docker Commands

**Managing the Application:**
```bash
# Start all services
docker compose up -d

# Stop all services (keeps data)
docker compose down

# Restart services
docker compose restart

# Rebuild after code changes
docker compose up -d --build

# View service status
docker compose ps
```

**Viewing Logs:**
```bash
# Follow all logs
docker compose logs -f

# View last 100 lines
docker compose logs --tail=100

# View specific service
docker compose logs -f backend
```

**Data Management:**
```bash
# Backup database
cp ./data/pings.db ./data/pings-backup-$(date +%Y%m%d).db

# Restore database
docker compose stop backend
cp ./data/pings-backup.db ./data/pings.db
docker compose start backend

# Delete all data (WARNING: irreversible!)
docker compose down -v
rm -rf ./data
```

### 💾 Data Persistence

Your ping data is automatically saved in the `./data/` directory on your host machine:
- **Database location**: `./data/pings.db`
- **Persistence**: Data survives container restarts and rebuilds
- **Backup**: Simply copy the database file to back up your data

## 💻 Manual Installation

If you prefer not to use Docker, you can install and run the components manually.

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd home-network-monitor
```

### Step 2: Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create configuration file
cp .env.example .env

# Edit configuration (optional)
nano .env
```

### Step 3: Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# For development - starts dev server
npm run dev

# OR for production - builds static files
npm run build
```

### Step 4: Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## ⚙️ Configuration

### Environment Variables (Manual Installation)

For manual installations, edit `backend/.env`:

```ini
# Server Configuration
PORT=8000
HOST=0.0.0.0

# Ping Configuration
PING_INTERVAL=60          # Seconds between pings
PING_TIMEOUT=5            # Ping timeout in seconds
PING_RETRIES=2            # Number of retry attempts

# Database
DATABASE_PATH=./data/pings.db

# Data Retention
RETENTION_DAYS=120        # Days to keep ping data
CLEANUP_HOUR=2            # Hour to run cleanup (0-23)

# Monitored Hosts (comma-separated)
MONITORED_HOSTS=router.local,8.8.8.8,1.1.1.1

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 🏠 Adding/Removing Monitored Hosts

**Method 1: Configuration File (recommended for initial setup)**

Edit the `MONITORED_HOSTS` variable in:
- Docker: `docker-compose.yml`
- Manual: `backend/.env`

```yaml
MONITORED_HOSTS=192.168.1.1,google.com,8.8.8.8,router.local
```

Then restart the application:
```bash
# Docker
docker compose restart backend

# Manual
# Stop and restart the backend server
```

**Method 2: API (for runtime changes)**

Use the API endpoints to add/remove hosts dynamically:

```bash
# Add a new host
curl -X POST http://localhost:8000/api/hosts \
  -H "Content-Type: application/json" \
  -d '{"hostname": "192.168.1.10", "display_name": "My Device"}'

# Delete a host (replace {id} with the host ID)
curl -X DELETE http://localhost:8000/api/hosts/{id}
```

Or use the interactive API documentation at http://localhost:8000/docs

## 🚀 Usage

### Accessing the Dashboard

Once the application is running (via Docker or manually), open your browser:

1. **Dashboard**: http://localhost (Docker) or http://localhost:5173 (Manual)
   - View real-time status cards for all monitored hosts
   - Select time ranges: 1h, 6h, 24h, 7d, 30d, 90d, 120d
   - View interactive latency charts
   - Check detailed statistics

2. **API Documentation**: http://localhost:8000/docs
   - Interactive Swagger UI
   - Test API endpoints directly
   - View request/response schemas

3. **Health Check**: http://localhost:8000/health
   - Check if backend is running
   - View scheduler status

### 📊 Using the Dashboard

1. **Select Hosts**: Use the host dropdown to choose which hosts to view
2. **Choose Time Range**: Click time range buttons (1h, 24h, 7d, etc.)
3. **View Charts**: Charts automatically update with selected hosts and time range
4. **Monitor Status**: Status cards show real-time information for each host

## 🎯 Production Deployment

### Docker Production (Recommended)

For production, simply run Docker Compose in detached mode:

```bash
# Start services
docker compose up -d

# Services will automatically restart on:
# - Container failure
# - System reboot (unless explicitly stopped)
```

**Production Best Practices:**

1. **Persistent Storage**: Database is already persisted in `./data/`
2. **Monitoring**: Check logs regularly with `docker compose logs -f`
3. **Backups**: Schedule regular database backups (see Data Management section)
4. **Updates**: Rebuild containers after pulling new code: `docker compose up -d --build`

### Adding HTTPS (Reverse Proxy)

For secure access, add a reverse proxy with SSL. Example using nginx:

**1. Install nginx on host:**
```bash
sudo apt install nginx
```

**2. Create nginx config** (`/etc/nginx/sites-available/network-monitor`):
```nginx
server {
    listen 80;
    server_name monitor.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monitor.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/monitor.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monitor.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**3. Enable and restart:**
```bash
sudo ln -s /etc/nginx/sites-available/network-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Manual Production Deployment (Systemd)

For manual installations without Docker:

Create `/etc/systemd/system/network-monitor.service`:

```ini
[Unit]
Description=Home Network Monitor Backend
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/home-network-monitor/backend
Environment="PATH=/path/to/home-network-monitor/backend/venv/bin"
ExecStart=/path/to/home-network-monitor/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable network-monitor
sudo systemctl start network-monitor
```

#### Manual Frontend Deployment

```bash
cd frontend

# Build for production
npm run build

# Serve with nginx or any static file server
```

The build output will be in `frontend/dist/`

## 📚 API Documentation

The API provides full access to manage hosts and retrieve ping data.

**Interactive Documentation**: http://localhost:8000/docs (Swagger UI)

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hosts` | List all configured hosts |
| POST | `/api/hosts` | Add a new host |
| DELETE | `/api/hosts/{id}` | Remove a host |
| GET | `/api/current-status` | Current status of all hosts |
| GET | `/api/ping-data/{hostname}` | Historical ping data |
| GET | `/api/health` | Backend health check |

### Example API Calls

**Get all hosts:**
```bash
curl http://localhost:8000/api/hosts
```

**Add a new host:**
```bash
curl -X POST http://localhost:8000/api/hosts \
  -H "Content-Type: application/json" \
  -d '{"hostname": "192.168.1.1", "display_name": "Router"}'
```

**Get current status:**
```bash
curl http://localhost:8000/api/current-status
```

**Get ping history:**
```bash
curl "http://localhost:8000/api/ping-data/8.8.8.8?start=1702468800000&end=1702555200000"
```

For detailed documentation and to test endpoints interactively, visit http://localhost:8000/docs

## Database Schema

### Tables

**ping_results**
- Stores ping result records
- Indexed on `(host, timestamp)` for fast time-range queries
- ~1.7M records for typical usage (10 hosts × 60s interval × 120 days)

**hosts**
- Stores host configuration
- hostname, display_name, enabled status

## Performance

- **Storage**: ~82 MB for 120 days of data (10 hosts, 60s interval)
- **Query Performance**: Optimized indexes enable sub-second queries
- **Concurrent Access**: SQLite WAL mode for better read/write concurrency
- **Frontend**: Chart.js handles 10,000+ data points smoothly

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Docker Issues

**Container Won't Start**
```bash
# Check logs for specific service
docker compose logs backend
docker compose logs frontend

# Check container status
docker compose ps

# Rebuild containers
docker compose down
docker compose build --no-cache
docker compose up -d
```

**Permission Errors with Ping**
The backend container runs ping with proper capabilities. If you still encounter issues:
```bash
# Give the container NET_RAW capability
# Edit docker-compose.yml and add under backend service:
cap_add:
  - NET_RAW
```

**Port Already in Use**
```bash
# Check what's using the ports
sudo lsof -i :80
sudo lsof -i :8000

# Either stop the conflicting service or change ports in docker-compose.yml
```

**Database Permission Issues**
```bash
# Ensure the data directory has correct permissions
mkdir -p ./data
chmod 755 ./data

# If running as non-root user, ensure ownership
chown -R $USER:$USER ./data
```

**Containers Keep Restarting**
```bash
# Check health status
docker compose ps

# View detailed logs
docker compose logs -f --tail=100

# Common issues:
# - Backend can't connect to database
# - Frontend can't reach backend
# - Environment variables misconfigured
```

**Cannot Reach Monitored Hosts**
```bash
# Make sure containers can reach your network hosts
# Test from within the container
docker compose exec backend ping -c 3 192.168.1.1

# If hosts are on local network, you may need host networking:
# Edit docker-compose.yml and add under backend service:
network_mode: "host"
```

### Backend Issues (Manual Installation)

**Ping Permission Errors**
```bash
# On Linux, you may need to allow ICMP for your user
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
```

**Database Locked Errors**
- Ensure only one backend instance is running
- Check that WAL mode is enabled

**Import Errors**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Port Already in Use**
```bash
# Change port in vite.config.ts or use a different port
npm run dev -- --port 3000
```

**API Connection Errors**
- Check that backend is running on port 8000
- Verify CORS_ORIGINS includes the frontend URL
- Check browser console for detailed errors

## 💻 Development

### Project Structure

```
home-network-monitor/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── config/         # Database & settings
│   │   ├── services/       # Business logic (ping, scheduler, cleanup)
│   │   ├── repositories/   # Data access layer
│   │   ├── routers/        # API endpoints
│   │   ├── models/         # Pydantic schemas
│   │   └── main.py         # Application entry point
│   ├── Dockerfile          # Backend container definition
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks (SWR)
│   │   ├── services/      # API client (axios)
│   │   ├── types/         # TypeScript type definitions
│   │   ├── App.tsx        # Main component
│   │   └── App.css        # Styling
│   ├── Dockerfile         # Frontend container definition
│   ├── nginx.conf         # Nginx configuration
│   └── package.json       # Node dependencies
│
├── docker-compose.yml      # Docker orchestration
├── DOCKER.md              # Detailed Docker documentation
└── README.md              # This file
```

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- SQLite (database)
- APScheduler (task scheduling)
- pythonping (ICMP ping)
- Pydantic (data validation)

**Frontend:**
- React + TypeScript
- Vite (build tool)
- Chart.js (charting)
- SWR (data fetching)
- Axios (HTTP client)

### Development Workflow

1. **Make changes** to backend or frontend code
2. **Test locally**:
   - Docker: `docker compose up -d --build`
   - Manual: Restart backend/frontend servers
3. **Test functionality** in browser
4. **Commit changes** to git

### Adding New Features

**Backend Endpoints:**
Edit `backend/app/routers/api.py` to add new API routes

**Frontend Components:**
Create new components in `frontend/src/components/`

**Database Schema:**
Modify `backend/app/config/database.py` for schema changes

## 📖 Additional Resources

- **[DOCKER.md](DOCKER.md)** - Comprehensive Docker deployment guide
  - Advanced Docker commands
  - Troubleshooting Docker issues
  - Production deployment with Docker
  - Security hardening
  - CI/CD integration

- **API Documentation** - Interactive API docs at http://localhost:8000/docs
  - Full endpoint reference
  - Request/response schemas
  - Try endpoints directly

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 💬 Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Questions**: Use GitHub Discussions for questions
- **Documentation**: Check [DOCKER.md](DOCKER.md) for Docker-specific help

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - JavaScript library for building UIs
- [Chart.js](https://www.chartjs.org/) - JavaScript charting library
- [Docker](https://www.docker.com/) - Containerization platform

---

**Made with ❤️ for network monitoring**
