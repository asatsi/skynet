package com.healthcare.ehr.controller;

import com.healthcare.ehr.model.TreatmentPlan;
import com.healthcare.ehr.service.TreatmentPlanService;
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
@RequestMapping("/api/ehr/treatment-plans")
public class TreatmentPlanController {

    private final TreatmentPlanService treatmentPlanService;

    public TreatmentPlanController(TreatmentPlanService treatmentPlanService) {
        this.treatmentPlanService = treatmentPlanService;
    }

    @GetMapping
    public ResponseEntity<List<TreatmentPlan>> getAllTreatmentPlans() {
        return ResponseEntity.ok(treatmentPlanService.getAllTreatmentPlans());
    }

    @GetMapping("/{id}")
    public ResponseEntity<TreatmentPlan> getTreatmentPlanById(@PathVariable Long id) {
        return ResponseEntity.ok(treatmentPlanService.getTreatmentPlanById(id));
    }

    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<TreatmentPlan>> getTreatmentPlansByPatientId(@PathVariable Long patientId) {
        return ResponseEntity.ok(treatmentPlanService.getTreatmentPlansByPatientId(patientId));
    }

    @PostMapping
    public ResponseEntity<TreatmentPlan> createTreatmentPlan(@Valid @RequestBody TreatmentPlan treatmentPlan) {
        TreatmentPlan created = treatmentPlanService.createTreatmentPlan(treatmentPlan);
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }
}
