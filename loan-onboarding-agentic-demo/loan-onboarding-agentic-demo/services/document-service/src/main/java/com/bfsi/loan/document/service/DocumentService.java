package com.bfsi.loan.document.service;
import com.bfsi.loan.document.entity.Document;
import com.bfsi.loan.document.repository.DocumentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;

@Service @RequiredArgsConstructor
public class DocumentService {
    private final DocumentRepository repo;
    public List<Document> getAll()                              { return repo.findAll(); }
    public Document       getById(Long id)                      { return repo.findById(id).orElseThrow(()->new RuntimeException("Document not found: "+id)); }
    public List<Document> getByCustomer(Long cid)              { return repo.findByCustomerId(cid); }
    public List<Document> getByLoan(Long lid)                  { return repo.findByLoanApplicationId(lid); }
    public Document       create(Document d)                    { d.setStatus("UPLOADED"); return repo.save(d); }
    public Document       verify(Long id, String officer)       { Document d=getById(id); d.setStatus("VERIFIED"); d.setVerifiedBy(officer); return repo.save(d); }
    public Document       reject(Long id, String reason)        { Document d=getById(id); d.setStatus("REJECTED"); d.setRejectionReason(reason); return repo.save(d); }
    public Map<String,Object> checklistStatus(Long loanId) {
        List<Document> docs = repo.findByLoanApplicationId(loanId);
        long verified = docs.stream().filter(d->"VERIFIED".equals(d.getStatus())).count();
        long pending  = docs.stream().filter(d->"PENDING".equals(d.getStatus())||"UPLOADED".equals(d.getStatus())).count();
        long rejected = docs.stream().filter(d->"REJECTED".equals(d.getStatus())).count();
        return Map.of("loanId",loanId,"total",docs.size(),"verified",verified,"pending",pending,"rejected",rejected,"complete",rejected==0&&pending==0&&verified>0);
    }
}
