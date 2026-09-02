package com.healthcare.patientmanagement.controller;

import com.healthcare.patientmanagement.model.MedicalRecord;
import com.healthcare.patientmanagement.service.MedicalRecordService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/patients/{patientId}/medical-records")
public class MedicalRecordController {

    private final MedicalRecordService medicalRecordService;

    public MedicalRecordController(MedicalRecordService medicalRecordService) {
        this.medicalRecordService = medicalRecordService;
    }

    @GetMapping
    public ResponseEntity<List<MedicalRecord>> getMedicalRecordsByPatientId(@PathVariable Long patientId) {
        List<MedicalRecord> records = medicalRecordService.getMedicalRecordsByPatientId(patientId);
        return ResponseEntity.ok(records);
    }

    @PostMapping
    public ResponseEntity<MedicalRecord> createMedicalRecord(@PathVariable Long patientId,
                                                             @Valid @RequestBody MedicalRecord medicalRecord) {
        MedicalRecord createdRecord = medicalRecordService.createMedicalRecord(patientId, medicalRecord);
        return new ResponseEntity<>(createdRecord, HttpStatus.CREATED);
    }
}
