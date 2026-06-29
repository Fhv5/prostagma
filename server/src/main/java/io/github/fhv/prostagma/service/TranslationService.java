package io.github.fhv.prostagma.service;

import tools.jackson.core.json.JsonReadFeature;
import tools.jackson.databind.ObjectMapper;
import com.ibm.icu.text.Transliterator;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.stereotype.Service;

import io.github.fhv.prostagma.dto.TranslationRequest;
import io.github.fhv.prostagma.dto.TranslationResponse;
import io.github.fhv.prostagma.dto.LlmTranslation;

@Service
public class TranslationService {
    private final ChatClient chatClient;
    private final Transliterator greekToLatinTransliterator;
    private final GoogleTranslateService googleTranslateService;
    private final ObjectMapper objectMapper;

    public TranslationService(ChatClient.Builder chatClientBuilder, GoogleTranslateService googleTranslateService, ObjectMapper objectMapper) {
        // System prompt defined on Modelfile
        this.chatClient = chatClientBuilder.build();
        this.greekToLatinTransliterator = Transliterator.getInstance("Greek-Latin; Latin-ASCII");
        this.googleTranslateService = googleTranslateService;
        this.objectMapper = objectMapper;        
    }
    
    public TranslationResponse translate(TranslationRequest request) {
        String originalText = request.text();
        String transliteratedText = this.greekToLatinTransliterator.transliterate(originalText);
        
        // String prompt = String.format("""Traduce: %s""", originalText);
        String prompt = originalText;
        String response = chatClient.prompt().user(prompt).call().content();
        String googleTranslation = this.googleTranslateService.translate(originalText);

        LlmTranslation llmData;
        try {
            llmData = objectMapper.readerFor(LlmTranslation.class)
                .with(JsonReadFeature.ALLOW_UNESCAPED_CONTROL_CHARS)
                .readValue(response);
        } catch (Exception e) {
            System.err.println("Error parsing response: " + response);
            System.err.println("Exception: " + e.getMessage());
            llmData = new LlmTranslation("Error", "Parsing error");
        }

        return new TranslationResponse(originalText, transliteratedText, llmData.literal(), llmData.interpreted(), googleTranslation);
    }
}
