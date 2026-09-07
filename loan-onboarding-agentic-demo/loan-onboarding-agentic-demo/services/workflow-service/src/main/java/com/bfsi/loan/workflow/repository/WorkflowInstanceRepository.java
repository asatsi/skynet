package com.bfsi.loan.workflow.repository;
import com.bfsi.loan.workflow.entity.WorkflowInstance;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;
public interface WorkflowInstanceRepository extends JpaRepository<WorkflowInstance,Long> {
    Optional<WorkflowInstance> findByLoanApplicationId(Long lid);
    List<WorkflowInstance> findByStatus(String status);
}
