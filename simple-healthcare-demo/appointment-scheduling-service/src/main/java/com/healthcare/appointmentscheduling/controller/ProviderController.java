package com.healthcare.appointmentscheduling.controller;

import com.healthcare.appointmentscheduling.model.Provider;
import com.healthcare.appointmentscheduling.service.ProviderService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/providers")
public class ProviderController {

    private final ProviderService providerService;

    public ProviderController(ProviderService providerService) {
        this.providerService = providerService;
    }

    @GetMapping
    public ResponseEntity<List<Provider>> getAllProviders() {
        return ResponseEntity.ok(providerService.getAllProviders());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Provider> getProviderById(@PathVariable Long id) {
        return ResponseEntity.ok(providerService.getProviderById(id));
    }

    @PostMapping
    public ResponseEntity<Provider> createProvider(@Valid @RequestBody Provider provider) {
        Provider created = providerService.createProvider(provider);
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Provider> updateProvider(@PathVariable Long id,
                                                   @Valid @RequestBody Provider provider) {
        return ResponseEntity.ok(providerService.updateProvider(id, provider));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProvider(@PathVariable Long id) {
        providerService.deleteProvider(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/specialization/{specialization}")
    public ResponseEntity<List<Provider>> getProvidersBySpecialization(@PathVariable String specialization) {
        return ResponseEntity.ok(providerService.getProvidersBySpecialization(specialization));
    }
}
