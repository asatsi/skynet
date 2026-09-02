package com.healthcare.appointmentscheduling.service;

import com.healthcare.appointmentscheduling.exception.ResourceNotFoundException;
import com.healthcare.appointmentscheduling.model.Appointment;
import com.healthcare.appointmentscheduling.model.AppointmentStatus;
import com.healthcare.appointmentscheduling.model.Provider;
import com.healthcare.appointmentscheduling.repository.AppointmentRepository;
import com.healthcare.appointmentscheduling.repository.ProviderRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;

@Service
@Transactional
public class AppointmentService {

    private final AppointmentRepository appointmentRepository;
    private final ProviderRepository providerRepository;

    public AppointmentService(AppointmentRepository appointmentRepository,
                              ProviderRepository providerRepository) {
        this.appointmentRepository = appointmentRepository;
        this.providerRepository = providerRepository;
    }

    @Transactional(readOnly = true)
    public List<Appointment> getAllAppointments() {
        return appointmentRepository.findAll();
    }

    @Transactional(readOnly = true)
    public Appointment getAppointmentById(Long id) {
        return appointmentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Appointment", "id", id));
    }

    public Appointment createAppointment(Appointment appointment) {
        Provider provider = providerRepository.findById(appointment.getProviderId())
                .orElseThrow(() -> new ResourceNotFoundException("Provider", "id", appointment.getProviderId()));

        if (appointment.getStatus() == null) {
            appointment.setStatus(AppointmentStatus.SCHEDULED);
        }
        return appointmentRepository.save(appointment);
    }

    public Appointment updateAppointment(Long id, Appointment appointmentDetails) {
        Appointment appointment = getAppointmentById(id);

        if (!appointment.getProviderId().equals(appointmentDetails.getProviderId())) {
            providerRepository.findById(appointmentDetails.getProviderId())
                    .orElseThrow(() -> new ResourceNotFoundException("Provider", "id", appointmentDetails.getProviderId()));
        }

        appointment.setPatientId(appointmentDetails.getPatientId());
        appointment.setProviderId(appointmentDetails.getProviderId());
        appointment.setAppointmentDate(appointmentDetails.getAppointmentDate());
        appointment.setAppointmentTime(appointmentDetails.getAppointmentTime());
        appointment.setDuration(appointmentDetails.getDuration());
        if (appointmentDetails.getStatus() != null) {
            appointment.setStatus(appointmentDetails.getStatus());
        }
        appointment.setReason(appointmentDetails.getReason());
        appointment.setNotes(appointmentDetails.getNotes());

        return appointmentRepository.save(appointment);
    }

    public Appointment updateAppointmentStatus(Long id, AppointmentStatus status) {
        Appointment appointment = getAppointmentById(id);
        appointment.setStatus(status);
        return appointmentRepository.save(appointment);
    }

    public void deleteAppointment(Long id) {
        Appointment appointment = getAppointmentById(id);
        appointmentRepository.delete(appointment);
    }

    @Transactional(readOnly = true)
    public List<Appointment> getAppointmentsByPatientId(Long patientId) {
        return appointmentRepository.findByPatientId(patientId);
    }

    @Transactional(readOnly = true)
    public List<Appointment> getAppointmentsByProviderId(Long providerId) {
        return appointmentRepository.findByProviderId(providerId);
    }

    @Transactional(readOnly = true)
    public List<Appointment> getAppointmentsByStatus(AppointmentStatus status) {
        return appointmentRepository.findByStatus(status);
    }

    @Transactional(readOnly = true)
    public List<Appointment> getAppointmentsByDate(LocalDate date) {
        return appointmentRepository.findByAppointmentDate(date);
    }
}
