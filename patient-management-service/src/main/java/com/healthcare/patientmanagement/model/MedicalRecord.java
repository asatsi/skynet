package com.healthcare.patientmanagement.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PastOrPresent;
import jakarta.validation.constraints.Size;

import java.time.LocalDate;

@Entity
@Table(name = "medical_records")
public class MedicalRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull(message = "Patient ID is required")
    @Column(nullable = false)
    private Long patientId;

    @NotNull(message = "Record date is required")
    @PastOrPresent(message = "Record date cannot be in the future")
    @Column(nullable = false)
    private LocalDate recordDate;

    @NotBlank(message = "Diagnosis is required")
    @Size(max = 500, message = "Diagnosis must not exceed 500 characters")
    @Column(nullable = false, length = 500)
    private String diagnosis;

    @Size(max = 1000, message = "Treatment must not exceed 1000 characters")
    @Column(length = 1000)
    private String treatment;

    @Size(max = 2000, message = "Notes must not exceed 2000 characters")
    @Column(length = 2000)
    private String notes;

    @NotBlank(message = "Physician is required")
    @Size(max = 100, message = "Physician name must not exceed 100 characters")
    @Column(nullable = false, length = 100)
    private String physician;

    public MedicalRecord() {
    }

    public MedicalRecord(Long patientId, LocalDate recordDate, String diagnosis,
                         String treatment, String notes, String physician) {
        this.patientId = patientId;
        this.recordDate = recordDate;
        this.diagnosis = diagnosis;
        this.treatment = treatment;
        this.notes = notes;
        this.physician = physician;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getPatientId() {
        return patientId;
    }

    public void setPatientId(Long patientId) {
        this.patientId = patientId;
    }

    public LocalDate getRecordDate() {
        return recordDate;
    }

    public void setRecordDate(LocalDate recordDate) {
        this.recordDate = recordDate;
    }

    public String getDiagnosis() {
        return diagnosis;
    }

    public void setDiagnosis(String diagnosis) {
        this.diagnosis = diagnosis;
    }

    public String getTreatment() {
        return treatment;
    }

    public void setTreatment(String treatment) {
        this.treatment = treatment;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public String getPhysician() {
        return physician;
    }

    public void setPhysician(String physician) {
        this.physician = physician;
    }

    @Override
    public String toString() {
        return "MedicalRecord{" +
                "id=" + id +
                ", patientId=" + patientId +
                ", recordDate=" + recordDate +
                ", diagnosis='" + diagnosis + '\'' +
                ", physician='" + physician + '\'' +
                '}';
    }
}
