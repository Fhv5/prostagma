package io.github.fhv.prostagma.service;

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
    private final tools.jackson.databind.ObjectMapper objectMapper;

    public TranslationService(ChatClient.Builder chatClientBuilder, ObjectMapper objectMapper) {
        // System prompt defined on Modelfile
        this.chatClient = chatClientBuilder.build();
        this.greekToLatinTransliterator = Transliterator.getInstance("Greek-Latin; Latin-ASCII");
        this.objectMapper = objectMapper;
    }
    
    public TranslationResponse translate(TranslationRequest request) {
        String originalText = request.text();
        String transliteratedText = this.greekToLatinTransliterator.transliterate(originalText);
        
        // String prompt = String.format("""Traduce: %s""", originalText);
        String prompt = originalText;

        String response = chatClient.prompt().user(prompt).call().content();

        LlmTranslation llmData;
        try {
            llmData = objectMapper.readValue(response, LlmTranslation.class);
        } catch (Exception e) {
            System.err.println("Error parsing response: " + response);
            System.err.println("Exception: " + e.getMessage());
            llmData = new LlmTranslation("Error", "Parsing error");
        }

        return new TranslationResponse(originalText, transliteratedText, llmData.literal(), llmData.interpreted());
    }
}
