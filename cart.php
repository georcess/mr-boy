<!-- ===== CART / ORDER SECTION ===== -->
<section id="cart" class="section">
  <h2>Your Cart 🛒</h2>
  <label for="customer-name"><strong>Customer Name:</strong></label>
  <input type="text" id="customer-name" placeholder="Enter your name">
  <ul id="cart-items"></ul>
  <p><strong>Total:</strong> ₱<span id="cart-total">0</span></p>

  <h3>Add-Ons (Optional)</h3>
  <button id="pearl-btn" onclick="addAddonToLastItem('Pearl', 9)" disabled>Add Pearl ₱9</button>

  <button onclick="showSection('menu')">➕ Add More Items</button>
  <button id="generate-btn" onclick="generateReceipt()" disabled>Generate Receipt</button>
  <button onclick="clearCart()">Cancel Order</button>

  <div id="receipt" style="margin-top:20px; border:1px solid #ccc; padding:10px; display:none;">
    <h3>Receipt 🧾</h3>
    <p><strong>Customer:</strong> <span id="receipt-name"></span></p>
    <ul id="receipt-items"></ul>
    <p><strong>Total:</strong> ₱<span id="receipt-total"></span></p>
    <hr>
    <p style="font-style: italic; text-align:center;">"Mr. Boy SpecialTea"</p>
    <h4 style="text-align:center; color:green;">✅ Thank you for your order! We appreciate your support.</h4>
  </div>
</section>
