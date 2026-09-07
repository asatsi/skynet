package com.bfsi.loan.risk.entity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity @Table(name="risk_assessments")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class RiskAssessment {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    private Long customerId;
    private Long loanApplicationId;
    private Integer creditScore;
    @Column(precision=5,scale=2) private BigDecimal debtToIncomeRatio;
    @Column(precision=5,scale=2) private BigDecimal loanToValueRatio;
    @Column(precision=5,scale=2) private BigDecimal riskScore;           // 0-100
    private String riskCategory;      // LOW | MEDIUM | HIGH | VERY_HIGH
    private String recommendation;    // APPROVE | CONDITIONAL_APPROVE | REJECT | MANUAL_REVIEW
    private String assessedBy;
    private String notes;
    @Builder.Default private String status = "PENDING"; // PENDING | COMPLETED
    @CreationTimestamp private LocalDateTime assessedAt;
}
