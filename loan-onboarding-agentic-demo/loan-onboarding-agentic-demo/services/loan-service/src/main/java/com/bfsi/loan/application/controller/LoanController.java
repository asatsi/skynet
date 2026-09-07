package com.bfsi.loan.application.controller;
import com.bfsi.loan.application.entity.LoanApplication;
import com.bfsi.loan.application.service.LoanService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController @RequestMapping("/api/v1/loans") @RequiredArgsConstructor
public class LoanController {
    private final LoanService svc;
    @GetMapping                               public List<LoanApplication> getAll()                                { return svc.getAll(); }
    @GetMapping("/{id}")                      public LoanApplication       getById(@PathVariable Long id)          { return svc.getById(id); }
    @GetMapping("/customer/{cid}")            public List<LoanApplication> byCustomer(@PathVariable Long cid)      { return svc.getByCustomer(cid); }
    @GetMapping("/status/{status}")           public List<LoanApplication> byStatus(@PathVariable String status)   { return svc.getByStatus(status); }
    @PostMapping                              public LoanApplication       create(@RequestBody LoanApplication l)   { return svc.create(l); }
    @PutMapping("/{id}")                      public LoanApplication       update(@PathVariable Long id, @RequestBody LoanApplication l){ return svc.update(id,l); }
    @PutMapping("/{id}/submit")              public LoanApplication       submit(@PathVariable Long id)            { return svc.submit(id); }
    @PutMapping("/{id}/review")              public LoanApplication       review(@PathVariable Long id, @RequestParam(defaultValue="SYSTEM") String officer){ return svc.startReview(id,officer); }
    @PutMapping("/{id}/approve")             public LoanApplication       approve(@PathVariable Long id, @RequestBody Map<String,String> body){ return svc.approve(id,body.getOrDefault("approver","SYSTEM"),body.get("notes")); }
    @PutMapping("/{id}/reject")              public LoanApplication       reject(@PathVariable Long id, @RequestBody Map<String,String> body) { return svc.reject(id,body.get("reason")); }
    @PutMapping("/{id}/disburse")            public LoanApplication       disburse(@PathVariable Long id)          { return svc.disburse(id); }
    @PutMapping("/{id}/status")              public Map<String,Object>    updateStatus(@PathVariable Long id, @RequestBody Map<String,String> body){ return svc.updateStatus(id,body.get("status"),body.get("notes")); }
}
