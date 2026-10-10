package com.aiadvisor.model;

import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;

@Entity
@Table(name = "insurance_plans")
public class InsurancePlan {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(nullable = false, length = 50)
    private String name;

    @OneToMany(mappedBy = "plan")
    private List<InsurancePlanVersion> versions = new ArrayList<>();

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<InsurancePlanVersion> getVersions() {
        return versions;
    }

    public void setVersions(List<InsurancePlanVersion> versions) {
        this.versions = versions;
    }
}
