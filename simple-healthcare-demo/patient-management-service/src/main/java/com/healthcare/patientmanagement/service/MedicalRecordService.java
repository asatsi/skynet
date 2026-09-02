package com.healthcare.patientmanagement.service;

import com.healthcare.patientmanagement.exception.ResourceNotFoundException;
import com.healthcare.patientmanagement.model.MedicalRecord;
import com.healthcare.patientmanagement.repository.MedicalRecordRepository;
import com.healthcare.patientmanagement.repository.PatientRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class MedicalRecordService {

    private final MedicalRecordRepository medicalRecordRepository;
    private final PatientRepository patientRepository;

    public MedicalRecordService(MedicalRecordRepository medicalRecordRepository,
                                PatientRepository patientRepository) {
        this.medicalRecordRepository = medicalRecordRepository;
        this.patientRepository = patientRepository;
    }

    @Transactional(readOnly = true)
    public List<MedicalRecord> getMedicalRecordsByPatientId(Long patientId) {
        if (!patientRepository.existsById(patientId)) {
            throw new ResourceNotFoundException("Patient", "id", patientId);
        }
        return medicalRecordRepository.findByPatientIdOrderByRecordDateDesc(patientId);
    }

    @Transactional
    public MedicalRecord createMedicalRecord(Long patientId, MedicalRecord medicalRecord) {
        if (!patientRepository.existsById(patientId)) {
            throw new ResourceNotFoundException("Patient", "id", patientId);
        }
        medicalRecord.setPatientId(patientId);
        return medicalRecordRepository.save(medicalRecord);
    }
}
