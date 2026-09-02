package com.healthcare.ehr.model;

import java.util.List;

/**
 * Aggregated view of a patient's electronic health record:
 * all lab results, diagnoses, and treatment plans in one payload.
 */
public class PatientSummary {

    private Long patientId;
    private List<LabResult> labResults;
    private List<Diagnosis> diagnoses;
    private List<TreatmentPlan> treatmentPlans;

    public PatientSummary() {
    }

    public PatientSummary(Long patientId, List<LabResult> labResults,
                          List<Diagnosis> diagnoses, List<TreatmentPlan> treatmentPlans) {
        this.patientId = patientId;
        this.labResults = labResults;
        this.diagnoses = diagnoses;
        this.treatmentPlans = treatmentPlans;
    }

    public Long getPatientId() {
        return patientId;
    }

    public void setPatientId(Long patientId) {
        this.patientId = patientId;
    }

    public List<LabResult> getLabResults() {
        return labResults;
    }

    public void setLabResults(List<LabResult> labResults) {
        this.labResults = labResults;
    }

    public List<Diagnosis> getDiagnoses() {
        return diagnoses;
    }

    public void setDiagnoses(List<Diagnosis> diagnoses) {
        this.diagnoses = diagnoses;
    }

    public List<TreatmentPlan> getTreatmentPlans() {
        return treatmentPlans;
    }

    public void setTreatmentPlans(List<TreatmentPlan> treatmentPlans) {
        this.treatmentPlans = treatmentPlans;
    }
}
