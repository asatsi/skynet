package com.healthcare.ehr.service;

import com.healthcare.ehr.model.PatientSummary;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class EhrService {

    private final LabResultService labResultService;
    private final DiagnosisService diagnosisService;
    private final TreatmentPlanService treatmentPlanService;

    public EhrService(LabResultService labResultService,
                      DiagnosisService diagnosisService,
                      TreatmentPlanService treatmentPlanService) {
        this.labResultService = labResultService;
        this.diagnosisService = diagnosisService;
        this.treatmentPlanService = treatmentPlanService;
    }

    @Transactional(readOnly = true)
    public PatientSummary getPatientSummary(Long patientId) {
        return new PatientSummary(
                patientId,
                labResultService.getLabResultsByPatientId(patientId),
                diagnosisService.getDiagnosesByPatientId(patientId),
                treatmentPlanService.getTreatmentPlansByPatientId(patientId)
        );
    }
}
