package com.aiadvisor.service;

import org.springframework.stereotype.Service;

@Service
public class ChatService {

    public String generateReply(String message) {
        return "(mocked) I received your message: '" + message + "'. "
            + "Real coverage analysis is not implemented yet.";
    }
}
