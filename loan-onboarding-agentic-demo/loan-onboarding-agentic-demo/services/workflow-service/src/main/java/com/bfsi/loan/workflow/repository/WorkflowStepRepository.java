package com.bfsi.loan.workflow.repository;
import com.bfsi.loan.workflow.entity.WorkflowStep;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;
public interface WorkflowStepRepository extends JpaRepository<WorkflowStep,Long> {
    List<WorkflowStep> findByWorkflowInstanceIdOrderByStepOrder(Long wid);
    List<WorkflowStep> findByLoanApplicationId(Long lid);
    Optional<WorkflowStep> findByWorkflowInstanceIdAndStepName(Long wid, String name);
}
