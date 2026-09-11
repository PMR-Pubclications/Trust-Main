package com.legacytrust.security;

import java.io.IOException;
import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.annotation.WebFilter;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@WebFilter(urlPatterns = {"/admin/*", "/admin/*"})
public class SecurityFilter implements Filter {

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        // Initialization logic if needed
    }

    private boolean isStaticResource(String uri) {
        return uri.endsWith(".css") || uri.endsWith(".js") || uri.endsWith(".png") || uri.endsWith(".jpg")
                || uri.endsWith(".jpeg") || uri.endsWith(".gif") || uri.endsWith(".svg") || uri.endsWith(".ico")
                || uri.endsWith(".woff") || uri.endsWith(".woff2") || uri.endsWith(".ttf") || uri.endsWith(".map")
                || uri.endsWith(".html") || uri.endsWith(".json") || uri.endsWith("/manifest.json");
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        HttpSession session = httpRequest.getSession(false);

        boolean isLoggedIn = (session != null && session.getAttribute("adminUser") != null);
        String requestUri = httpRequest.getRequestURI();
        String context = httpRequest.getContextPath();

        String loginServletPath = context + "/login";
        String loginPage = context + "/login.jsp";
        String logoutPath = context + "/logout";

        boolean isLoginRequest = requestUri.equals(loginServletPath);
        boolean isLoginPage = requestUri.equals(loginPage) || requestUri.endsWith("/login.jsp");
        boolean isLogoutRequest = requestUri.equals(logoutPath);
        boolean isHealth = requestUri.equals(context + "/health") || requestUri.equals(context + "/health/");
        boolean isStatic = isStaticResource(requestUri);

        // Allow access to static resources, login/logout/health endpoints, and the login page
        if (isLoggedIn || isLoginRequest || isLoginPage || isLogoutRequest || isHealth || isStatic) {
            chain.doFilter(request, response);
            return;
        }

        // Otherwise redirect to login page
        httpResponse.sendRedirect(context + "/login.jsp");
    }

    @Override
    public void destroy() {
        // Cleanup logic if needed
    }
}
