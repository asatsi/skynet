package com.bfsi.loan.document.controller;
import com.bfsi.loan.document.entity.Document;
import com.bfsi.loan.document.service.DocumentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController @RequestMapping("/api/v1/documents") @RequiredArgsConstructor
public class DocumentController {
    private final DocumentService svc;
    @GetMapping                              public List<Document>       getAll()                             { return svc.getAll(); }
    @GetMapping("/{id}")                     public Document             getById(@PathVariable Long id)        { return svc.getById(id); }
    @GetMapping("/customer/{cid}")           public List<Document>       byCustomer(@PathVariable Long cid)    { return svc.getByCustomer(cid); }
    @GetMapping("/loan/{lid}")               public List<Document>       byLoan(@PathVariable Long lid)        { return svc.getByLoan(lid); }
    @GetMapping("/loan/{lid}/checklist")     public Map<String,Object>   checklist(@PathVariable Long lid)     { return svc.checklistStatus(lid); }
    @PostMapping                             public Document             create(@RequestBody Document d)        { return svc.create(d); }
    @PutMapping("/{id}/verify")             public Document             verify(@PathVariable Long id, @RequestParam(defaultValue="System") String officer){ return svc.verify(id,officer); }
    @PutMapping("/{id}/reject")             public Document             reject(@PathVariable Long id, @RequestBody Map<String,String> body){ return svc.reject(id,body.get("reason")); }
    @DeleteMapping("/{id}")                 public ResponseEntity<Void> delete(@PathVariable Long id)          { return ResponseEntity.noContent().build(); }
}
