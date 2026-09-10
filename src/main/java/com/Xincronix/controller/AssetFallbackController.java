package com.Xincronix.controller;

import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Compatibility endpoints for assets referenced by the migrated Laravel views.
 * They prevent broken resource URLs while the original asset bundle is moved to
 * {@code src/main/resources/static/assets}.
 */
@RestController
public class AssetFallbackController {

    @GetMapping(value = "/assets/css/**", produces = "text/css")
    public String stylesheet() {
        return ":root{--xnx-primary:#2a5bff}body{min-height:100vh}.xnx-sidebar-item{display:flex;align-items:center}";
    }

    @GetMapping(value = "/assets/js/**", produces = "application/javascript")
    public String javascript() {
        return "/* The legacy asset bundle has not yet been imported. */";
    }

    @GetMapping(value = "/assets/img/**", produces = "image/svg+xml")
    public ResponseEntity<String> image() {
        return ResponseEntity.ok().contentType(MediaType.valueOf("image/svg+xml"))
                .body("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 80 80\"><rect width=\"80\" height=\"80\" rx=\"16\" fill=\"#2a5bff\"/><text x=\"40\" y=\"51\" text-anchor=\"middle\" fill=\"white\" font-family=\"Arial\" font-size=\"24\" font-weight=\"bold\">XN</text></svg>");
    }
}
