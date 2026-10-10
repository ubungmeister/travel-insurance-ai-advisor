package com.aiadvisor.security;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app.supabase")
public record SupabaseProperties(String url, String publishableKey, String jwtAudience) {

    public String issuer() {
        return url.replaceAll("/+$", "") + "/auth/v1";
    }

    public String jwkSetUri() {
        return issuer() + "/.well-known/jwks.json";
    }
}
