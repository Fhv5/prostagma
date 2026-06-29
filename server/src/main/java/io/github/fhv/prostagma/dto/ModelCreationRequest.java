package io.github.fhv.prostagma.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record ModelCreationRequest(
    String name,
    ModelFiles files
) {
    public record ModelFiles(
        @JsonProperty("Modelfile")
        String modelfile
    ) {}
}


