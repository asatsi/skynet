package com.healthcare.ehr.service;

import com.healthcare.ehr.exception.ResourceNotFoundException;
import com.healthcare.ehr.model.LabResult;
import com.healthcare.ehr.repository.LabResultRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class LabResultService {

    private final LabResultRepository labResultRepository;

    public LabResultService(LabResultRepository labResultRepository) {
        this.labResultRepository = labResultRepository;
    }

    @Transactional(readOnly = true)
    public List<LabResult> getAllLabResults() {
        return labResultRepository.findAll();
    }

    @Transactional(readOnly = true)
    public LabResult getLabResultById(Long id) {
        return labResultRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("LabResult", "id", id));
    }

    @Transactional(readOnly = true)
    public List<LabResult> getLabResultsByPatientId(Long patientId) {
        return labResultRepository.findByPatientId(patientId);
    }

    @Transactional
    public LabResult createLabResult(LabResult labResult) {
        return labResultRepository.save(labResult);
    }
}
