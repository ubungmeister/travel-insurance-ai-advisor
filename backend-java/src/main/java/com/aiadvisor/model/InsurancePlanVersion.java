package com.aiadvisor.model;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;

@Entity
@Table(name = "insurance_plan_versions")
public class InsurancePlanVersion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "plan_id", nullable = false)
    private InsurancePlan plan;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "terms_version_id", nullable = false)
    private InsuranceTermsVersion termsVersion;

    @Column(nullable = false)
    private Integer version;

    @Column(name = "valid_from", nullable = false)
    private LocalDate validFrom;

    @Column(name = "valid_to")
    private LocalDate validTo;

    @OneToMany(mappedBy = "planVersion")
    private List<PlanVariant> variants = new ArrayList<>();

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public InsurancePlan getPlan() {
        return plan;
    }

    public void setPlan(InsurancePlan plan) {
        this.plan = plan;
    }

    public InsuranceTermsVersion getTermsVersion() {
        return termsVersion;
    }

    public void setTermsVersion(InsuranceTermsVersion termsVersion) {
        this.termsVersion = termsVersion;
    }

    public Integer getVersion() {
        return version;
    }

    public void setVersion(Integer version) {
        this.version = version;
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

    public List<PlanVariant> getVariants() {
        return variants;
    }

    public void setVariants(List<PlanVariant> variants) {
        this.variants = variants;
    }
}
