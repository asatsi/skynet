package com.healthcare.ehr.repository;

import com.healthcare.ehr.model.Diagnosis;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DiagnosisRepository extends JpaRepository<Diagnosis, Long> {

    List<Diagnosis> findByPatientId(Long patientId);
}
