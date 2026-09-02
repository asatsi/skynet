package com.healthcare.appointmentscheduling.repository;

import com.healthcare.appointmentscheduling.model.Appointment;
import com.healthcare.appointmentscheduling.model.AppointmentStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface AppointmentRepository extends JpaRepository<Appointment, Long> {

    List<Appointment> findByPatientId(Long patientId);

    List<Appointment> findByProviderId(Long providerId);

    List<Appointment> findByStatus(AppointmentStatus status);

    List<Appointment> findByAppointmentDate(LocalDate appointmentDate);
}
