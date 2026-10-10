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
@Table(name = "coverage_types")
public class CoverageType {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(nullable = false, unique = true, length = 50)
    private String code;

    @Column(nullable = false, length = 150)
    private String name;

    @OneToMany(mappedBy = "coverageType")
    private List<VariantCoverage> variantCoverages = new ArrayList<>();

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

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<VariantCoverage> getVariantCoverages() {
        return variantCoverages;
    }

    public void setVariantCoverages(List<VariantCoverage> variantCoverages) {
        this.variantCoverages = variantCoverages;
    }
}
