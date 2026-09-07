package com.bfsi.loan.workflow.controller;
import com.bfsi.loan.workflow.entity.WorkflowInstance;
import com.bfsi.loan.workflow.entity.WorkflowStep;
import com.bfsi.loan.workflow.service.WorkflowService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController @RequestMapping("/api/v1/workflows") @RequiredArgsConstructor
public class WorkflowController {
    private final WorkflowService svc;
    @GetMapping                                  public List<WorkflowInstance> getAll()                         { return svc.getAll(); }
    @GetMapping("/{id}")                         public WorkflowInstance       getById(@PathVariable Long id)    { return svc.getById(id); }
    @GetMapping("/loan/{lid}")                   public WorkflowInstance       byLoan(@PathVariable Long lid)    { return svc.getByLoan(lid); }
    @GetMapping("/{id}/steps")                   public List<WorkflowStep>     getSteps(@PathVariable Long id)   { return svc.getSteps(id); }
    @GetMapping("/loan/{lid}/steps")             public List<WorkflowStep>     stepsByLoan(@PathVariable Long lid){ return svc.getStepsByLoan(lid); }
    @GetMapping("/loan/{lid}/summary")           public Map<String,Object>     summary(@PathVariable Long lid)   { return svc.summary(lid); }
    @PostMapping("/initiate")                    public WorkflowInstance       initiate(@RequestBody Map<String,Object> body){
        return svc.initiate(Long.valueOf(body.get("loanApplicationId").toString()),
                            Long.valueOf(body.get("customerId").toString()),
                            body.getOrDefault("officer","SYSTEM").toString());
    }
    @PutMapping("/steps/{sid}/complete")         public WorkflowStep complete(@PathVariable Long sid, @RequestBody Map<String,String> body){ return svc.completeStep(sid,body.getOrDefault("officer","SYSTEM"),body.getOrDefault("notes","")); }
    @PutMapping("/steps/{sid}/approve")          public WorkflowStep approve(@PathVariable Long sid, @RequestBody Map<String,String> body) { return svc.approveStep(sid,body.getOrDefault("approver","SYSTEM"),body.getOrDefault("notes","")); }
    @PutMapping("/steps/{sid}/reject")           public WorkflowStep reject(@PathVariable Long sid, @RequestBody Map<String,String> body)  { return svc.rejectStep(sid,body.getOrDefault("rejector","SYSTEM"),body.get("reason")); }
}
