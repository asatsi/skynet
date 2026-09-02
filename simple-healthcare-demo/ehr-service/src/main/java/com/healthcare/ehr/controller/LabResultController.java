package com.healthcare.ehr.controller;

import com.healthcare.ehr.model.LabResult;
import com.healthcare.ehr.service.LabResultService;
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
@RequestMapping("/api/ehr/lab-results")
public class LabResultController {

    private final LabResultService labResultService;

    public LabResultController(LabResultService labResultService) {
        this.labResultService = labResultService;
    }

    @GetMapping
    public ResponseEntity<List<LabResult>> getAllLabResults() {
        return ResponseEntity.ok(labResultService.getAllLabResults());
    }

    @GetMapping("/{id}")
    public ResponseEntity<LabResult> getLabResultById(@PathVariable Long id) {
        return ResponseEntity.ok(labResultService.getLabResultById(id));
    }

    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<LabResult>> getLabResultsByPatientId(@PathVariable Long patientId) {
        return ResponseEntity.ok(labResultService.getLabResultsByPatientId(patientId));
    }

    @PostMapping
    public ResponseEntity<LabResult> createLabResult(@Valid @RequestBody LabResult labResult) {
        LabResult created = labResultService.createLabResult(labResult);
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }
}
