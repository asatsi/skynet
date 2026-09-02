package com.healthcare.ehr.repository;

import com.healthcare.ehr.model.TreatmentPlan;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TreatmentPlanRepository extends JpaRepository<TreatmentPlan, Long> {

    List<TreatmentPlan> findByPatientId(Long patientId);
}
