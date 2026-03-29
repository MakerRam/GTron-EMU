# API Security & CORS Configuration

## CORS (Cross-Origin Resource Sharing)

The API server includes CORS headers enabled by default using `flask-cors`.

### How CORS Works

CORS allows web browsers to make requests to the API from different origins:

```
Browser origin:    http://localhost:8000
API origin:        http://localhost:5000
                   ↓
flask-cors adds headers:
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, OPTIONS
  Access-Control-Allow-Headers: Content-Type
```

### Current Configuration

**Enabled by default for all origins:**

```python
# firmware_emulator/src/api_server.py, line ~36
CORS(app)  # Allows all origins to access all endpoints
```

**Allowed methods:** GET (query only, read-only)

### Security Implications

#### Current Setup (Development)

✅ **Safe for**:
- Local development (localhost)
- Private networks (192.168.x.x)
- Testing environments

⚠️ **Risks**:
- Public internet exposure: Any website can poll your API
- No authentication: State data is publicly readable
- No rate limiting: Possible DoS attacks

#### Production Recommendations

If deploying to public internet:

1. **Restrict Origins**:
```python
CORS(app, origins=["https://yourdomain.com"])
```

2. **Add Authentication**:
```python
@app.route('/api/state')
def get_state():
    token = request.headers.get('Authorization')
    if not validate_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(exporter.get_state_dict())
```

3. **Enable HTTPS**:
```bash
python firmware_emulator/src/main.py --port COM3 --ssl-cert cert.pem --ssl-key key.pem
```

4. **Add Rate Limiting**:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/state')
@limiter.limit("60 per minute")  # Max 60 requests per minute
def get_state():
    ...
```

## Data Security

### What Data is Exposed

**Via API endpoints:**
- Device state (guide positions, motor speeds, sensor values)
- Lamp colors and camera flags
- System status (door locked, E-stop, power)
- Last executed command

**Not exposed:**
- LabVIEW application code or logic
- Machine configuration parameters
- User credentials or authentication tokens
- Internal system metrics

### Recommendations

1. **Only use on private networks** (development, lab testing)
2. **Disable API in production** if not needed: `--no-api`
3. **Use VPN** if accessing from external networks
4. **Monitor logs** for suspicious activity (too many requests, invalid patterns)
5. **Keep Python/Flask updated** for security patches

## API Endpoint Security

### GET /health
- **Risk**: Low
- **Data exposed**: API version only
- **Typical use**: Health checks, connection monitoring

### GET /api/state
- **Risk**: Medium
- **Data exposed**: Complete device state (can infer operations)
- **Typical use**: Full monitoring, diagnostics

### GET /api/state/summary
- **Risk**: Medium
- **Data exposed**: Essential state only (reduced surface area)
- **Typical use**: High-frequency dashboard polling

## Logging & Audit Trail

All API requests are logged to `logs/` directory:

```
logs/
├── emulator_YYYYMMDD_HHMMSS.log       # API requests logged here
├── serial_YYYYMMDD_HHMMSS.log         # Serial traffic
├── commands_YYYYMMDD_HHMMSS.log       # State transitions
└── debug_YYYYMMDD_HHMMSS.log          # Detailed debug info
```

**To audit API usage:**

```bash
grep "GET /api" logs/emulator_*.log | wc -l  # Count API requests
grep -i error logs/emulator_*.log            # Find errors
```

## Firewall Rules (Linux/macOS)

### Allow only localhost:

```bash
# Block external access to API port
sudo ufw deny in 5000  # UFW
sudo pfctl -e        # PF (macOS)
```

### Allow specific IP:

```bash
sudo ufw allow from 192.168.1.100 to any port 5000
```

### View current rules:

```bash
sudo ufw status
sudo pfctl -s rules
```

## Testing Security

### Verify CORS headers:

```bash
curl -v http://localhost:5000/health
# Look for: Access-Control-Allow-Origin header
```

### Check for open ports:

```bash
netstat -tulpn | grep 5000   # Linux
lsof -i :5000                 # macOS
netstat -ano | findstr :5000  # Windows
```

### Simulate attack (local testing only):

```bash
# Rapid requests (should not crash or leak data)
for i in {1..1000}; do curl -s http://localhost:5000/api/state > /dev/null; done

# Memory usage should remain stable
# Monitor: ps aux | grep main.py
```

## Configuration for Different Environments

### Development (Localhost)
```bash
python3 firmware_emulator/src/main.py --port COM3
# CORS: Enabled (all origins)
# Authentication: None
# HTTPS: No
# Rate limiting: No
```

### Lab Testing (Private Network)
```bash
python3 firmware_emulator/src/main.py --port COM3 --api-port 5000
# CORS: Enabled (all origins on private network)
# Authentication: None
# HTTPS: No
# Rate limiting: No
# Firewall: Restrict to 192.168.x.x subnet only
```

### Production (Public Internet)
```bash
# Not recommended - use --no-api instead
# If required, implement:
# - CORS origin restriction
# - Token-based authentication
# - HTTPS/TLS encryption
# - Rate limiting per IP
# - VPN requirement
# - Firewall whitelist
# - Audit logging
```

---

**Summary**: Current setup is suitable for **development and testing only**. For production or public deployment, implement the security measures outlined above.
