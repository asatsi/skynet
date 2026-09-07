package com.bfsi.loan.risk.service;
import com.bfsi.loan.risk.entity.RiskAssessment;
import com.bfsi.loan.risk.repository.RiskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.util.List;

@Service @RequiredArgsConstructor
public class RiskService {
    private final RiskRepository repo;

    public List<RiskAssessment> getAll()                       { return repo.findAll(); }
    public RiskAssessment       getById(Long id)               { return repo.findById(id).orElseThrow(()->new RuntimeException("Risk assessment not found: "+id)); }
    public List<RiskAssessment> getByCustomer(Long cid)       { return repo.findByCustomerId(cid); }
    public List<RiskAssessment> getByLoan(Long lid)           { return repo.findByLoanApplicationId(lid); }
    public RiskAssessment       getLatestByLoan(Long lid)     { return repo.findTopByLoanApplicationIdOrderByAssessedAtDesc(lid).orElseThrow(()->new RuntimeException("No risk assessment for loan: "+lid)); }
    public RiskAssessment       create(RiskAssessment r)       { return repo.save(assess(r)); }

    private RiskAssessment assess(RiskAssessment r) {
        double score = 0;
        int cs = r.getCreditScore() != null ? r.getCreditScore() : 650;
        if (cs >= 780) score += 20; else if (cs >= 720) score += 35; else if (cs >= 680) score += 55; else score += 75;
        BigDecimal dti = r.getDebtToIncomeRatio() != null ? r.getDebtToIncomeRatio() : BigDecimal.valueOf(40);
        if (dti.doubleValue() < 30) score += 5; else if (dti.doubleValue() < 45) score += 20; else score += 40;
        BigDecimal ltv = r.getLoanToValueRatio() != null ? r.getLoanToValueRatio() : BigDecimal.valueOf(70);
        if (ltv.doubleValue() < 60) score += 5; else if (ltv.doubleValue() < 80) score += 15; else score += 30;
        r.setRiskScore(BigDecimal.valueOf(Math.min(score, 100)));
        if      (score < 30)  { r.setRiskCategory("LOW");       r.setRecommendation("APPROVE"); }
        else if (score < 55)  { r.setRiskCategory("MEDIUM");    r.setRecommendation("CONDITIONAL_APPROVE"); }
        else if (score < 75)  { r.setRiskCategory("HIGH");      r.setRecommendation("MANUAL_REVIEW"); }
        else                  { r.setRiskCategory("VERY_HIGH"); r.setRecommendation("REJECT"); }
        r.setStatus("COMPLETED");
        return r;
    }
}
