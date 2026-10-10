package com.aiadvisor.model;

import java.math.BigDecimal;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "variant_coverages")
public class VariantCoverage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "plan_variant_id", nullable = false)
    private PlanVariant planVariant;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "coverage_type_id", nullable = false)
    private CoverageType coverageType;

    @Column(name = "limit_amount", nullable = false, precision = 15, scale = 2)
    private BigDecimal limitAmount;

    @Column(nullable = false, length = 3)
    private String currency;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public PlanVariant getPlanVariant() {
        return planVariant;
    }

    public void setPlanVariant(PlanVariant planVariant) {
        this.planVariant = planVariant;
    }

    public CoverageType getCoverageType() {
        return coverageType;
    }

    public void setCoverageType(CoverageType coverageType) {
        this.coverageType = coverageType;
    }

    public BigDecimal getLimitAmount() {
        return limitAmount;
    }

    public void setLimitAmount(BigDecimal limitAmount) {
        this.limitAmount = limitAmount;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }
}
