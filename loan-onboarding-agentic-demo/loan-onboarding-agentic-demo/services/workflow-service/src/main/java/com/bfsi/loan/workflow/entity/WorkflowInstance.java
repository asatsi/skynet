package com.bfsi.loan.workflow.entity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import java.time.LocalDateTime;

@Entity @Table(name="workflow_instances")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class WorkflowInstance {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    private Long loanApplicationId;
    private Long customerId;
    @Builder.Default private String status = "INITIATED"; // INITIATED|IN_PROGRESS|AWAITING_APPROVAL|APPROVED|REJECTED|COMPLETED
    private String currentStep;
    private Integer totalSteps;
    private Integer completedSteps;
    private String assignedOfficer;
    private String approvedBy;
    private String rejectionReason;
    @CreationTimestamp private LocalDateTime createdAt;
    @UpdateTimestamp  private LocalDateTime updatedAt;
}
