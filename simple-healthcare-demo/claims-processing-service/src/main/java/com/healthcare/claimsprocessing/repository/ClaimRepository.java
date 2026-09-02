package com.healthcare.claimsprocessing.repository;

import com.healthcare.claimsprocessing.model.Claim;
import com.healthcare.claimsprocessing.model.ClaimStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ClaimRepository extends JpaRepository<Claim, Long> {

    List<Claim> findByPatientId(Long patientId);

    List<Claim> findByStatus(ClaimStatus status);

    Optional<Claim> findByClaimNumber(String claimNumber);

    boolean existsByClaimNumber(String claimNumber);
}
