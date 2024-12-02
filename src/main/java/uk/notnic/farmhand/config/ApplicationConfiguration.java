package uk.notnic.farmhand.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import uk.notnic.farmhand.repository.UserRepository;

@Configuration
public class ApplicationConfiguration {

  private final UserRepository userRepository;

  public ApplicationConfiguration(UserRepository userRepository) {
    this.userRepository = userRepository;
  }

  // UserDetailsService bean to find a username in the database.
  @Bean
  public UserDetailsService userDetailsService() {
    return username -> userRepository.findByUsername(username)
        .orElseThrow(() -> new UsernameNotFoundException("User not found"));
  }

  // AuthenticationProvider bean for user authentication.
  @Bean
  public AuthenticationProvider authenticationProvider() {
    DaoAuthenticationProvider daoAuthenticationProvider = new DaoAuthenticationProvider();
    daoAuthenticationProvider.setUserDetailsService(userDetailsService());
    daoAuthenticationProvider.setPasswordEncoder(passwordEncoder());
    return daoAuthenticationProvider;
  }

  // PasswordEncoder bean to hash passwords.
  @Bean
  protected PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();
  }

  // AuthenticationManager bean which manages authentication.
  @Bean
  public AuthenticationManager authenticationManager(AuthenticationConfiguration configuration) throws Exception {
    return configuration.getAuthenticationManager();
  }
}
