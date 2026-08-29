# itch.io

## What Data We Can Extract (Oracle)

**API:** `https://itch.io/api/1`
**Status:** ❌ Needs API key
**Items:** 0 (not accessible without auth)

### Endpoints (need API key)
```
GET /my-games              — list my games
POST /my-games             — create game
PUT /my-games/{id}         — update game
POST /my-games/{id}/uploads — upload build
```

### CLI (butler)
```bash
butler login                    # authenticate
butler upload <dir> <user>/<game>  # publish
butler push <dir> <user>/<game>:<channel>  # update
```

## How to Set Up (get-me-money)

### Human Steps (required)
1. Go to itch.io
2. Create account
3. Go to itch.io/my-api-keys
4. Generate API key

### Agent Steps (after human setup)
```bash
# Install butler CLI
wget https://broth.itch.ovh/butler/linux-amd64/LATEST/archive/default -O butler.zip
unzip butler.zip && chmod +x butler

# Login
butler login

# Upload game
butler upload ./my-game myuser/my-game

# Update
butler push ./my-game myuser/my-game:stable
```

### What Agent Can Do Autonomously
- ✅ Upload games/assets
- ✅ Update builds
- ✅ Monitor sales
- ❌ Nothing needs human after account setup

### Fee: Adjustable (default 10%)
### Payment: USD, PayPal
