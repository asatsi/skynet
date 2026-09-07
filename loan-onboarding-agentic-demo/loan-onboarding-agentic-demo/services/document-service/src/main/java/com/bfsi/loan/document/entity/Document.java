package com.bfsi.loan.document.entity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import java.time.LocalDateTime;

@Entity @Table(name="documents")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class Document {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    private Long customerId;
    private Long loanApplicationId;
    private String documentType;   // FINANCIAL_STATEMENT|BANK_STATEMENT|TAX_RETURN|BUSINESS_LICENSE|COLLATERAL_DOCS|ID_PROOF
    private String fileName;
    private String fileSize;
    @Builder.Default private String status = "PENDING"; // PENDING|UPLOADED|VERIFIED|REJECTED
    private String rejectionReason;
    private String verifiedBy;
    @CreationTimestamp private LocalDateTime uploadedAt;
    @UpdateTimestamp  private LocalDateTime updatedAt;
}
