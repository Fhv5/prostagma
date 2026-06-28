package io.github.fhv.prostagma.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record TranslationResponse(
    @JsonProperty("original")
    String original,
    @JsonProperty("transliteration")
    String transliteration,
    @JsonProperty("literal")
    String literal,
    @JsonProperty("interpreted")
    String interpreted) 
{}
