package com.aiadvisor.dto;

import java.util.UUID;

public record CurrentUserResponse(UUID authUserId, String email) {
}
