// المنتجات مؤقتًا
// لاحقًا سنجعلها تأتي من لوحة الإدارة

const products = [

    {
        id: 1,
        name: "بطاقة عين NFC",
        price: 49,
        icon: "💳",
        description: "بطاقة NFC ذكية وأنيقة"
    },

    {
        id: 2,
        name: "بطاقة عين NFC - أسود",
        price: 59,
        icon: "🖤",
        description: "بطاقة NFC بتصميم أسود"
    }

];


let cart = [];


// عرض المنتجات

function displayProducts() {

    const container =
        document.getElementById("products-container");

    container.innerHTML = "";

    products.forEach(product => {

        const card = document.createElement("div");

        card.className = "product-card";

        card.innerHTML = `

            <div class="product-image">
                ${product.icon}
            </div>

            <div class="product-info">

                <h3>
                    ${product.name}
                </h3>

                <p>
                    ${product.description}
                </p>

                <div class="product-price">
                    ${product.price} ريال
                </div>

                <button
                    class="add-button"
                    onclick="addToCart(${product.id})">

                    أضف للسلة

                </button>

            </div>
        `;

        container.appendChild(card);

    });

}


// إضافة للسلة

function addToCart(productId) {

    const product =
        products.find(p => p.id === productId);

    cart.push(product);

    updateCart();

    alert("تمت إضافة المنتج إلى السلة 🛒");

}


// تحديث السلة

function updateCart() {

    document.getElementById("cart-count")
        .textContent = cart.length;

    const items =
        document.getElementById("cart-items");

    const total =
        document.getElementById("cart-total");

    if (cart.length === 0) {

        items.innerHTML = "السلة فارغة";

        total.textContent = "0";

        return;

    }


    items.innerHTML = "";

    let totalPrice = 0;


    cart.forEach((product, index) => {

        totalPrice += product.price;

        const item =
            document.createElement("div");

        item.style.padding = "10px 0";

        item.innerHTML = `

            ${product.name}
            -
            ${product.price} ريال

            <button
                onclick="removeFromCart(${index})">

                حذف

            </button>

        `;

        items.appendChild(item);

    });


    total.textContent = totalPrice;

}


// حذف من السلة

function removeFromCart(index) {

    cart.splice(index, 1);

    updateCart();

}


// فتح السلة

function openCart() {

    document.getElementById("cart-modal")
        .style.display = "flex";

}


// إغلاق السلة

function closeCart() {

    document.getElementById("cart-modal")
        .style.display = "none";

}


// تشغيل المتجر

displayProducts();