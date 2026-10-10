package com.aiadvisor.service;

import java.util.Map;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;

import com.aiadvisor.dto.LoginRequest;
import com.aiadvisor.dto.LoginResponse;
import com.aiadvisor.dto.RefreshRequest;
import com.aiadvisor.exception.ApiException;
import com.aiadvisor.security.SupabaseProperties;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class AuthService {

    private final RestClient restClient;
    private final SupabaseProperties supabase;
    private final ObjectMapper objectMapper;

    public AuthService(SupabaseProperties supabase, ObjectMapper objectMapper, RestClient.Builder builder) {
        this.supabase = supabase;
        this.objectMapper = objectMapper;
        this.restClient = builder.baseUrl(supabase.url().replaceAll("/+$", "")).build();
    }

    public LoginResponse login(LoginRequest request) {
        return requestToken("password",
            Map.of("email", request.email(), "password", request.password()),
            "Invalid email or password");
    }

    public LoginResponse refresh(RefreshRequest request) {
        return requestToken("refresh_token",
            Map.of("refresh_token", request.refreshToken()),
            "Invalid or expired refresh token");
    }

    public void logout(String accessToken) {
        try {
            restClient.post()
                .uri("/auth/v1/logout")
                .header("apikey", supabase.publishableKey())
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + accessToken)
                .exchange((request, response) -> {
                    int status = response.getStatusCode().value();
                    if (status == 401 || status == 403) {
                        throw new ApiException(HttpStatus.UNAUTHORIZED, "Invalid or expired token");
                    }
                    if (status >= 400) {
                        throw new ApiException(HttpStatus.BAD_GATEWAY,
                            "Authentication service returned an unexpected error");
                    }
                    return null;
                });
        } catch (ResourceAccessException ex) {
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "Authentication service is unavailable");
        }
    }

    private LoginResponse requestToken(String grantType, Map<String, Object> payload, String unauthorizedDetail) {
        try {
            return restClient.post()
                .uri(uriBuilder -> uriBuilder.path("/auth/v1/token").queryParam("grant_type", grantType).build())
                .header("apikey", supabase.publishableKey())
                .contentType(MediaType.APPLICATION_JSON)
                .body(payload)
                .exchange((request, response) -> toLoginResponse(response.getStatusCode().value(),
                    response.getBody().readAllBytes(), unauthorizedDetail));
        } catch (ResourceAccessException ex) {
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "Authentication service is unavailable");
        }
    }

    private LoginResponse toLoginResponse(int status, byte[] rawBody, String unauthorizedDetail) {
        if (status == 429) {
            throw new ApiException(HttpStatus.TOO_MANY_REQUESTS, "Too many attempts, please try again later");
        }
        if (status == 400) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, unauthorizedDetail);
        }
        if (status >= 400) {
            throw new ApiException(HttpStatus.BAD_GATEWAY, "Authentication service returned an unexpected error");
        }

        JsonNode body;
        try {
            body = objectMapper.readTree(rawBody);
        } catch (Exception ex) {
            throw new ApiException(HttpStatus.BAD_GATEWAY, "Authentication service returned an unexpected response");
        }
        if (body == null
            || !body.hasNonNull("access_token")
            || !body.hasNonNull("refresh_token")
            || !body.hasNonNull("expires_in")
            || !body.hasNonNull("expires_at")) {
            throw new ApiException(HttpStatus.BAD_GATEWAY, "Authentication service returned an unexpected response");
        }

        return new LoginResponse(
            body.get("access_token").asText(),
            body.get("refresh_token").asText(),
            body.path("token_type").asText("bearer"),
            body.get("expires_in").asLong(),
            body.get("expires_at").asLong());
    }
}
