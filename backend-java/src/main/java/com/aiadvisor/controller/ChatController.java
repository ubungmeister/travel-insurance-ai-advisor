package com.aiadvisor.controller;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.aiadvisor.dto.ChatRequest;
import com.aiadvisor.dto.ChatResponse;
import com.aiadvisor.service.ChatService;

import jakarta.validation.Valid;

// Protected by SecurityConfig (anyRequest().authenticated()); a valid Supabase
// JWT is required even though the user identity isn't used yet.
@RestController
@RequestMapping("/api/v1")
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @PostMapping("/chat")
    public ChatResponse chat(@Valid @RequestBody ChatRequest request) {
        return new ChatResponse(chatService.generateReply(request.message()));
    }
}
