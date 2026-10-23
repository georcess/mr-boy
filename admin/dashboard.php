<!-- ===== ADMIN DASHBOARD ===== -->
<section id="admin" class="section">
  <h2>Admin Dashboard 📊</h2>

  <!-- Admin Gate: Shown if not logged in as admin -->
  <div id="admin-auth-gate" style="display: none; padding: 40px 20px; max-width: 500px; margin: 20px auto; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <div style="font-size: 48px; margin-bottom: 10px;">🔒</div>
    <h3 style="color: #4b2e2e; margin-bottom: 10px;">Admin Access Restricted</h3>
    <p style="color: #666; margin-bottom: 20px;">You must be logged in as an Administrator to view incoming customer orders and manage store records.</p>
    <button onclick="openAuthModal('login')" style="background-color: #4b2e2e; color: white;">🔑 Login as Admin</button>
  </div>

  <!-- Admin Content: Shown only for admins -->
  <div id="admin-content" style="overflow-x:auto; padding: 20px;">
    <table id="order-table" style="width:100%; border-collapse: collapse; background: white; color: black;">
      <thead>
        <tr style="background-color: #4b2e2e; color: white;">
          <th style="padding: 10px; border: 1px solid #ddd;">Date/Time</th>
          <th style="padding: 10px; border: 1px solid #ddd;">Customer</th>
          <th style="padding: 10px; border: 1px solid #ddd;">Orders</th>
          <th style="padding: 10px; border: 1px solid #ddd;">Total Price</th>
          <th style="padding: 10px; border: 1px solid #ddd;">Action</th>
        </tr>
      </thead>
      <tbody id="admin-order-list">
      </tbody>
    </table>
    <button onclick="clearAllOrders()" style="margin-top: 20px; background: red; color: white;">Clear All Records</button>
  </div>
</section>
