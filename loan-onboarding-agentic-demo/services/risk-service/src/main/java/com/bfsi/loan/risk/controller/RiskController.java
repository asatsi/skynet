package com.bfsi.loan.risk.controller;
import com.bfsi.loan.risk.entity.RiskAssessment;
import com.bfsi.loan.risk.service.RiskService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController @RequestMapping("/api/v1/risk") @RequiredArgsConstructor
public class RiskController {
    private final RiskService svc;
    @GetMapping                             public List<RiskAssessment> getAll()                           { return svc.getAll(); }
    @GetMapping("/{id}")                    public RiskAssessment       getById(@PathVariable Long id)      { return svc.getById(id); }
    @GetMapping("/customer/{cid}")          public List<RiskAssessment> byCustomer(@PathVariable Long cid)  { return svc.getByCustomer(cid); }
    @GetMapping("/loan/{lid}")              public List<RiskAssessment> byLoan(@PathVariable Long lid)      { return svc.getByLoan(lid); }
    @GetMapping("/loan/{lid}/latest")       public RiskAssessment       latestByLoan(@PathVariable Long lid){ return svc.getLatestByLoan(lid); }
    @PostMapping("/assess")                 public RiskAssessment       assess(@RequestBody RiskAssessment r){ return svc.create(r); }
}
