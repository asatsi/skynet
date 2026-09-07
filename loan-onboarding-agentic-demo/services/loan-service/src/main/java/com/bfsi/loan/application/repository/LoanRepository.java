package com.bfsi.loan.application.repository;
import com.bfsi.loan.application.entity.LoanApplication;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface LoanRepository extends JpaRepository<LoanApplication,Long> {
    List<LoanApplication> findByCustomerId(Long cid);
    List<LoanApplication> findByStatus(String status);
    List<LoanApplication> findByAssignedOfficer(String officer);
    List<LoanApplication> findByLoanType(String type);
}
