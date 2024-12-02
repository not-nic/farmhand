package uk.notnic.farmhand.service;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import uk.notnic.farmhand.dto.AuthenticationRequest;
import uk.notnic.farmhand.dto.RegisterRequest;
import uk.notnic.farmhand.model.Role;
import uk.notnic.farmhand.model.User;
import uk.notnic.farmhand.repository.UserRepository;

import java.util.Collections;

@Service
public class AuthenticationService {

  private final UserRepository userRepository;
  private final PasswordEncoder passwordEncoder;
  private final JwtTokenService jwtTokenService;
  private final AuthenticationManager authenticationManager;

  public AuthenticationService(
        UserRepository userRepository,
        PasswordEncoder passwordEncoder,
        JwtTokenService jwtTokenService,
        AuthenticationManager authenticationManager) {
    this.userRepository = userRepository;
    this.passwordEncoder = passwordEncoder;
    this.jwtTokenService = jwtTokenService;
    this.authenticationManager = authenticationManager;
  }

  /**
   * Registers a new user.
   * @param request the request containing user details (username, email, password).
   * @return A ResponseEntity containing either a success message and a token, or an error message if
   * a username or email already exists.
   */
  public ResponseEntity<?> registerUser(RegisterRequest request) {

    // check if a username already exists, either by this user or another.
    if (userRepository.existsByUsername(request.getUsername())) {
      return ResponseEntity
              .status(HttpStatus.BAD_REQUEST)
              .body("A user with this username already exists");
    }

    // check if the user already has an account, by checking their email.
    if (userRepository.existsByEmail(request.getEmail())) {
      return ResponseEntity
              .status(HttpStatus.BAD_REQUEST)
              .body("A user with this email already exists");
    }

    // create new user details
    User newUser = new User(
            null,
            request.getUsername(),
            request.getEmail(),
            passwordEncoder.encode(request.getPassword()),
            Role.USER
    );

    // save new user
    userRepository.save(newUser);

    // give the new user their JWT token
    String jwtToken = jwtTokenService.generateToken(newUser);
    return ResponseEntity.ok().body(Collections.singletonMap("Token", jwtToken));
  }

  /**
   * Authenticates an existing user with a new token.
   * @param request the request containing user details (username & password).
   * @return A ResponseEntity containing either a success message and a new token, or an error message if
   * details are not recognised.
   */
  public ResponseEntity<?> authUser(AuthenticationRequest request) {
    // try to authenticate the user by checking their username and password.
    try {
      authenticationManager.authenticate(
          new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
      );

      User user = userRepository.findByUsername(request.getUsername()).orElseThrow();

      String jwtToken = jwtTokenService.generateToken(user);
      return ResponseEntity.ok(Collections.singletonMap("Token", jwtToken));

      // catch AuthenticationException as the user details are incorrect.
    } catch (AuthenticationException e) {
      return ResponseEntity
              .status(HttpStatus.UNAUTHORIZED)
              .body("Invalid username or password.");
    }
  }
}
