package com.bfsi.loan.customer.repository;

import com.bfsi.loan.customer.entity.Customer;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;

public interface CustomerRepository extends JpaRepository<Customer, Long> {
    @Query("SELECT c FROM Customer c WHERE LOWER(c.companyName) LIKE LOWER(CONCAT('%',:name,'%')) " +
           "OR LOWER(c.firstName) LIKE LOWER(CONCAT('%',:name,'%')) " +
           "OR LOWER(c.lastName) LIKE LOWER(CONCAT('%',:name,'%'))")
    List<Customer> searchByName(@Param("name") String name);
    List<Customer> findByStatus(String status);
    List<Customer> findByCreditScoreGreaterThanEqual(Integer minScore);
}
