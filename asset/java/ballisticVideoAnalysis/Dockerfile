FROM maven:3.9.9-eclipse-temurin-17 AS build
WORKDIR /build
COPY pom.xml .
COPY src/main/java ./src/main/java
RUN mvn -B -DskipTests package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /build/target/ballistic-video-analysis.jar /app/ballistic-video-analysis.jar
RUN mkdir -p /var/log/ballistics-video-analysis \
    && chown -R 10001:10001 /app /var/log/ballistics-video-analysis
USER 10001:10001
EXPOSE 9090
ENV BALLISTICS_LOG_FILE=/var/log/ballistics-video-analysis/ballistics-%g.log
ENTRYPOINT ["java", "-jar", "/app/ballistic-video-analysis.jar"]
