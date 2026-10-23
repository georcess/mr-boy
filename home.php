<!-- ===== HOME SECTION ===== -->
<div id="home" class="section active">
  <header class="hero">
    <div class="hero-text">
      <div class="hero h1"></div>
    </div>
    <section class="logo">
      <img src="public/images/IMG_2476.jpeg" alt="Mr. Boy SpecialTea Logo" />
      <h2>Mr. Boy SpecialTea</h2>
      <p>Dela Costa V, Burgos Montalban</p>
    </section>
  </header>

  <!-- ===== FEATURED CATEGORY PRODUCTS CAROUSEL SLIDER ===== -->
  <section class="featured-slider-section">
    <div class="section-badge">✨ HIGHLIGHTED CATEGORY FAVORITES</div>
    <h2 class="slider-title">Featured From Every Category</h2>
    <p class="slider-subtitle">Explore 1 top customer choice from each drink and snack line with smooth sliding!</p>

    <!-- Category Switcher Tabs -->
    <div class="slider-category-tabs">
      <button class="cat-pill active" onclick="jumpToSlide(0)">Milktea 🧋</button>
      <button class="cat-pill" onclick="jumpToSlide(1)">Iced Coffee ☕</button>
      <button class="cat-pill" onclick="jumpToSlide(2)">Fruit Tea 🍹</button>
      <button class="cat-pill" onclick="jumpToSlide(3)">Frappé 🥤</button>
      <button class="cat-pill" onclick="jumpToSlide(4)">Hot Cups ☕</button>
      <button class="cat-pill" onclick="jumpToSlide(5)">Snacks 🍟</button>
    </div>

    <div class="carousel-container" onmouseenter="pauseSlider()" onmouseleave="resumeSlider()">
      <!-- Nav Arrows -->
      <button class="carousel-arrow prev" onclick="prevSlide()" aria-label="Previous Slide">&#10094;</button>
      <button class="carousel-arrow next" onclick="nextSlide()" aria-label="Next Slide">&#10095;</button>

      <!-- Slides Wrapper -->
      <div class="carousel-track" id="carousel-track">
        
        <!-- Slide 1: Milktea -->
        <div class="carousel-slide active">
          <div class="slide-card">
            <div class="slide-image-col">
              <span class="slide-tag">⭐ Bestseller</span>
              <img src="public/images/Taro.jpeg" alt="CreamCheese Purple Taro">
              <span class="slide-price-pill">Starts ₱29</span>
            </div>
            <div class="slide-info-col">
              <span class="slide-cat-label">🧋 MILKTEA</span>
              <h3>CreamCheese Purple Taro</h3>
              <p>Rich, velvety purple taro blended with our signature silky creamcheese foam. A crowd favorite with balanced sweetness.</p>
              <div class="slide-actions">
                <button onclick="addToCart('CreamCheese Purple Taro 16oz', 29)" class="btn-primary-order">Order 16oz &bull; ₱29</button>
                <button onclick="addToCart('CreamCheese Purple Taro 22oz', 39)" class="btn-primary-order">Order 22oz &bull; ₱39</button>
                <button onclick="showSection('menu')" class="btn-outline-view">View Menu &rarr;</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Slide 2: Iced Coffee -->
        <div class="carousel-slide">
          <div class="slide-card">
            <div class="slide-image-col">
              <span class="slide-tag">🔥 Top Pick</span>
              <img src="public/images/caramelmacchiato.jpg" alt="Caramel Macchiato">
              <span class="slide-price-pill">Starts ₱29</span>
            </div>
            <div class="slide-info-col">
              <span class="slide-cat-label">☕ ICED COFFEE</span>
              <h3>Caramel Macchiato</h3>
              <p>Bold dark espresso layered over chilled fresh milk and crowned with luscious handcrafted golden caramel drizzle.</p>
              <div class="slide-actions">
                <button onclick="addToCart('Caramel Macchiato 16oz', 29)" class="btn-primary-order">Order 16oz &bull; ₱29</button>
                <button onclick="addToCart('Caramel Macchiato 22oz', 39)" class="btn-primary-order">Order 22oz &bull; ₱39</button>
                <button onclick="showSection('menu')" class="btn-outline-view">View Menu &rarr;</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Slide 3: Fruit Tea -->
        <div class="carousel-slide">
          <div class="slide-card">
            <div class="slide-image-col">
              <span class="slide-tag">🌴 Refreshing</span>
              <img src="public/images/passionfruit.jpg" alt="Passion Fruit Tea">
              <span class="slide-price-pill">Starts ₱29</span>
            </div>
            <div class="slide-info-col">
              <span class="slide-cat-label">🍹 FRUIT TEA</span>
              <h3>Passion Fruit Tea</h3>
              <p>Zesty and tangy tropical passion fruit infused with freshly brewed fragrant jasmine tea. Refreshingly crisp.</p>
              <div class="slide-actions">
                <button onclick="addToCart('Passion Fruit 16oz', 29)" class="btn-primary-order">Order 16oz &bull; ₱29</button>
                <button onclick="addToCart('Passion Fruit 22oz', 39)" class="btn-primary-order">Order 22oz &bull; ₱39</button>
                <button onclick="showSection('menu')" class="btn-outline-view">View Menu &rarr;</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Slide 4: Frappe -->
        <div class="carousel-slide">
          <div class="slide-card">
            <div class="slide-image-col">
              <span class="slide-tag">✨ Creamy Delight</span>
              <img src="public/images/blueberryburstfrappee.jpg" alt="Blueberry Burst Frappé">
              <span class="slide-price-pill">Starts ₱29</span>
            </div>
            <div class="slide-info-col">
              <span class="slide-cat-label">🥤 FRAPPÉ</span>
              <h3>Blueberry Burst Frappé</h3>
              <p>Decadent cream-based blueberry ice blend with rich berry swirls, topped with fluffy whipped cream.</p>
              <div class="slide-actions">
                <button onclick="addToCart('Blueberry Burst 16oz', 29)" class="btn-primary-order">Order 16oz &bull; ₱29</button>
                <button onclick="addToCart('Blueberry Burst 22oz', 39)" class="btn-primary-order">Order 22oz &bull; ₱39</button>
                <button onclick="showSection('menu')" class="btn-outline-view">View Menu &rarr;</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Slide 5: Hot Cups -->
        <div class="carousel-slide">
          <div class="slide-card">
            <div class="slide-image-col">
              <span class="slide-tag">☕ Warm Comfort</span>
              <img src="public/images/hotcaramelmacchiato.jpg" alt="Hot Caramel Macchiato">
              <span class="slide-price-pill">₱35</span>
            </div>
            <div class="slide-info-col">
              <span class="slide-cat-label">☕ HOT CUPS</span>
              <h3>Hot Caramel Macchiato</h3>
              <p>Warm, aromatic brewed espresso with steamed velvety milk and soothing caramel notes to comfort your morning.</p>
              <div class="slide-actions">
                <button onclick="addToCart('Hot Caramel Macchiato 12oz', 35)" class="btn-primary-order">Order 12oz &bull; ₱35</button>
                <button onclick="showSection('menu')" class="btn-outline-view">View Menu &rarr;</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Slide 6: Snacks -->
        <div class="carousel-slide">
          <div class="slide-card">
            <div class="slide-image-col">
              <span class="slide-tag">🍟 Crispy Snack</span>
              <img src="public/images/fries.jpeg" alt="French Fries">
              <span class="slide-price-pill">Starts ₱29</span>
            </div>
            <div class="slide-info-col">
              <span class="slide-cat-label">🍟 SNACKS</span>
              <h3>Crispy French Fries</h3>
              <p>Golden, crispy seasoned fries fried fresh to perfection. The ultimate companion to your favorite drinks.</p>
              <div class="slide-actions">
                <button onclick="addToCart('French Fries Medium', 29)" class="btn-primary-order">Order Medium &bull; ₱29</button>
                <button onclick="addToCart('French Fries Large', 49)" class="btn-primary-order">Order Large &bull; ₱49</button>
                <button onclick="showSection('menu')" class="btn-outline-view">View Menu &rarr;</button>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Pagination Dots -->
      <div class="carousel-dots" id="carousel-dots">
        <span class="dot active" onclick="jumpToSlide(0)"></span>
        <span class="dot" onclick="jumpToSlide(1)"></span>
        <span class="dot" onclick="jumpToSlide(2)"></span>
        <span class="dot" onclick="jumpToSlide(3)"></span>
        <span class="dot" onclick="jumpToSlide(4)"></span>
        <span class="dot" onclick="jumpToSlide(5)"></span>
      </div>
    </div>
  </section>

  <!-- ===== OUR APPROACH ===== -->
  <section class="light">
    <h2>Our Approach</h2>
    <p>Here's how we make it better.</p>

    <div class="card-grid">
      <div class="card small">
        <h3>Simple Flavors</h3>
        <p>Easy, balanced blends.</p>
      </div>

      <div class="card small">
        <h3>Clean Labels</h3>
        <p>Clear, honest ingredients.</p>
      </div>

      <div class="card small">
        <h3>Ethically Sourced</h3>
        <p>Fair &amp; sustainable farms.</p>
      </div>

      <div class="card small">
        <h3>Balanced Sweetness</h3>
        <p>Naturally brewed, lightly sweetened.</p>
      </div>
    </div>
  </section>

  <section class="cta">
    <p>&ldquo;Welcome to Mr.Boy SpecialTea. Enjoy the taste of our drinks at an affordable price! From Milk Tea, Fruit Tea, and Coffee!&rdquo;</p>
    <button id="start-ordering">Start Ordering</button>
  </section>
</div>
