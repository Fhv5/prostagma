package io.github.fhv.prostagma.config;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;

@Component
public class OllamaStartupValidator implements ApplicationRunner {
    private final RestClient restClient;
    private final ObjectMapper objectMapper;

    @Value("${spring.ai.ollama.base-url:http://localhost:11434}")
    String baseUrl;

    @Value("${spring.ai.ollama.chat.options.model:meltemi-en:latest}")
    String model;

    @Value("classpath:modelfiles/meltemi-en.json")
    Resource modelfile;

    public OllamaStartupValidator(RestClient restClient) {
        this.restClient = restClient;
        this.objectMapper = new ObjectMapper();
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        System.out.println("Ollama URL: " + baseUrl);
        System.out.println("Ollama Model: " + model);

        String getUrl = baseUrl + "/api/tags";
        String createUrl = baseUrl + "/api/create";

        try {

            String response = restClient.get()
                    .uri(getUrl)
                    .retrieve()
                    .body(String.class);

            JsonNode root = objectMapper.readTree(response);

            JsonNode models = root.get("models");
            boolean modelFound = false;
            for (JsonNode model : models) {
                if (model != null && model.get("name").asString().equals(this.model)) {
                    modelFound = true;
                    break;
                }
            }
            if (!modelFound) {
                JsonNode requestPayload = objectMapper.readTree(modelfile.getInputStream());

                restClient.post()
                        .uri(createUrl)
                        .body(requestPayload)
                        .exchange((request, clientResponse) -> {
                            try (BufferedReader reader = new BufferedReader(
                                    new InputStreamReader(clientResponse.getBody(), StandardCharsets.UTF_8))) {
                                String line;
                                JsonNode data;
                                while ((line = reader.readLine()) != null) {
                                    if (line.trim().isEmpty()) continue;
                                    data = objectMapper.readTree(line);
                                    if (data == null) continue;
                                    
                                    String status = data.has("status") ? data.get("status").asText() : "";

                                    if (data.has("total") && data.has("completed")) {
                                        long total = data.get("total").asLong();
                                        long completed = data.get("completed").asLong();
                                        if (total > 0) {
                                            int percent = (int) ((completed * 100) / total);
                                            System.out.print("\r" + status + " - Progress: " + percent + "%        ");
                                            System.out.flush();
                                        }
                                    } else {
                                        System.out.print("\r" + status + "                                      ");
                                        System.out.flush();
                                    }
                                }
                                System.out.println(); // Salto de línea final
                            }
                            return null;
                        });
            }
            System.out.println("We are good to go");
        } catch (Exception e) {
            System.err.println("Ollama Error during startup: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }

    }
}
