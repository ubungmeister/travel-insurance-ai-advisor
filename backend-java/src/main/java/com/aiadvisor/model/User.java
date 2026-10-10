package com.aiadvisor.model;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "auth_user_id", unique = true)
    private UUID authUserId;

    @Column(nullable = false, unique = true, length = 255)
    private String email;

    @OneToMany(mappedBy = "user")
    private List<Policy> policies = new ArrayList<>();

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public UUID getAuthUserId() {
        return authUserId;
    }

    public void setAuthUserId(UUID authUserId) {
        this.authUserId = authUserId;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public List<Policy> getPolicies() {
        return policies;
    }

    public void setPolicies(List<Policy> policies) {
        this.policies = policies;
    }
}
