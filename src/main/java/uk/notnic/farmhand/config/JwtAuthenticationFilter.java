package uk.notnic.farmhand.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import uk.notnic.farmhand.service.JwtTokenService;

import java.io.IOException;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

  private final JwtTokenService jwtTokenService;
  private final UserDetailsService userDetailsService;

  public JwtAuthenticationFilter(JwtTokenService jwtTokenService, UserDetailsService userDetailsService) {
    this.jwtTokenService = jwtTokenService;
    this.userDetailsService = userDetailsService;
  }

  @Override
  protected void doFilterInternal(
    HttpServletRequest request,
    HttpServletResponse response,
    FilterChain filterChain
  ) throws ServletException, IOException {

    final String header = request.getHeader("Authorization");

    if (header == null || !header.startsWith("Bearer")) {
      filterChain.doFilter(request, response);
      return;
    }

    final String jwtToken = header.substring(7);
    final String username = jwtTokenService.extractUsername(jwtToken);
    final SecurityContext securityContext = SecurityContextHolder.getContext();

    // check if user exists, but is not authenticated.
    if (username != null && securityContext.getAuthentication() == null) {

      // get username from database
      UserDetails userDetails = this.userDetailsService.loadUserByUsername(username);

      // if the JWT token is valid grant the user a username & password auth token.
      if (jwtTokenService.validToken(jwtToken, userDetails)) {
        UsernamePasswordAuthenticationToken authenticationToken = new UsernamePasswordAuthenticationToken(
          userDetails,
          null,
          userDetails.getAuthorities()
        );

        // set user details to the authentication token.
        authenticationToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));


        // update the security context of this username & password authentication.
        securityContext.setAuthentication(authenticationToken);
      }
    }

    filterChain.doFilter(request, response);
  }
}
