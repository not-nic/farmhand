package uk.notnic.farmhand.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
public class SecurityConfiguration {

  private final JwtAuthenticationFilter jwtAuthenticationFilter;
  private final AuthenticationProvider authenticationProvider;

  public SecurityConfiguration(JwtAuthenticationFilter jwtAuthenticationFilter,
                               AuthenticationProvider authenticationProvider) {
    this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    this.authenticationProvider = authenticationProvider;
  }

  /**
   * Define a custom SecurityFilterChain so that anyone can sign up but only authorised users can view notes.
   * @param http The HttpSecurity object used to configure security rules.
   * @return A SecurityFilterChain.
   * @throws Exception If there's an error during configuration.
   */
  @Bean
  public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http.csrf(AbstractHttpConfigurer::disable)
      .authorizeHttpRequests(auth -> auth
              .requestMatchers("/api/auth/**").permitAll() // allow everyone to access the auth API to sign up.
              .requestMatchers("/api/**").authenticated() // only allow authenticated users to access notes.
      )
      .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
      .authenticationProvider(authenticationProvider)
      .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
    return http.build();
  }
}
