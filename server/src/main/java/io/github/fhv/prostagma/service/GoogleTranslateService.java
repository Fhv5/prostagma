package io.github.fhv.prostagma.service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;

@Service
public class GoogleTranslateService {
    private final RestClient restClient;
    private final ObjectMapper objectMapper;

    public GoogleTranslateService(RestClient.Builder restClientBuilder) {
        this.restClient = restClientBuilder.build();
        this.objectMapper = new ObjectMapper();
    }

    public String translate(String text) {
        try {
            String url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=el&tl=en&dt=t&q={text}";
            
            String response = restClient.get()
                    .uri(url, text)
                    .retrieve()
                    .body(String.class);
            
            JsonNode root = objectMapper.readTree(response);
            return root.get(0).get(0).get(0).asString();
        } catch (Exception e) {
            System.err.println("Google Translate Error: " + e.getMessage());
            return "Google Translate error.";
        }
    }
    
}
