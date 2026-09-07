package com.bfsi.loan.kyc.controller;
import com.bfsi.loan.kyc.entity.KycRecord;
import com.bfsi.loan.kyc.service.KycService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController @RequestMapping("/api/v1/kyc") @RequiredArgsConstructor
public class KycController {
    private final KycService svc;
    @GetMapping                              public List<KycRecord> getAll()                                { return svc.getAll(); }
    @GetMapping("/{id}")                     public KycRecord       getById(@PathVariable Long id)          { return svc.getById(id); }
    @GetMapping("/customer/{customerId}")    public List<KycRecord> getByCustomer(@PathVariable Long customerId){ return svc.getByCustomer(customerId); }
    @GetMapping("/customer/{customerId}/latest") public KycRecord  getLatest(@PathVariable Long customerId) { return svc.getLatestByCustomer(customerId); }
    @PostMapping                             public KycRecord       create(@RequestBody KycRecord r)         { return svc.create(r); }
    @PostMapping("/customer/{customerId}/initiate") public KycRecord initiate(@PathVariable Long customerId) { return svc.initiate(customerId); }
    @PutMapping("/{id}/verify")              public KycRecord       verify(@PathVariable Long id, @RequestParam(defaultValue="System") String officer){ return svc.verify(id,officer); }
    @PutMapping("/{id}/fail")               public KycRecord       fail(@PathVariable Long id, @RequestBody Map<String,String> body){ return svc.fail(id,body.get("reason")); }
}
