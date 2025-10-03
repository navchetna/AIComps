# Qdrant Instance Manager - Quick Start

A simple API service that creates personal Qdrant vector database instances for each user.

## Creating Your Instance

To create your personal Qdrant instance, make a POST request with your username:

```bash
curl -X POST "http://localhost:8060/create_instance?user=YOUR_USERNAME" | jq
```

**Example response:**
```json
{
  "user": "john",
  "ip": "127.0.0.1",
  "port": 49152,
  "ttl": 600
}
```

## Important Information

### Save Your Port Number!

**The `port` number in the response is your personal database connection.** You'll need this port to connect to your Qdrant instance.

✅ **Write it down or save it somewhere**  
✅ **Use this port for all your database operations**

### Instance Lifetime

- Your instance will remain active for **10 minutes (600 seconds)**
- After 10 minutes of inactivity, the instance will be automatically cleaned up
- You can create a new instance anytime using the same username

### Re-creating an Instance

If you make another request with the same username while your instance is still active:

```bash
curl -X POST "http://localhost:8000/create_instance?user=john"
```

**Response:**
```json
{
  "message": "Instance already exists for john",
  "user": "john",
  "ip": "127.0.0.1",
  "port": 49152,
  "ttl": 423
}
```

The `ttl` field shows how many seconds remain before your instance expires.

## Connecting to Your Instance

Once you have your port number, you can connect to your Qdrant instance at:

```
http://127.0.0.1:YOUR_PORT
```

**Example:**
If your port is `49152`, connect to: `http://127.0.0.1:49152`

You can use this connection string with:
- Qdrant client libraries
- HTTP requests
- The Qdrant web UI (if exposed)

## Quick Reference

| Field | Description |
|-------|-------------|
| `user` | Your username |
| `ip` | Always `127.0.0.1` (localhost) |
| `port` | **Your personal database port - SAVE THIS!** |
| `ttl` | Time remaining before instance expires (seconds) |

---

**Remember:** Keep your port number handy - you'll need it to work with your database!