package com.Xincronix.controller;

import java.util.List;
import java.util.Map;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** Temporary endpoint retained for the administration view during migration. */
@RestController
public class AdminCompatibilityController {

    @RequestMapping("/admin/**")
    public Map<String, Object> adminApi() {
        return Map.of("status", "success", "data", List.of());
    }
}
