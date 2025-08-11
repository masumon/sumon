from .product import (
    add_product,
    get_all_products,
    get_product_by_id,
    update_product,
    delete_product
)

from .stock import (
    add_stock,
    get_stock_by_product,  # ← এখানে ঠিক করা হয়েছে
    reduce_stock
)

from .sale import (
    record_sale,
    get_sales_by_product
)
