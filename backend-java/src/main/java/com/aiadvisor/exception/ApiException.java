package com.aiadvisor.exception;

import org.springframework.http.HttpStatus;

// Carries the HTTP status + client-facing message; rendered as {"detail": ...}
// by GlobalExceptionHandler to match the FastAPI error contract.
public class ApiException extends RuntimeException {

    private final HttpStatus status;

    public ApiException(HttpStatus status, String message) {
        super(message);
        this.status = status;
    }

    public HttpStatus getStatus() {
        return status;
    }
}
