package com.bfsi.loan.risk.repository;
import com.bfsi.loan.risk.entity.RiskAssessment;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;
public interface RiskRepository extends JpaRepository<RiskAssessment,Long> {
    List<RiskAssessment> findByCustomerId(Long cid);
    List<RiskAssessment> findByLoanApplicationId(Long lid);
    Optional<RiskAssessment> findTopByLoanApplicationIdOrderByAssessedAtDesc(Long lid);
    List<RiskAssessment> findByRiskCategory(String cat);
}
