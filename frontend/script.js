const productList = document.getElementById("product-list");
const loadingIndicator = document.getElementById("loading");
const modal = document.getElementById("product-modal");
const modalImage = document.getElementById("modal-image");
const modalTitle = document.getElementById("modal-title");
const modalDescription = document.getElementById("modal-description");
const modalPrice = document.getElementById("modal-price");
const modalAddToCart = document.getElementById("modal-add-to-cart");
const closeModal = document.getElementById("close-modal");
const API_URL = "https://fakestoreapi.com/products";

let currentProduct = null;

/**
 * Log an event to the backend
 */
function logEvent(action, details) {
  const event = {
    action,
    ...details,
    route: window.location.pathname,
    agent: navigator.userAgent,
  };
  console.log("event ", event);
  fetch("http://localhost:3000/logs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(event),
  }).catch((error) => console.error("Error logging event:", error));
}

/**
 * Render products dynamically
 */
function renderProducts(products) {
  loadingIndicator.style.display = "none";
  products.forEach((product) => {
    const productDiv = document.createElement("div");
    productDiv.classList.add("product");

    productDiv.innerHTML = `
            <img src="${product.image}" alt="${product.title}">
            <h4>${product.title}</h4>
            <p>$${product.price.toFixed(2)}</p>
            <button>Add to Cart</button>
        `;

    let hoverTimeout = null;

    // Hover event (after 1 seconds)
    productDiv.addEventListener("mouseenter", () => {
      hoverTimeout = setTimeout(() => {
        logEvent("HOVER_PRODUCT", { product: product.title });
      }, 1000);
    });

    productDiv.addEventListener("mouseleave", () => {
      clearTimeout(hoverTimeout);
    });

    // Add to Cart button event (outside product details)
    productDiv.querySelector("button").addEventListener("click", (e) => {
      e.stopPropagation();
      logEvent("ADD_TO_CART_OUTSIDE", {
        product: product.title,
        price: product.price,
      });
      alert(`${product.title} added to cart!`);
    });

    // Product click event for details
    productDiv.addEventListener("click", () => {
      logEvent("ENTER_PRODUCT_DETAILS", { product: product.title });
      showProductDetails(product);
    });

    productList.appendChild(productDiv);
  });
}

/**
 * Show product details in a modal
 */
function showProductDetails(product) {
  currentProduct = product;
  modalImage.src = product.image;
  modalTitle.textContent = product.title;
  modalDescription.textContent = product.description;
  modalPrice.textContent = product.price.toFixed(2);
  modal.style.display = "flex";
}

// Close modal
closeModal.addEventListener("click", () => {
  modal.style.display = "none";
});

// Modal Add to Cart event (inside product details)
modalAddToCart.addEventListener("click", () => {
  logEvent("ADD_TO_CART_INSIDE", {
    product: currentProduct.title,
    price: currentProduct.price,
  });
  alert(`${currentProduct.title} added to cart!`);
});

/**
 * Fetch and display products
 */
function fetchProducts() {
  fetch(API_URL)
    .then((response) => response.json())
    .then((products) => renderProducts(products))
    .catch((error) => console.error("Error fetching products:", error));
}

// Initialize the app
fetchProducts();
