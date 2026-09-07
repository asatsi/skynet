package com.bfsi.loan.customer.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity @Table(name="customers")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class Customer {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    @NotBlank private String firstName;
    @NotBlank private String lastName;
    @NotBlank private String companyName;
    @Email    private String email;
    private String phone;
    private String address;
    private String panNumber;
    private String taxId;
    @Column(precision=15,scale=2) private BigDecimal annualRevenue;
    private String businessType;   // LLC | CORPORATION | PARTNERSHIP | SOLE_PROPRIETOR
    private Integer yearsInOperation;
    private Integer creditScore;
    @Builder.Default private String status = "ACTIVE"; // ACTIVE | INACTIVE | BLACKLISTED
    @CreationTimestamp private LocalDateTime createdAt;
    @UpdateTimestamp  private LocalDateTime updatedAt;
}
