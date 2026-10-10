package com.aiadvisor.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record ChatRequest(@NotBlank @Size(max = 2000) String message) {

    // Mirror Pydantic's str_strip_whitespace: trim before validation runs.
    public ChatRequest {
        if (message != null) {
            message = message.strip();
        }
    }
}
