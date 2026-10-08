# Ballistic Video Analysis

Standalone Java TCP service for receiving the video feed. Everything required to build and install this service is in this directory; it does not use the repository's parent build.

## Requirements

- Linux with systemd for native service installation
- Java 17 or newer (JDK required to build; JRE sufficient to run)
- Maven 3.8 or newer to build

## Build and run

From this directory, create the executable JAR:

```sh
mvn clean package
```

The shaded artifact is `target/ballistic-video-analysis.jar`. Run it directly with:

```sh
java -jar target/ballistic-video-analysis.jar
```

It listens on TCP port 9090 by default. The server accepts a client connection and reads its feed until the client disconnects.

## Install as a systemd service

Run the installer from this directory as root (Maven and Java must be installed):

```sh
sudo ./deploy.sh
```

The script builds the JAR, installs it under `/opt/ballistics-video-analysis/`, installs the systemd unit at `/etc/systemd/system/ballistics.service`, and starts/enables the service. Existing `/etc/ballistics-video-analysis/application.properties` is preserved across updates.

```sh
sudo systemctl status ballistics.service
sudo journalctl -u ballistics.service -f
sudo systemctl stop ballistics.service
sudo systemctl start ballistics.service
```

To update after changing the source, run `sudo ./deploy.sh` again. It replaces the JAR and restarts the service; local configuration is not overwritten.

## Configuration

The installed configuration file is `/etc/ballistics-video-analysis/application.properties`:

```properties
server.port=9090
logging.file=/var/log/ballistics-video-analysis/ballistics-%g.log
logging.max-bytes=10485760
logging.file-count=5
```

`logging.file` is a Java logging pattern; `%g` denotes the rotated file number. Files rotate at the configured byte limit, keeping the configured number of files. Logs are also written to stderr for capture by the systemd journal. Restart the service after editing configuration.

The same settings can be overridden with JVM system properties (`-Dserver.port=...`, `-Dlogging.file=...`, etc.) or environment variables (`BALLISTICS_PORT`, `BALLISTICS_LOG_FILE`, `BALLISTICS_LOG_MAX_BYTES`, `BALLISTICS_LOG_FILE_COUNT`). Select a different properties file with `-Dballistics.config=/path/to/application.properties` or `BALLISTICS_CONFIG`.

## Verify service health

`systemctl is-active ballistics.service` confirms the process is running. To check that the TCP socket accepts connections, use:

```sh
nc -vz 127.0.0.1 9090
```

Use the configured `server.port` if it differs from the default. A successful connection is accepted and logged; no HTTP health endpoint is provided because this service uses a raw TCP feed.

## Docker (optional)

Build and run the same standalone service in a container:

```sh
docker build -t ballistic-video-analysis .
docker run --rm -p 9090:9090 ballistic-video-analysis
```

Set the same `BALLISTICS_*` environment variables to override the port or logging settings. Native systemd installation remains the primary deployment path.
