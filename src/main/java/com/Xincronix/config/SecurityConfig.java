package com.Xincronix.config;

import java.util.List;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.util.matcher.AntPathRequestMatcher;
import org.springframework.security.web.util.matcher.OrRequestMatcher;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import com.Xincronix.security.AuthCookieService;
import com.Xincronix.security.CustomUserDetailsService;
import com.Xincronix.security.GoogleOAuthSuccessHandler;
import com.Xincronix.security.JwtAuthenticationFilter;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;
    private final CustomUserDetailsService userDetailsService;
    private final AuthCookieService authCookieService;
    private final GoogleOAuthSuccessHandler googleOAuthSuccessHandler;

    public SecurityConfig(JwtAuthenticationFilter jwtAuthFilter,
                          CustomUserDetailsService userDetailsService,
                          AuthCookieService authCookieService,
                          GoogleOAuthSuccessHandler googleOAuthSuccessHandler) {
        this.jwtAuthFilter = jwtAuthFilter;
        this.userDetailsService = userDetailsService;
        this.authCookieService = authCookieService;
        this.googleOAuthSuccessHandler = googleOAuthSuccessHandler;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(
                    "/", "/inicio", "/index.html",
                    "/login", "/Login", "/Login.html", "/auth/Login.html",
                    "/registro", "/Registro", "/registro.html", "/auth/registro.html",
                    "/assets/**", "/css/**", "/js/**", "/img/**",
                    "/error", "/informacion/**", "/favicon.ico",
                    "/reset-password", "/api/auth/**",
                    // Google OAuth
                    "/oauth2/**", "/login/oauth2/**"
                ).permitAll()
                .requestMatchers(HttpMethod.POST,
                    "/login", "/api/auth/login", "/api/auth/register", "/api/auth/registro", "/api/login")
                    .permitAll()
                .requestMatchers("/api/auth/logout", "/api/logout", "/logout").permitAll()
                .requestMatchers("/panel/supervisor", "/supervisor_panel", "/supervisor/**", "/api/supervisor/**")
                    .hasAnyRole("SUPERVISOR", "MANAGER", "ADMINISTRADOR")
                .requestMatchers("/admin/**", "/api/admin/**", "/panel/admin", "/panel/admin/**",
                    "/admin_panel", "/admin/dashboard")
                    .hasRole("ADMINISTRADOR")
                .anyRequest().authenticated()
            )
            .oauth2Login(oauth -> oauth
                .loginPage("/login")
                .successHandler(googleOAuthSuccessHandler)
                .failureUrl("/login?error=google")
            )
            .authenticationProvider(authenticationProvider())
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .logout(logout -> logout
                .logoutRequestMatcher(new OrRequestMatcher(
                        new AntPathRequestMatcher("/logout", "POST"),
                        new AntPathRequestMatcher("/logout", "GET"),
                        new AntPathRequestMatcher("/api/auth/logout", "POST")
                ))
                .logoutSuccessHandler((request, response, authentication) -> {
                    authCookieService.clear(response);
                    if (request.getRequestURI().startsWith("/api/")) {
                        response.setContentType("application/json;charset=UTF-8");
                        response.getWriter().write("{\"success\":true,\"status\":\"success\",\"message\":\"Sesión cerrada\"}");
                    } else {
                        response.sendRedirect("/login?logout");
                    }
                })
                .deleteCookies(AuthCookieService.COOKIE_NAME)
                .permitAll()
            )
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint((request, response, authException) -> {
                    if (wantsJson(request)) {
                        response.setStatus(401);
                        response.setContentType("application/json;charset=UTF-8");
                        response.getWriter().write("{\"success\":false,\"status\":\"error\",\"message\":\"No autenticado\"}");
                    } else {
                        response.sendRedirect("/login");
                    }
                })
                .accessDeniedHandler((request, response, accessDeniedException) -> {
                    if (wantsJson(request)) {
                        response.setStatus(403);
                        response.setContentType("application/json;charset=UTF-8");
                        response.getWriter().write("{\"success\":false,\"status\":\"error\",\"message\":\"Permiso insuficiente\"}");
                    } else {
                        response.sendRedirect("/login");
                    }
                })
            );

        return http.build();
    }

    private static boolean wantsJson(jakarta.servlet.http.HttpServletRequest request) {
        String uri = request.getRequestURI();
        String accept = request.getHeader("Accept");
        String xhr = request.getHeader("X-Requested-With");
        if (uri.startsWith("/api/")) {
            return true;
        }
        if ("XMLHttpRequest".equalsIgnoreCase(xhr)) {
            return true;
        }
        return accept != null && accept.contains("application/json") && !accept.contains("text/html");
    }

    @Bean
    public AuthenticationProvider authenticationProvider() {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userDetailsService);
        provider.setPasswordEncoder(passwordEncoder());
        provider.setHideUserNotFoundExceptions(true);
        return provider;
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOriginPatterns(List.of("*"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);
        config.setExposedHeaders(List.of("Authorization", "Set-Cookie"));

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}
