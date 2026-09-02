package com.healthcare.claimsprocessing.service;

import com.healthcare.claimsprocessing.exception.DuplicateResourceException;
import com.healthcare.claimsprocessing.exception.ResourceNotFoundException;
import com.healthcare.claimsprocessing.model.Claim;
import com.healthcare.claimsprocessing.model.ClaimStatus;
import com.healthcare.claimsprocessing.repository.ClaimRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@Transactional
public class ClaimService {

    private final ClaimRepository claimRepository;

    public ClaimService(ClaimRepository claimRepository) {
        this.claimRepository = claimRepository;
    }

    @Transactional(readOnly = true)
    public List<Claim> getAllClaims() {
        return claimRepository.findAll();
    }

    @Transactional(readOnly = true)
    public Claim getClaimById(Long id) {
        return claimRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Claim", "id", id));
    }

    @Transactional(readOnly = true)
    public Claim getClaimByClaimNumber(String claimNumber) {
        return claimRepository.findByClaimNumber(claimNumber)
                .orElseThrow(() -> new ResourceNotFoundException("Claim", "claimNumber", claimNumber));
    }

    @Transactional(readOnly = true)
    public List<Claim> getClaimsByPatientId(Long patientId) {
        return claimRepository.findByPatientId(patientId);
    }

    @Transactional(readOnly = true)
    public List<Claim> getClaimsByStatus(ClaimStatus status) {
        return claimRepository.findByStatus(status);
    }

    public Claim createClaim(Claim claim) {
        if (claimRepository.existsByClaimNumber(claim.getClaimNumber())) {
            throw new DuplicateResourceException(
                    "Claim already exists with claim number: " + claim.getClaimNumber());
        }
        if (claim.getStatus() == null) {
            claim.setStatus(ClaimStatus.SUBMITTED);
        }
        return claimRepository.save(claim);
    }

    public Claim updateClaim(Long id, Claim claimDetails) {
        Claim existingClaim = claimRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Claim", "id", id));

        if (!existingClaim.getClaimNumber().equals(claimDetails.getClaimNumber())
                && claimRepository.existsByClaimNumber(claimDetails.getClaimNumber())) {
            throw new DuplicateResourceException(
                    "Claim already exists with claim number: " + claimDetails.getClaimNumber());
        }

        existingClaim.setClaimNumber(claimDetails.getClaimNumber());
        existingClaim.setPatientId(claimDetails.getPatientId());
        existingClaim.setPolicyNumber(claimDetails.getPolicyNumber());
        existingClaim.setClaimDate(claimDetails.getClaimDate());
        existingClaim.setClaimAmount(claimDetails.getClaimAmount());
        existingClaim.setStatus(claimDetails.getStatus());
        existingClaim.setDescription(claimDetails.getDescription());
        existingClaim.setUpdatedAt(LocalDateTime.now());

        return claimRepository.save(existingClaim);
    }

    public Claim updateClaimStatus(Long id, ClaimStatus status) {
        Claim existingClaim = claimRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Claim", "id", id));
        existingClaim.setStatus(status);
        existingClaim.setUpdatedAt(LocalDateTime.now());
        return claimRepository.save(existingClaim);
    }

    public void deleteClaim(Long id) {
        Claim existingClaim = claimRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Claim", "id", id));
        claimRepository.delete(existingClaim);
    }
}
