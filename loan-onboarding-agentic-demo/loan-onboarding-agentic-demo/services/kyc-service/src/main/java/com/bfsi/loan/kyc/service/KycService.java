package com.bfsi.loan.kyc.service;
import com.bfsi.loan.kyc.entity.KycRecord;
import com.bfsi.loan.kyc.repository.KycRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service @RequiredArgsConstructor
public class KycService {
    private final KycRepository repo;
    public List<KycRecord> getAll()                    { return repo.findAll(); }
    public KycRecord       getById(Long id)            { return repo.findById(id).orElseThrow(()->new RuntimeException("KYC not found: "+id)); }
    public List<KycRecord> getByCustomer(Long cid)    { return repo.findByCustomerId(cid); }
    public KycRecord       getLatestByCustomer(Long cid){ return repo.findTopByCustomerIdOrderByCreatedAtDesc(cid).orElseThrow(()->new RuntimeException("No KYC for customer: "+cid)); }
    public KycRecord       create(KycRecord r)         { r.setStatus("PENDING"); return repo.save(r); }
    public KycRecord       initiate(Long customerId)   {
        KycRecord r = KycRecord.builder().customerId(customerId).status("IN_PROGRESS").build();
        return repo.save(r);
    }
    public KycRecord       verify(Long id, String officer) {
        KycRecord r = getById(id);
        r.setPanVerified(true); r.setAddressVerified(true);
        r.setBankVerified(true); r.setComplianceChecked(true); r.setAmlCleared(true);
        r.setStatus("COMPLETED"); r.setVerifiedBy(officer);
        r.setRemarks("All checks passed. KYC verified by " + officer);
        return repo.save(r);
    }
    public KycRecord       fail(Long id, String reason) {
        KycRecord r = getById(id);
        r.setStatus("FAILED"); r.setRemarks(reason);
        return repo.save(r);
    }
}
