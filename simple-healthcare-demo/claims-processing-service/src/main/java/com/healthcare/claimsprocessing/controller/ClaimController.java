package com.healthcare.claimsprocessing.controller;

import com.healthcare.claimsprocessing.model.Claim;
import com.healthcare.claimsprocessing.model.ClaimStatus;
import com.healthcare.claimsprocessing.service.ClaimService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/claims")
public class ClaimController {

    private final ClaimService claimService;

    public ClaimController(ClaimService claimService) {
        this.claimService = claimService;
    }

    @GetMapping
    public ResponseEntity<List<Claim>> getAllClaims() {
        List<Claim> claims = claimService.getAllClaims();
        return ResponseEntity.ok(claims);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Claim> getClaimById(@PathVariable Long id) {
        Claim claim = claimService.getClaimById(id);
        return ResponseEntity.ok(claim);
    }

    @GetMapping("/claim-number/{claimNumber}")
    public ResponseEntity<Claim> getClaimByClaimNumber(@PathVariable String claimNumber) {
        Claim claim = claimService.getClaimByClaimNumber(claimNumber);
        return ResponseEntity.ok(claim);
    }

    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<Claim>> getClaimsByPatientId(@PathVariable Long patientId) {
        List<Claim> claims = claimService.getClaimsByPatientId(patientId);
        return ResponseEntity.ok(claims);
    }

    @GetMapping("/status/{status}")
    public ResponseEntity<List<Claim>> getClaimsByStatus(@PathVariable ClaimStatus status) {
        List<Claim> claims = claimService.getClaimsByStatus(status);
        return ResponseEntity.ok(claims);
    }

    @PostMapping
    public ResponseEntity<Claim> createClaim(@Valid @RequestBody Claim claim) {
        Claim createdClaim = claimService.createClaim(claim);
        return new ResponseEntity<>(createdClaim, HttpStatus.CREATED);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Claim> updateClaim(@PathVariable Long id, @Valid @RequestBody Claim claim) {
        Claim updatedClaim = claimService.updateClaim(id, claim);
        return ResponseEntity.ok(updatedClaim);
    }

    @PatchMapping("/{id}/status")
    public ResponseEntity<Claim> updateClaimStatus(
            @PathVariable Long id,
            @RequestBody Map<String, String> statusUpdate) {
        ClaimStatus status = ClaimStatus.valueOf(statusUpdate.get("status"));
        Claim updatedClaim = claimService.updateClaimStatus(id, status);
        return ResponseEntity.ok(updatedClaim);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteClaim(@PathVariable Long id) {
        claimService.deleteClaim(id);
        return ResponseEntity.noContent().build();
    }
}
