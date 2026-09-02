package com.healthcare.patientmanagement.repository;

import com.healthcare.patientmanagement.model.Patient;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PatientRepository extends JpaRepository<Patient, Long> {

    Optional<Patient> findByEmail(String email);

    Optional<Patient> findBySsn(String ssn);

    boolean existsByEmail(String email);

    boolean existsBySsn(String ssn);
}
