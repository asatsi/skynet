package com.healthcare.ehr.service;

import com.healthcare.ehr.exception.ResourceNotFoundException;
import com.healthcare.ehr.model.TreatmentPlan;
import com.healthcare.ehr.repository.TreatmentPlanRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class TreatmentPlanService {

    private final TreatmentPlanRepository treatmentPlanRepository;

    public TreatmentPlanService(TreatmentPlanRepository treatmentPlanRepository) {
        this.treatmentPlanRepository = treatmentPlanRepository;
    }

    @Transactional(readOnly = true)
    public List<TreatmentPlan> getAllTreatmentPlans() {
        return treatmentPlanRepository.findAll();
    }

    @Transactional(readOnly = true)
    public TreatmentPlan getTreatmentPlanById(Long id) {
        return treatmentPlanRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("TreatmentPlan", "id", id));
    }

    @Transactional(readOnly = true)
    public List<TreatmentPlan> getTreatmentPlansByPatientId(Long patientId) {
        return treatmentPlanRepository.findByPatientId(patientId);
    }

    @Transactional
    public TreatmentPlan createTreatmentPlan(TreatmentPlan treatmentPlan) {
        return treatmentPlanRepository.save(treatmentPlan);
    }
}
