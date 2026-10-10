package com.aiadvisor.security;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.oauth2.core.OAuth2Error;
import org.springframework.security.oauth2.core.OAuth2TokenValidator;
import org.springframework.security.oauth2.core.OAuth2TokenValidatorResult;
import org.springframework.security.oauth2.jose.jws.SignatureAlgorithm;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtIssuerValidator;
import org.springframework.security.oauth2.jwt.JwtValidators;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.oauth2.server.resource.web.BearerTokenAuthenticationEntryPoint;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@EnableConfigurationProperties(SupabaseProperties.class)
public class SecurityConfig {

    // Endpoints that must work without a verified access token. /logout forwards
    // the raw token to Supabase and lets Supabase decide validity, mirroring the
    // FastAPI behavior (it used get_bearer_token, not get_current_user).
    private static final String[] PUBLIC_ENDPOINTS = {
        "/health",
        "/health/db",
        "/api/auth/login",
        "/api/auth/refresh",
        "/api/auth/logout",
        // springdoc / Swagger UI
        "/swagger-ui.html",
        "/swagger-ui/**",
        "/v3/api-docs/**",
    };

    @Bean
    SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .cors(Customizer.withDefaults())
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(PUBLIC_ENDPOINTS).permitAll()
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> oauth2
                .authenticationEntryPoint(new BearerTokenAuthenticationEntryPoint())
                .jwt(Customizer.withDefaults()));
        return http.build();
    }

    @Bean
    JwtDecoder jwtDecoder(SupabaseProperties supabase) {
        NimbusJwtDecoder decoder = NimbusJwtDecoder
            .withJwkSetUri(supabase.jwkSetUri())
            .jwsAlgorithm(SignatureAlgorithm.ES256)
            .build();

        OAuth2TokenValidator<Jwt> audienceValidator = jwt -> {
            if (jwt.getAudience() != null && jwt.getAudience().contains(supabase.jwtAudience())) {
                return OAuth2TokenValidatorResult.success();
            }
            return OAuth2TokenValidatorResult.failure(
                new OAuth2Error("invalid_token", "The required audience is missing", null));
        };

        decoder.setJwtValidator(JwtValidators.createDefaultWithValidators(
            new JwtIssuerValidator(supabase.issuer()),
            audienceValidator));
        return decoder;
    }
}
