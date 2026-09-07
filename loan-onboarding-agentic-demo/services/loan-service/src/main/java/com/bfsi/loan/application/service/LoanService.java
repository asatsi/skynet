package com.bfsi.loan.application.service;
import com.bfsi.loan.application.entity.LoanApplication;
import com.bfsi.loan.application.repository.LoanRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;

@Service @RequiredArgsConstructor
public class LoanService {
    private final LoanRepository repo;
    public List<LoanApplication> getAll()                        { return repo.findAll(); }
    public LoanApplication       getById(Long id)                { return repo.findById(id).orElseThrow(()->new RuntimeException("Loan not found: "+id)); }
    public List<LoanApplication> getByCustomer(Long cid)        { return repo.findByCustomerId(cid); }
    public List<LoanApplication> getByStatus(String status)     { return repo.findByStatus(status.toUpperCase()); }
    public LoanApplication       create(LoanApplication l)       { l.setStatus("DRAFT"); return repo.save(l); }
    public LoanApplication       update(Long id, LoanApplication req) {
        LoanApplication l = getById(id);
        if (req.getLoanType()     != null) l.setLoanType(req.getLoanType());
        if (req.getAmount()       != null) l.setAmount(req.getAmount());
        if (req.getPurpose()      != null) l.setPurpose(req.getPurpose());
        if (req.getTenureMonths() != null) l.setTenureMonths(req.getTenureMonths());
        if (req.getPriority()     != null) l.setPriority(req.getPriority());
        if (req.getInternalNotes()!= null) l.setInternalNotes(req.getInternalNotes());
        return repo.save(l);
    }
    public LoanApplication submit(Long id)                       { LoanApplication l=getById(id); l.setStatus("SUBMITTED"); return repo.save(l); }
    public LoanApplication startReview(Long id, String officer)  { LoanApplication l=getById(id); l.setStatus("UNDER_REVIEW"); l.setAssignedOfficer(officer); return repo.save(l); }
    public LoanApplication approve(Long id, String approver, String notes) {
        LoanApplication l=getById(id); l.setStatus("APPROVED"); l.setApprovedBy(approver); l.setInternalNotes(notes); return repo.save(l);
    }
    public LoanApplication reject(Long id, String reason)        { LoanApplication l=getById(id); l.setStatus("REJECTED"); l.setRejectionReason(reason); return repo.save(l); }
    public LoanApplication disburse(Long id)                     { LoanApplication l=getById(id); l.setStatus("DISBURSED"); return repo.save(l); }
    public Map<String,Object> updateStatus(Long id, String status, String notes) {
        LoanApplication l = getById(id); l.setStatus(status.toUpperCase());
        if (notes != null) l.setInternalNotes(notes);
        repo.save(l);
        return Map.of("id",id,"status",l.getStatus(),"message","Status updated to "+l.getStatus());
    }
}
