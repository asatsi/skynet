package com.bfsi.loan.document.repository;
import com.bfsi.loan.document.entity.Document;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface DocumentRepository extends JpaRepository<Document,Long> {
    List<Document> findByCustomerId(Long cid);
    List<Document> findByLoanApplicationId(Long lid);
    List<Document> findByCustomerIdAndLoanApplicationId(Long cid, Long lid);
    List<Document> findByStatus(String status);
}
