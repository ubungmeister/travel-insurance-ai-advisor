package com.aiadvisor.model;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.OffsetDateTime;
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
@Table(name = "policies")
public class Policy {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "policy_number", nullable = false, length = 50)
    private String policyNumber;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "plan_variant_id", nullable = false)
    private PlanVariant planVariant;

    @Column(name = "trip_purpose", nullable = false, length = 50)
    private String tripPurpose;

    @Column(name = "declared_sport_category", nullable = false, length = 50)
    private String declaredSportCategory;

    @Column(name = "start_date", nullable = false)
    private LocalDate startDate;

    @Column(name = "end_date", nullable = false)
    private LocalDate endDate;

    @Column(nullable = false, length = 30)
    private String status;

    @Column(name = "price_paid", nullable = false, precision = 12, scale = 2)
    private BigDecimal pricePaid;

    @Column(nullable = false, length = 3)
    private String currency;

    @Column(name = "created_at", nullable = false, updatable = false, insertable = false)
    private OffsetDateTime createdAt;

    @Column(name = "updated_at", nullable = false, insertable = false)
    private OffsetDateTime updatedAt;

    @OneToMany(mappedBy = "policy")
    private List<InsuredPerson> insuredPeople = new ArrayList<>();

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getPolicyNumber() {
        return policyNumber;
    }

    public void setPolicyNumber(String policyNumber) {
        this.policyNumber = policyNumber;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public PlanVariant getPlanVariant() {
        return planVariant;
    }

    public void setPlanVariant(PlanVariant planVariant) {
        this.planVariant = planVariant;
    }

    public String getTripPurpose() {
        return tripPurpose;
    }

    public void setTripPurpose(String tripPurpose) {
        this.tripPurpose = tripPurpose;
    }

    public String getDeclaredSportCategory() {
        return declaredSportCategory;
    }

    public void setDeclaredSportCategory(String declaredSportCategory) {
        this.declaredSportCategory = declaredSportCategory;
    }

    public LocalDate getStartDate() {
        return startDate;
    }

    public void setStartDate(LocalDate startDate) {
        this.startDate = startDate;
    }

    public LocalDate getEndDate() {
        return endDate;
    }

    public void setEndDate(LocalDate endDate) {
        this.endDate = endDate;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public BigDecimal getPricePaid() {
        return pricePaid;
    }

    public void setPricePaid(BigDecimal pricePaid) {
        this.pricePaid = pricePaid;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    public OffsetDateTime getUpdatedAt() {
        return updatedAt;
    }

    public List<InsuredPerson> getInsuredPeople() {
        return insuredPeople;
    }

    public void setInsuredPeople(List<InsuredPerson> insuredPeople) {
        this.insuredPeople = insuredPeople;
    }
}
