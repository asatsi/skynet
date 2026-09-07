package com.bfsi.loan.workflow.service;
import com.bfsi.loan.workflow.entity.WorkflowInstance;
import com.bfsi.loan.workflow.entity.WorkflowStep;
import com.bfsi.loan.workflow.repository.WorkflowInstanceRepository;
import com.bfsi.loan.workflow.repository.WorkflowStepRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Service @RequiredArgsConstructor
public class WorkflowService {
    private final WorkflowInstanceRepository wRepo;
    private final WorkflowStepRepository     sRepo;

    private static final List<String[]> STEPS = List.of(
        new String[]{"KYC_VERIFICATION","Verify customer identity and compliance"},
        new String[]{"DOCUMENT_REVIEW","Review and verify all submitted documents"},
        new String[]{"RISK_ASSESSMENT","Perform credit and risk analysis"},
        new String[]{"CREDIT_COMMITTEE","Credit committee review and scoring"},
        new String[]{"FINAL_APPROVAL","Senior officer final approval (HITL)"},
        new String[]{"DISBURSEMENT","Loan disbursement and account setup"}
    );

    public List<WorkflowInstance> getAll()              { return wRepo.findAll(); }
    public WorkflowInstance       getById(Long id)      { return wRepo.findById(id).orElseThrow(()->new RuntimeException("Workflow not found: "+id)); }
    public WorkflowInstance       getByLoan(Long lid)   { return wRepo.findByLoanApplicationId(lid).orElseThrow(()->new RuntimeException("No workflow for loan: "+lid)); }
    public List<WorkflowStep>     getSteps(Long wid)    { return sRepo.findByWorkflowInstanceIdOrderByStepOrder(wid); }
    public List<WorkflowStep>     getStepsByLoan(Long lid){ return sRepo.findByLoanApplicationId(lid); }

    public WorkflowInstance initiate(Long loanId, Long customerId, String officer) {
        WorkflowInstance w = WorkflowInstance.builder()
            .loanApplicationId(loanId).customerId(customerId)
            .status("IN_PROGRESS").currentStep("KYC_VERIFICATION")
            .totalSteps(STEPS.size()).completedSteps(0).assignedOfficer(officer).build();
        w = wRepo.save(w);
        for (int i=0; i<STEPS.size(); i++) {
            sRepo.save(WorkflowStep.builder()
                .workflowInstanceId(w.getId()).loanApplicationId(loanId)
                .stepOrder(i+1).stepName(STEPS.get(i)[0]).stepDescription(STEPS.get(i)[1])
                .status(i==0?"IN_PROGRESS":"PENDING").assignedTo(officer).build());
        }
        return w;
    }

    public WorkflowStep completeStep(Long stepId, String officer, String notes) {
        WorkflowStep s = sRepo.findById(stepId).orElseThrow(()->new RuntimeException("Step not found: "+stepId));
        s.setStatus("COMPLETED"); s.setCompletedBy(officer); s.setNotes(notes); s.setCompletedAt(LocalDateTime.now());
        sRepo.save(s);
        WorkflowInstance w = wRepo.findById(s.getWorkflowInstanceId()).orElseThrow();
        w.setCompletedSteps(w.getCompletedSteps()+1);
        List<WorkflowStep> allSteps = sRepo.findByWorkflowInstanceIdOrderByStepOrder(w.getId());
        WorkflowStep next = allSteps.stream().filter(st->"PENDING".equals(st.getStatus())).findFirst().orElse(null);
        if (next != null) { next.setStatus("IN_PROGRESS"); sRepo.save(next); w.setCurrentStep(next.getStepName()); }
        else { w.setStatus("COMPLETED"); w.setCurrentStep("COMPLETED"); }
        wRepo.save(w);
        return s;
    }

    public WorkflowStep approveStep(Long stepId, String approver, String notes) {
        WorkflowStep s = sRepo.findById(stepId).orElseThrow(()->new RuntimeException("Step not found: "+stepId));
        s.setStatus("APPROVED"); s.setCompletedBy(approver); s.setNotes(notes); s.setCompletedAt(LocalDateTime.now());
        sRepo.save(s);
        WorkflowInstance w = wRepo.findById(s.getWorkflowInstanceId()).orElseThrow();
        w.setApprovedBy(approver); w.setCompletedSteps(w.getCompletedSteps()+1);
        wRepo.save(w);
        return s;
    }

    public WorkflowStep rejectStep(Long stepId, String rejector, String reason) {
        WorkflowStep s = sRepo.findById(stepId).orElseThrow(()->new RuntimeException("Step not found: "+stepId));
        s.setStatus("REJECTED"); s.setCompletedBy(rejector); s.setNotes(reason); s.setCompletedAt(LocalDateTime.now());
        sRepo.save(s);
        WorkflowInstance w = wRepo.findById(s.getWorkflowInstanceId()).orElseThrow();
        w.setStatus("REJECTED"); w.setRejectionReason(reason); wRepo.save(w);
        return s;
    }

    public Map<String,Object> summary(Long loanId) {
        WorkflowInstance w = getByLoan(loanId);
        List<WorkflowStep> steps = getSteps(w.getId());
        long done = steps.stream().filter(s->List.of("COMPLETED","APPROVED").contains(s.getStatus())).count();
        long pending = steps.stream().filter(s->"PENDING".equals(s.getStatus())).count();
        long inProg = steps.stream().filter(s->"IN_PROGRESS".equals(s.getStatus())).count();
        return Map.of("loanId",loanId,"workflowId",w.getId(),"status",w.getStatus(),
                      "currentStep",w.getCurrentStep()!=null?w.getCurrentStep():"",
                      "totalSteps",w.getTotalSteps(),"completedSteps",done,
                      "pendingSteps",pending,"inProgressSteps",inProg,"steps",steps);
    }
}
