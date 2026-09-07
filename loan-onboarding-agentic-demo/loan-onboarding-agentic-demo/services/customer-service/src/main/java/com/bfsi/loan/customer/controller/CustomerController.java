package com.bfsi.loan.customer.controller;

import com.bfsi.loan.customer.entity.Customer;
import com.bfsi.loan.customer.service.CustomerService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController @RequestMapping("/api/v1/customers") @RequiredArgsConstructor
public class CustomerController {
    private final CustomerService svc;

    @GetMapping                             public List<Customer>       getAll()                           { return svc.getAll(); }
    @GetMapping("/{id}")                    public Customer             getById(@PathVariable Long id)      { return svc.getById(id); }
    @GetMapping("/search")                  public List<Customer>       search(@RequestParam String name)   { return svc.search(name); }
    @PostMapping                            public Customer             create(@Valid @RequestBody Customer c) { return svc.create(c); }
    @PutMapping("/{id}")                    public Customer             update(@PathVariable Long id, @Valid @RequestBody Customer c) { return svc.update(id,c); }
    @DeleteMapping("/{id}")                 public ResponseEntity<Void> delete(@PathVariable Long id)       { svc.delete(id); return ResponseEntity.noContent().build(); }
    @GetMapping("/{id}/credit-profile")     public Map<String,Object>   creditProfile(@PathVariable Long id){ return svc.creditProfile(id); }
}
