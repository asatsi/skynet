package com.healthcare.ehr.controller;

import com.healthcare.ehr.model.PatientSummary;
import com.healthcare.ehr.service.EhrService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/ehr")
public class EhrController {

    private final EhrService ehrService;

    public EhrController(EhrService ehrService) {
        this.ehrService = ehrService;
    }

    @GetMapping("/patient/{patientId}/summary")
    public ResponseEntity<PatientSummary> getPatientSummary(@PathVariable Long patientId) {
        return ResponseEntity.ok(ehrService.getPatientSummary(patientId));
    }
}
