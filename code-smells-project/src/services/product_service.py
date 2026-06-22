"""Regra de negócio de produtos. Orquestra validação e repositório."""
import logging

from src.models import ProductRepository
from src.services.validators import validate_product

logger = logging.getLogger(__name__)

DEFAULT_CATEGORY = "geral"


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.products = product_repository

    def list_products(self) -> list[dict]:
        products = self.products.find_all()
        logger.info("Produtos listados", extra={"total": len(products)})
        return products

    def get_product(self, product_id: int) -> dict | None:
        return self.products.find_by_id(product_id)

    def search_products(self, term, categoria, min_price, max_price) -> list[dict]:
        return self.products.search(term, categoria, min_price, max_price)

    def create_product(self, data: dict) -> dict:
        """Retorna {'erro': msg} em caso de validação inválida, ou {'id': novo_id}."""
        error = validate_product(data)
        if error:
            return {"erro": error}

        product_id = self.products.create(
            data["nome"],
            data.get("descricao", ""),
            data["preco"],
            data["estoque"],
            data.get("categoria", DEFAULT_CATEGORY),
        )
        logger.info("Produto criado", extra={"product_id": product_id})
        return {"id": product_id}

    def update_product(self, product_id: int, data: dict) -> dict:
        """Retorna {'erro': msg, 'not_found': bool} ou {'updated': True}."""
        if not self.products.find_by_id(product_id):
            return {"erro": "Produto não encontrado", "not_found": True}

        error = validate_product(data)
        if error:
            return {"erro": error}

        self.products.update(
            product_id,
            data["nome"],
            data.get("descricao", ""),
            data["preco"],
            data["estoque"],
            data.get("categoria", DEFAULT_CATEGORY),
        )
        return {"updated": True}

    def delete_product(self, product_id: int) -> dict:
        if not self.products.find_by_id(product_id):
            return {"erro": "Produto não encontrado", "not_found": True}
        self.products.delete(product_id)
        logger.info("Produto deletado", extra={"product_id": product_id})
        return {"deleted": True}
