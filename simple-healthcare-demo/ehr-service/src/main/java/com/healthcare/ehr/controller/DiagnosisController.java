package com.healthcare.ehr.controller;

import com.healthcare.ehr.model.Diagnosis;
import com.healthcare.ehr.service.DiagnosisService;
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
@RequestMapping("/api/ehr/diagnoses")
public class DiagnosisController {

    private final DiagnosisService diagnosisService;

    public DiagnosisController(DiagnosisService diagnosisService) {
        this.diagnosisService = diagnosisService;
    }

    @GetMapping
    public ResponseEntity<List<Diagnosis>> getAllDiagnoses() {
        return ResponseEntity.ok(diagnosisService.getAllDiagnoses());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Diagnosis> getDiagnosisById(@PathVariable Long id) {
        return ResponseEntity.ok(diagnosisService.getDiagnosisById(id));
    }

    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<Diagnosis>> getDiagnosesByPatientId(@PathVariable Long patientId) {
        return ResponseEntity.ok(diagnosisService.getDiagnosesByPatientId(patientId));
    }

    @PostMapping
    public ResponseEntity<Diagnosis> createDiagnosis(@Valid @RequestBody Diagnosis diagnosis) {
        Diagnosis created = diagnosisService.createDiagnosis(diagnosis);
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }
}
