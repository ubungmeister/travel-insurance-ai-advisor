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
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "plan_variants")
@Getter
@Setter
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
}
