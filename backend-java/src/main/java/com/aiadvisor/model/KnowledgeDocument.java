package com.aiadvisor.model;

import java.time.OffsetDateTime;

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
@Table(name = "knowledge_documents")
public class KnowledgeDocument {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "terms_version_id", nullable = false)
    private InsuranceTermsVersion termsVersion;

    @Column(nullable = false, length = 255)
    private String title;

    @Column(name = "file_name", nullable = false, length = 255)
    private String fileName;

    @Column(name = "storage_path", nullable = false, unique = true, length = 500)
    private String storagePath;

    @Column(nullable = false, unique = true, length = 64)
    private String checksum;

    @Column(name = "processing_status", nullable = false, length = 20)
    private String processingStatus;

    @Column(name = "created_at", nullable = false, updatable = false, insertable = false)
    private OffsetDateTime createdAt;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public InsuranceTermsVersion getTermsVersion() {
        return termsVersion;
    }

    public void setTermsVersion(InsuranceTermsVersion termsVersion) {
        this.termsVersion = termsVersion;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public String getStoragePath() {
        return storagePath;
    }

    public void setStoragePath(String storagePath) {
        this.storagePath = storagePath;
    }

    public String getChecksum() {
        return checksum;
    }

    public void setChecksum(String checksum) {
        this.checksum = checksum;
    }

    public String getProcessingStatus() {
        return processingStatus;
    }

    public void setProcessingStatus(String processingStatus) {
        this.processingStatus = processingStatus;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }
}
