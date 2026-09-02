package com.healthcare.appointmentscheduling.service;

import com.healthcare.appointmentscheduling.exception.ResourceNotFoundException;
import com.healthcare.appointmentscheduling.model.Provider;
import com.healthcare.appointmentscheduling.repository.ProviderRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
public class ProviderService {

    private final ProviderRepository providerRepository;

    public ProviderService(ProviderRepository providerRepository) {
        this.providerRepository = providerRepository;
    }

    @Transactional(readOnly = true)
    public List<Provider> getAllProviders() {
        return providerRepository.findAll();
    }

    @Transactional(readOnly = true)
    public Provider getProviderById(Long id) {
        return providerRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Provider", "id", id));
    }

    public Provider createProvider(Provider provider) {
        providerRepository.findByEmail(provider.getEmail()).ifPresent(existing -> {
            throw new IllegalArgumentException("Provider with email '" + provider.getEmail() + "' already exists");
        });
        return providerRepository.save(provider);
    }

    public Provider updateProvider(Long id, Provider providerDetails) {
        Provider provider = getProviderById(id);

        providerRepository.findByEmail(providerDetails.getEmail()).ifPresent(existing -> {
            if (!existing.getId().equals(id)) {
                throw new IllegalArgumentException("Provider with email '" + providerDetails.getEmail() + "' already exists");
            }
        });

        provider.setFirstName(providerDetails.getFirstName());
        provider.setLastName(providerDetails.getLastName());
        provider.setSpecialization(providerDetails.getSpecialization());
        provider.setEmail(providerDetails.getEmail());
        provider.setPhone(providerDetails.getPhone());

        return providerRepository.save(provider);
    }

    public void deleteProvider(Long id) {
        Provider provider = getProviderById(id);
        providerRepository.delete(provider);
    }

    @Transactional(readOnly = true)
    public List<Provider> getProvidersBySpecialization(String specialization) {
        return providerRepository.findBySpecialization(specialization);
    }
}
