package com.healthcare.appointmentscheduling.repository;

import com.healthcare.appointmentscheduling.model.Provider;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProviderRepository extends JpaRepository<Provider, Long> {

    Optional<Provider> findByEmail(String email);

    List<Provider> findBySpecialization(String specialization);
}
