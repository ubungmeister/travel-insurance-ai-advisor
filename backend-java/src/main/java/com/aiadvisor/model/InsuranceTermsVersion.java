package com.aiadvisor.model;

import java.time.LocalDate;
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
@Table(name = "insurance_terms_versions")
public class InsuranceTermsVersion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(nullable = false, unique = true, length = 50)
    private String code;

    @Column(name = "valid_from", nullable = false)
    private LocalDate validFrom;

    @Column(name = "valid_to")
    private LocalDate validTo;

    @OneToMany(mappedBy = "termsVersion")
    private List<InsurancePlanVersion> planVersions = new ArrayList<>();

    @OneToMany(mappedBy = "termsVersion")
    private List<KnowledgeDocument> knowledgeDocuments = new ArrayList<>();

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public LocalDate getValidFrom() {
        return validFrom;
    }

    public void setValidFrom(LocalDate validFrom) {
        this.validFrom = validFrom;
    }

    public LocalDate getValidTo() {
        return validTo;
    }

    public void setValidTo(LocalDate validTo) {
        this.validTo = validTo;
    }

    public List<InsurancePlanVersion> getPlanVersions() {
        return planVersions;
    }

    public void setPlanVersions(List<InsurancePlanVersion> planVersions) {
        this.planVersions = planVersions;
    }

    public List<KnowledgeDocument> getKnowledgeDocuments() {
        return knowledgeDocuments;
    }

    public void setKnowledgeDocuments(List<KnowledgeDocument> knowledgeDocuments) {
        this.knowledgeDocuments = knowledgeDocuments;
    }
}
