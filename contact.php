<!-- ===== CONTACT SECTION ===== -->
<section id="contact" class="section">
  <h2>Contact Us</h2>
  <p><strong>Address:</strong> Blk 14 Lot 4 Phase 1 Dela Costa Homes V Burgos Rodriguez Rizal, Rodriguez, Philippines, 1860</p>
  <p><strong>Phone:</strong> 0917 888 4737</p>
  <p><strong>Email:</strong> <a href="mailto:mrboyspecialteadelacosta@gmail.com">mrboyspecialteadelacosta@gmail.com</a></p>
  <form action="api/save_contact.php" method="POST" class="contact-form">
    <input type="text" name="name" placeholder="Your name" class="form-input" required>
    <input type="email" name="email" placeholder="Your email" class="form-input" required>
    <input type="text" name="contact" placeholder="Your contact" class="form-input" required>
    <textarea name="message" placeholder="Your message" class="form-input" required></textarea>
    <button type="submit" class="submit-button">Submit</button>
  </form>
</section>
