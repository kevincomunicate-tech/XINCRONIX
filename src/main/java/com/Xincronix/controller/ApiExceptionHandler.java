package com.Xincronix.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.DisabledException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

import java.util.LinkedHashMap;
import java.util.Map;

@RestControllerAdvice
public class ApiExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<Map<String, Object>> validation(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new LinkedHashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error -> errors.put(error.getField(), error.getDefaultMessage()));
        return ResponseEntity.unprocessableEntity().body(Map.of("success", false, "message", "Revisa los datos enviados", "errors", errors));
    }

    @ExceptionHandler({BadCredentialsException.class, DisabledException.class})
    ResponseEntity<Map<String, Object>> authentication(Exception ex) {
        String message = ex instanceof DisabledException ? "Tu cuenta está inactiva" : "Correo o contraseña incorrectos";
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("success", false, "message", message));
    }

    @ExceptionHandler(ResponseStatusException.class)
    ResponseEntity<Map<String, Object>> status(ResponseStatusException ex) {
        return ResponseEntity.status(ex.getStatusCode()).body(Map.of("success", false, "message", ex.getReason()));
    }
}
