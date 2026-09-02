package com.healthcare.appointmentscheduling.controller;

import com.healthcare.appointmentscheduling.model.Appointment;
import com.healthcare.appointmentscheduling.model.AppointmentStatus;
import com.healthcare.appointmentscheduling.service.AppointmentService;
import jakarta.validation.Valid;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/appointments")
public class AppointmentController {

    private final AppointmentService appointmentService;

    public AppointmentController(AppointmentService appointmentService) {
        this.appointmentService = appointmentService;
    }

    @GetMapping
    public ResponseEntity<List<Appointment>> getAllAppointments() {
        return ResponseEntity.ok(appointmentService.getAllAppointments());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Appointment> getAppointmentById(@PathVariable Long id) {
        return ResponseEntity.ok(appointmentService.getAppointmentById(id));
    }

    @PostMapping
    public ResponseEntity<Appointment> createAppointment(@Valid @RequestBody Appointment appointment) {
        Appointment created = appointmentService.createAppointment(appointment);
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Appointment> updateAppointment(@PathVariable Long id,
                                                         @Valid @RequestBody Appointment appointment) {
        return ResponseEntity.ok(appointmentService.updateAppointment(id, appointment));
    }

    @PatchMapping("/{id}/status")
    public ResponseEntity<Appointment> updateAppointmentStatus(@PathVariable Long id,
                                                               @RequestBody Map<String, String> statusUpdate) {
        String statusValue = statusUpdate.get("status");
        if (statusValue == null) {
            throw new IllegalArgumentException("Status is required");
        }
        AppointmentStatus status;
        try {
            status = AppointmentStatus.valueOf(statusValue.toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Invalid status: '" + statusValue
                    + "'. Valid values are: SCHEDULED, CONFIRMED, CANCELLED, COMPLETED, NO_SHOW");
        }
        return ResponseEntity.ok(appointmentService.updateAppointmentStatus(id, status));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteAppointment(@PathVariable Long id) {
        appointmentService.deleteAppointment(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<Appointment>> getAppointmentsByPatientId(@PathVariable Long patientId) {
        return ResponseEntity.ok(appointmentService.getAppointmentsByPatientId(patientId));
    }

    @GetMapping("/provider/{providerId}")
    public ResponseEntity<List<Appointment>> getAppointmentsByProviderId(@PathVariable Long providerId) {
        return ResponseEntity.ok(appointmentService.getAppointmentsByProviderId(providerId));
    }

    @GetMapping("/status/{status}")
    public ResponseEntity<List<Appointment>> getAppointmentsByStatus(@PathVariable String status) {
        AppointmentStatus appointmentStatus;
        try {
            appointmentStatus = AppointmentStatus.valueOf(status.toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Invalid status: '" + status
                    + "'. Valid values are: SCHEDULED, CONFIRMED, CANCELLED, COMPLETED, NO_SHOW");
        }
        return ResponseEntity.ok(appointmentService.getAppointmentsByStatus(appointmentStatus));
    }

    @GetMapping("/date/{date}")
    public ResponseEntity<List<Appointment>> getAppointmentsByDate(
            @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        return ResponseEntity.ok(appointmentService.getAppointmentsByDate(date));
    }
}
