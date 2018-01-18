#!/usr/bin/env python3
"""
Data Mesh Implementation - Data Product Framework
Implements domain-oriented data products with self-service capabilities
"""

import json
import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pathlib import Path
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DataProductMetadata:
    """Metadata for a data product"""
    name: str
    domain: str
    version: str
    description: str
    owner: str
    contact_email: str
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    sla: Dict[str, Any]
    schema_version: str
    data_classification: str  # public, internal, confidential, restricted

@dataclass
class DataProductSchema:
    """Schema definition for a data product"""
    fields: List[Dict[str, Any]]
    primary_key: List[str]
    partitioning: Optional[Dict[str, Any]] = None
    indexes: Optional[List[Dict[str, Any]]] = None

@dataclass
class DataProductSLA:
    """Service Level Agreement for a data product"""
    availability: float  # 99.9%
    freshness_minutes: int  # Maximum age of data
    completeness_threshold: float  # Minimum completeness %
    accuracy_threshold: float  # Minimum accuracy %
    response_time_ms: int  # Maximum API response time

class DataProductInterface(ABC):
    """Abstract interface for data products"""
    
    @abstractmethod
    def get_data(self, filters: Dict = None, limit: int = None) -> Dict:
        """Get data from the product"""
        pass
    
    @abstractmethod
    def get_schema(self) -> DataProductSchema:
        """Get the data schema"""
        pass
    
    @abstractmethod
    def get_metadata(self) -> DataProductMetadata:
        """Get product metadata"""
        pass
    
    @abstractmethod
    def health_check(self) -> Dict:
        """Check product health"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict:
        """Get product metrics"""
        pass

class CustomerDataProduct(DataProductInterface):
    """Customer domain data product"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.metadata = DataProductMetadata(
            name="customer-analytics",
            domain="customer",
            version="1.0.0",
            description="Customer analytics data product with demographics and behavior",
            owner="Customer Analytics Team",
            contact_email="customer-analytics@company.com",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["customer", "analytics", "demographics", "behavior"],
            sla={
                "availability": 99.9,
                "freshness_minutes": 60,
                "completeness_threshold": 95.0,
                "accuracy_threshold": 98.0,
                "response_time_ms": 500
            },
            schema_version="1.0",
            data_classification="internal"
        )
        
        self.schema = DataProductSchema(
            fields=[
                {"name": "customer_id", "type": "string", "nullable": False, "description": "Unique customer identifier"},
                {"name": "customer_name", "type": "string", "nullable": False, "description": "Customer full name"},
                {"name": "email", "type": "string", "nullable": True, "description": "Customer email address"},
                {"name": "segment", "type": "string", "nullable": False, "description": "Customer segment (Premium, Standard, Basic)"},
                {"name": "registration_date", "type": "timestamp", "nullable": False, "description": "Customer registration date"},
                {"name": "total_orders", "type": "integer", "nullable": True, "description": "Total number of orders"},
                {"name": "total_spent", "type": "decimal", "nullable": True, "description": "Total amount spent"},
                {"name": "avg_order_value", "type": "decimal", "nullable": True, "description": "Average order value"},
                {"name": "last_order_date", "type": "timestamp", "nullable": True, "description": "Date of last order"},
                {"name": "customer_lifetime_value", "type": "decimal", "nullable": True, "description": "Calculated CLV"},
                {"name": "churn_risk_score", "type": "decimal", "nullable": True, "description": "Churn risk score (0-1)"}
            ],
            primary_key=["customer_id"],
            partitioning={"field": "registration_date", "type": "monthly"},
            indexes=[
                {"fields": ["segment"], "type": "btree"},
                {"fields": ["email"], "type": "hash"}
            ]
        )
    
    def get_data(self, filters: Dict = None, limit: int = None) -> Dict:
        """Get customer data"""
        # In a real implementation, this would query the actual data source
        sample_data = [
            {
                "customer_id": "CUST001",
                "customer_name": "John Doe",
                "email": "john.doe@email.com",
                "segment": "Premium",
                "registration_date": "2023-01-15T10:30:00Z",
                "total_orders": 25,
                "total_spent": 2500.00,
                "avg_order_value": 100.00,
                "last_order_date": "2024-01-20T14:22:00Z",
                "customer_lifetime_value": 5000.00,
                "churn_risk_score": 0.15
            },
            {
                "customer_id": "CUST002",
                "customer_name": "Jane Smith",
                "email": "jane.smith@email.com",
                "segment": "Standard",
                "registration_date": "2023-03-22T09:15:00Z",
                "total_orders": 12,
                "total_spent": 800.00,
                "avg_order_value": 66.67,
                "last_order_date": "2024-01-18T11:45:00Z",
                "customer_lifetime_value": 1600.00,
                "churn_risk_score": 0.35
            }
        ]
        
        # Apply filters if provided
        if filters:
            filtered_data = []
            for record in sample_data:
                include = True
                for key, value in filters.items():
                    if key in record and record[key] != value:
                        include = False
                        break
                if include:
                    filtered_data.append(record)
            sample_data = filtered_data
        
        # Apply limit if provided
        if limit:
            sample_data = sample_data[:limit]
        
        return {
            "data": sample_data,
            "count": len(sample_data),
            "metadata": {
                "product": self.metadata.name,
                "version": self.metadata.version,
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def get_schema(self) -> DataProductSchema:
        """Get the data schema"""
        return self.schema
    
    def get_metadata(self) -> DataProductMetadata:
        """Get product metadata"""
        return self.metadata
    
    def health_check(self) -> Dict:
        """Check product health"""
        # In a real implementation, this would check data source connectivity,
        # data freshness, quality metrics, etc.
        return {
            "status": "healthy",
            "checks": {
                "data_source_connectivity": "ok",
                "data_freshness": "ok",
                "data_quality": "ok",
                "api_response_time": "ok"
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def get_metrics(self) -> Dict:
        """Get product metrics"""
        return {
            "usage": {
                "daily_requests": 1250,
                "unique_consumers": 15,
                "avg_response_time_ms": 245
            },
            "quality": {
                "completeness": 98.5,
                "accuracy": 99.2,
                "freshness_minutes": 45
            },
            "sla_compliance": {
                "availability": 99.95,
                "response_time": 98.8,
                "data_quality": 99.1
            }
        }

class SalesDataProduct(DataProductInterface):
    """Sales domain data product"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.metadata = DataProductMetadata(
            name="sales-analytics",
            domain="sales",
            version="1.2.0",
            description="Sales analytics data product with transactions and performance metrics",
            owner="Sales Analytics Team",
            contact_email="sales-analytics@company.com",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["sales", "revenue", "transactions", "performance"],
            sla={
                "availability": 99.5,
                "freshness_minutes": 30,
                "completeness_threshold": 99.0,
                "accuracy_threshold": 99.5,
                "response_time_ms": 300
            },
            schema_version="1.2",
            data_classification="internal"
        )
        
        self.schema = DataProductSchema(
            fields=[
                {"name": "order_id", "type": "string", "nullable": False, "description": "Unique order identifier"},
                {"name": "customer_id", "type": "string", "nullable": False, "description": "Customer identifier"},
                {"name": "product_id", "type": "string", "nullable": False, "description": "Product identifier"},
                {"name": "order_date", "type": "timestamp", "nullable": False, "description": "Order date and time"},
                {"name": "quantity", "type": "integer", "nullable": False, "description": "Quantity ordered"},
                {"name": "unit_price", "type": "decimal", "nullable": False, "description": "Unit price"},
                {"name": "total_amount", "type": "decimal", "nullable": False, "description": "Total order amount"},
                {"name": "discount_amount", "type": "decimal", "nullable": True, "description": "Discount applied"},
                {"name": "region", "type": "string", "nullable": False, "description": "Sales region"},
                {"name": "sales_rep_id", "type": "string", "nullable": True, "description": "Sales representative ID"},
                {"name": "order_status", "type": "string", "nullable": False, "description": "Order status"}
            ],
            primary_key=["order_id"],
            partitioning={"field": "order_date", "type": "daily"},
            indexes=[
                {"fields": ["customer_id"], "type": "btree"},
                {"fields": ["order_date"], "type": "btree"},
                {"fields": ["region"], "type": "hash"}
            ]
        )
    
    def get_data(self, filters: Dict = None, limit: int = None) -> Dict:
        """Get sales data"""
        sample_data = [
            {
                "order_id": "ORD001",
                "customer_id": "CUST001",
                "product_id": "PROD001",
                "order_date": "2024-01-20T14:22:00Z",
                "quantity": 2,
                "unit_price": 50.00,
                "total_amount": 100.00,
                "discount_amount": 0.00,
                "region": "North",
                "sales_rep_id": "REP001",
                "order_status": "completed"
            }
        ]
        
        return {
            "data": sample_data,
            "count": len(sample_data),
            "metadata": {
                "product": self.metadata.name,
                "version": self.metadata.version,
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def get_schema(self) -> DataProductSchema:
        return self.schema
    
    def get_metadata(self) -> DataProductMetadata:
        return self.metadata
    
    def health_check(self) -> Dict:
        return {
            "status": "healthy",
            "checks": {
                "data_source_connectivity": "ok",
                "data_freshness": "ok",
                "data_quality": "ok",
                "api_response_time": "ok"
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def get_metrics(self) -> Dict:
        return {
            "usage": {
                "daily_requests": 2100,
                "unique_consumers": 25,
                "avg_response_time_ms": 180
            },
            "quality": {
                "completeness": 99.8,
                "accuracy": 99.9,
                "freshness_minutes": 15
            },
            "sla_compliance": {
                "availability": 99.7,
                "response_time": 99.5,
                "data_quality": 99.8
            }
        }

class DataProductRegistry:
    """Registry for managing data products"""
    
    def __init__(self):
        self.products: Dict[str, DataProductInterface] = {}
        self.load_products()
    
    def load_products(self):
        """Load available data products"""
        # Initialize data products
        self.products["customer-analytics"] = CustomerDataProduct({})
        self.products["sales-analytics"] = SalesDataProduct({})
        
        logger.info(f"Loaded {len(self.products)} data products")
    
    def get_product(self, product_name: str) -> DataProductInterface:
        """Get a data product by name"""
        if product_name not in self.products:
            raise ValueError(f"Data product '{product_name}' not found")
        return self.products[product_name]
    
    def list_products(self) -> List[Dict]:
        """List all available data products"""
        products_list = []
        for name, product in self.products.items():
            metadata = product.get_metadata()
            products_list.append({
                "name": metadata.name,
                "domain": metadata.domain,
                "version": metadata.version,
                "description": metadata.description,
                "owner": metadata.owner,
                "tags": metadata.tags,
                "data_classification": metadata.data_classification
            })
        return products_list
    
    def get_product_catalog(self) -> Dict:
        """Get complete product catalog"""
        catalog = {
            "products": self.list_products(),
            "domains": list(set(p.get_metadata().domain for p in self.products.values())),
            "total_products": len(self.products),
            "generated_at": datetime.now().isoformat()
        }
        return catalog

# FastAPI application for data mesh API
app = FastAPI(title="Data Mesh API", version="1.0.0")
registry = DataProductRegistry()

class DataRequest(BaseModel):
    filters: Optional[Dict] = None
    limit: Optional[int] = None

@app.get("/")
def root():
    return {"message": "Data Mesh API", "version": "1.0.0"}

@app.get("/catalog")
def get_catalog():
    """Get the complete data product catalog"""
    return registry.get_product_catalog()

@app.get("/products")
def list_products():
    """List all available data products"""
    return registry.list_products()

@app.get("/products/{product_name}")
def get_product_info(product_name: str):
    """Get information about a specific data product"""
    try:
        product = registry.get_product(product_name)
        metadata = product.get_metadata()
        schema = product.get_schema()
        
        return {
            "metadata": asdict(metadata),
            "schema": asdict(schema)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/products/{product_name}/data")
def get_product_data(product_name: str, request: DataRequest):
    """Get data from a specific data product"""
    try:
        product = registry.get_product(product_name)
        return product.get_data(request.filters, request.limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/products/{product_name}/health")
def get_product_health(product_name: str):
    """Get health status of a data product"""
    try:
        product = registry.get_product(product_name)
        return product.health_check()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/products/{product_name}/metrics")
def get_product_metrics(product_name: str):
    """Get metrics for a data product"""
    try:
        product = registry.get_product(product_name)
        return product.get_metrics()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/domains/{domain_name}/products")
def get_domain_products(domain_name: str):
    """Get all products for a specific domain"""
    domain_products = []
    for product in registry.products.values():
        metadata = product.get_metadata()
        if metadata.domain == domain_name:
            domain_products.append({
                "name": metadata.name,
                "version": metadata.version,
                "description": metadata.description
            })
    
    if not domain_products:
        raise HTTPException(status_code=404, detail=f"No products found for domain '{domain_name}'")
    
    return {"domain": domain_name, "products": domain_products}

def main():
    """Run the Data Mesh API server"""
    logger.info("Starting Data Mesh API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()