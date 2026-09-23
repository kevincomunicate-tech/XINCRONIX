package com.Xincronix.repository;
import com.Xincronix.model.LoginVerificationCode;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
public interface LoginVerificationCodeRepository extends JpaRepository<LoginVerificationCode, Long> {
    Optional<LoginVerificationCode> findByUsuarioIdUsuario(Integer idUsuario);
}
