const productList = document.getElementById("product-list");
const loadingIndicator = document.getElementById("loading");
const modal = document.getElementById("product-modal");
const modalImage = document.getElementById("modal-image");
const modalTitle = document.getElementById("modal-title");
const modalDescription = document.getElementById("modal-description");
const modalPrice = document.getElementById("modal-price");
const modalAddToCart = document.getElementById("modal-add-to-cart");
const closeModal = document.getElementById("close-modal");
const API_CLOTHES_URL = "https://fakestoreapi.com/products";
const API_BOOKS_URL = "https://openlibrary.org/subjects/fantasy.json?limit=10";

let currentProduct = null;
let currentRoute = "Clothes";

document.getElementById("clothes-button").addEventListener("click", () => {
  currentRoute = "Clothes";
  fetchProducts(API_CLOTHES_URL);
});

document.getElementById("books-button").addEventListener("click", () => {
  currentRoute = "Books";
  fetchBooks();
});

/**
 * Log an event to the backend
 */
function logEvent(action, details, route) {
  const event = {
    action,
    ...details,
    route: route,
    agent: getBrowserName(),
  };
  console.log("event ", event);
  fetch("http://localhost:3000/logs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(event),
  }).catch((error) => console.error("Error logging event:", error));
}

/**
 * Get Browser name
 */ function getBrowserName() {
  const userAgent = navigator.userAgent;
  let browserName;

  if (userAgent.indexOf("Chrome") > -1) {
    browserName = "Chrome";
  } else if (userAgent.indexOf("Firefox") > -1) {
    browserName = "Firefox";
  } else if (userAgent.indexOf("Safari") > -1) {
    browserName = "Safari";
  } else if (
    userAgent.indexOf("MSIE") > -1 ||
    userAgent.indexOf("Trident") > -1
  ) {
    browserName = "Internet Explorer";
  } else {
    browserName = "Unknown";
  }

  return browserName;
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
            <img src="${product.image || product.cover}" alt="${product.title}">
            <h4>${product.title}</h4>
            <p>${
              product.price
                ? "$" + product.price.toFixed(2)
                : "No price available"
            }</p>
            <button>Buy</button>
        `;

    let hoverTimeout = null;

    // Hover event (after 1 second)
    productDiv.addEventListener("mouseenter", () => {
      hoverTimeout = setTimeout(() => {
        logEvent(
          `HOVER`,
          {
            product: product.title,
            price: product.price,
          },
          currentRoute + " home"
        );
      }, 1000);
    });

    productDiv.addEventListener("mouseleave", () => {
      clearTimeout(hoverTimeout);
    });

    // Buy button event (home page)
    productDiv.querySelector("button").addEventListener("click", (e) => {
      e.stopPropagation();
      logEvent(
        `BUY`,
        {
          product: product.title,
          price: product.price,
        },
        currentRoute + " home"
      );
      alert(`${product.title} added to cart!`);
    });

    // Product click event for details
    productDiv.addEventListener("click", () => {
      logEvent(
        `ENTER_PRODUCT_DETAILS`,
        {
          product: product.title,
          price: product.price,
        },
        currentRoute + " details"
      );
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
  modalImage.src = product.image || product.cover;
  modalTitle.textContent = product.title;
  modalDescription.textContent =
    product.description || "No description available";
  modalPrice.textContent = product.price ? product.price.toFixed(2) : "N/A";
  modal.style.display = "flex";
}

// Close modal
closeModal.addEventListener("click", () => {
  modal.style.display = "none";
});

// Modal Buy event (inside product details)
modalAddToCart.addEventListener("click", () => {
  logEvent(
    `BUY`,
    {
      product: currentProduct.title,
      price: currentProduct.price,
    },
    currentRoute + " details"
  );
  alert(`${currentProduct.title} added to cart!`);
});

/**
 * Fetch and display clothes
 */
function fetchProducts(apiUrl) {
  loadingIndicator.classList.add("loading-visible");
  productList.style.display = "none";
  setTimeout(() => {
    loadingIndicator.style.display = "block";
    fetch(apiUrl)
      .then((response) => response.json())
      .then((products) => {
        productList.innerHTML = ""; // Clear previous products
        renderProducts(products);
        productList.style.display = "grid"; // Show products after loading
      })
      .catch((error) => console.error("Error fetching products:", error));
  }, 500);
}

/**
 * Fetch and display books
 */
function fetchBooks() {
  loadingIndicator.classList.add("loading-visible");
  productList.style.display = "none";
  setTimeout(() => {
    loadingIndicator.style.display = "block";
    fetch(API_BOOKS_URL)
      .then((response) => response.json())
      .then((data) => {
        productList.innerHTML = "";
        renderProducts(
          data.works.map((work) => ({
            title: work.title,
            description: getRandomDescription(),
            cover: work.cover_id
              ? `https://covers.openlibrary.org/b/id/${work.cover_id}-L.jpg`
              : "",
            price: getRandomPrice(),
          }))
        );
        productList.style.display = "grid";
      })
      .catch((error) => console.error("Error fetching books:", error));
  }, 500);
}

/**
 * Get a random price for books
 */
function getRandomPrice() {
  const minPrice = 5;
  const maxPrice = 30;
  return parseFloat(
    (Math.random() * (maxPrice - minPrice) + minPrice).toFixed(2)
  );
}

/**
 * Get a random description for books
 */
function getRandomDescription() {
  const descriptions = [
    "An epic tale of adventure and fantasy.",
    "A mysterious journey that defies logic.",
    "A gripping fantasy that will captivate your mind.",
    "A timeless story of love and loss.",
    "A magical world filled with creatures and surprises.",
  ];
  return descriptions[Math.floor(Math.random() * descriptions.length)];
}

// Initialize the app with clothes by default
fetchProducts(API_CLOTHES_URL);
