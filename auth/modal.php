<!-- ===== AUTH MODAL (LOGIN / REGISTER) ===== -->
<div id="auth-modal" class="auth-modal" style="display: none;">
  <div class="auth-modal-overlay" onclick="closeAuthModal()"></div>
  <div class="auth-modal-card">
    <button class="auth-close-btn" onclick="closeAuthModal()">&times;</button>
    
    <div class="auth-tabs">
      <button id="tab-login-btn" class="auth-tab active" onclick="switchAuthTab('login')">Login</button>
      <button id="tab-register-btn" class="auth-tab" onclick="switchAuthTab('register')">Register</button>
    </div>

    <div id="auth-alert" class="auth-alert" style="display: none;"></div>

    <!-- LOGIN FORM -->
    <form id="login-form" class="auth-form" onsubmit="handleLogin(event)">
      <div class="auth-input-group">
        <label for="login-username">Username or Email</label>
        <input type="text" id="login-username" class="auth-input" placeholder="Enter username or email" required autocomplete="username">
      </div>
      <div class="auth-input-group">
        <label for="login-password">Password</label>
        <input type="password" id="login-password" class="auth-input" placeholder="Enter password" required autocomplete="current-password">
      </div>
      <button type="submit" id="login-submit-btn" class="auth-submit-btn">Login ☕</button>
      <p class="auth-footer-text">
        Don't have an account? <a href="javascript:void(0)" onclick="switchAuthTab('register')">Register here</a>
      </p>
    </form>

    <!-- REGISTER FORM -->
    <form id="register-form" class="auth-form" onsubmit="handleRegister(event)" style="display: none;">
      <div class="auth-input-group">
        <label for="reg-fullname">Full Name</label>
        <input type="text" id="reg-fullname" class="auth-input" placeholder="e.g. Juan Dela Cruz" required autocomplete="name">
      </div>
      <div class="auth-input-group">
        <label for="reg-username">Username</label>
        <input type="text" id="reg-username" class="auth-input" placeholder="Choose a username" required autocomplete="username">
      </div>
      <div class="auth-input-group">
        <label for="reg-email">Email Address</label>
        <input type="email" id="reg-email" class="auth-input" placeholder="name@example.com" required autocomplete="email">
      </div>
      <div class="auth-input-group">
        <label for="reg-password">Password (min. 6 characters)</label>
        <input type="password" id="reg-password" class="auth-input" placeholder="Create a password" required minlength="6" autocomplete="new-password">
      </div>
      <button type="submit" id="reg-submit-btn" class="auth-submit-btn">Create Account ✨</button>
      <p class="auth-footer-text">
        Already have an account? <a href="javascript:void(0)" onclick="switchAuthTab('login')">Login here</a>
      </p>
    </form>
  </div>
</div>
