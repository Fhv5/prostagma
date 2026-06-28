package io.github.fhv.prostagma.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import io.github.fhv.prostagma.dto.TranslationRequest;
import io.github.fhv.prostagma.dto.TranslationResponse;
import io.github.fhv.prostagma.service.TranslationService;
import lombok.AllArgsConstructor;

@RestController
@AllArgsConstructor
@RequestMapping("/api/v1/translate")
public class TranslateController {

    private final TranslationService translationService;

    @PostMapping
    public ResponseEntity<TranslationResponse> generate(
        @RequestBody TranslationRequest request) {
            return new ResponseEntity<>(translationService.translate(request), HttpStatus.OK);
    }

}
