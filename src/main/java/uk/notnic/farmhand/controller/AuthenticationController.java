package uk.notnic.farmhand.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import uk.notnic.farmhand.dto.AuthenticationRequest;
import uk.notnic.farmhand.dto.RegisterRequest;
import uk.notnic.farmhand.service.AuthenticationService;

@RestController
@RequestMapping("/api/auth")
public class AuthenticationController {

  private final AuthenticationService authenticationService;

  public AuthenticationController(AuthenticationService authenticationService) {
    this.authenticationService = authenticationService;
  }

  @PostMapping("/register")
  public ResponseEntity<?> registerUser(@RequestBody RegisterRequest registerRequest) {
    return ResponseEntity.ok(authenticationService.registerUser(registerRequest));
  }

  @PostMapping("/login")
  public ResponseEntity<?> login(@RequestBody AuthenticationRequest authenticationRequest) {
    return ResponseEntity.ok(authenticationService.authUser(authenticationRequest));
  }

}
