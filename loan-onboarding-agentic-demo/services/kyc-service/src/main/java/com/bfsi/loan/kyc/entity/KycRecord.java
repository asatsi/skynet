package com.bfsi.loan.kyc.entity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import java.time.LocalDateTime;

@Entity @Table(name="kyc_records")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class KycRecord {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    @Column(nullable=false) private Long customerId;
    @Builder.Default private String status = "PENDING"; // PENDING|IN_PROGRESS|COMPLETED|FAILED
    @Builder.Default private Boolean panVerified       = false;
    @Builder.Default private Boolean addressVerified   = false;
    @Builder.Default private Boolean bankVerified      = false;
    @Builder.Default private Boolean complianceChecked = false;
    @Builder.Default private Boolean amlCleared        = false;
    private String remarks;
    private String verifiedBy;
    @CreationTimestamp private LocalDateTime createdAt;
    @UpdateTimestamp  private LocalDateTime updatedAt;
}
