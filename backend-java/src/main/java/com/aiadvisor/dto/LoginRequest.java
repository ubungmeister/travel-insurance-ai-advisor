package com.aiadvisor.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record LoginRequest(
    @NotBlank @Size(min = 3, max = 255) String email,
    @NotBlank @Size(min = 1, max = 72) String password) {
}
