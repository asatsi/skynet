package com.bfsi.loan.customer.service;

import com.bfsi.loan.customer.entity.Customer;
import com.bfsi.loan.customer.repository.CustomerRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;

@Service @RequiredArgsConstructor
public class CustomerService {
    private final CustomerRepository repo;

    public List<Customer> getAll()                          { return repo.findAll(); }
    public Customer       getById(Long id)                  { return repo.findById(id).orElseThrow(() -> new RuntimeException("Customer not found: " + id)); }
    public List<Customer> search(String name)               { return repo.searchByName(name); }
    public Customer       create(Customer c)                { return repo.save(c); }
    public Customer       update(Long id, Customer req)     {
        Customer c = getById(id);
        c.setFirstName(req.getFirstName()); c.setLastName(req.getLastName());
        c.setCompanyName(req.getCompanyName()); c.setEmail(req.getEmail());
        c.setPhone(req.getPhone()); c.setAddress(req.getAddress());
        c.setAnnualRevenue(req.getAnnualRevenue()); c.setBusinessType(req.getBusinessType());
        c.setYearsInOperation(req.getYearsInOperation()); c.setCreditScore(req.getCreditScore());
        c.setStatus(req.getStatus());
        return repo.save(c);
    }
    public void           delete(Long id)                   { repo.deleteById(id); }
    public Map<String,Object> creditProfile(Long id) {
        Customer c = getById(id);
        String rating = c.getCreditScore() >= 750 ? "EXCELLENT" : c.getCreditScore() >= 700 ? "GOOD" : c.getCreditScore() >= 650 ? "FAIR" : "POOR";
        boolean eligible = c.getCreditScore() >= 650 && "ACTIVE".equals(c.getStatus());
        Map<String,Object> profile = new java.util.LinkedHashMap<>();
        profile.put("customerId",       id);
        profile.put("firstName",        c.getFirstName());
        profile.put("lastName",         c.getLastName());
        profile.put("companyName",      c.getCompanyName());
        profile.put("address",          c.getAddress());
        profile.put("creditScore",      c.getCreditScore());
        profile.put("rating",           rating);
        profile.put("eligible",         eligible);
        profile.put("annualRevenue",    c.getAnnualRevenue());
        profile.put("yearsInOperation", c.getYearsInOperation());
        return profile;
    }
}
