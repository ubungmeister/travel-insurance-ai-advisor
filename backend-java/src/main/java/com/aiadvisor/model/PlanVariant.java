package com.aiadvisor.model;

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
@Table(name = "plan_variants")
public class PlanVariant {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "plan_version_id", nullable = false)
    private InsurancePlanVersion planVersion;

    @Column(nullable = false, length = 30)
    private String territory;

    @Column(name = "sport_category", length = 50)
    private String sportCategory;

    @OneToMany(mappedBy = "planVariant")
    private List<Policy> policies = new ArrayList<>();

    @OneToMany(mappedBy = "planVariant")
    private List<VariantCoverage> coverages = new ArrayList<>();

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public InsurancePlanVersion getPlanVersion() {
        return planVersion;
    }

    public void setPlanVersion(InsurancePlanVersion planVersion) {
        this.planVersion = planVersion;
    }

    public String getTerritory() {
        return territory;
    }

    public void setTerritory(String territory) {
        this.territory = territory;
    }

    public String getSportCategory() {
        return sportCategory;
    }

    public void setSportCategory(String sportCategory) {
        this.sportCategory = sportCategory;
    }

    public List<Policy> getPolicies() {
        return policies;
    }

    public void setPolicies(List<Policy> policies) {
        this.policies = policies;
    }

    public List<VariantCoverage> getCoverages() {
        return coverages;
    }

    public void setCoverages(List<VariantCoverage> coverages) {
        this.coverages = coverages;
    }
}
