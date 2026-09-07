package com.bfsi.loan.workflow.entity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import java.time.LocalDateTime;

@Entity @Table(name="workflow_steps")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class WorkflowStep {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    private Long workflowInstanceId;
    private Long loanApplicationId;
    private Integer stepOrder;
    private String stepName;          // KYC_VERIFICATION|DOCUMENT_REVIEW|RISK_ASSESSMENT|CREDIT_COMMITTEE|FINAL_APPROVAL|DISBURSEMENT
    private String stepDescription;
    @Builder.Default private String status = "PENDING"; // PENDING|IN_PROGRESS|COMPLETED|FAILED|AWAITING_APPROVAL|APPROVED|REJECTED|SKIPPED
    private String assignedTo;
    private String completedBy;
    private String notes;
    @CreationTimestamp private LocalDateTime createdAt;
    private LocalDateTime completedAt;
}
