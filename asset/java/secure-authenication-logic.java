import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import org.mindrot.jbcrypt.BCrypt; // Recommended library for secure password hashing

@WebServlet("/login")
public class LoginServlet extends HttpServlet {

    protected void doPost(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        String username = request.getParameter("username");
        String passwordInput = request.getParameter("password");

        try (Connection conn = DatabaseConnector.getConnection()) {
            String sql = "SELECT admin_id, username, password_hash, role, is_active FROM legacy_trust_admins WHERE username = ?";
            
            try (PreparedStatement stmt = conn.prepareStatement(sql)) {
                stmt.setString(1, username);
                try (ResultSet rs = stmt.executeQuery()) {
                    if (rs.next()) {
                        boolean isActive = rs.getBoolean("is_active");
                        String storedHash = rs.getString("password_hash");

                        // Verify password using BCrypt and check if account is active
                        if (isActive && BCrypt.checkpw(passwordInput, storedHash)) {
                            // Authentication successful: Create secure session
                            HttpSession session = request.getSession(true);
                            session.setMaxInactiveInterval(900); // Timeout after 15 minutes of inactivity
                            session.setAttribute("adminUser", rs.getString("username"));
                            session.setAttribute("adminRole", rs.getString("role"));

                            response.sendRedirect(request.getContextPath() + "/admin/dashboard.jsp");
                            return;
                        }
                    }
                }
            }
        } catch (Exception e) {
            // Log the exception securely (avoid exposing raw stack traces to users)
            e.printStackTrace();
        }

        // Authentication failed: Redirect back with error
        response.sendRedirect(request.getContextPath() + "/login.jsp?error=InvalidCredentials");
    }
}
