FROM maven:3.9-eclipse-temurin-25 AS builder
WORKDIR /server

COPY pom.xml .

RUN mvn dependency:go-offline -B

COPY src ./src

RUN mvn clean package -DskipTests

FROM eclipse-temurin:25-jre
WORKDIR /server

RUN addgroup --system prostagma && adduser --system --ingroup prostagma prostagmauser
USER prostagmauser

COPY --from=builder /server/target/prostagma-*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]