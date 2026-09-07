package com.bfsi.loan.application.entity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity @Table(name="loan_applications")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class LoanApplication {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    private Long customerId;
    private String loanType;          // WORKING_CAPITAL|TERM_LOAN|EQUIPMENT_FINANCE|TRADE_FINANCE
    @Column(precision=15,scale=2) private BigDecimal amount;
    private String currency;
    private String purpose;
    private Integer tenureMonths;
    @Column(precision=5,scale=2) private BigDecimal interestRate;
    @Builder.Default private String status = "DRAFT"; // DRAFT|SUBMITTED|UNDER_REVIEW|APPROVED|REJECTED|DISBURSED|CLOSED
    private String priority;          // LOW|MEDIUM|HIGH|URGENT
    private String assignedOfficer;
    private String approvedBy;
    private String rejectionReason;
    private String internalNotes;
    @CreationTimestamp private LocalDateTime createdAt;
    @UpdateTimestamp  private LocalDateTime updatedAt;
}
