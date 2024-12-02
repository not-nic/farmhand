package uk.notnic.farmhand.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/hello")
public class HelloWorldController {

    @GetMapping("")
    public ResponseEntity<String> getUserNotes(Authentication authentication) {
        return ResponseEntity.ok(String.format("Hello %s!", authentication.getName()));
    }
}
