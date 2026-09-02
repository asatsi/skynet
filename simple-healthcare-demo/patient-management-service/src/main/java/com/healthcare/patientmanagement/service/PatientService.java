package com.healthcare.patientmanagement.service;

import com.healthcare.patientmanagement.exception.DuplicateResourceException;
import com.healthcare.patientmanagement.exception.ResourceNotFoundException;
import com.healthcare.patientmanagement.model.Patient;
import com.healthcare.patientmanagement.repository.PatientRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class PatientService {

    private final PatientRepository patientRepository;

    public PatientService(PatientRepository patientRepository) {
        this.patientRepository = patientRepository;
    }

    @Transactional(readOnly = true)
    public List<Patient> getAllPatients() {
        return patientRepository.findAll();
    }

    @Transactional(readOnly = true)
    public Patient getPatientById(Long id) {
        return patientRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Patient", "id", id));
    }

    @Transactional
    public Patient createPatient(Patient patient) {
        if (patientRepository.existsByEmail(patient.getEmail())) {
            throw new DuplicateResourceException(
                    "A patient with email '" + patient.getEmail() + "' already exists");
        }
        if (patientRepository.existsBySsn(patient.getSsn())) {
            throw new DuplicateResourceException(
                    "A patient with SSN '" + patient.getSsn() + "' already exists");
        }
        return patientRepository.save(patient);
    }

    @Transactional
    public Patient updatePatient(Long id, Patient patientDetails) {
        Patient patient = getPatientById(id);

        patientRepository.findByEmail(patientDetails.getEmail())
                .filter(existing -> !existing.getId().equals(id))
                .ifPresent(existing -> {
                    throw new DuplicateResourceException(
                            "A patient with email '" + patientDetails.getEmail() + "' already exists");
                });

        patientRepository.findBySsn(patientDetails.getSsn())
                .filter(existing -> !existing.getId().equals(id))
                .ifPresent(existing -> {
                    throw new DuplicateResourceException(
                            "A patient with SSN '" + patientDetails.getSsn() + "' already exists");
                });

        patient.setFirstName(patientDetails.getFirstName());
        patient.setLastName(patientDetails.getLastName());
        patient.setDateOfBirth(patientDetails.getDateOfBirth());
        patient.setEmail(patientDetails.getEmail());
        patient.setPhone(patientDetails.getPhone());
        patient.setAddress(patientDetails.getAddress());
        patient.setSsn(patientDetails.getSsn());
        patient.setBloodType(patientDetails.getBloodType());
        patient.setAllergies(patientDetails.getAllergies());

        return patientRepository.save(patient);
    }

    @Transactional
    public void deletePatient(Long id) {
        Patient patient = getPatientById(id);
        patientRepository.delete(patient);
    }
}
