package com.bfsi.loan.kyc.repository;
import com.bfsi.loan.kyc.entity.KycRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;
public interface KycRepository extends JpaRepository<KycRecord, Long> {
    List<KycRecord>   findByCustomerId(Long customerId);
    Optional<KycRecord> findTopByCustomerIdOrderByCreatedAtDesc(Long customerId);
    List<KycRecord>   findByStatus(String status);
}
