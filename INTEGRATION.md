# Running the three repos together

| Repo | Role | Runtime |
|------|------|---------|
| `Trust-Main` | Node API + web assets | container `trust-main`, port 3000 |
| `AudioVideoEngine-CPP` | Native A/V engine (CMake) | container `av-engine`, built from its git URL |
| `Trust-Shell` | Android browser shell | APK, built with Gradle |

## Start the backend stack
```bash
docker compose up --build
curl http://localhost:3000/health
```
`av-engine` starts first (`depends_on`); `trust-main` reaches it at hostname `av-engine` (`AV_ENGINE_HOST`).

## Build the shell
```bash
git clone https://github.com/PMR-Pubclications/Trust-Shell.git
cd Trust-Shell && ./gradlew assembleRelease
```
The shell talks to the API at `http://<host>:3000` (use `http://10.0.2.2:3000` from the Android emulator).

## Config
`TRUST_ADMIN_KEY` (admin key), `PORT` (default 3000), `TRUST_DB_PATH` (SQLite file override).
